import os
import requests
import zipfile
import io
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from requests.auth import HTTPBasicAuth

print("--- PHASE 1: ENTERPRISE CLOUD STRESS TEST (50K SANDBOX) ---")

# 1. Secure Authentication
load_dotenv()
db_uri = os.getenv("SUPABASE_DB_URI")
kaggle_user = os.getenv("KAGGLE_USERNAME")
kaggle_key = os.getenv("KAGGLE_KEY")

engine = create_engine(db_uri)

# 2. Kaggle API Stream
dataset_path = "mirbektoktogaraev/should-this-loan-be-approved-or-denied"
api_url = f"https://www.kaggle.com/api/v1/datasets/download/{dataset_path}"

print("Authenticating with Kaggle and streaming dataset...")
response = requests.get(api_url, auth=HTTPBasicAuth(kaggle_user, kaggle_key))

if response.status_code != 200:
    raise ConnectionError(f"API Request Failed. Status Code: {response.status_code}")

# 3. The 50k Memory Extraction
print("Extracting a 50,000-row stress-test batch in RAM...")
virtual_zip = zipfile.ZipFile(io.BytesIO(response.content))
csv_filename = virtual_zip.namelist()[0]

# Stress Test Parameter applied here
df = pd.read_csv(virtual_zip.open(csv_filename), low_memory=False, nrows=50000)
print(f"Sandbox Data loaded: {df.shape[0]:,} rows.")

# 4. The Cloud Push
print("Pushing 50k batch to Supabase table 'raw_sba_sandbox'...")
print("Executing chunked network transfer...")

df.to_sql('raw_sba_sandbox', engine, if_exists='replace', index=False, chunksize=5000)

print("\nSUCCESS: Phase 1 Stress Test Complete.")