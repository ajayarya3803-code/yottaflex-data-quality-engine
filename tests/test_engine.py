
import pandas as pd
import pytest

from src.validation.engine import (
    load_rules_config,
    validate_dataset
)


def test_customers_validation_engine():

    customers = pd.read_csv("data/raw/customers.csv")

    config = load_rules_config(
        "config/rules/customers.yaml"
    )

    results = validate_dataset(
        customers,
        config
    )

    assert len(results) == 6

    for result in results:
        assert result["total_records"] == 10
        assert result["passed_records"] + result["failed_records"] == 10


def test_orders_validation_engine():

    customers = pd.read_csv("data/raw/customers.csv")
    orders = pd.read_csv("data/raw/orders.csv")

    config = load_rules_config(
        "config/rules/orders.yaml"
    )

    results = validate_dataset(
        orders,
        config,
        reference_datasets={"customers": customers},
        as_of=pd.Timestamp("2026-11-11 10:00:00", tz="UTC")
    )

    assert len(results) == 11

    for result in results:
        assert result["total_records"] == 15
        assert result["passed_records"] + result["failed_records"] == 15



def test_empty_customers_dataset():
    df = pd.DataFrame(
        columns=["customer_id", "customer_name", "email", "created_at"]
    )

    config = load_rules_config("config/rules/customers.yaml")

    results = validate_dataset(df, config)

    assert len(results) == 6

    for result in results:
        assert result["total_records"] == 0
        assert result["passed_records"] == 0
        assert result["failed_records"] == 0
        assert result["status"] == "PASS"



def test_missing_required_column():
    df = pd.DataFrame({
        "customer_id": ["C101"],
        "customer_name": ["Alex"]
    })

    config = load_rules_config("config/rules/customers.yaml")

    with pytest.raises(ValueError, match="missing in dataset"):
        validate_dataset(df, config)



def test_malformed_customer_records():
    df = pd.DataFrame({
        "customer_id": ["C101", None, "C103"],
        "customer_name": ["Alex", "Sam", None],
        "email": ["alex@example.com", "invalid-email", "jane@example.com"],
        "created_at": [
            "2026-11-10",
            "2026-11-11",
            "2026-11-12"
        ]
    })

    config = load_rules_config("config/rules/customers.yaml")

    results = validate_dataset(df, config)

    completeness_result = next(
        r for r in results if r["rule_type"] == "completeness"
    )
    email_result = next(
    r for r in results if r["rule_id"] == "CUS005"
    )

    assert completeness_result["failed_records"] == 1
    assert email_result["failed_records"] == 1


def test_cancelled_order_without_reason():
    orders = pd.DataFrame({
        "order_id": ["O201"],
        "customer_id": ["C101"],
        "amount": [500],
        "currency": ["INR"],
        "order_status": ["CANCELLED"],
        "order_timestamp": ["2026-11-10T10:00:00"],
        "cancellation_reason": [None],
        "source_extract_timestamp": ["2026-11-13T10:00:00+00:00"]
    })

    customers = pd.DataFrame({
        "customer_id": ["C101"]
    })

    config = load_rules_config("config/rules/orders.yaml")

    results = validate_dataset(
        orders,
        config,
        reference_datasets={"customers": customers},
        as_of=pd.Timestamp("2026-11-13T10:10:00Z")
    )

    result = next(r for r in results if r["rule_id"] == "ORD007")

    assert result["failed_records"] == 1
    assert result["status"] == "FAIL"


def test_order_with_nonexistent_customer():
    orders = pd.DataFrame({
        "order_id": ["O202"],
        "customer_id": ["C999"],
        "amount": [500],
        "currency": ["INR"],
        "order_status": ["PLACED"],
        "order_timestamp": ["2026-11-10T10:00:00"],
        "cancellation_reason": [None],
        "source_extract_timestamp": ["2026-11-13T10:00:00+00:00"]
    })

    customers = pd.DataFrame({
        "customer_id": ["C101"]
    })

    config = load_rules_config("config/rules/orders.yaml")

    results = validate_dataset(
        orders,
        config,
        reference_datasets={"customers": customers},
        as_of=pd.Timestamp("2026-11-13T10:10:00Z")
    )

    result = next(
        r for r in results if r["rule_type"] == "referential_integrity"
    )

    assert result["failed_records"] == 1
    assert result["status"] == "FAIL"
