"""
Unit tests for CSV Extractor
"""
from pathlib import Path
import polars as pl
from src.etl.extract import CSVExtractor


def test_csv_extractor_read_file(tmp_path: Path):
    sample_file = tmp_path / "sample_test.csv"
    sample_df = pl.DataFrame({
        "Year": [2024],
        "Vendor": ["Microsoft"],
        "VendorRevenue - USD": [12000.0]
    })
    sample_df.write_csv(sample_file)

    extractor = CSVExtractor(tmp_path)
    extracted = extractor.extract_file(sample_file)

    assert len(extracted) == 1
    assert "Vendor" in extracted.columns
    assert extracted["Vendor"][0] == "Microsoft"
