import os
from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd
from dotenv import load_dotenv

# 1. Security Protocol: Unlock the local safe
load_dotenv()
DB_URL = os.getenv("SUPABASE_URL")

# Initialize the Dash engine and the Cloud Hook
app = Dash(__name__)
server = app.server

# 2. The Data Ingestion (Testing the Secure Connection)
# Instead of mock data, we are securely calling the vault.
try:
    # We will just read one table or 5 rows to ensure the connection works without crashing your memory.
    # Replace 'your_table_name' with the actual name of your SBA table in Neon.
    query = 'SELECT * FROM powerbi_historical_view;'
    data = pd.read_sql(query, DB_URL)
    connection_status = "Secure Database Connection: SUCCESS ✅"
except Exception as e:
    data = pd.DataFrame({"State": ["ERROR"], "Default_Rate": [0]})
    connection_status = f"Database Connection FAILED ❌: {e}"

# 3. The Analytical Engine (Plotly)
if not data.empty and "State" in data.columns:
    fig = px.bar(data, x="State", y="Default_Rate", title="SBA Default Rates (Live Data)")
else:
    fig = px.bar(title="Awaiting Live Data")

# 4. The Frontend Layout (Enterprise Off-White Theme)
app.layout = html.Div(
    style={'backgroundColor': '#F8F9FA', 'minHeight': '100vh', 'padding': '20px', 'fontFamily': 'Arial, sans-serif'},
    children=[
        html.H1(children='SBA Liquidity Risk UI', style={'color': '#2C3E50'}),
        html.Div(children=connection_status, style={'fontWeight': 'bold', 'color': '#E74C3C', 'marginBottom': '20px'}),
        
        dcc.Graph(
            id='risk-graph',
            figure=fig
        )
    ]
)

# Run the local server
if __name__ == '__main__':
    app.run(debug=True)