
import pandas as pd


def check_completeness(df: pd.DataFrame, column: str) -> pd.Series:
    """
    Returns True for records where the column is populated.
    Returns False for missing or blank values.
    """
    values = df[column]

    valid = values.notna() & values.astype("string").str.strip().ne("")

    return valid.fillna(False)
