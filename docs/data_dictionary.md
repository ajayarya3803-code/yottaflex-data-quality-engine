
# Data Dictionary — Yottaflex Data Quality Framework

## 1. Project Overview

This project implements a configurable data quality framework
for an e-commerce order processing system.

Source datasets:
- Customers
- Orders

## 2. Customers Dataset

Grain: One record per customer.

| Column | Type | Nullable | Constraint |
|---|---|---|---|
| customer_id | VARCHAR | No | Primary Key |
| customer_name | VARCHAR | No | Not blank |
| email | VARCHAR | No | Valid email |
| created_at | TIMESTAMP | No | Valid timestamp |

## 3. Orders Dataset

Grain: One record per order.

| Column | Type | Nullable | Constraint |
|---|---|---|---|
| order_id | VARCHAR | No | Primary Key |
| customer_id | VARCHAR | No | Foreign Key |
| amount | DECIMAL(12,2) | No | 0 < amount <= 100000 |
| currency | VARCHAR(3) | No | INR or USD |
| order_status | VARCHAR | No | Valid status |
| order_timestamp | TIMESTAMP | No | Valid timestamp |
| cancellation_reason | VARCHAR | Yes | Required if cancelled |
| source_extract_timestamp | TIMESTAMP | No | Freshness validation |

## 4. Relationships

customers.customer_id (1) -> orders.customer_id (Many)

Every order must reference an existing customer.

## 5. Business Rules

| Rule ID | Rule | Severity |
|---|---|---|
| CUS001 | Customer ID completeness | Critical |
| CUS002 | Customer ID uniqueness | Critical |
| ORD001 | Order ID completeness | Critical |
| ORD002 | Order ID uniqueness | Critical |
| ORD003 | Customer referential integrity | High |
| ORD004 | Amount range validation | High |
| ORD005 | Source freshness validation | Medium |
| ORD006 | Valid order status | High |
| ORD007 | Cancellation reason validation | High |

## 6. Valid Order Statuses

PLACED, PROCESSING, SHIPPED, DELIVERED, CANCELLED

## 7. Pipeline Metadata

| Column | Purpose |
|---|---|
| run_id | Unique pipeline execution ID |
| source_file | Original source filename |
| source_row_number | Original source row |
| ingested_at | Ingestion timestamp |

## 8. Data Quality Expectations

- Primary keys must be unique and non-null.
- Foreign keys must reference existing customers.
- Amount must be greater than zero and at most 100000.
- Order status must belong to the supported list.
- Cancelled orders must have a cancellation reason.
- Source extracts must meet the configured freshness threshold.
- Invalid records must be traceable in quarantine.
- Repeated execution must not create unintended duplicates.

## 9. Naming Conventions

- Tables and columns: snake_case
- Timestamps: ISO-8601
- IDs: Stable identifiers
- Severity: critical, high, medium, low
- Pipeline status: success, success_with_rejects, failed
