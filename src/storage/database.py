
from pathlib import Path

import duckdb


DB_PATH = Path("data/output/quality_engine.duckdb")


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(DB_PATH))


def create_tables():
    with get_connection() as conn:

        conn.execute("""
            CREATE TABLE IF NOT EXISTS pipeline_runs (
                run_id VARCHAR PRIMARY KEY,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                status VARCHAR,
                total_records BIGINT,
                passed_records BIGINT,
                failed_records BIGINT,
                error_message VARCHAR
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS rule_results (
                run_id VARCHAR,
                dataset VARCHAR,
                rule_id VARCHAR,
                rule_name VARCHAR,
                rule_type VARCHAR,
                severity VARCHAR,
                total_records BIGINT,
                passed_records BIGINT,
                failed_records BIGINT,
                status VARCHAR,
                PRIMARY KEY (run_id, dataset, rule_id)
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS quarantine_records (
                run_id VARCHAR,
                dataset VARCHAR,
                record_index BIGINT,
                record_json VARCHAR,
                failed_rules VARCHAR
            )
        """)

    print("DuckDB tables created successfully.")
