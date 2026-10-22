"""Loading the Census Business Trends and Outlook Survey(BTOS) excel file and turn them into clean data, changing it from wide to long format."""
from pathlib import Path
import pandas as pd

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")

def find_file(level:str) -> Path:
   matches = sorted(RAW_DIR.glob(f"*{level}.xlsx"))
   if not matches:
       raise FileNotFoundError(f"No file found for level '{level}' in {RAW_DIR}")
   return matches[-1]

def drop_footnotes(df: pd.DataFrame, key_col:str) -> pd.DataFrame:
    key =pd.to_numeric(df[key_col], errors = "coerce")
    return df[key.notna()].copy()

def to_long(df: pd.DataFrame) -> pd.DataFrame:
    date_cols = [c for c in df.columns if str(c).isdigit()]
    id_cols = [c for c in df.columns if c not in date_cols]
    return df.melt(id_vars = id_cols, value_vars = date_cols,var_name = 'cycle',value_name = 'value')

def clean_values(new_df:pd.DataFrame) -> pd.DataFrame:
    new_df = new_df.copy()
    new_df["status"] = "ok"
    new_df.loc[new_df["value"] =="S","status"] = "suppressed"
    new_df.loc[new_df["value"]==".","status"] = "not_collected"
    new_df["percentage"] = pd.to_numeric(
        new_df["value"].astype(str).str.rstrip("%"), errors = "coerce"
    )
    return new_df

def load_dates(path: Path) -> pd.DataFrame:
    dates  = pd.read_excel(path, sheet_name = "Collection and Reference Dates")
    dates = drop_footnotes(dates,"Smpdt")
    dates["cycle"] = dates["Smpdt"].astype(int).astype(str)
    dates = dates[["cycle","Reference Period Start","Ref End"]]
    return dates.rename(columns = 
                        {"Reference Period Start": "period_start",
                         "Ref End":"period_end"
                         })

def adding_dates(new_df: pd.DataFrame, dates: pd.DataFrame) -> pd.DataFrame:
    merged_data = new_df.merge(dates, on='cycle',how='left',validate='many_to_one')
    missing = merged_data["period_start"].isna().sum()
    assert missing == 0, f'{missing} : rows have no data: check the cycle types'
    return merged_data

def run(level:str) -> pd.DataFrame:
    path = find_file(level)
    raw = pd.read_excel(path,sheet_name = "Response Estimates")
    df = drop_footnotes(raw,"Question ID")
    long = clean_values(to_long(df))
    return adding_dates(long, load_dates(path))

def main() -> None:
    PROCESSED_DIR.mkdir(parents = True, exist_ok = True)
    for level in["National","Sector"]:
        result = run(level)
        out = PROCESSED_DIR / f"{level.lower()}_long.csv"
        result.to_csv(out, index=False)
        print(f"{level}: {len(result):,} rows -> {out}")

if __name__ == "__main__":
    main()


