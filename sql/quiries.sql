-- AI adoption over time 
SELECT period_start,percentage
FROM national
WHERE question_id = 7 AND answer = 'Yes' AND status = 'ok'
ORDER BY period_start