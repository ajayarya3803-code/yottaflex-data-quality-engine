
import json

import pandas as pd

from src.storage.database import get_connection


def insert_pipeline_run(run_data: dict):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO pipeline_runs (
                run_id, start_time, end_time, status,
                total_records, passed_records, failed_records,
                error_message
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (run_id) DO UPDATE SET
                end_time = EXCLUDED.end_time,
                status = EXCLUDED.status,
                total_records = EXCLUDED.total_records,
                passed_records = EXCLUDED.passed_records,
                failed_records = EXCLUDED.failed_records,
                error_message = EXCLUDED.error_message
        """, [
            run_data["run_id"],
            run_data["start_time"],
            run_data.get("end_time"),
            run_data["status"],
            run_data["total_records"],
            run_data["passed_records"],
            run_data["failed_records"],
            run_data.get("error_message")
        ])


def insert_rule_results(run_id: str, results: list):
    with get_connection() as conn:
        for result in results:
            conn.execute("""
                INSERT INTO rule_results (
                    run_id, dataset, rule_id, rule_name,
                    rule_type, severity, total_records,
                    passed_records, failed_records, status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (run_id, dataset, rule_id) DO UPDATE SET
                    rule_name = EXCLUDED.rule_name,
                    rule_type = EXCLUDED.rule_type,
                    severity = EXCLUDED.severity,
                    total_records = EXCLUDED.total_records,
                    passed_records = EXCLUDED.passed_records,
                    failed_records = EXCLUDED.failed_records,
                    status = EXCLUDED.status
            """, [
                run_id,
                result["dataset"],
                result["rule_id"],
                result["rule_name"],
                result["rule_type"],
                result["severity"],
                result["total_records"],
                result["passed_records"],
                result["failed_records"],
                result["status"]
            ])


def get_pipeline_runs():
    with get_connection() as conn:
        return conn.execute("""
            SELECT *
            FROM pipeline_runs
            ORDER BY start_time DESC
        """).df()


def get_rule_results(run_id: str):
    with get_connection() as conn:
        return conn.execute("""
            SELECT *
            FROM rule_results
            WHERE run_id = ?
        """, [run_id]).df()


def save_quarantine_records(run_id: str, results: list):

    quarantined = {}

    # Collect failed records and their rule IDs
    for result in results:

        dataset = result["dataset"]
        rule_id = result["rule_id"]
        failed_rows = result["failed_rows"]

        for index, row in failed_rows.iterrows():

            key = (dataset, int(index))

            if key not in quarantined:

                # Convert Pandas missing values to JSON null
                clean_record = {
                    column: (
                        None if pd.isna(value) else value
                    )
                    for column, value in row.to_dict().items()
                }

                quarantined[key] = {
                    "run_id": run_id,
                    "dataset": dataset,
                    "record_index": int(index),
                    "record_json": json.dumps(
                        clean_record,
                        default=str,
                        allow_nan=False
                    ),
                    "failed_rules": set()
                }

            quarantined[key]["failed_rules"].add(rule_id)

    # Prepare database rows
    rows = []

    for record in quarantined.values():

        rows.append((
            record["run_id"],
            record["dataset"],
            record["record_index"],
            record["record_json"],
            json.dumps(sorted(record["failed_rules"]))
        ))

    # Idempotent replacement for the same run
    with get_connection() as conn:

        conn.execute("BEGIN TRANSACTION")

        try:

            conn.execute("""
                DELETE FROM quarantine_records
                WHERE run_id = ?
            """, [run_id])

            if rows:
                conn.executemany("""
                    INSERT INTO quarantine_records (
                        run_id,
                        dataset,
                        record_index,
                        record_json,
                        failed_rules
                    )
                    VALUES (?, ?, ?, ?, ?)
                """, rows)

            conn.execute("COMMIT")

        except Exception:
            conn.execute("ROLLBACK")
            raise

    print(f"Quarantined records: {len(rows)}")
