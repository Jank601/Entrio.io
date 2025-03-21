-- Query 3: Returns 2 company names - the company with the most and the least amount of funding
SELECT company_name, funding_total_usd
FROM companies
WHERE funding_total_usd = (SELECT MAX(funding_total_usd) FROM companies)
UNION ALL
SELECT company_name, funding_total_usd
FROM companies
WHERE funding_total_usd = (SELECT MIN(funding_total_usd) FROM companies WHERE funding_total_usd > 0);