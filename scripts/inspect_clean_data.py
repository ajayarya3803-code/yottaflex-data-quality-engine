
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.storage.database import get_connection


def inspect_clean_data():
    with get_connection() as conn:
        run = conn.execute("""
            SELECT run_id
            FROM pipeline_runs
            WHERE status IN ('SUCCESS', 'COMPLETED_WITH_ERRORS')
            ORDER BY start_time DESC
            LIMIT 1
        """).fetchone()

    if not run:
        print("No completed pipeline run found.")
        return

    run_id = run[0]
    print(f"Inspecting Run ID: {run_id}\n")

    for dataset in ["customers", "orders"]:
        file_path = (
            PROJECT_ROOT
            / "data"
            / "output"
            / "clean"
            / dataset
            / f"run_id={run_id}"
            / "data.parquet"
        )

        if not file_path.exists():
            print(f"{dataset}: Published file not found.")
            continue

        df = pd.read_parquet(file_path)

        print(f"Dataset: {dataset}")
        print(f"Clean records: {len(df)}")
        print(f"Columns: {list(df.columns)}")
        print(df.head(3))
        print("-" * 50)


if __name__ == "__main__":
    inspect_clean_data()
