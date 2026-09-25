"""
MarketShare-ETL-Pipeline: End-to-End Orchestrator
Executes: Extract -> Transform -> Validate Quality -> Load Dual Databases -> Generate Insights
"""
import sys
from pathlib import Path
import polars as pl

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import duckdb
from src.config import config
from src.generator import MarketShareDataGenerator
from src.etl.extract import CSVExtractor
from src.etl.transform import MarketShareTransformer
from src.etl.load import DatabaseLoader
from src.etl.quality import DataQualityValidator
from src.analytics.market_metrics import MarketMetricsEngine


def run_pipeline():
    print("==================================================================")
    print("        [+] MarketShare-ETL: END-TO-END PIPELINE RUNNER           ")
    print("==================================================================\n")

    # 0. Ensure raw CSV files exist
    csv_files = list(config.RAW_DIR.glob("*.csv"))
    if not csv_files:
        print("[*] Step 0: Bootstrapping raw CSV feeds...")
        generator = MarketShareDataGenerator(seed=42)
        generator.write_csv_feeds(config.RAW_DIR)
        csv_files = list(config.RAW_DIR.glob("*.csv"))

    # 1. Extract
    print(f"[*] Step 1: Extracting {len(csv_files)} CSV files from {config.RAW_DIR}...")
    extractor = CSVExtractor(config.RAW_DIR)
    raw_dict = extractor.extract_all()
    for name, df in raw_dict.items():
        print(f"    - Extracted '{name}': {len(df):,} rows, {len(df.columns)} columns")

    # 2. Transform
    print("\n[*] Step 2: Transforming data with Polars...")
    final_df = MarketShareTransformer.transform_and_aggregate(list(raw_dict.values()))
    print(f"[+] Transformation complete: {len(final_df):,} conformed rows")

    # 3. Quality Validation
    print("\n[*] Step 3: Running Data Quality Audit...")
    report = DataQualityValidator.audit(final_df)
    print(f"    - Total Records:       {report.total_records:,}")
    print(f"    - Null Vendors:        {report.null_vendors}")
    print(f"    - Negative Revenues:   {report.negative_revenues}")
    print(f"    - Tracked Years:       {report.unique_years}")
    print(f"    - Unique Vendors:      {report.unique_vendors}")
    print(f"    - Audit Status:        {'PASSED' if report.passed else 'FAILED'}")

    # 4. Load
    print("\n[*] Step 4: Loading into DuckDB and SQLite dual databases...")
    loader = DatabaseLoader(config.DUCKDB_PATH, config.SQLITE_PATH)
    res = loader.load_all(final_df)
    print(f"[+] Loaded DuckDB: {res['duckdb']}")
    print(f"[+] Loaded SQLite: {res['sqlite']}")

    # 5. Summary Analytics
    print("\n[*] Step 5: Computing Market Analytics...")
    conn = duckdb.connect(str(config.DUCKDB_PATH))
    engine = MarketMetricsEngine(conn)
    summary = engine.get_executive_summary()
    print(f"    - 2019 Global Market Size: ${summary['market_size_2019_usd'] / 1000.0:,.2f}B")
    print(f"    - 2024 Global Market Size: ${summary['market_size_2024_usd'] / 1000.0:,.2f}B")
    print(f"    - 5-Year Market CAGR:      +{summary['market_cagr_pct']:.2f}%")

    print("\n[*] 2024 Top 5 Global Vendors by Market Share:")
    shares = engine.get_market_share_trajectory()
    top5_2024 = shares.filter(pl.col("Year") == 2024).head(5).to_dicts()
    for r in top5_2024:
        print(f"    #{r['Market_Rank']} {r['Vendor']:<26} | Revenue: ${r['Annual_Revenue_USD']:,.2f}M | Share: {r['Global_Market_Share_Pct']}%")

    conn.close()
    print("\n==================================================================")
    print("                     [#] PIPELINE SUCCESS [#]                     ")
    print("==================================================================\n")


if __name__ == "__main__":
    run_pipeline()
