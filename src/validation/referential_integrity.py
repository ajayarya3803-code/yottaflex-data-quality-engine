
import pandas as pd


def check_referential_integrity(
    df: pd.DataFrame,
    column: str,
    reference_df: pd.DataFrame,
    reference_column: str
) -> pd.Series:
    """
    Returns True if the value exists in the reference dataset.
    Returns False for missing, blank, or unmatched values.
    """
    values = df[column]

    valid = (
        values.isin(reference_df[reference_column])
        & values.notna()
        & values.astype("string").str.strip().ne("")
    )

    return valid.fillna(False)

