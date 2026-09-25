"""
Unit tests for Dual Database Loader (DuckDB + SQLite)
"""
from pathlib import Path
import sqlite3
import duckdb
import polars as pl
from src.etl.load import DatabaseLoader


def test_dual_database_loader(tmp_path: Path):
    duckdb_file = tmp_path / "test_market_share.duckdb"
    sqlite_file = tmp_path / "test_market_share.sqlite"

    df = pl.DataFrame({
        "Year": [2024],
        "Super_Region": ["North America"],
        "Region": ["North America"],
        "Country": ["USA"],
        "Vendor": ["Microsoft"],
        "Service_1": ["Cloud"],
        "Service_2": ["Managed Services"],
        "Service_3": ["Enterprise"],
        "Vertical": ["BFSI"],
        "Ticker": ["MSFT"],
        "HQ_Country": ["USA"],
        "Vendor_Revenue_USD": [50000.0],
        "Constant_Currency_Revenue_USD": [50100.0],
        "Total_Regional_Market_USD": [100000.0],
        "Market_Share_Pct": [50.0],
    })

    loader = DatabaseLoader(duckdb_file, sqlite_file)
    loader.load_all(df)

    # Test DuckDB persistence
    conn_duck = duckdb.connect(str(duckdb_file))
    res_duck = conn_duck.sql("SELECT COUNT(*) FROM market_share;").fetchone()[0]
    assert res_duck == 1
    conn_duck.close()

    # Test SQLite persistence
    conn_sqlite = sqlite3.connect(str(sqlite_file))
    cursor = conn_sqlite.cursor()
    cursor.execute("SELECT COUNT(*) FROM market_share;")
    res_sqlite = cursor.fetchone()[0]
    assert res_sqlite == 1
    conn_sqlite.close()
