
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.storage.database import get_connection

with get_connection() as conn:
    result = conn.execute("""
        SELECT run_id, status, error_message, total_records
        FROM pipeline_runs
        WHERE status = 'FAILED'
        ORDER BY start_time DESC
        LIMIT 1
    """).fetchone()

    if result:
        print("Failed run ID:", result[0])
        print("Status:", result[1])
        print("Error:", result[2])
        print("Records processed:", result[3])

        assert result[1] == "FAILED"
        assert result[2] is not None
        assert result[2] != ""
        assert result[3] == 0

        print("\nFailure handling verification passed!")
    else:
        print("No failed pipeline run found.")
