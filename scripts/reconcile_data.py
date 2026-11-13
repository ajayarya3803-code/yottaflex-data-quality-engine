
import sys
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.storage.database import get_connection


def reconcile_data():
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

        quarantine_counts = conn.execute("""
            SELECT dataset, COUNT(*) AS rejected_records
            FROM quarantine_records
            WHERE run_id = ?
            GROUP BY dataset
        """, [run_id]).df()

    print(f"Reconciliation for run: {run_id}\n")

    all_reconciled = True

    for dataset in ["customers", "orders"]:
        input_path = PROJECT_ROOT / "data" / "generated" / f"{dataset}.csv"

        clean_path = (
            PROJECT_ROOT / "data" / "output" / "clean"
            / dataset / f"run_id={run_id}" / "data.parquet"
        )

        input_count = len(pd.read_csv(input_path))

        clean_count = len(pd.read_parquet(clean_path))

        matching = quarantine_counts[
            quarantine_counts["dataset"] == dataset
        ]

        rejected_count = (
            int(matching.iloc[0]["rejected_records"])
            if not matching.empty else 0
        )

        accounted_count = clean_count + rejected_count
        reconciled = input_count == accounted_count

        all_reconciled &= reconciled

        print(f"Dataset: {dataset}")
        print(f"Input records: {input_count:,}")
        print(f"Clean records: {clean_count:,}")
        print(f"Quarantined records: {rejected_count:,}")
        print(f"Accounted records: {accounted_count:,}")
        print(f"Reconciled: {reconciled}")
        print("-" * 45)

    print(f"\nOverall reconciliation: {all_reconciled}")


if __name__ == "__main__":
    reconcile_data()
