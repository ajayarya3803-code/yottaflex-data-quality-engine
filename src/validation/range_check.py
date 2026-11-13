
import pandas as pd


def check_range(
    df: pd.DataFrame,
    column: str,
    min_value: float,
    max_value: float,
    min_inclusive: bool = False,
    max_inclusive: bool = True
) -> pd.Series:

    values = pd.to_numeric(df[column], errors="coerce")

    lower_check = (
        values.ge(min_value)
        if min_inclusive
        else values.gt(min_value)
    )

    upper_check = (
        values.le(max_value)
        if max_inclusive
        else values.lt(max_value)
    )

    valid = values.notna() & lower_check & upper_check

    return valid.fillna(False)
