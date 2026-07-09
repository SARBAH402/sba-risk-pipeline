from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd

app = Dash(__name__)
server = app.server

data = pd.DataFrame({
    "State": ["CA", "TX", "NY", "FL", "IL"],
    "Default_Rate": [15.2, 12.8, 14.1, 16.5, 11.9]

})

fig = px.bar(data, x = "State", y = "Default_Rate", title = "SBA Default Rates by State (%)")

app.layout = html.Div(children=[
    html.H1(children="SBA Liquidity Risk UI"),
    html.Div(children="Interactive Risk Assessment Engine."),

    dcc.Graph(
        id = "risk-graph",
        figure = fig
    )
])

if __name__ == '__main__':
    app.run(debug=True)