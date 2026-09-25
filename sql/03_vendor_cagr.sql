-- 03_vendor_cagr.sql
-- 5-Year Compound Annual Growth Rate (CAGR) by Tech Vendor (2019 to 2024)
-- Formula: ( (End_Revenue / Start_Revenue) ^ (1/N) ) - 1

WITH vendor_endpoints AS (
    SELECT 
        Vendor,
        Ticker,
        HQ_Country,
        SUM(CASE WHEN Year = 2019 THEN Vendor_Revenue_USD ELSE 0 END) AS Revenue_2019,
        SUM(CASE WHEN Year = 2024 THEN Vendor_Revenue_USD ELSE 0 END) AS Revenue_2024
    FROM market_share
    WHERE Year IN (2019, 2024)
    GROUP BY Vendor, Ticker, HQ_Country
)
SELECT 
    Vendor,
    Ticker,
    HQ_Country,
    ROUND(Revenue_2019, 2) AS Revenue_2019_USD,
    ROUND(Revenue_2024, 2) AS Revenue_2024_USD,
    ROUND(
        (POWER(Revenue_2024 / NULLIF(Revenue_2019, 0), 1.0 / 5.0) - 1.0) * 100.0, 
        2
    ) AS Five_Year_CAGR_Pct
FROM vendor_endpoints
WHERE Revenue_2019 > 0
ORDER BY Five_Year_CAGR_Pct DESC;
