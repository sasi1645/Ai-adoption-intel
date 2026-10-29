import pandas as pd
from fastapi import FastAPI, HTTPException
from sqlalchemy import text

from ai_adoption_intel.load import get_engine

app = FastAPI()
engine = get_engine()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/national/ai-adoption")
def national_ai_adoption():
    query = """ SELECT period_start,percentage
    FROM national
    WHERE question_id = 7 AND answer = 'Yes' AND status = 'ok'
    ORDER BY period_start; """
    df = pd.read_sql_query(query, con=engine)
    records = df.to_dict(orient="records")
    return records


@app.get("/sectors/ai-adoption")
def sector_ai_adoption(sector: str):
    query = text(""" SELECT period_start,percentage
    FROM sector
    WHERE question_id = 7 AND answer = 'Yes' AND status = 'ok' AND sector = :sector
    ORDER BY period_start; """)
    df = pd.read_sql_query(query, con=engine, params={"sector": sector})
    if df.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No AI adoption data was found for number {sector} sector",
        )
    records = df.to_dict(orient="records")
    return records


@app.get("/sectors/ranking")
def sector_ranking(limit: int = 5):
    query = text(""" SELECT sector.sector,sector_names.name,percentage
    FROM sector
    JOIN sector_names ON sector.sector = sector_names.sector
    WHERE question_id = 7 AND answer = 'Yes' AND status = 'ok' AND period_start = (SELECT MAX(period_start) FROM sector)
    ORDER BY percentage DESC
     LIMIT :limit; """)
    df = pd.read_sql_query(query, con=engine, params={"limit": limit})
    records = df.to_dict(orient="records")
    return records
