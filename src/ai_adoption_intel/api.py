from fastapi import FastAPI,HTTPException
from sqlalchemy import text
from ai_adoption_intel.load import get_engine
import pandas as pd

app = FastAPI()
engine = get_engine()

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/national/ai-adoption")
def national_ai_adoption():
    query =""" SELECT period_start,percentage
    FROM national
    WHERE question_id = 7 AND answer = 'Yes' AND status = 'ok'
    ORDER BY period_start; """
    df = pd.read_sql_query(query,con = engine)
    records = df.to_dict(orient="records") 
    return records


@app.get("/sectors/ai-adoption")
def sector_ai_adoption(sector:str):
    query =text(""" SELECT period_start,percentage
    FROM sector
    WHERE question_id = 7 AND answer = 'Yes' AND status = 'ok' AND sector = :sector
    ORDER BY period_start; """)
    df = pd.read_sql_query(query,con = engine,params={"sector":sector})
    if df.empty:
        raise HTTPException(status_code = 404, detail = f"No AI adoption data was forund for number {sector} sector")
    records = df.to_dict(orient = "records")
    return records