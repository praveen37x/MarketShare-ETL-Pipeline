-- 01_market_share_by_vendor.sql
-- Computes Annual Market Share % and Rankings by Vendor across 2019-2024

WITH annual_vendor_totals AS (
    SELECT 
        Year,
        Vendor,
        Ticker,
        HQ_Country,
        ROUND(SUM(Vendor_Revenue_USD), 2) AS Annual_Revenue_USD
    FROM market_share
    GROUP BY Year, Vendor, Ticker, HQ_Country
),
annual_market_totals AS (
    SELECT 
        Year,
        SUM(Annual_Revenue_USD) AS Total_Global_Market_USD
    FROM annual_vendor_totals
    GROUP BY Year
)
SELECT 
    v.Year,
    v.Vendor,
    v.Ticker,
    v.HQ_Country,
    v.Annual_Revenue_USD,
    ROUND((v.Annual_Revenue_USD / m.Total_Global_Market_USD) * 100.0, 2) AS Global_Market_Share_Pct,
    DENSE_RANK() OVER (PARTITION BY v.Year ORDER BY v.Annual_Revenue_USD DESC) AS Market_Rank
FROM annual_vendor_totals v
JOIN annual_market_totals m ON v.Year = m.Year
ORDER BY v.Year ASC, v.Annual_Revenue_USD DESC;
