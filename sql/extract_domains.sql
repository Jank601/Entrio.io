-- Query 2: Extracts the main domain from the homepage url feature (http://www.experifun.com -> experifun)
SELECT 
    company_name,
    homepage_url,
    -- Remove everything up to "www." (if present) or after protocol
    -- Then take everything until the first dot
    SUBSTR(
        REPLACE(
            REPLACE(
                REPLACE(LOWER(homepage_url), 'http://', ''),
                'https://', ''
            ),
            'www.', ''
        ),
        1,
        INSTR(
            REPLACE(
                REPLACE(
                    REPLACE(LOWER(homepage_url), 'http://', ''),
                    'https://', ''
                ),
                'www.', ''
            ),
            '.'
        ) - 1
    ) AS main_domain
FROM companies
WHERE homepage_url IS NOT NULL;