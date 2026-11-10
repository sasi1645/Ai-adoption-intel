from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()
MODEL = "gpt-5.4-mini"
forbidden = ['delete','drop','truncate','update','alter','insert','create','grant','revoke']
SCHEMA_PROMT = """You write PostgreSQL queries for the ai_adoption_intel database.
Return only the SQL query: no explanation, no markdown.
Only write SELECT queries.

Tables:
- national(question_id INTEGER, question TEXT, answer_id INTEGER, answer TEXT,
  cycle TEXT, value TEXT, percentage FLOAT, status TEXT,
  period_start DATE, period_end DATE)
  All U.S. businesses. One row per question, answer and survey period. Has no sector column.
- sector(sector TEXT, question_id INTEGER, question TEXT, answer_id INTEGER, answer TEXT,
  cycle TEXT, value TEXT, percentage FLOAT, status TEXT,
  period_start DATE, period_end DATE)
  The same data, broken down by industry sector.
- sector_names(sector TEXT, name TEXT)
  One row per sector code, e.g. '11' = 'Agriculture, Forestry, Fishing and Hunting'.
  Join to sector on sector.sector = sector_names.sector.

Rules:
- question_id = 7: did the business use AI in the last two weeks.
- question_id = 24: does the business expect to use AI in the next six months.
- answer = 'Yes' means the business uses (or expects to use) AI.
- percentage is the share of businesses (%) that gave this answer in that period.
  Use percentage for numbers; never use value.
- Always filter status = 'ok' (other values: 'suppressed', 'not_collected').
- The latest period is period_start = (SELECT MAX(period_start) FROM <table>).
- Sector 'XX' means multi-sector or multi-state companies.

Example:
Question: Which sectors had the highest AI use in the latest period?
SQL:
SELECT sector.sector, sector_names.name, percentage
FROM sector
JOIN sector_names ON sector.sector = sector_names.sector
WHERE question_id = 7 AND answer = 'Yes' AND status = 'ok'
  AND period_start = (SELECT MAX(period_start) FROM sector)
ORDER BY percentage DESC
LIMIT 5;"""
client = OpenAI()
def generate_sql(question: str):
    response = client.responses.create(
        model = MODEL,
        instructions = SCHEMA_PROMT,
        input = question
    )
    return response.output_text

def is_safe_sql(sql:str) -> bool:
    sql = sql.lower().strip()
    if not sql.startswith(("select","with")):
        return False
    sql = sql.rstrip(";")
    if ";" in sql:
        return False
    for word in forbidden:
        if word in sql:
            return False
    return True
