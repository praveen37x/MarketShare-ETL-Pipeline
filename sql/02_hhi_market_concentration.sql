-- 02_hhi_market_concentration.sql
-- Herfindahl-Hirschman Index (HHI) for Market Concentration
-- HHI = SUM( (Market_Share_Pct)^2 )
-- HHI < 1500: Competitive / Unconcentrated
-- 1500 <= HHI <= 2500: Moderately Concentrated
-- HHI > 2500: Highly Concentrated / Oligopoly

WITH annual_shares AS (
    SELECT 
        Year,
        Vendor,
        SUM(Vendor_Revenue_USD) AS rev,
        SUM(Vendor_Revenue_USD) / SUM(SUM(Vendor_Revenue_USD)) OVER (PARTITION BY Year) * 100.0 AS share_pct
    FROM market_share
    GROUP BY Year, Vendor
)
SELECT 
    Year,
    ROUND(SUM(POWER(share_pct, 2)), 1) AS HHI_Score,
    COUNT(DISTINCT Vendor) AS Active_Vendors_Count,
    CASE 
        WHEN SUM(POWER(share_pct, 2)) > 2500 THEN 'Highly Concentrated (Oligopoly)'
        WHEN SUM(POWER(share_pct, 2)) >= 1500 THEN 'Moderately Concentrated'
        ELSE 'Competitive / Unconcentrated'
    END AS Market_Structure_Classification
FROM annual_shares
GROUP BY Year
ORDER BY Year ASC;
