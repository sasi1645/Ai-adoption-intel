-- AI adoption over time 
SELECT period_start,percentage
FROM national
WHERE question_id = 7 AND answer = 'Yes' AND status = 'ok'
ORDER BY period_start;

-- Top sectors AI use in latest period and names. 
SELECT sector.sector,sector_names.name,period_start,percentage
FROM sector
JOIN sector_names ON sector.sector = sector_names.sector
WHERE question_id = 7 AND answer = 'Yes' AND status = 'ok' AND period_start = (SELECT MAX(period_start) FROM sector)
ORDER BY percentage DESC
Limit 5;