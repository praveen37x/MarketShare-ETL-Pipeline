"""
Unit tests for Market Analytics (HHI and CAGR)
"""
import duckdb
from src.analytics.market_metrics import MarketMetricsEngine


def test_market_metrics_engine():
    conn = duckdb.connect(":memory:")
    conn.execute("""
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

    # Insert 2 vendors for 2019 and 2024
    conn.execute("""
        INSERT INTO market_share VALUES 
        (2019, 'North America', 'NA', 'USA', 'VendorA', 'S1', 'S2', 'S3', 'V1', 'VA', 'USA', 1000.0, 1000.0, 2000.0, 50.0),
        (2019, 'North America', 'NA', 'USA', 'VendorB', 'S1', 'S2', 'S3', 'V1', 'VB', 'USA', 1000.0, 1000.0, 2000.0, 50.0),
        (2024, 'North America', 'NA', 'USA', 'VendorA', 'S1', 'S2', 'S3', 'V1', 'VA', 'USA', 2000.0, 2000.0, 4000.0, 50.0),
        (2024, 'North America', 'NA', 'USA', 'VendorB', 'S1', 'S2', 'S3', 'V1', 'VB', 'USA', 2000.0, 2000.0, 4000.0, 50.0);
    """)

    engine = MarketMetricsEngine(conn)
    summary = engine.get_executive_summary()
    assert summary["total_vendors"] == 2
    assert summary["market_size_2019_usd"] == 2000.0
    assert summary["market_size_2024_usd"] == 4000.0
    assert summary["market_cagr_pct"] > 14.0

    hhi_df = engine.get_hhi_scores()
    assert len(hhi_df) == 2
    # Equal 50/50 split -> HHI = 50^2 + 50^2 = 5000 (Highly Concentrated)
    assert hhi_df["HHI_Score"][0] == 5000.0

    conn.close()
