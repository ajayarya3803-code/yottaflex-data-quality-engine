import time
import argparse
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pandas as pd

from src.storage.database import create_tables
from src.storage.repository import (
    insert_pipeline_run,
    insert_rule_results,
    save_quarantine_records
)
from src.transformation.publisher import publish_clean_dataset
from src.validation.engine import load_rules_config, validate_dataset


def utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def run_pipeline(input_dir="data/raw", run_id=None):

    input_dir = Path(input_dir)
    pipeline_start = time.perf_counter()

    run_id = run_id or str(uuid4())
    start_time = utc_now()

    create_tables()

    run_data = {
        "run_id": run_id,
        "start_time": start_time,
        "end_time": None,
        "status": "RUNNING",
        "total_records": 0,
        "passed_records": 0,
        "failed_records": 0,
        "error_message": None
    }

    insert_pipeline_run(run_data)

    datasets = ["customers", "orders"]
    reference_datasets = {}
    all_results = []

    total_records = 0
    passed_records = 0
    failed_records = 0

    try:
        for dataset_name in datasets:

            print(f"\nProcessing dataset: {dataset_name}")

            # 1. Read input data
            input_path = input_dir / f"{dataset_name}.csv"
            df = pd.read_csv(input_path)

            print(f"Input records: {len(df):,}")

            # 2. Load validation configuration
            config_path = f"config/rules/{dataset_name}.yaml"
            rules_config = load_rules_config(config_path)

            # 3. Execute validation
            results = validate_dataset(
                df,
                rules_config,
                reference_datasets=reference_datasets,
                as_of=pd.Timestamp.now(tz="UTC")
            )

            all_results.extend(results)

            # 4. Calculate dataset-level record counts
            failed_indices = set()

            for result in results:
                failed_indices.update(result["failed_rows"].index)

            dataset_failed = len(failed_indices)
            dataset_total = len(df)
            dataset_passed = dataset_total - dataset_failed

            # 5. Publish clean records
            publish_result = publish_clean_dataset(
                df=df,
                results=results,
                dataset_name=dataset_name,
                run_id=run_id
            )

            print(f"Clean records: {publish_result['clean_records']:,}")
            print(f"Rejected records: {publish_result['rejected_records']:,}")
            print(f"Published to: {publish_result['output_path']}")

            total_records += dataset_total
            passed_records += dataset_passed
            failed_records += dataset_failed

            print(f"Total records: {dataset_total:,}")
            print(f"Passed records: {dataset_passed:,}")
            print(f"Failed records: {dataset_failed:,}")

            # 6. Make customers available for orders validation
            reference_datasets[dataset_name] = df

        # 7. Persist rule-level results
        insert_rule_results(run_id, all_results)

        # 8. Save rejected records
        save_quarantine_records(run_id, all_results)

        # 9. Update final pipeline status
        run_data.update({
            "end_time": utc_now(),
            "status": (
                "SUCCESS" if failed_records == 0
                else "COMPLETED_WITH_ERRORS"
            ),
            "total_records": total_records,
            "passed_records": passed_records,
            "failed_records": failed_records
        })

        insert_pipeline_run(run_data)

        elapsed_seconds = time.perf_counter() - pipeline_start

        print("\nPipeline execution completed.")
        print(f"Run ID: {run_id}")
        print(f"Overall status: {run_data['status']}")
        print(f"Total: {total_records:,}")
        print(f"Passed: {passed_records:,}")
        print(f"Failed: {failed_records:,}")
        print(f"Execution time: {elapsed_seconds:.2f} seconds")

    except Exception as error:

        run_data.update({
            "end_time": utc_now(),
            "status": "FAILED",
            "total_records": total_records,
            "passed_records": passed_records,
            "failed_records": failed_records,
            "error_message": str(error)
        })

        insert_pipeline_run(run_data)

        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--input-dir",
        default="data/raw",
        help="Directory containing customers.csv and orders.csv"
    )

    parser.add_argument(
    "--run-id",
    default=None,
    help="Reuse an existing run ID for a safe rerun"
    )

    args = parser.parse_args()

    run_pipeline(
    input_dir=args.input_dir,
    run_id=args.run_id
    )
