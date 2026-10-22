import os
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine,text

PROCESSED_DIR = Path("data/processed")
def get_engine():
    load_dotenv() 
    URL = os.getenv("DATABASE_URL")
    if not URL:
        raise FileNotFoundError("DATABASE_URL is not found in the environment variables. please check your .env file.")
    engine = create_engine(URL)
    return engine

def read_processed(name:str) -> pd.DataFrame:
    path = PROCESSED_DIR/f"{name}_long.csv"
    if not path.exists():
        raise FileNotFoundError(f"{path} does not exist. Please run the data processing script first.")
    df = pd.read_csv(path,parse_dates=["period_start","period_end"])
    df = df.rename(columns = {"Question ID":"question_id", 
              "Question":"question",
              "Answer ID":"answer_id",
              "Answer":"answer"}
              )
    return df

def load_table(df: pd.DataFrame, table: str,engine) -> None:
    with engine.begin() as conn:
        conn.execute(text(f"TRUNCATE {table}"))
    df.to_sql(name = table, con=engine,if_exists="append",index=False)

def main()-> None:
    engine = get_engine()
    table = "national"
    df = read_processed(table)
    load_table(df,table,engine)
    print(f"Loaded the {len(df)} rows into {table}")

if __name__ == "__main__":
    main()

    