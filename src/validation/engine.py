
from pathlib import Path

import pandas as pd
import yaml

from src.validation.completeness import check_completeness
from src.validation.uniqueness import check_uniqueness
from src.validation.referential_integrity import (
    check_referential_integrity
)
from src.validation.range_check import check_range
from src.validation.freshness import check_freshness
from src.validation.custom_rules import (
    check_allowed_values,
    check_required_when,
    check_email_format
)


def load_rules_config(config_path: str) -> dict:
    """Load validation rules from a YAML file."""

    with open(config_path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def validate_dataset(
    df: pd.DataFrame,
    rules_config: dict,
    reference_datasets: dict = None,
    as_of: pd.Timestamp = None
) -> list:

    reference_datasets = reference_datasets or {}

    if as_of is None:
        as_of = pd.Timestamp.now(tz="UTC")

    dataset_name = rules_config["dataset"]
    results = []

    for rule in rules_config["rules"]:

        rule_id = rule["rule_id"]
        rule_name = rule["name"]
        rule_type = rule["type"]
        column = rule["column"]
        severity = rule["severity"]

        if column not in df.columns:
            raise ValueError(
                f"Column '{column}' missing in dataset '{dataset_name}'"
            )

        # 1. Completeness
        if rule_type == "completeness":
            passed = check_completeness(df, column)

        # 2. Uniqueness
        elif rule_type == "uniqueness":
            passed = check_uniqueness(df, column)

        # 3. Referential integrity
        elif rule_type == "referential_integrity":
            reference_name = rule["reference_dataset"]

            if reference_name not in reference_datasets:
                raise ValueError(
                    f"Reference dataset '{reference_name}' not provided"
                )

            passed = check_referential_integrity(
                df,
                column,
                reference_datasets[reference_name],
                rule["reference_column"]
            )

        # 4. Range
        elif rule_type == "range":
            passed = check_range(
                df,
                column,
                rule["min"],
                rule["max"],
                rule.get("min_inclusive", False),
                rule.get("max_inclusive", True)
            )

        # 5. Freshness
        elif rule_type == "freshness":
            passed = check_freshness(
                df,
                column,
                rule["max_age_hours"],
                as_of
            )

        # 6. Custom rules
        elif rule_type == "custom":

            check_name = rule["check"]

            if check_name == "allowed_values":
                passed = check_allowed_values(
                    df,
                    column,
                    rule["allowed_values"]
                )

            elif check_name == "required_when":
                passed = check_required_when(
                    df,
                    column,
                    rule["condition_column"],
                    rule["condition_value"]
                )

            elif check_name == "email_format":
                passed = check_email_format(df, column)

            else:
                raise ValueError(
                    f"Unsupported custom check: {check_name}"
                )

        else:
            raise ValueError(
                f"Unsupported rule type: {rule_type}"
            )

        failed_rows = df.loc[~passed].copy()

        results.append({
            "dataset": dataset_name,
            "rule_id": rule_id,
            "rule_name": rule_name,
            "rule_type": rule_type,
            "severity": severity,
            "total_records": len(df),
            "passed_records": int(passed.sum()),
            "failed_records": int((~passed).sum()),
            "status": "PASS" if passed.all() else "FAIL",
            "failed_rows": failed_rows
        })

    return results
