-- 04_regional_breakdown.sql
-- Regional Market Dominance Breakdown (2024 Snapshot)
-- Identifies top vendor and regional spend distribution

WITH regional_vendor_totals AS (
    SELECT 
        Super_Region,
        Vendor,
        SUM(Vendor_Revenue_USD) AS Regional_Revenue
    FROM market_share
    WHERE Year = 2024
    GROUP BY Super_Region, Vendor
),
regional_totals AS (
    SELECT 
        Super_Region,
        SUM(Regional_Revenue) AS Total_Market
    FROM regional_vendor_totals
    GROUP BY Super_Region
)
SELECT 
    r.Super_Region,
    r.Vendor,
    ROUND(r.Regional_Revenue, 2) AS Regional_Revenue_USD,
    ROUND((r.Regional_Revenue / t.Total_Market) * 100.0, 2) AS Regional_Share_Pct,
    DENSE_RANK() OVER (PARTITION BY r.Super_Region ORDER BY r.Regional_Revenue DESC) AS Regional_Rank
FROM regional_vendor_totals r
JOIN regional_totals t ON r.Super_Region = t.Super_Region
ORDER BY r.Super_Region ASC, Regional_Rank ASC;
