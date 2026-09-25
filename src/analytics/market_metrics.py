"""
MarketShare-ETL-Pipeline: Market Metrics Engine
Executes analytical SQL and computes market share trajectory, HHI, and vendor growth.
"""
from typing import Any
import duckdb
import polars as pl
from src.config import config


class MarketMetricsEngine:
    """Calculates competitive market metrics using DuckDB."""

    def __init__(self, conn: duckdb.DuckDBPyConnection):
        self.conn = conn

    def get_market_share_trajectory(self) -> pl.DataFrame:
        """Execute market share rankings query."""
        sql_path = config.SQL_DIR / "01_market_share_by_vendor.sql"
        with open(sql_path, "r", encoding="utf-8") as f:
            query = f.read()
        return self.conn.sql(query).pl()

    def get_hhi_scores(self) -> pl.DataFrame:
        """Execute HHI concentration query."""
        sql_path = config.SQL_DIR / "02_hhi_market_concentration.sql"
        with open(sql_path, "r", encoding="utf-8") as f:
            query = f.read()
        return self.conn.sql(query).pl()

    def get_vendor_cagr_ranking(self) -> pl.DataFrame:
        """Execute 5-year CAGR ranking query."""
        sql_path = config.SQL_DIR / "03_vendor_cagr.sql"
        with open(sql_path, "r", encoding="utf-8") as f:
            query = f.read()
        return self.conn.sql(query).pl()

    def get_executive_summary(self) -> dict[str, Any]:
        """Calculates executive market overview metrics."""
        sql = """
        SELECT 
            COUNT(DISTINCT Vendor) AS total_vendors,
            COUNT(DISTINCT Super_Region) AS total_regions,
            ROUND(SUM(CASE WHEN Year = 2024 THEN Vendor_Revenue_USD ELSE 0 END), 2) AS market_size_2024,
            ROUND(SUM(CASE WHEN Year = 2019 THEN Vendor_Revenue_USD ELSE 0 END), 2) AS market_size_2019
        FROM market_share;
        """
        row = self.conn.sql(sql).pl().to_dicts()[0]
        rev_19 = row["market_size_2019"]
        rev_24 = row["market_size_2024"]
        cagr = round(((rev_24 / rev_19) ** (1.0 / 5.0) - 1.0) * 100.0, 2) if rev_19 > 0 else 0.0

        return {
            "total_vendors": row["total_vendors"],
            "total_regions": row["total_regions"],
            "market_size_2019_usd": rev_19,
            "market_size_2024_usd": rev_24,
            "market_cagr_pct": cagr,
        }
