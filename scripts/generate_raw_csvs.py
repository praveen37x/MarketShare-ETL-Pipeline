"""
MarketShare-ETL-Pipeline: Raw CSV Feeds Generator Script
Pre-populates data/raw/ with multi-year market share CSVs (2019-2024).
"""
import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.config import config
from src.generator import MarketShareDataGenerator


def main():
    print("==================================================================")
    print("      [+] MarketShare-ETL: Generating Raw CSV Feeds (2019-2024)   ")
    print("==================================================================\n")

    config.RAW_DIR.mkdir(parents=True, exist_ok=True)
    generator = MarketShareDataGenerator(seed=42)
    files = generator.write_csv_feeds(config.RAW_DIR)

    for f in files:
        print(f"[+] Generated: {f} ({f.stat().st_size:,} bytes)")

    print(f"\n[+] Successfully created {len(files)} annual CSV feeds in {config.RAW_DIR}")


if __name__ == "__main__":
    main()
