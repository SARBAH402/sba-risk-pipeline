import os
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from sqlalchemy import create_engine

print("--- PHASE 3: THE CLOUD MERGE (SANDBOX PIPELINE) ---")

# 1. Secure Authentication
load_dotenv()
db_uri = os.getenv("SUPABASE_DB_URI")
engine = create_engine(db_uri)

# 2. Extract (Sandbox to RAM)
print("Querying sandbox datasets from Supabase into active memory...")
sba_df = pd.read_sql("SELECT * FROM raw_sba_sandbox", engine)
macro_df = pd.read_sql("SELECT * FROM raw_macro_sandbox", engine)

# --- THE BULLETPROOF SCHEMA STANDARDIZATION ---
print("Standardizing schema case-sensitivity...")
# Force all macro columns to lowercase to prevent PostgreSQL capitalization conflicts
macro_df.columns = macro_df.columns.str.lower()
# Failsafe: If the FRED raw tag 'cpiaucsl' bypassed the rename, catch it here
if 'cpiaucsl' in macro_df.columns:
    macro_df = macro_df.rename(columns={'cpiaucsl': 'cpi'})
# Failsafe: If columns are completely stripped, force the 2-column FRED standard
if 'date' not in macro_df.columns:
    macro_df.columns = ['date', 'cpi']
# ----------------------------------------------

# 3. Transform: Data Cleaning & Feature Engineering
print("Executing In-Memory Feature Engineering...")

# Define the Target Variable
sba_df = sba_df.dropna(subset=['MIS_Status'])
sba_df['is_default'] = np.where(sba_df['MIS_Status'] == 'CHGOFF', 1, 0)

# Clean Currency Columns (Removing $ and commas)
sba_df['GrAppv'] = sba_df['GrAppv'].astype(str).str.replace(r'[$,]', '', regex=True).astype(float)

# Align Timelines for the Macro Merge
print("Aligning timelines and joining Macroeconomic data...")
sba_df['ApprovalDate'] = pd.to_datetime(sba_df['ApprovalDate'], format='mixed', errors='coerce')
sba_df['approval_month_year'] = sba_df['ApprovalDate'].dt.to_period('M')

macro_df['date'] = pd.to_datetime(macro_df['date'], errors='coerce')
macro_df['macro_month_year'] = macro_df['date'].dt.to_period('M')

# The Cloud Merge
merged_df = pd.merge(sba_df, macro_df, left_on='approval_month_year', right_on='macro_month_year', how='left')

# Feature Selection & Categorical Encoding
print("One-Hot Encoding critical geographical variables...")
features = ['BankState', 'Term', 'GrAppv', 'cpi', 'is_default']
final_df = merged_df[features].dropna().copy()
final_df = final_df.rename(columns={'Term': 'term_month'})

# Encode BankState into distinct columns
final_df = pd.get_dummies(final_df, columns=['BankState'], prefix='bank_state', dtype=int)

print(f"Final Matrix Engineered: {final_df.shape[0]:,} loans ready for Machine Learning.")

# 4. Load (RAM to Cloud)
print("Pushing ML-ready matrix to Supabase table 'ml_ready_sandbox'...")
final_df.to_sql('ml_ready_sandbox', engine, if_exists='replace', index=False, chunksize=5000)

print("\nSUCCESS: Phase 3 Sandbox ETL Complete.")
print("The 'ml_ready_sandbox' is now live in your Supabase database.")