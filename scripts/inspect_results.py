
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.storage.database import get_connection


with get_connection() as conn:

    # 1. Display pipeline execution history
    print("\n========== PIPELINE RUNS ==========")

    runs = conn.execute("""
        SELECT *
        FROM pipeline_runs
        ORDER BY start_time DESC
    """).df()

    print(runs.to_string(index=False))

    # 2. Get latest completed pipeline run
    latest_run = conn.execute("""
        SELECT run_id, status
        FROM pipeline_runs
        WHERE status IN ('SUCCESS', 'COMPLETED_WITH_ERRORS')
        ORDER BY start_time DESC
        LIMIT 1
    """).fetchone()

    if latest_run is None:
        print("\nNo completed pipeline runs found.")
        raise SystemExit(0)

    run_id, status = latest_run

    print(f"\n========== LATEST RUN: {run_id} ==========")
    print(f"Status: {status}")

    # 3. Display rule-level results for this run
    print("\n========== RULE RESULTS ==========")

    results = conn.execute("""
        SELECT
            dataset,
            rule_id,
            rule_name,
            severity,
            total_records,
            passed_records,
            failed_records,
            status
        FROM rule_results
        WHERE run_id = ?
        ORDER BY dataset, rule_id
    """, [run_id]).df()

    print(results.to_string(index=False))

    # 4. Display overall summary
    print("\n========== SUMMARY ==========")

    summary = conn.execute("""
        SELECT
            SUM(total_records) AS total_rule_evaluations,
            SUM(passed_records) AS passed_rule_evaluations,
            SUM(failed_records) AS failed_rule_evaluations,
            COUNT(*) AS total_rules
        FROM rule_results
        WHERE run_id = ?
    """, [run_id]).df()

    print(summary.to_string(index=False))
