
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.storage.database import get_connection


with get_connection() as conn:

    latest_run = conn.execute("""
        SELECT run_id
        FROM pipeline_runs
        WHERE status IN ('SUCCESS', 'COMPLETED_WITH_ERRORS')
        ORDER BY start_time DESC
        LIMIT 1
    """).fetchone()

    if latest_run is None:
        print("No completed pipeline run found.")
        raise SystemExit(0)

    run_id = latest_run[0]

    print(f"\nRun ID: {run_id}")

    print("\n========== QUARANTINE SUMMARY ==========")

    summary = conn.execute("""
        SELECT
            dataset,
            COUNT(*) AS quarantined_records
        FROM quarantine_records
        WHERE run_id = ?
        GROUP BY dataset
    """, [run_id]).df()

    print(summary.to_string(index=False))

    print("\n========== QUARANTINED RECORDS ==========")

    records = conn.execute("""
        SELECT
            dataset,
            record_index,
            record_json,
            failed_rules
        FROM quarantine_records
        WHERE run_id = ?
        ORDER BY dataset, record_index
    """, [run_id]).df()

    print(records.to_string(index=False))
