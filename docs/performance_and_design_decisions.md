# Performance Benchmark and Design Decisions

## 1. Performance Benchmark

The data quality engine was tested using generated datasets containing 400,000 records.

| Metric | Customers | Orders | Total |
|---|---:|---:|---:|
| Input records | 100,000 | 300,000 | 400,000 |
| Clean records | 98,507 | 290,246 | 388,753 |
| Quarantined records | 1,493 | 9,754 | 11,247 |

### Execution Results

- Recorded execution time: 8.90 seconds
- Approximate throughput: 44,944 records per second
- Pipeline status: `COMPLETED_WITH_ERRORS`
- Reconciliation: Passed

*Benchmark results are environment-dependent and may vary across machines and execution runs.*

## 2. Data Reconciliation

Every input record was accounted for after processing.

| Dataset | Input | Clean | Quarantined | Reconciled |
|---|---:|---:|---:|---|
| Customers | 100,000 | 98,507 | 1,493 | Yes |
| Orders | 300,000 | 290,246 | 9,754 | Yes |
| **Total** | **400,000** | **388,753** | **11,247** | **Yes** |

Reconciliation formula:

`Input Records = Clean Records + Quarantined Records`

## 3. Design Decisions

### Python and Pandas
Used for local data ingestion and validation because they provide a straightforward way to implement and demonstrate configurable data quality checks.

### YAML-driven Rules
Validation rules are separated from application logic, allowing rules to be modified without changing the validation engine.

### DuckDB
Used for persisting pipeline execution history, rule-level results, and quarantined records in a lightweight analytical database.

### Parquet
Used for clean dataset publishing because it provides a columnar storage format suitable for analytical workloads.

### Run-level Output Isolation
Clean outputs are stored in run-specific directories to prevent separate executions from overwriting one another.

### Idempotent Execution
A reusable run ID allows persisted results to be updated without duplicating pipeline, rule-result, or quarantine records.

## 4. Trade-offs and Future Improvements

- **Local processing:** Pandas is suitable for this challenge's scale. Larger production workloads could use Apache Spark or Databricks.
- **Local storage:** DuckDB provides simple local persistence. Production deployments could use a managed database or cloud storage.
- **Execution model:** The current pipeline runs synchronously. A production implementation could introduce workflow orchestration using Apache Airflow.
- **Monitoring:** Execution metrics are persisted in DuckDB. A production system could expose them through dashboards and alerting.

These improvements are potential production extensions, not dependencies of the current implementation.