
import pandas as pd


def check_freshness(
    df: pd.DataFrame,
    column: str,
    max_age_hours: int,
    as_of: pd.Timestamp
) -> pd.Series:

    timestamps = pd.to_datetime(df[column], errors="coerce", utc=True)
    reference_time = pd.Timestamp(as_of)

    if reference_time.tzinfo is None:
        reference_time = reference_time.tz_localize("UTC")
    else:
        reference_time = reference_time.tz_convert("UTC")

    age = reference_time - timestamps

    valid = (
        timestamps.notna()
        & age.ge(pd.Timedelta(0))
        & age.le(pd.Timedelta(hours=max_age_hours))
    )

    return valid.fillna(False)
