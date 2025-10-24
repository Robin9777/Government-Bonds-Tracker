from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
import os
from CallBacks import *

app = Dash(__name__)

debts_ = ["US", "FR", "DE", "IT", "UK"]
maturities_ = ["2Y", "5Y", "10Y", "30Y"]

def get_rate_curve():

    df = pd.DataFrame(index=maturities_, columns=debts_)

    for d in debts_:
        for m in maturities_:
            file_path = os.path.join("GovDatas", f"{d}_{m}.parquet")
            if os.path.exists(file_path):
                eod = pd.read_parquet(file_path)
                if not eod.empty:
                    df.loc[m, d] = eod["close"].iloc[-1]
                else:
                    df.loc[m, d] = None
            else:
                df.loc[m, d] = None

    df = df.astype(float)

    df_long = df.reset_index().melt(id_vars="index", var_name="Country", value_name="Rate")
    df_long.rename(columns={"index": "Maturity"}, inplace=True)

    # Crée le graphique
    fig = px.line(df_long, x="Maturity", y="Rate", color="Country",
                  markers=True,
                  title="Government Bond Rate Curves (Last Close)")

    return fig


rate_curve = get_rate_curve()

# --- Layout ---
app.layout = html.Div(children=[
    html.H1(children="Gov Tracker"),

    dcc.Tabs(children=[

        dcc.Tab(label="Outright", children=[
            html.Label("Select Country:"),
            dcc.Dropdown(
                options=debts_, 
                value="US", 
                id="debt-dropdown"
            ),
            html.Label("Select Maturity:"),
            dcc.Dropdown(
                options=maturities_, 
                value="10Y", 
                id="maturity-dropdown"
            ),

            # Outright + RateCurve
            html.Div([
                html.Div([
                    html.Div([
                        dcc.Graph(id="gov-graph", style={"width": "70%", "height": "500px"}),
                        html.Div(id="outright-metrics", className="metrics-panel")
                    ], style={
                        "display": "flex",
                        "justify-content": "space-between",
                        "align-items": "flex-start"
                    })
                ], style={"width": "50%"}),

                html.Div([
                    dcc.Graph(id="rate-curves", figure=rate_curve, style={"width": "100%", "height": "500px"})
                ], style={"width": "50%"})
            ], style={"display": "flex", "justify-content": "space-between"}),
            
            # Curve Spread + Fly
            html.Div([
                html.Div([
                    html.H3("Curve Spread"),
                    html.Label("Select Maturities:"),
                    dcc.Dropdown(options=maturities_, value="2Y", id="curve-spread-maturity1-dropdown"),
                    dcc.Dropdown(options=maturities_, value="10Y", id="curve-spread-maturity2-dropdown"),
                    html.Div([
                        dcc.Graph(id="curve-spread-graph", style={"width": "70%", "height": "400px"}),
                        html.Div(id="curve-metrics", className="metrics-panel")
                    ], style={"display": "flex", "justify-content": "space-between"})
                ], style={"width": "50%"}),

                html.Div([
                    html.H3("Butterfly (Fly) Spread"),
                    html.Label("Select Maturities:"),
                    dcc.Dropdown(options=maturities_, value="2Y", id="fly-maturity1-dropdown"),
                    dcc.Dropdown(options=maturities_, value="5Y", id="fly-maturity2-dropdown"),
                    dcc.Dropdown(options=maturities_, value="10Y", id="fly-maturity3-dropdown"),
                    html.Div([
                        dcc.Graph(id="fly-graph", style={"width": "70%", "height": "400px"}),
                        html.Div(id="fly-metrics", className="metrics-panel")
                    ], style={"display": "flex", "justify-content": "space-between"})
                ], style={"width": "50%"})
            ], style={"display": "flex", "justify-content": "space-between"})
        ]),

        dcc.Tab(label="Credit Spread", children=[
            html.Label("Select Country:"),
            dcc.Dropdown(
                options=debts_, 
                value="US", 
                id="credit1-dropdown"
            ),
            dcc.Dropdown(
                options=debts_, 
                value="DE", 
                id="credit2-dropdown"
            ),
            html.Label("Select Maturity:"),
            dcc.Dropdown(
                options=maturities_, 
                value="10Y", 
                id="maturity2-dropdown"
            ),
            html.Div([
                html.Div([
                    dcc.Graph(id="credit-graph", style={"width": "70%", "height": "500px"}),
                    html.Div(id="credit-metrics", className="metrics-panel")
                ], style={
                    "display": "flex",
                    "justify-content": "space-between",
                    "align-items": "flex-start"
                })
            ])
        ])
    ])
])



# %%%%%%%%%%        Launch        %%%%%%%%%%%%
if __name__ == "__main__":
    app.run(debug=True)
