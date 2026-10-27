from fastapi import FastAPI
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