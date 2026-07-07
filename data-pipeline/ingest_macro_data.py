import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

print("--- PHASE 2: MACRO DATA STREAM (SANDBOX SYNC) ---")

# 1. Secure Authentication
load_dotenv()
db_uri = os.getenv("SUPABASE_DB_URI")
engine = create_engine(db_uri)

# 2. FRED API Stream
fred_cpi_url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=CPIAUCSL"

print("Streaming full CPI timeline directly from FRED...")
macro_df = pd.read_csv(fred_cpi_url)

# 3. Standardization
macro_df = macro_df.rename(columns={'DATE': 'date', 'CPIAUCSL': 'cpi'})

# 4. The Cloud Push
print("Pushing macro data to Supabase table 'raw_macro_sandbox'...")
macro_df.to_sql('raw_macro_sandbox', engine, if_exists='replace', index=False)

print("\nSUCCESS: Phase 2 Sandbox Sync Complete.")