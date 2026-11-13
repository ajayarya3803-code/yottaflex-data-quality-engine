
import pandas as pd

from src.validation.completeness import check_completeness
from src.validation.uniqueness import check_uniqueness
from src.validation.referential_integrity import check_referential_integrity
from src.validation.range_check import check_range
from src.validation.freshness import check_freshness
from src.validation.custom_rules import (
    check_allowed_values,
    check_required_when,
    check_email_format
)


def test_completeness():
    df = pd.DataFrame({
        "customer_id": ["C101", "C102", None, " ", "C105"]
    })

    result = check_completeness(df, "customer_id")

    assert result.tolist() == [True, True, False, False, True]


def test_uniqueness():
    df = pd.DataFrame({
        "customer_id": ["C101", "C102", "C101", None, "C105"]
    })

    result = check_uniqueness(df, "customer_id")

    assert result.tolist() == [True, True, False, False, True]


def test_referential_integrity():
    customers = pd.DataFrame({
        "customer_id": ["C101", "C102", "C103"]
    })

    orders = pd.DataFrame({
        "customer_id": ["C101", "C999", "C102", None, " "]
    })

    result = check_referential_integrity(
        orders,
        "customer_id",
        customers,
        "customer_id"
    )

    assert result.tolist() == [True, False, True, False, False]


def test_range():
    df = pd.DataFrame({
        "amount": [500, 1000, -100, 150000, 0, None, 100000]
    })

    result = check_range(df, "amount", 0, 100000)

    assert result.tolist() == [
        True, True, False, False, False, False, True
    ]



def test_freshness():
    df = pd.DataFrame({
        "source_extract_timestamp": [
            "2026-11-11 10:00:00",
            "2026-11-10 20:00:00",
            "2026-11-10 08:00:00",
            None,
            "invalid",
            "2026-11-12 10:00:00"
        ]
    })

    result = check_freshness(
        df,
        "source_extract_timestamp",
        24,
        pd.Timestamp("2026-11-11 10:00:00", tz="UTC")
    )

    assert result.tolist() == [True, True, False, False, False, False]


def test_allowed_values():
    df = pd.DataFrame({
        "status": ["PLACED", "SHIPPED", "INVALID", None]
    })

    result = check_allowed_values(
        df, "status",
        ["PLACED", "SHIPPED", "DELIVERED"]
    )

    assert result.tolist() == [True, True, False, False]


def test_required_when():
    df = pd.DataFrame({
        "order_status": ["CANCELLED", "PLACED", "CANCELLED"],
        "cancellation_reason": ["Customer request", None, None]
    })

    result = check_required_when(
        df, "cancellation_reason",
        "order_status", "CANCELLED"
    )

    assert result.tolist() == [True, True, False]


def test_email_format():
    df = pd.DataFrame({
        "email": [
            "test@gmail.com",
            "invalid-email",
            "user@example.co.in",
            None
        ]
    })

    result = check_email_format(df, "email")

    assert result.tolist() == [True, False, True, False]
