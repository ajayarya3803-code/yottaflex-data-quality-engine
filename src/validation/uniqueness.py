
import pandas as pd


def check_uniqueness(df: pd.DataFrame, column: str) -> pd.Series:
    """
    Returns True for the first occurrence of a value.
    Returns False for subsequent duplicate occurrences.
    Missing and blank values are treated as invalid.
    """
    values = df[column]

    valid = values.notna() & values.astype("string").str.strip().ne("")

    unique = ~values.duplicated(keep="first")

    return (valid & unique).fillna(False)
