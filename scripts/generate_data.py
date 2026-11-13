
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"

RAW_DIR.mkdir(parents=True, exist_ok=True)


def generate_customers():

    customers = [
        ("C101", "Arun", "arun@gmail.com", "2026-01-01T10:00:00"),
        ("C102", "Rahul", "rahul@gmail.com", "2026-01-02T10:00:00"),
        ("C103", "Priya", "priya@gmail.com", "2026-01-03T10:00:00"),
        ("C104", "Sneha", "sneha@gmail.com", "2026-01-04T10:00:00"),
        ("C105", "Kiran", "kiran@gmail.com", "2026-01-05T10:00:00"),
        ("C106", "Ananya", "ananya@gmail.com", "2026-01-06T10:00:00"),
        ("C107", "Vikram", "vikram@gmail.com", "2026-01-07T10:00:00"),
        ("C108", "Meera", "meera@gmail.com", "2026-01-08T10:00:00"),
        ("C109", "Rohit", "rohit@gmail.com", "2026-01-09T10:00:00"),
        ("C110", "Divya", "divya@gmail.com", "2026-01-10T10:00:00"),
    ]

    df = pd.DataFrame(
        customers,
        columns=[
            "customer_id",
            "customer_name",
            "email",
            "created_at"
        ]
    )

    df.to_csv(RAW_DIR / "customers.csv", index=False)

    print(f"Customers generated: {len(df)}")


def generate_orders():

    records = [
        ("O101", "C101", 1500, "INR", "PLACED", "2026-11-10T10:00:00", None),
        ("O102", "C102", 2500, "INR", "SHIPPED", "2026-11-10T11:00:00", None),
        ("O103", "C103", 500, "INR", "DELIVERED", "2026-11-10T12:00:00", None),
        ("O104", "C104", 100000, "INR", "PLACED", "2026-11-10T13:00:00", None),
        ("O105", "C105", 1, "INR", "PROCESSING", "2026-11-10T14:00:00", None),

        # Missing customer ID
        ("O106", None, 800, "INR", "PLACED", "2026-11-10T15:00:00", None),

        # Invalid customer reference
        ("O107", "C999", 1200, "INR", "PLACED", "2026-11-10T16:00:00", None),

        # Invalid amount
        ("O108", "C106", -100, "INR", "PLACED", "2026-11-10T17:00:00", None),

        # Amount above maximum
        ("O109", "C107", 150000, "INR", "PLACED", "2026-11-10T18:00:00", None),

        # Invalid status
        ("O110", "C108", 2000, "INR", "INVALID", "2026-11-10T19:00:00", None),

        # Cancelled order without reason
        ("O111", "C109", 3000, "INR", "CANCELLED", "2026-11-10T20:00:00", None),

        # Missing order ID
        (None, "C110", 4000, "INR", "PLACED", "2026-11-10T21:00:00", None),

        # Duplicate order ID
        ("O101", "C101", 1500, "INR", "PLACED", "2026-11-10T10:00:00", None),

        # Invalid currency
        ("O112", "C102", 1000, "EUR", "PLACED", "2026-11-10T22:00:00", None),

        # Valid cancelled order
        ("O113", "C103", 600, "INR", "CANCELLED", "2026-11-10T23:00:00", "Customer request"),
    ]

    df = pd.DataFrame(
        records,
        columns=[
            "order_id",
            "customer_id",
            "amount",
            "currency",
            "order_status",
            "order_timestamp",
            "cancellation_reason"
        ]
    )

    # Generate a fresh UTC source extract timestamp
    extract_timestamp = (
        datetime.now(timezone.utc) - timedelta(minutes=5)
    ).isoformat(timespec="seconds")

    df["source_extract_timestamp"] = extract_timestamp

    df.to_csv(RAW_DIR / "orders.csv", index=False)

    print(f"Orders generated: {len(df)}")
    print(f"Source extract timestamp: {extract_timestamp}")


if __name__ == "__main__":

    generate_customers()
    generate_orders()

    print("Sample data generation completed.")
