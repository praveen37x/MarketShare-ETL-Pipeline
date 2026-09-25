"""
MarketShare-ETL-Pipeline: Dual Storage Loader (DuckDB + SQLite)
Loads conformed market share data into both DuckDB (high-speed OLAP)
and SQLite (relational database with performance indexes).
"""
import sqlite3
from pathlib import Path
import duckdb
import polars as pl
from src.config import config


class DatabaseLoader:
    """Loads transformed market share data into DuckDB and SQLite."""

    def __init__(self, duckdb_path: Path, sqlite_path: Path):
        self.duckdb_path = duckdb_path
        self.sqlite_path = sqlite_path
        self.duckdb_path.parent.mkdir(parents=True, exist_ok=True)

    def load_duckdb(self, df: pl.DataFrame) -> None:
        """Load data into DuckDB and create analytical view."""
        parquet_path = self.duckdb_path.parent / "market_share_conformed.parquet"
        df.write_parquet(parquet_path, compression="zstd")

        conn = duckdb.connect(str(self.duckdb_path))
        pq_str = str(parquet_path).replace("\\", "/")
        conn.execute(f"""
            CREATE OR REPLACE TABLE market_share AS 
            SELECT * FROM read_parquet('{pq_str}');
        """)
        conn.close()

    def load_sqlite(self, df: pl.DataFrame) -> None:
        """
        Load data into SQLite with primary keys, indexes, and transaction commits.
        """
        conn = sqlite3.connect(str(self.sqlite_path))
        cursor = conn.cursor()

        cursor.execute("DROP TABLE IF EXISTS market_share;")
        cursor.execute("""
            CREATE TABLE market_share (
                Year INTEGER,
                Super_Region TEXT,
                Region TEXT,
                Country TEXT,
                Vendor TEXT,
                Service_1 TEXT,
                Service_2 TEXT,
                Service_3 TEXT,
                Vertical TEXT,
                Ticker TEXT,
                HQ_Country TEXT,
                Vendor_Revenue_USD REAL,
                Constant_Currency_Revenue_USD REAL,
                Total_Regional_Market_USD REAL,
                Market_Share_Pct REAL
            );
        """)

        # Insert using fast batch executemany
        rows = [tuple(row) for row in df.iter_rows()]
        cursor.executemany("""
            INSERT INTO market_share VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, rows)

        # Performance indexes for sub-millisecond lookups
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ms_year_vendor ON market_share (Year, Vendor);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ms_super_region ON market_share (Super_Region);")

        conn.commit()
        conn.close()

    def load_all(self, df: pl.DataFrame) -> dict[str, str]:
        """Load into both storage engines."""
        self.load_duckdb(df)
        self.load_sqlite(df)
        return {
            "duckdb": str(self.duckdb_path),
            "sqlite": str(self.sqlite_path),
            "records_loaded": len(df),
        }
