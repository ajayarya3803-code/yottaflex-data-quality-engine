
from datetime import datetime, timezone
from uuid import uuid4

from src.storage.database import create_tables
from src.storage.repository import (
    insert_pipeline_run,
    insert_rule_results,
    get_pipeline_runs,
    get_rule_results
)


def test_storage_operations():
    create_tables()

    run_id = str(uuid4())

    run_data = {
        "run_id": run_id,
        "start_time": datetime.now(timezone.utc).replace(tzinfo=None),
        "end_time": None,
        "status": "RUNNING",
        "total_records": 10,
        "passed_records": 8,
        "failed_records": 2,
        "error_message": None
    }

    insert_pipeline_run(run_data)

    results = [{
        "dataset": "customers",
        "rule_id": "C001",
        "rule_name": "Customer ID completeness",
        "rule_type": "completeness",
        "severity": "HIGH",
        "total_records": 10,
        "passed_records": 8,
        "failed_records": 2,
        "status": "FAIL"
    }]

    insert_rule_results(run_id, results)

    assert len(get_pipeline_runs()) >= 1
    assert len(get_rule_results(run_id)) == 1
