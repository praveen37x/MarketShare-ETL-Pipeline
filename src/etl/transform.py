"""
MarketShare-ETL-Pipeline: Vectorized Data Transformer
Uses Polars for high-speed cleaning, column regex standardization,
service taxonomy normalization, and market share calculation.
"""
import re
from typing import Any
import polars as pl
from src.config import config


class MarketShareTransformer:
    """Cleans and standardizes raw market share data."""

    @staticmethod
    def clean_column_name(col: str) -> str:
        """
        Standardizes column header:
        - Strips whitespace
        - Maps known variants (Vendor Name, Vendor.1, Vendor1 -> Vendor)
        - Normalizes revenue column variations
        """
        c = col.strip()
        # Direct dictionary check first
        if c in config.COLUMN_MAPPINGS:
            return config.COLUMN_MAPPINGS[c]

        # Handle Vendor.1 / Vendor1 / Vendor Name
        if re.match(r"^Vendor[\.\s_]*\d*$", c, re.IGNORECASE) or c.lower() == "vendor name":
            return "Vendor"

        # Handle VendorRevenue variations
        if "revenue" in c.lower() and "constant" not in c.lower():
            return "Vendor_Revenue_USD"
        if "constant" in c.lower():
            return "Constant_Currency_Revenue_USD"

        # General regex cleanup
        c = re.sub(r"[^\w\s]", "", c)
        c = re.sub(r"\s+", "_", c)
        return config.COLUMN_MAPPINGS.get(c, c)

    @classmethod
    def clean_service_names(cls, service_col: pl.Expr) -> pl.Expr:
        """Normalizes service taxonomy into canonical categories."""
        return (
            service_col
            .str.to_lowercase()
            .str.strip_chars()
            .replace({
                "application implementation": "Application Implementation",
                "managed services": "Managed Services",
                "data & ai consulting": "Data & AI Consulting",
                "infrastructure operations": "Infrastructure Operations",
            }, default=service_col.str.to_titlecase())
        )

    @classmethod
    def transform_single(cls, df: pl.DataFrame) -> pl.DataFrame:
        """Standardize and clean a single raw DataFrame."""
        # 1. Rename columns using standard regex cleaner
        rename_map = {orig: cls.clean_column_name(orig) for orig in df.columns}
        cleaned_df = df.rename(rename_map)

        # 2. Cast data types & clean strings
        cleaned_df = cleaned_df.with_columns([
            pl.col("Year").cast(pl.Int32),
            pl.col("Vendor").str.strip_chars(),
            pl.col("Super_Region").str.strip_chars(),
            pl.col("Vendor_Revenue_USD").cast(pl.Float64).fill_null(0.0),
            pl.col("Constant_Currency_Revenue_USD").cast(pl.Float64).fill_null(0.0),
        ])

        if "Service_2" in cleaned_df.columns:
            cleaned_df = cleaned_df.with_columns(
                cls.clean_service_names(pl.col("Service_2")).alias("Service_2")
            )

        return cleaned_df

    @classmethod
    def transform_and_aggregate(cls, dataframes: list[pl.DataFrame]) -> pl.DataFrame:
        """
        Concatenate multiple annual frames, deduplicate, and calculate market share % by Super Region and Year.
        """
        transformed = [cls.transform_single(df) for df in dataframes if len(df) > 0]
        if not transformed:
            return pl.DataFrame()

        combined = pl.concat(transformed, how="diagonal")

        # Deduplicate
        dedup = combined.unique()

        # Derive Market Total by Year & Super Region
        market_totals = (
            dedup
            .group_by(["Year", "Super_Region"])
            .agg(pl.col("Vendor_Revenue_USD").sum().alias("Total_Regional_Market_USD"))
        )

        final_df = (
            dedup
            .join(market_totals, on=["Year", "Super_Region"], how="left")
            .with_columns([
                ((pl.col("Vendor_Revenue_USD") / pl.col("Total_Regional_Market_USD")) * 100.0)
                .round(2)
                .alias("Market_Share_Pct")
            ])
            .sort(["Year", "Super_Region", "Vendor_Revenue_USD"], descending=[False, False, True])
        )

        return final_df
