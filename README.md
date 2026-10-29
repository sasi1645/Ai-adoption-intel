# AI Adoption Intelligence

A data pipeline that collects data from the U.S. Census Bureau's Business Trends and Outlook Survey (BTOS) and stores it in PostgreSQL for analysing AI use among U.S. businesses, nationally and by industry sector.

## Why it matters

Tracking AI adoption helps business leaders, policymakers and researchers understand how fast U.S. businesses are moving from traditional ways of working to AI-supported ones, and which industries are leading or falling behind.

## Key finding

AI use among U.S. businesses rose from **17.3%** (period starting November 3, 2025) to **23.8%** (period starting September 7, 2026): an increase of **6.5 percentage points**, or a **37.6% rise**, in under a year.

*Share of businesses answering "Yes" to: "In the last two weeks, did this business use Artificial Intelligence (AI) in any of its business functions?"*

## Data pipeline

```
Census Excel files ──► ingest.py ──► clean CSV files ──► load.py ──► PostgreSQL
   (data/raw)                         (data/processed)               (national, sector)
```

1. **Find** the latest raw Census Excel file for each level (national, sector), even if Census changes the file name.
2. **Remove** footnote and blank rows that Census adds at the bottom of each sheet.
3. **Reshape** the data from wide (one column per survey cycle) to long (one row per answer per cycle).
4. **Label** every value with a status: `ok`, `suppressed` (hidden by Census for quality or confidentiality) or `not_collected` (question not asked in that cycle).
5. **Convert** percentages from text (`"23.8%"`) to numbers (`23.8`).
6. **Add** the real start and end dates of each survey period from the "Collection and Reference Dates" sheet, with a check that every row receives a date.
7. **Save** the cleaned data as CSV files in `data/processed/`.
8. **Load** both tables into PostgreSQL. The loader empties each table before inserting, so it is safe to re-run and never creates duplicates.

**Testing:** `pytest` checks the cleaning logic, including that suppressed and missing values are labelled correctly and that footnote rows are removed.

## Tech stack

| Area | Tools |
|---|---|
| Language and environment | Python 3.12, uv |
| Data processing | pandas, openpyxl |
| Database | PostgreSQL 18, SQLAlchemy, psycopg |
| Configuration | python-dotenv (database credentials kept out of the code) |
| Testing | pytest |
| Exploration | Jupyter |

## How to run it

**Requirements:** Python 3.12+, [uv](https://docs.astral.sh/uv/) and PostgreSQL.

1. **Clone the project and install dependencies**
   ```bash
   git clone https://github.com/sasi1645/Ai-adoption-intel.git
   cd Ai-adoption-intel
   uv sync
   ```

2. **Download the data.** From the [Census BTOS data page](https://www.census.gov/hfp/btos/data), download the **National** and **Sector** Excel files into `data/raw/`.

3. **Create the database and tables**
   ```sql
   CREATE DATABASE ai_adoption_intel;
   \c ai_adoption_intel
   \i sql/create_tables.sql
   ```

4. **Add your database connection.** Create a `.env` file in the project root (it is ignored by git):
   ```
   DATABASE_URL=postgresql+psycopg://USER:PASSWORD@localhost:5432/ai_adoption_intel
   ```

5. **Run the pipeline**
   ```bash
   uv run python -m ai_adoption_intel.ingest   # clean the raw files
   uv run python -m ai_adoption_intel.load     # load them into PostgreSQL
   ```

6. **Run the tests**
   ```bash
   uv run pytest
   ```

## Project structure

```
Ai-adoption-intel/
├── data/                  # not in git
│   ├── raw/               # Census Excel downloads
│   └── processed/         # cleaned CSV files
├── notebooks/
│   └── 01_explore.ipynb   # first exploration of the raw data
├── sql/
│   ├── create_tables.sql  # table definitions
│   └── queries.sql        # analysis queries
├── src/ai_adoption_intel/
│   ├── ingest.py          # find, clean, reshape and date the data
│   └── load.py            # load the cleaned data into PostgreSQL
├── tests/
│   └── test_ingest.py     # pytest tests for the cleaning logic
└── pyproject.toml         # project and dependencies (uv)
```

## Data notes

- **Source:** U.S. Census Bureau, Business Trends and Outlook Survey (BTOS), collected every two weeks.
- **AI questions:** Question 7 (AI use in the last two weeks) and Question 24 (expected AI use in the next six months).
- **Sector codes** follow two-digit NAICS sectors. The code `XX` refers to multi-unit companies that operate in multiple sectors or multiple states.
- **Gap in the data:** no data was collected for the cycles covering October 6 to November 16, 2025, due to the federal funding lapse.

## API
A REST API, built with **FastAPI**, that serves the cleaned AI-adoption data from PostgreSQL as JSON.
- **Run it:** (from the project root, with PostgreSQL running)

uv run fastapi dev src/ai_adoption_intel/api.py
- **Interactive Docs:** http://127.0.0.1:8000/docs

| End Point | Parameters | Returns |
|---|---|---|
| `Get(/health)` | - |`{"status":"ok"}` |
| `Get(/national/ai-adoption)` | - | Share of U.S. businesses using AI, one record per survey period: `[{"period_start",percentage},...]` |
| `Get(/sectors/ai-adoption)` | `sector` (text,required), e.g. `?sector=44` | same trend one industry sector |
| `Get(/sectors/ranking)` | `limit` (integer,default=5), e.g. `limit=3` | The top sectors AI in use in last period: `[{"sector",percentage},...]` |

**Errors:** `404` if a sector has no data (e.g. `?sector=99`); `422` if a required parameter is missing or has the wrong type (e.g. `?limit=abc`).

## Next steps

- [x] **Stage 1:** data pipeline, tests and PostgreSQL database
- [ ] **Stage 2:** REST API with FastAPI and Docker
- [ ] **Stage 3:** ask questions in plain English, answered by an LLM that writes SQL
- [ ] **Stage 4:** RAG over Census reports and research, with citations
- [ ] **Stage 5:** an agent that chooses between querying data, searching documents and charting
- [ ] **Stage 6:** evaluation and LLM observability
- [ ] **Stage 7:** deployment with CI/CD and a public demo
- [ ] **Stage 8:** forecasting AI adoption by sector with a machine learning model