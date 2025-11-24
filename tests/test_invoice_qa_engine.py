import importlib
from pathlib import Path

import pandas as pd


def test_invoice_qa_engine_imports():
    """
    Smoke test: module should import without raising exceptions.
    """
    mod = importlib.import_module("invoice_qa_engine")
    assert mod is not None


def test_load_database_reads_excel(tmp_path):
    """
    Functional smoke test for `load_database`.

    This assumes `invoice_qa_engine` exposes a function:

        load_database(path: str) -> pandas.DataFrame

    If your function has a different name or signature,
    adjust the import and call accordingly.
    """
    mod = importlib.import_module("invoice_qa_engine")

    # ---- adjust this name if yours is different ----
    assert hasattr(mod, "load_database"), "Expected `load_database` in invoice_qa_engine"
    load_database = getattr(mod, "load_database")
    # ------------------------------------------------

    # Create a tiny fake Excel file
    data = pd.DataFrame(
        [
            {"Invoice No": "T001", "Amount": 100.0},
            {"Invoice No": "T002", "Amount": 200.0},
        ]
    )
    excel_path: Path = tmp_path / "sample_invoices.xlsx"
    data.to_excel(excel_path, index=False)

    # Call your loader
    df = load_database(str(excel_path))

    # Basic checks
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert set(df.columns) >= {"Invoice No", "Amount"}
