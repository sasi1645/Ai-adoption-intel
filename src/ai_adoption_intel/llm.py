import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from sqlalchemy.exc import DBAPIError

from ai_adoption_intel.load import get_engine

load_dotenv()
sql_MODEL = "gpt-5.4"
answer_model = "gpt-5.4-mini"
FORBIDDEN = [
    "delete",
    "drop",
    "truncate",
    "update",
    "alter",
    "insert",
    "create",
    "grant",
    "revoke",
]
SCHEMA_PROMPT = """You write PostgreSQL queries for the ai_adoption_intel database.
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
- sector_names(sector,name) 
-sector values:
('11','Agriculture, Forestry, Fishing and Hunting'),
('21','Mining, Quarrying, and Oil and Gas Extraction'),
('22','Utilities'),
('23','Construction'),
('31', 'Manufacturing'),
('42', 'Wholesale Trade'),
('44', 'Retail Trade'),
('48', 'Transportation and Warehousing'),
('51', 'Information'),
('52', 'Finance and Insurance'),
('53', 'Real Estate and Rental and Leasing'),
('54', 'Professional, Scientific, and Technical Services'),
('55',	'Management of Companies and Enterprises'),
('56',	'Administrative and Support and Waste Management'),
('61',	'Educational Services'),
('62',	'Health Care and Social Assistance'),
('71',	'Arts, Entertainment, and Recreation'),
('72',	'Accommodation and Food Services'),
('81',	'Other Services (except Public Administration)'),
('XX',	'Multi-sector or multi-state companies');

Rules:
- question_id = 7: did the business use AI in the last two weeks.
- question_id = 24: does the business expect to use AI in the next six months.
- answer = 'Yes' means the business uses (or expects to use) AI.
- percentage is the share of businesses (%) that gave this answer in that period.
  Use percentage for numbers; never use value.
- Always filter status = 'ok' (other values: 'suppressed', 'not_collected').
- The latest period is period_start = (SELECT MAX(period_start) FROM <table>).
- Sector 'XX' means multi-sector or multi-state companies.
- For questions about industries, exclude sector 'XX'.
- If the question asks about an industry that is not in this list, do not guess. Return exactly: SELECT 1 WHERE false;
- For sector questions, always select sector_names.name.
- Use only the exact sector codes listed above. Never use NAICS code ranges such as '44-45', '31-33' or '48-49'.
- sector_names(sector TEXT, name TEXT). Join to sector on sector.sector = sector_names.sector

Map everyday terms to the closest listed sector when the meaning is clear, e.g.:
- cinema, movies, music → '71' Arts, Entertainment, and Recreation
- hospital, clinic, nursing home → '62' Health Care and Social Assistance
- banks → '52' Finance and Insurance
If no listed sector clearly fits, return exactly: SELECT 1 WHERE false;

Example1:
Question: Which sectors had the highest AI use in the latest period?
SQL:
SELECT sector.sector, sector_names.name, percentage
FROM sector
JOIN sector_names ON sector.sector = sector_names.sector
WHERE question_id = 7 AND answer = 'Yes' AND status = 'ok'
  AND period_start = (SELECT MAX(period_start) FROM sector)
ORDER BY percentage DESC
LIMIT 5;
Example2:
Question: How has AI use changed in retail?
SQL:
SELECT
  s.period_start,
  s.percentage AS ai_use_percentage,sn.name
FROM sector s
JOIN sector_names sn ON s.sector = sn.sector
WHERE s.sector = '44'
  AND s.question_id = 7
  AND s.answer = 'Yes'
  AND s.status = 'ok'
ORDER BY s.period_start;"""

ANSWER_PROMPT = """You answer the quetions using only the provide rows of data.
Answer should be in one sentance.
percentages: 
Percentages are the share of businesses in that group (all U.S. businesses, or the named sector) that gave this answer.
Only use the data provided.
If the data provides period_start and period_end make sure to mention them.
use names not codes for sectors. If mention of code give both name and code at that time.
If there are many rows summerize them give the first and last value and overall direction.
No lists, bolds, or mentions of SQL and not offer further help.
"""
client = OpenAI()
readonly_engine = get_engine("READONLY_DATABASE_URL")


def generate_sql(question: str) -> str:
    response = client.responses.create(
        model=sql_MODEL, instructions=SCHEMA_PROMPT, input=question
    )
    return response.output_text


def is_safe_sql(sql: str) -> bool:
    sql = sql.lower().strip()
    if not sql.startswith(("select", "with")):
        return False
    sql = sql.rstrip(";")
    if ";" in sql:
        return False
    for word in FORBIDDEN:
        if word in sql:
            return False
    return True


def explain(question: str, rows: list) -> str:
    if not rows:
        return "No matching data was Found."
    response = client.responses.create(
        model=answer_model,
        instructions=ANSWER_PROMPT,
        input=f"Question: {question}\n Data: {rows}",
    )
    return response.output_text


def ask(question: str) -> dict:
    sql = generate_sql(question)
    if not is_safe_sql(sql):
        raise ValueError("The query is not safe for the database.")
    try:
        df = pd.read_sql_query(sql, con=readonly_engine)
    except DBAPIError:
        raise ValueError("The generated query could not be run") from explain
    records = df.to_dict(orient="records")
    answer = explain(question, records)
    return {"question": question, "sql": sql, "rows": records, "answer": answer}
