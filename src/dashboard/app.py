"""
MarketShare-ETL-Pipeline: Executive Market Share & Vendor Intelligence Portal
Interactive Streamlit dashboard visualizing Gartner/IDC market share trends,
HHI concentration dynamics, 5-year CAGR benchmarks, and SQL querying.
"""
import sys
from pathlib import Path
import streamlit as st
import duckdb
import polars as pl
import pandas as pd

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.config import config
from src.generator import MarketShareDataGenerator
from src.etl.extract import CSVExtractor
from src.etl.transform import MarketShareTransformer
from src.etl.load import DatabaseLoader
from src.analytics.market_metrics import MarketMetricsEngine

st.set_page_config(
    page_title="Global IT & Cloud Market Share Intelligence",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .metric-card {
        background-color: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 8px;
        padding: 16px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_database_connection():
    config.RAW_DIR.mkdir(parents=True, exist_ok=True)
    config.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # If database doesn't exist, run full pipeline on the fly
    if not config.DUCKDB_PATH.exists():
        generator = MarketShareDataGenerator(seed=42)
        generator.write_csv_feeds(config.RAW_DIR)

        extractor = CSVExtractor(config.RAW_DIR)
        raw_dict = extractor.extract_all()

        final_df = MarketShareTransformer.transform_and_aggregate(list(raw_dict.values()))
        loader = DatabaseLoader(config.DUCKDB_PATH, config.SQLITE_PATH)
        loader.load_all(final_df)

    return duckdb.connect(str(config.DUCKDB_PATH))


conn = get_database_connection()
engine = MarketMetricsEngine(conn)

# Sidebar
st.sidebar.title("🌐 MarketShare-ETL")
st.sidebar.caption("Gartner & IDC Global Vendor Intelligence")

st.sidebar.markdown("---")
st.sidebar.subheader("Pipeline Health")
raw_files = len(list(config.RAW_DIR.glob("*.csv")))
st.sidebar.write(f"📁 **Raw Annual CSV Feeds:** {raw_files} files (2019-2024)")

rec_cnt = conn.sql("SELECT COUNT(*) FROM market_share;").fetchone()[0]
st.sidebar.write(f"✨ **Conformed Records:** {rec_cnt:,} rows")
st.sidebar.write(f"🗄️ **Storage Engines:** DuckDB + SQLite")

# Top Header Banner
st.title("🌐 Global IT Services & Cloud Market Share Intelligence")
st.caption("Institutional ETL Pipeline & Market Concentration Analytics (2019–2024) — Made by Praveen Tripathi")

summary = engine.get_executive_summary()

c1, c2, c3, c4 = st.columns(4)
c1.metric("2024 Market Size", f"${summary['market_size_2024_usd'] / 1000.0:,.1f} Billion")
c2.metric("2019 Market Size", f"${summary['market_size_2019_usd'] / 1000.0:,.1f} Billion")
c3.metric("5-Year Market CAGR", f"+{summary['market_cagr_pct']:.1f}%")
c4.metric("Tracked Premier Vendors", summary['total_vendors'])

st.markdown("---")

tab_share, tab_hhi, tab_cagr, tab_regional, tab_sql = st.tabs([
    "📊 Market Share Trajectory",
    "🏛️ Market Concentration (HHI)",
    "🚀 5-Year CAGR Leaders",
    "🌍 Regional & Service Breakdown",
    "💻 DuckDB SQL Studio"
])

# ----------------- TAB 1: Market Share Trajectory -----------------
with tab_share:
    st.subheader("📊 Global Vendor Market Share Trajectory (2019–2024)")
    shares_df = engine.get_market_share_trajectory().to_pandas()

    pivot_share = shares_df.pivot(index="Year", columns="Vendor", values="Global_Market_Share_Pct")
    st.line_chart(pivot_share)

    st.subheader("2024 Market Share Leaderboard")
    df_2024 = shares_df[shares_df["Year"] == 2024][["Market_Rank", "Vendor", "Ticker", "HQ_Country", "Annual_Revenue_USD", "Global_Market_Share_Pct"]]
    st.dataframe(df_2024.reset_index(drop=True), use_container_width=True)

# ----------------- TAB 2: HHI Concentration -----------------
with tab_hhi:
    st.subheader("🏛️ Herfindahl-Hirschman Index (HHI) Market Concentration")
    st.caption("Standard antitrust & regulatory metric: HHI < 1500 (Competitive), 1500-2500 (Moderately Concentrated), > 2500 (Oligopoly).")

    hhi_df = engine.get_hhi_scores().to_pandas()
    st.line_chart(hhi_df.set_index("Year")["HHI_Score"])
    st.dataframe(hhi_df, use_container_width=True)

# ----------------- TAB 3: 5-Year CAGR Leaders -----------------
with tab_cagr:
    st.subheader("🚀 5-Year Compound Annual Growth Rate (CAGR) by Vendor")
    cagr_df = engine.get_vendor_cagr_ranking().to_pandas()

    st.bar_chart(cagr_df.set_index("Vendor")["Five_Year_CAGR_Pct"])
    st.dataframe(cagr_df, use_container_width=True)

# ----------------- TAB 4: Regional Breakdown -----------------
with tab_regional:
    st.subheader("🌍 Regional Spend & Market Dominance Breakdown (2024)")
    sql_reg = config.SQL_DIR / "04_regional_breakdown.sql"
    with open(sql_reg, "r", encoding="utf-8") as f:
        reg_df = conn.sql(f.read()).pl().to_pandas()

    st.dataframe(reg_df, use_container_width=True)

# ----------------- TAB 5: SQL Studio -----------------
with tab_sql:
    st.subheader("💻 In-Process DuckDB SQL Studio")
    st.caption("Query the conformed market share lakehouse directly.")

    sample_sql = """
    SELECT 
        Vendor,
        Service_1,
        ROUND(SUM(Vendor_Revenue_USD), 2) AS Total_Revenue_USD,
        ROUND(AVG(Market_Share_Pct), 2) AS Avg_Market_Share_Pct
    FROM market_share
    WHERE Year = 2024
    GROUP BY Vendor, Service_1
    ORDER BY Total_Revenue_USD DESC
    LIMIT 15;
    """
    query_str = st.text_area("SQL Query", sample_sql, height=140)

    if st.button("▶ Run SQL Query"):
        try:
            res_df = conn.sql(query_str).pl().to_pandas()
            st.dataframe(res_df, use_container_width=True)
            st.caption(f"Retrieved {len(res_df)} rows.")
        except Exception as e:
            st.error(f"SQL Execution Error: {e}")
