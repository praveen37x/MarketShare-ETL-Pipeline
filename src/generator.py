"""
MarketShare-ETL-Pipeline: Multi-Year Raw Data Generator
Generates realistic Gartner/IDC style market share CSV feeds for 2019-2024.
Includes realistic real-world dirty data patterns:
- Irregular column names (e.g., 'Vendor.1', 'VendorRevenue - USD')
- Whitespace variations in service labels
- Regional and industry segmentation across premier tech vendors
"""
import random
import csv
from pathlib import Path
from src.config import config


class MarketShareDataGenerator:
    """Generates annual CSV feeds for 2019-2024."""

    def __init__(self, seed: int = 42):
        random.seed(seed)

    def generate_annual_dataset(self, year: int) -> list[dict[str, str | float]]:
        """Generate market share records for a specific calendar year."""
        records = []
        year_idx = year - 2019  # 0 to 5

        # Base market growth multiplier (tech market expanding ~12-18% annually)
        growth_multiplier = (1.14) ** year_idx

        for vendor, meta in config.MAJOR_VENDORS.items():
            # Base revenue profile
            if vendor in ["Microsoft", "Amazon Web Services", "Google Cloud"]:
                base_rev = 25000.0 * random.uniform(0.9, 1.1)
                share_growth = (1.22) ** year_idx  # Hyper-scale cloud growing faster
            elif vendor in ["Oracle", "Salesforce", "SAP"]:
                base_rev = 12000.0 * random.uniform(0.9, 1.1)
                share_growth = (1.12) ** year_idx
            else:
                base_rev = 6000.0 * random.uniform(0.9, 1.1)
                share_growth = (1.15) ** year_idx

            annual_rev = base_rev * share_growth

            for super_region in config.SUPER_REGIONS:
                reg_weight = {"North America": 0.48, "Western Europe": 0.26, "Asia/Pacific": 0.18, "Latin America": 0.05, "Middle East & Africa": 0.03}[super_region]
                reg_rev = annual_rev * reg_weight

                for s1 in config.SERVICES_1:
                    s2 = random.choice(config.SERVICES_2)
                    # Simulate real-world raw dirty formatting (trailing whitespace and irregular case)
                    if random.random() < 0.25:
                        s2_dirty = s2.lower() + "  "
                    else:
                        s2_dirty = s2

                    vert = random.choice(config.VERTICALS)
                    rev_usd = round((reg_rev / len(config.SERVICES_1)) * random.uniform(0.85, 1.15), 2)
                    cc_rev = round(rev_usd * random.uniform(0.96, 1.04), 2)

                    records.append({
                        "Year": str(year),
                        "Super Region": super_region,
                        "Region": super_region,
                        "Country": "Global Aggregate",
                        "Vendor.1": vendor,  # Dirty duplicate column name
                        "Service 1": s1,
                        "Service 2": s2_dirty,
                        "Service 3": "Enterprise Solutions",
                        "Vertical": vert,
                        "Ticker": meta["ticker"],
                        "HQ_Country": meta["hq"],
                        "VendorRevenue - USD": rev_usd,
                        "ConstantCurrency Revenue - USD": cc_rev,
                    })

        return records

    def write_csv_feeds(self, output_dir: Path, years: list[int] | None = None) -> list[Path]:
        """Write CSV files for all designated years into output_dir."""
        output_dir.mkdir(parents=True, exist_ok=True)
        target_years = years or [2019, 2020, 2021, 2022, 2023, 2024]
        created_paths = []

        for y in target_years:
            rows = self.generate_annual_dataset(y)
            out_file = output_dir / f"market_share_{y}.csv"
            with open(out_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)
            created_paths.append(out_file)

        return created_paths
