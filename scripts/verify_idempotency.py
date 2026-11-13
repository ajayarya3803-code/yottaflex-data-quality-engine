
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.storage.database import get_connection

run_id = "318c23d0-7723-4375-9f66-0dcea8da5c5c"

with get_connection() as conn:
    run_count = conn.execute("""
        SELECT COUNT(*) FROM pipeline_runs WHERE run_id = ?
    """, [run_id]).fetchone()[0]

    rule_count = conn.execute("""
        SELECT COUNT(*) FROM rule_results WHERE run_id = ?
    """, [run_id]).fetchone()[0]

    quarantine_count = conn.execute("""
        SELECT COUNT(*) FROM quarantine_records WHERE run_id = ?
    """, [run_id]).fetchone()[0]

    print("Pipeline run rows:", run_count)
    print("Rule result rows:", rule_count)
    print("Quarantine records:", quarantine_count)

    assert run_count == 1, "Duplicate pipeline run rows found"
    assert rule_count == 17, "Unexpected rule result count"
    assert quarantine_count == 11247, "Unexpected quarantine count"

    print("\nIdempotency verification passed!")
