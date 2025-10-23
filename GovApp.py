from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
import os

app = Dash(__name__)

debts_ = ["US", "FR", "DE"]
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
            html.Div([
                dcc.Graph(id="gov-graph", style={"width": "50%"}),
                dcc.Graph(id="rate-curves", figure=rate_curve, style={"width": "50%"})
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
            dcc.Graph(id="credit-graph")
        ])
    ])
])


@callback(
    Output("gov-graph", "figure"),
    Input("debt-dropdown", "value"),
    Input("maturity-dropdown", "value")
)
def update_graph(country, maturity):
    file_path = os.path.join("GovDatas", f"{country}_{maturity}.parquet")
    
    if os.path.exists(file_path):
        df = pd.read_parquet(file_path)

        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
        fig = px.line(df, x="date", y="close", 
                      title=f"{country} {maturity} Government Bond")
    else:
        fig = px.line(title=f"No data for {country} {maturity}")
    
    return fig


@callback(
    Output("credit-graph", "figure"),
    Input("credit1-dropdown", "value"),
    Input("credit2-dropdown", "value"),
    Input("maturity2-dropdown", "value")
)
def update_graph(country1, country2, maturity):

    file_path_1 = os.path.join("GovDatas", f"{country1}_{maturity}.parquet")
    file_path_2 = os.path.join("GovDatas", f"{country2}_{maturity}.parquet")

    if os.path.exists(file_path_1) and os.path.exists(file_path_2):
        df1 = pd.read_parquet(file_path_1)
        df2 = pd.read_parquet(file_path_2)

        if "date" in df1.columns and "date" in df2.columns:
            df1["date"] = pd.to_datetime(df1["date"])
            df2["date"] = pd.to_datetime(df2["date"])

        df = pd.merge(df1[["date", "close"]], df2[["date", "close"]],
                      on="date", suffixes=(f"_{country1}", f"_{country2}"))

        df["spread"] = df[f"close_{country1}"] - df[f"close_{country2}"]

        fig = px.line(df, x="date", y="spread",
                      title=f"Credit Spread: {country1} - {country2} ({maturity})",
                      labels={"spread": "Yield Spread (bps)"})
    else:
        fig = px.line(title=f"No data for {country1} or {country2} ({maturity})")

    return fig

# %%%%%%%%%%        Launch        %%%%%%%%%%%%
if __name__ == "__main__":
    app.run(debug=True)
