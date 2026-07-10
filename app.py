import os
from dash import Dash, html, dcc, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from dotenv import load_dotenv
import joblib
import warnings

warnings.filterwarnings('ignore')

# 1. The Proven Vault Extraction
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(BASE_DIR, '.env')
load_dotenv(dotenv_path=env_path, override=True)
DB_URL = os.getenv("DATABASE_URL")

# 2. Load the Predictive Engine
try:
    model_path = os.path.join(BASE_DIR, 'production_xgboost_engine.pkl')
    xgb_model = joblib.load(model_path)
    ml_status = "Inference Engine: ONLINE"
except Exception as e:
    xgb_model = None
    ml_status = f"Inference Engine: OFFLINE ({e})"

EXPECTED_COLS = ['term_month', 'GrAppv', 'cpi', 'bank_state_AK', 'bank_state_AL', 'bank_state_AR', 'bank_state_AZ', 'bank_state_CA', 'bank_state_CO', 'bank_state_CT', 'bank_state_DC', 'bank_state_DE', 'bank_state_FL', 'bank_state_GA', 'bank_state_HI', 'bank_state_IA', 'bank_state_ID', 'bank_state_IL', 'bank_state_IN', 'bank_state_KS', 'bank_state_KY', 'bank_state_LA', 'bank_state_MA', 'bank_state_MD', 'bank_state_ME', 'bank_state_MI', 'bank_state_MN', 'bank_state_MO', 'bank_state_MS', 'bank_state_MT', 'bank_state_NC', 'bank_state_ND', 'bank_state_NE', 'bank_state_NH', 'bank_state_NJ', 'bank_state_NM', 'bank_state_NV', 'bank_state_NY', 'bank_state_OH', 'bank_state_OK', 'bank_state_OR', 'bank_state_PA', 'bank_state_PR', 'bank_state_RI', 'bank_state_SC', 'bank_state_SD', 'bank_state_TN', 'bank_state_TX', 'bank_state_UT', 'bank_state_VA', 'bank_state_VT', 'bank_state_WA', 'bank_state_WI', 'bank_state_WV', 'bank_state_WY']
state_codes = [col.split('_')[-1] for col in EXPECTED_COLS if 'bank_state_' in col]

# Initialize Dash
app = Dash(__name__)
server = app.server

# 3. Data Ingestion
try:
    query = 'SELECT * FROM powerbi_historical_view;' 
    data = pd.read_sql(query, DB_URL)
    connection_status = "Cloud Sync: VERIFIED"
except Exception as e:
    data = pd.DataFrame() 
    connection_status = "Cloud Sync: FAILED"

# 4. Historical Engine
if not data.empty:
    total_exposure = data['loan_amount'].sum()
    capital_loss = data.loc[data['is_default'] == 1, 'loan_amount'].sum()
    default_rate = (data['is_default'].mean()) * 100
    avg_term = data['term_months'].mean()

    exposure_str = f"${total_exposure / 1e9:.2f}bn" if total_exposure > 1e9 else f"${total_exposure / 1e6:.2f}M"
    loss_str = f"${capital_loss / 1e6:.2f}M"
    rate_str = f"{default_rate:.2f}%"
    term_str = f"{avg_term:.2f}"

    # Chart 1: Bar
    sector_df = data.groupby('sector_name', as_index=False)['is_default'].mean().nlargest(10, 'is_default').sort_values('is_default', ascending=True)
    bar_colors = ['#BDC3C7' if rate < 0.28 else '#1A5276' for rate in sector_df['is_default']]
    fig_bar = px.bar(sector_df, x="is_default", y="sector_name", orientation='h')
    fig_bar.update_traces(marker_color=bar_colors, hovertemplate='<b>%{y}</b><br>Default Rate: %{x:.2%}<extra></extra>')
    fig_bar.update_layout(title={'text': "Top 10 Highest Risk Industries", 'x': 0.5, 'xanchor': 'center'}, height=280, xaxis_tickformat='.0%', paper_bgcolor='white', plot_bgcolor='white', xaxis_title=None, yaxis_title=None, margin=dict(l=10, r=20, t=40, b=10))

    # Chart 2: Map
    state_df = data.groupby('bank_state', as_index=False)['is_default'].mean()
    fig_map = px.choropleth(state_df, locations='bank_state', locationmode="USA-states", color='is_default', scope="usa", color_continuous_scale="Blues")
    fig_map.update_layout(title={'text': "State-Level Risk Distribution", 'x': 0.5, 'xanchor': 'center'}, height=280, coloraxis_showscale=False, paper_bgcolor='white', plot_bgcolor='white', margin=dict(l=10, r=10, t=40, b=10))
    fig_map.update_traces(hovertemplate='<b>%{location}</b><br>Default Rate: %{z:.2%}<extra></extra>')

    # Chart 3: Trend
    data['approval_year'] = pd.to_datetime(data['approval_date']).dt.year
    trend_data = data[(data['approval_year'] >= 1997) & (data['approval_year'] <= 2006)]
    trend_df = trend_data.groupby('approval_year', as_index=False).agg(annual_risk=('is_default', 'mean'), inflation=('inflation_index', 'mean'))

    fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
    fig_trend.add_trace(go.Bar(x=trend_df['approval_year'], y=trend_df['annual_risk'], name="Annual Risk", marker_color='#E5E7E9', hovertemplate='Risk: %{y:.2%}<extra></extra>'), secondary_y=False)
    fig_trend.add_trace(go.Scatter(x=trend_df['approval_year'], y=trend_df['inflation'], name="Inflation Index", mode='lines', line=dict(color='#1A5276', width=3), hovertemplate='Inflation: %{y:.2f}<extra></extra>'), secondary_y=True)
    
    fig_trend.update_layout(title={'text': "Annual Risk vs. Inflation Trends (1997-2006)", 'x': 0.5, 'xanchor': 'center'}, showlegend=False, height=220, paper_bgcolor='white', plot_bgcolor='white', hovermode="x unified", margin=dict(l=20, r=20, t=40, b=10))
    fig_trend.update_xaxes(dtick=1, showgrid=False, range=[1996.5, 2006.5])
    fig_trend.update_yaxes(title_text="", tickformat=".0%", secondary_y=False, showgrid=False)
    fig_trend.update_yaxes(title_text="", secondary_y=True, showgrid=False)

else:
    exposure_str = loss_str = rate_str = term_str = "N/A"
    fig_bar = px.bar(title="Awaiting Data")
    fig_map = px.choropleth(title="Awaiting Data")
    fig_trend = px.line(title="Awaiting Data")

# 5. Frontend Layout
card_style = {'backgroundColor': 'white', 'padding': '10px 15px', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'textAlign': 'center', 'flex': '1'}

app.layout = html.Div(style={'backgroundColor': '#F8F9FA', 'minHeight': '100vh', 'padding': '15px 25px', 'fontFamily': 'Segoe UI, Arial, sans-serif'}, children=[
    
    # Header
    html.Div(style={'textAlign': 'center', 'marginBottom': '15px', 'backgroundColor': 'white', 'padding': '10px', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.05)'}, children=[
        html.H2("LIQUIDITY RISK: PREDICTIVE MODELING", style={'color': '#2C3E50', 'margin': '0', 'fontWeight': 'bold', 'fontSize': '24px'}),
        html.Div(f"{connection_status} | {ml_status}", style={'color': '#7F8C8D', 'fontSize': '12px', 'marginTop': '2px', 'fontWeight': 'bold'})
    ]),

    # --- TIER 1: FORWARD-LOOKING PREDICTIVE WIDGET ---
    html.H4("I. Scenario Simulator (Algorithmic Risk Scoring)", style={'color': '#2C3E50', 'borderBottom': '2px solid #BDC3C7', 'paddingBottom': '2px', 'margin': '0 0 10px 0', 'fontSize': '16px'}),
    
    html.Div(style={'display': 'flex', 'gap': '20px', 'backgroundColor': 'white', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'marginBottom': '20px', 'padding': '15px'}, children=[
        
        # Left Side: Inputs
        html.Div(style={'flex': '4', 'borderRight': '2px solid #F0F2F6', 'paddingRight': '20px'}, children=[
            html.Label("Requested Capital ($):", style={'fontWeight': 'bold', 'color': '#34495E', 'fontSize': '12px'}),
            dcc.Input(id='input-amount', type='number', value=150000, style={'width': '100%', 'padding': '4px', 'marginBottom': '8px'}),
            
            html.Label("Amortization Term (Months):", style={'fontWeight': 'bold', 'color': '#34495E', 'fontSize': '12px'}),
            dcc.Slider(id='input-term', min=12, max=240, step=12, value=84, marks={12: '1Yr', 84: '7Yr', 240: '20Yr'}),
            html.Br(),
            
            html.Label("Macroeconomic CPI:", style={'fontWeight': 'bold', 'color': '#34495E', 'fontSize': '12px'}),
            dcc.Input(id='input-cpi', type='number', value=200.5, step=0.1, style={'width': '100%', 'padding': '4px', 'marginBottom': '8px'}),
            
            html.Label("Geographic Jurisdiction:", style={'fontWeight': 'bold', 'color': '#34495E', 'fontSize': '12px'}),
            dcc.Dropdown(id='input-state', options=[{'label': s, 'value': s} for s in state_codes], value='TX', style={'marginBottom': '10px'}),
            
            html.Button('Calculate Risk Score', id='predict-btn', n_clicks=0, style={'width': '100%', 'padding': '8px', 'backgroundColor': '#2C3E50', 'color': 'white', 'fontWeight': 'bold', 'border': 'none', 'borderRadius': '5px', 'cursor': 'pointer'})
        ]),
        
        # Right Side: Gauge Chart Output
        html.Div(style={'flex': '6'}, children=[
            dcc.Graph(id='prediction-gauge')
        ])
    ]),

    # --- TIER 2: BACKWARD-LOOKING HISTORICAL DASHBOARD ---
    html.H4("II. Historical Portfolio Analytics (Macro View)", style={'color': '#2C3E50', 'borderBottom': '2px solid #BDC3C7', 'paddingBottom': '2px', 'margin': '0 0 10px 0', 'fontSize': '16px'}),
    
    # KPIs Row (Using Flexbox gap for clean gutters)
    html.Div(style={'display': 'flex', 'gap': '20px', 'marginBottom': '20px'}, children=[
        html.Div(style=card_style, children=[html.H2(exposure_str, style={'fontSize': '24px', 'margin': '0', 'color': '#2C3E50'}), html.P("Total Exposure", style={'color': '#7F8C8D', 'margin': '2px 0 0 0', 'fontWeight': 'bold', 'fontSize': '11px'})]),
        html.Div(style=card_style, children=[html.H2(loss_str, style={'fontSize': '24px', 'margin': '0', 'color': '#2C3E50'}), html.P("Total Capital Loss", style={'color': '#7F8C8D', 'margin': '2px 0 0 0', 'fontWeight': 'bold', 'fontSize': '11px'})]),
        html.Div(style=card_style, children=[html.H2(rate_str, style={'fontSize': '24px', 'margin': '0', 'color': '#2C3E50'}), html.P("Historical Default Rate", style={'color': '#7F8C8D', 'margin': '2px 0 0 0', 'fontWeight': 'bold', 'fontSize': '11px'})]),
        html.Div(style=card_style, children=[html.H2(term_str, style={'fontSize': '24px', 'margin': '0', 'color': '#2C3E50'}), html.P("Average Term", style={'color': '#7F8C8D', 'margin': '2px 0 0 0', 'fontWeight': 'bold', 'fontSize': '11px'})])
    ]),

    # --- RESTORED: TWO SEPARATE CARDS WITH A 20PX GUTTER ---
    html.Div(style={'display': 'flex', 'gap': '20px', 'marginBottom': '20px'}, children=[
        html.Div(style={'flex': '1', 'backgroundColor': 'white', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'padding': '10px'}, children=[
            dcc.Graph(figure=fig_bar)
        ]),
        html.Div(style={'flex': '1', 'backgroundColor': 'white', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'padding': '10px'}, children=[
            dcc.Graph(figure=fig_map)
        ])
    ]),

    html.Div(style={'backgroundColor': 'white', 'borderRadius': '8px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'padding': '10px'}, children=[
        dcc.Graph(figure=fig_trend)
    ])
])

# 6. The Translation Layer (Callback)
@app.callback(
    Output('prediction-gauge', 'figure'),
    Input('predict-btn', 'n_clicks'),
    State('input-amount', 'value'),
    State('input-term', 'value'),
    State('input-cpi', 'value'),
    State('input-state', 'value')
)
def update_prediction(n_clicks, amount, term, cpi, state):
    if xgb_model is None:
        return go.Figure().update_layout(title="Inference Engine Offline.", height=240)

    input_df = pd.DataFrame(columns=EXPECTED_COLS)
    input_df.loc[0] = 0 
    input_df['GrAppv'] = amount
    input_df['term_month'] = term
    input_df['cpi'] = cpi

    state_col_name = f"bank_state_{state}"
    if state_col_name in EXPECTED_COLS:
        input_df[state_col_name] = 1

    probability = xgb_model.predict_proba(input_df)[0][1] * 100

    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = probability,
        title = {'text': "Probability of Default (PD)", 'font': {'size': 16}},
        number = {'suffix': "%", 'font': {'size': 32, 'color': '#2C3E50'}},
        gauge = {
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "#2C3E50"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 28], 'color': '#EAFAF1'},
                {'range': [28, 60], 'color': '#FEF9E7'},
                {'range': [60, 100], 'color': '#FDEDEC'}
            ],
            'threshold': {'line': {'color': "#E74C3C", 'width': 4}, 'thickness': 0.75, 'value': 28}
        }
    ))
    fig.update_layout(height=240, paper_bgcolor='white', font={'color': "#2C3E50", 'family': "Arial"}, margin=dict(t=50, b=10, l=20, r=20))
    
    return fig

if __name__ == '__main__':
    app.run(debug=True)