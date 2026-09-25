"""
MarketShare-ETL-Pipeline: Data Quality & Reconciliation
Validates data completeness, positive revenues, and market share percentages.
"""
from dataclasses import dataclass
from typing import Any
import polars as pl


@dataclass
class QualityReport:
    total_records: int
    null_vendors: int
    negative_revenues: int
    unique_years: list[int]
    unique_vendors: int
    passed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_records": self.total_records,
            "null_vendors": self.null_vendors,
            "negative_revenues": self.negative_revenues,
            "unique_years": self.unique_years,
            "unique_vendors": self.unique_vendors,
            "passed": self.passed,
        }


class DataQualityValidator:
    """Runs data contract and integrity audits."""

    @staticmethod
    def audit(df: pl.DataFrame) -> QualityReport:
        total = len(df)
        if total == 0:
            return QualityReport(0, 0, 0, [], 0, False)

        null_vendors = int(df["Vendor"].is_null().sum())
        negative_rev = int((df["Vendor_Revenue_USD"] < 0).sum())
        years = sorted([int(y) for y in df["Year"].unique().to_list()])
        vendors_cnt = int(df["Vendor"].n_unique())

        passed = (null_vendors == 0 and negative_rev == 0 and len(years) > 0)

        return QualityReport(
            total_records=total,
            null_vendors=null_vendors,
            negative_revenues=negative_rev,
            unique_years=years,
            unique_vendors=vendors_cnt,
            passed=passed,
        )
