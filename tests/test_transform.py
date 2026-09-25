"""
Unit tests for Market Share Transformation & Column Normalization
"""
import polars as pl
from src.etl.transform import MarketShareTransformer


def test_clean_column_name():
    # Tests the exact problem Nirmit29's project addressed
    assert MarketShareTransformer.clean_column_name("Vendor.1") == "Vendor"
    assert MarketShareTransformer.clean_column_name("Vendor1") == "Vendor"
    assert MarketShareTransformer.clean_column_name("Vendor Name") == "Vendor"
    assert MarketShareTransformer.clean_column_name("Super Region") == "Super_Region"
    assert MarketShareTransformer.clean_column_name("VendorRevenue - USD") == "Vendor_Revenue_USD"


def test_transform_single():
    df = pl.DataFrame({
        "Year": [2024],
        "Super Region": ["North America"],
        "Vendor.1": ["Microsoft"],
        "Service 2": ["application implementation  "],
        "VendorRevenue - USD": [15000.0],
        "ConstantCurrency Revenue - USD": [15100.0],
    })

    cleaned = MarketShareTransformer.transform_single(df)
    assert "Vendor" in cleaned.columns
    assert "Vendor.1" not in cleaned.columns
    assert cleaned["Service_2"][0] == "Application Implementation"
    assert cleaned["Vendor_Revenue_USD"][0] == 15000.0


def test_market_share_aggregation():
    df1 = pl.DataFrame({
        "Year": [2024, 2024],
        "Super Region": ["North America", "North America"],
        "Vendor.1": ["VendorA", "VendorB"],
        "Service 2": ["Managed Services", "Managed Services"],
        "VendorRevenue - USD": [300.0, 700.0],
        "ConstantCurrency Revenue - USD": [300.0, 700.0],
    })

    final_df = MarketShareTransformer.transform_and_aggregate([df1])
    assert "Market_Share_Pct" in final_df.columns
    assert "Total_Regional_Market_USD" in final_df.columns

    # VendorB has 700 out of 1000 = 70.0%
    row_b = final_df.filter(pl.col("Vendor") == "VendorB")
    assert row_b["Market_Share_Pct"][0] == 70.0

    # VendorA has 300 out of 1000 = 30.0%
    row_a = final_df.filter(pl.col("Vendor") == "VendorA")
    assert row_a["Market_Share_Pct"][0] == 30.0
