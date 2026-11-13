
import pandas as pd


def check_allowed_values(
    df: pd.DataFrame,
    column: str,
    allowed_values: list
) -> pd.Series:

    values = df[column]

    valid = (
        values.notna()
        & values.astype("string").str.strip().ne("")
        & values.isin(allowed_values)
    )

    return valid.fillna(False)


def check_required_when(
    df: pd.DataFrame,
    column: str,
    condition_column: str,
    condition_value: str
) -> pd.Series:

    values = df[column]

    condition = df[condition_column].eq(condition_value)

    required = (
        values.notna()
        & values.astype("string").str.strip().ne("")
    )

    return (~condition | required).fillna(False)


def check_email_format(
    df: pd.DataFrame,
    column: str
) -> pd.Series:

    values = df[column].astype("string")

    valid = values.str.fullmatch(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        na=False
    )

    return valid.fillna(False)
