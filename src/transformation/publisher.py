
from pathlib import Path

import pandas as pd


CLEAN_OUTPUT_DIR = Path("data/output/clean")


def publish_clean_dataset(
    df: pd.DataFrame,
    results: list,
    dataset_name: str,
    run_id: str
) -> dict:

    # Collect indices of records that failed any validation rule
    failed_indices = set()

    for result in results:
        failed_indices.update(
            result["failed_rows"].index.tolist()
        )

    # Retain only records that passed every rule
    clean_df = df.loc[
        ~df.index.isin(failed_indices)
    ].copy()

    # Create run-specific output directory
    output_dir = (
        CLEAN_OUTPUT_DIR
        / dataset_name
        / f"run_id={run_id}"
    )

    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "data.parquet"
    temp_path = output_dir / "data.tmp.parquet"

    try:
        # Write temporary file first
        clean_df.to_parquet(
            temp_path,
            engine="pyarrow",
            index=False
        )

        # Replace final output after successful write
        temp_path.replace(output_path)

    except Exception:
        if temp_path.exists():
            temp_path.unlink()
        raise

    return {
        "dataset": dataset_name,
        "total_records": len(df),
        "clean_records": len(clean_df),
        "rejected_records": len(failed_indices),
        "output_path": str(output_path)
    }
