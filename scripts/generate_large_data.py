
import argparse
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "data" / "generated"


def generate_data(customers_count, orders_count, seed):
    rng = np.random.default_rng(seed)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # ---------------- CUSTOMERS ----------------

    customer_ids = [
        f"C{i:07d}" for i in range(1, customers_count + 1)
    ]

    customers = pd.DataFrame({
        "customer_id": customer_ids,
        "customer_name": [
            f"Customer_{i}" for i in range(1, customers_count + 1)
        ],
        "email": [
            f"customer{i}@example.com"
            for i in range(1, customers_count + 1)
        ],
        "created_at": rng.choice(
            pd.date_range("2025-01-01", periods=365).astype(str),
            size=customers_count
        )
    })

    # Inject customer data-quality issues.
    invalid_email_indices = rng.choice(
        customers_count,
        size=max(1, customers_count // 100),
        replace=False
    )

    customers.loc[invalid_email_indices, "email"] = "invalid-email"

    null_name_indices = rng.choice(
        customers_count,
        size=max(1, customers_count // 200),
        replace=False
    )

    customers.loc[null_name_indices, "customer_name"] = None

    # ---------------- ORDERS ----------------

    valid_statuses = [
        "PLACED", "PROCESSING", "SHIPPED",
        "DELIVERED", "CANCELLED"
    ]

    extract_timestamp = (
        pd.Timestamp.now(tz="UTC") - pd.Timedelta(minutes=5)
    ).isoformat(timespec="seconds")

    orders = pd.DataFrame({
        "order_id": [
            f"O{i:08d}" for i in range(1, orders_count + 1)
        ],
        "customer_id": rng.choice(customer_ids, size=orders_count),
        "amount": rng.integers(100, 50000, size=orders_count),
        "currency": rng.choice(
            ["INR", "USD"], size=orders_count, p=[0.9, 0.1]
        ),
        "order_status": rng.choice(
            valid_statuses, size=orders_count
        ),
        "order_timestamp": pd.date_range(
            "2026-01-01", periods=orders_count, freq="min"
        ).astype(str),
        "cancellation_reason": None,
        "source_extract_timestamp": extract_timestamp
    })

    # Add cancellation reasons to cancelled orders.
    cancelled_mask = orders["order_status"].eq("CANCELLED")
    orders.loc[cancelled_mask, "cancellation_reason"] = rng.choice(
        ["Customer request", "Payment issue", "Out of stock"],
        size=int(cancelled_mask.sum())
    )

    # Inject approximately 1% data-quality issues per category.
    def select_indices(count):
        return rng.choice(
            orders_count,
            size=max(1, count),
            replace=False
        )

    # Missing customer references.
    idx = select_indices(orders_count // 200)
    orders.loc[idx, "customer_id"] = None

    # Invalid customer references.
    idx = select_indices(orders_count // 200)
    orders.loc[idx, "customer_id"] = "C9999999"

    # Negative amounts.
    idx = select_indices(orders_count // 200)
    orders.loc[idx, "amount"] = -100

    # Amounts exceeding the configured maximum.
    idx = select_indices(orders_count // 200)
    orders.loc[idx, "amount"] = 150000

    # Invalid order status.
    idx = select_indices(orders_count // 500)
    orders.loc[idx, "order_status"] = "UNKNOWN"

    # Missing cancellation reasons.
    cancelled_indices = orders.index[
        orders["order_status"].eq("CANCELLED")
    ].to_numpy()

    if len(cancelled_indices):
        missing_reason_indices = rng.choice(
            cancelled_indices,
            size=max(1, len(cancelled_indices) // 100),
            replace=False
        )
        orders.loc[
            missing_reason_indices, "cancellation_reason"
        ] = None

    # Unsupported currency.
    idx = select_indices(orders_count // 500)
    orders.loc[idx, "currency"] = "EUR"

    # Duplicate order IDs.
    duplicate_indices = select_indices(orders_count // 200)
    orders.loc[duplicate_indices, "order_id"] = orders.loc[
        duplicate_indices - 1, "order_id"
    ].to_numpy()

    # Missing order IDs.
    idx = select_indices(orders_count // 500)
    orders.loc[idx, "order_id"] = None

    # ---------------- SAVE ----------------

    customers_path = OUTPUT_DIR / "customers_large.csv"
    orders_path = OUTPUT_DIR / "orders_large.csv"

    customers.to_csv(customers_path, index=False)
    orders.to_csv(orders_path, index=False)

    print("Large datasets generated successfully.")
    print(f"Customers: {len(customers):,}")
    print(f"Orders: {len(orders):,}")
    print(f"Total records: {len(customers) + len(orders):,}")
    print(f"Output directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--customers", type=int, default=100_000)
    parser.add_argument("--orders", type=int, default=300_000)
    parser.add_argument("--seed", type=int, default=42)

    args = parser.parse_args()

    if args.customers < 1 or args.orders < 1:
        parser.error("Customer and order counts must be positive.")

    generate_data(args.customers, args.orders, args.seed)
