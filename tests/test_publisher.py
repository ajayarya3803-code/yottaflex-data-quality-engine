
import pandas as pd

from src.transformation import publisher
from src.transformation.publisher import publish_clean_dataset


def test_publisher_excludes_all_rejected_records(tmp_path, monkeypatch):
    monkeypatch.setattr(publisher, "CLEAN_OUTPUT_DIR", tmp_path)

    df = pd.DataFrame({
        "order_id": ["O101", "O102", "O103", "O104"],
        "amount": [100, -50, 200, 300]
    })

    results = [
        {
            "dataset": "orders",
            "failed_rows": df.loc[[1]].copy()
        },
        {
            "dataset": "orders",
            "failed_rows": df.loc[[2]].copy()
        }
    ]

    output = publish_clean_dataset(
        df=df,
        results=results,
        dataset_name="orders",
        run_id="test-run-001"
    )

    published_df = pd.read_parquet(output["output_path"])

    assert output["total_records"] == 4
    assert output["clean_records"] == 2
    assert output["rejected_records"] == 2
    assert published_df["order_id"].tolist() == ["O101", "O104"]


def test_publisher_keeps_all_records_when_no_failures(tmp_path, monkeypatch):
    monkeypatch.setattr(publisher, "CLEAN_OUTPUT_DIR", tmp_path)

    df = pd.DataFrame({
        "customer_id": ["C101", "C102", "C103"]
    })

    results = [
        {
            "dataset": "customers",
            "failed_rows": df.iloc[0:0].copy()
        }
    ]

    output = publish_clean_dataset(
        df=df,
        results=results,
        dataset_name="customers",
        run_id="test-run-002"
    )

    published_df = pd.read_parquet(output["output_path"])

    assert output["clean_records"] == 3
    assert output["rejected_records"] == 0
    assert len(published_df) == 3
