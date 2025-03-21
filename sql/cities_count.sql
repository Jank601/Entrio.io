-- Query 1: Returns a list of cities and the number of times each city appears in the dataset
SELECT city, COUNT(*) AS count
FROM companies
WHERE city IS NOT NULL
GROUP BY city
ORDER BY count DESC;