
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.storage.database import get_connection

with get_connection() as conn:
    runs = conn.execute("""
        SELECT run_id, status, total_records, passed_records, failed_records
        FROM pipeline_runs
        WHERE total_records = 400000
          AND status = 'COMPLETED_WITH_ERRORS'
        ORDER BY start_time DESC
        LIMIT 2
    """).fetchall()

    if len(runs) < 2:
        print("Could not find two completed large-data runs.")
        raise SystemExit(1)

    print("\nLatest two large-data runs:")

    for run in runs:
        run_id = run[0]

        rule_count = conn.execute("""
            SELECT COUNT(*)
            FROM rule_results
            WHERE run_id = ?
        """, [run_id]).fetchone()[0]

        quarantine_count = conn.execute("""
            SELECT COUNT(*)
            FROM quarantine_records
            WHERE run_id = ?
        """, [run_id]).fetchone()[0]

        customers_file = (
            PROJECT_ROOT / "data/output/clean/customers"
            / f"run_id={run_id}" / "data.parquet"
        )

        orders_file = (
            PROJECT_ROOT / "data/output/clean/orders"
            / f"run_id={run_id}" / "data.parquet"
        )

        print(f"\nRun ID: {run_id}")
        print(f"Status: {run[1]}")
        print(f"Total records: {run[2]:,}")
        print(f"Passed: {run[3]:,}")
        print(f"Failed: {run[4]:,}")
        print(f"Rule results: {rule_count}")
        print(f"Quarantine records: {quarantine_count}")
        print(f"Customer output exists: {customers_file.exists()}")
        print(f"Orders output exists: {orders_file.exists()}")
