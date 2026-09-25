"""
MarketShare-ETL-Pipeline: Configuration & Schema Mappings
"""
from pathlib import Path


class Config:
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    RAW_DIR: Path = DATA_DIR / "raw"
    PROCESSED_DIR: Path = DATA_DIR / "processed"
    SQL_DIR: Path = BASE_DIR / "sql"

    # Dual Storage Options (DuckDB for high-speed OLAP, SQLite for relational persistence)
    DUCKDB_PATH: Path = PROCESSED_DIR / "market_share.duckdb"
    SQLITE_PATH: Path = PROCESSED_DIR / "market_share.sqlite"

    # Canonical Standard Column Name Mapping (Handling duplicate suffixes & irregular vendor headers)
    COLUMN_MAPPINGS: dict[str, str] = {
        "Vendor Name": "Vendor",
        "Vendor.1": "Vendor",
        "Vendor1": "Vendor",
        "vendor": "Vendor",
        "Super Region": "Super_Region",
        "super_region": "Super_Region",
        "VendorRevenue - USD": "Vendor_Revenue_USD",
        "Vendor_Revenue_USD_Millions": "Vendor_Revenue_USD",
        "ConstantCurrency Revenue - USD": "Constant_Currency_Revenue_USD",
        "Constant_Currency_Revenue_USD_Millions": "Constant_Currency_Revenue_USD",
        "Service 1": "Service_1",
        "Service 2": "Service_2",
        "Service 3": "Service_3",
    }

    # Canonical Vendors & Market Tickers
    MAJOR_VENDORS = {
        "Microsoft": {"ticker": "MSFT", "hq": "United States"},
        "Amazon Web Services": {"ticker": "AMZN", "hq": "United States"},
        "Google Cloud": {"ticker": "GOOGL", "hq": "United States"},
        "IBM": {"ticker": "IBM", "hq": "United States"},
        "Oracle": {"ticker": "ORCL", "hq": "United States"},
        "Salesforce": {"ticker": "CRM", "hq": "United States"},
        "SAP": {"ticker": "SAP", "hq": "Germany"},
        "Accenture": {"ticker": "ACN", "hq": "Ireland"},
        "Tata Consultancy Services": {"ticker": "TCS.NS", "hq": "India"},
        "Infosys": {"ticker": "INFY", "hq": "India"},
        "Snowflake": {"ticker": "SNOW", "hq": "United States"},
        "Datadog": {"ticker": "DDOG", "hq": "United States"},
    }

    SUPER_REGIONS = ["North America", "Western Europe", "Asia/Pacific", "Latin America", "Middle East & Africa"]
    SERVICES_1 = ["Cloud Infrastructure & Platform Services", "Enterprise Application Software", "IT Management Services", "Cybersecurity & Identity"]
    SERVICES_2 = ["Managed Services", "Application Implementation", "Data & AI Consulting", "Infrastructure Operations"]
    VERTICALS = ["Banking & Financial Services", "Healthcare & Life Sciences", "Retail & Consumer Goods", "Public Sector & Government", "Manufacturing"]


config = Config()
