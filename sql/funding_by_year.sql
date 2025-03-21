-- Query 4: Returns a company name, the funding_total_usd of the company and the SUM of the funding_total_usd of all the companies which were founded in the same year as the company
SELECT 
    a.company_name, 
    a.funding_total_usd,
    (SELECT SUM(b.funding_total_usd) 
     FROM companies b 
     WHERE b.founded_year = a.founded_year) as total_funding_for_year
FROM companies a
WHERE a.founded_year IS NOT NULL
ORDER BY a.company_name;