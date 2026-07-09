import os
from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd
from dotenv import load_dotenv

# 1. The Proven Vault Extraction
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(BASE_DIR, '.env')

load_dotenv(dotenv_path=env_path, override=True)
DB_URL = os.getenv("DATABASE_URL")

if not DB_URL:
    raise ValueError("SECURITY LOCK: Engine cannot see the password in .env. Halting execution.")

# Initialize the Dash engine
app = Dash(__name__)
server = app.server

# 2. The Data Ingestion
try:
    query = 'SELECT * FROM powerbi_historical_view;' # <-- Keep your actual view name here
    data = pd.read_sql(query, DB_URL)
    connection_status = "Live Cloud Connection: SUCCESS ✅"
except Exception as e:
    data = pd.DataFrame() # Empty dataframe on failure
    connection_status = f"Database Connection FAILED ❌: {e}"

# 3. The Analytical Engine (Using your exact columns)
if not data.empty and "sector_name" in data.columns and "loan_amount" in data.columns:
    # Economics Logic: Group by sector and sum the total loan amounts
    sector_exposure = data.groupby('sector_name', as_index=False)['loan_amount'].sum()
    
    # Sort the values so the largest sectors appear first
    sector_exposure = sector_exposure.sort_values('loan_amount', ascending=False)

    # Build the interactive chart
    fig = px.bar(
        sector_exposure, 
        x="sector_name", 
        y="loan_amount", 
        title="Total SBA Liquidity Exposure by Sector",
        color_discrete_sequence=['#2C3E50'] # Professional Navy Blue
    )
    
    # Clean up the visual axes for the portfolio
    fig.update_layout(xaxis_title="Industry Sector", yaxis_title="Total Loan Amount ($)")
else:
    # Fallback if columns are missing
    fig = px.bar(title="Awaiting Column Mapping: 'sector_name' or 'loan_amount' not found")

# 4. The Frontend Layout (Enterprise Off-White Theme)
app.layout = html.Div(
    style={'backgroundColor': '#F8F9FA', 'minHeight': '100vh', 'padding': '20px', 'fontFamily': 'Arial, sans-serif'},
    children=[
        html.H1(children='SBA Liquidity Risk UI', style={'color': '#2C3E50'}),
        html.Div(children=connection_status, style={'fontWeight': 'bold', 'color': '#27AE60', 'marginBottom': '20px'}),
        dcc.Graph(id='risk-graph', figure=fig)
    ]
)

if __name__ == '__main__':
    app.run(debug=True)