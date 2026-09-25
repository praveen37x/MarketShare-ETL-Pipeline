"""
MarketShare-ETL-Pipeline: Robust Data Extractor
Extracts multi-year CSV feeds from disk with automated encoding fallback.
"""
from pathlib import Path
from typing import Any
import polars as pl


class CSVExtractor:
    """Extracts raw market share CSV files."""

    def __init__(self, raw_dir: Path):
        self.raw_dir = raw_dir

    def extract_file(self, file_path: Path) -> pl.DataFrame:
        """Read a single CSV file with encoding fallback."""
        try:
            return pl.read_csv(file_path, encoding="utf8-lossy", ignore_errors=True)
        except Exception:
            return pl.read_csv(file_path, encoding="latin1", ignore_errors=True)

    def extract_all(self, pattern: str = "*.csv") -> dict[str, pl.DataFrame]:
        """Extract all matching CSV files from raw_dir."""
        files = list(self.raw_dir.glob(pattern))
        if not files:
            files = list(self.raw_dir.glob("*.CSV"))

        extracted = {}
        for f in sorted(files):
            df = self.extract_file(f)
            extracted[f.name] = df

        return extracted
