from dash import callback, Output, Input, html # type: ignore
import os
import pandas as pd  # type: ignore
import plotly.express as px  # type: ignore
from datetime import datetime, timedelta


@callback(
    Output("gov-graph", "figure"),
    Output("outright-metrics", "children"),
    Input("debt-dropdown", "value"),
    Input("maturity-dropdown", "value")
)
def outright_graph(country, maturity):
    file_path = os.path.join("GovDatas", f"{country}_{maturity}.parquet")
    
    if os.path.exists(file_path):
        df = pd.read_parquet(file_path)

        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
        fig = px.line(df, x="date", y="close", 
                      title=f"{country} {maturity} Government Bond")
        
        last = df["close"].iloc[-1]
        mean = df["close"].mean()
        vol = df["close"].std()
        z_score = (last - mean) / vol

        metrics = {
            "Last": f"{last:.2f} bps",
            "Mean": f"{mean:.2f} bps",
            "Vol": f"{vol:.2f} bps",
            "z-score": f"{z_score:.2f}"
        }

        metrics_cards = [
            html.Div([
                html.H5(name, style={"margin": "0"}),
                html.P(value, style={
                    "color": "green" if z_score > 0 or name == "Last" else "red",
                    "margin": "0"
                })
            ], className="metric-card") for name, value in metrics.items()
        ]

    else:
        fig = px.line(title=f"No data for {country} {maturity}")
        metrics_cards = [html.Div("No data available", className="metric-card")]

    metrics_container = html.Div(metrics_cards, style={
        "display": "flex",
        "flexDirection": "column",
        "gap": "4px",
        "paddingLeft": "10px"
    })

    return fig, metrics_container


@callback(
    Output("credit-graph", "figure"),
    Output("credit-metrics", "children"),
    Input("credit1-dropdown", "value"),
    Input("credit2-dropdown", "value"),
    Input("maturity2-dropdown", "value")
)
def credit_spread_graph(country1, country2, maturity):

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
        
        last = df["spread"].iloc[-1]
        mean = df["spread"].mean()
        vol = df["spread"].std()
        z_score = (last-mean)/vol

        metrics = {
            "Last" : f"{last:.2f} bps",
            "Mean" : f"{mean:.2f} bps",
            "Vol" : f"{vol:.2f} bps",
            "z-score" : f"{z_score:.2f} bps"
        }
        metrics_cards = [
            html.Div([
                html.H4(name),
                html.H2(value, style={"color": "green" if ("+" in value or name == "Last") else "red"})
            ], className="metric-card") for name, value in metrics.items()
        ]

    else:

        fig = px.line(title=f"No data for {country1} or {country2} ({maturity})")
        metrics_cards = [html.Div("No data available", className="metric-card")]

    return fig, metrics_cards


@callback(
    Output("curve-spread-graph", "figure"),
    Output("curve-metrics", "children"),  # 🔹 on ajoute un deuxième Output
    Input("debt-dropdown", "value"),
    Input("curve-spread-maturity1-dropdown", "value"),
    Input("curve-spread-maturity2-dropdown", "value")
)
def curve_spread_graph(debt: str, mat1: str, mat2: str):

    file_path_1 = os.path.join("GovDatas", f"{debt}_{mat1}.parquet")
    file_path_2 = os.path.join("GovDatas", f"{debt}_{mat2}.parquet")

    if os.path.exists(file_path_1) and os.path.exists(file_path_2):
        df1 = pd.read_parquet(file_path_1)
        df2 = pd.read_parquet(file_path_2)

        if "date" in df1.columns and "date" in df2.columns:
            df1["date"] = pd.to_datetime(df1["date"])
            df2["date"] = pd.to_datetime(df2["date"])

        df = pd.merge(df1[["date", "close"]], df2[["date", "close"]],
                      on="date", suffixes=(f"_{mat2}", f"_{mat1}"))

        df["spread"] = df[f"close_{mat1}"] - df[f"close_{mat2}"]

        fig = px.line(df, x="date", y="spread",
                      title=f"Curve Spread: {mat1} - {mat2} ({debt})",
                      labels={"spread": "Yield Spread (bps)"})
        
        last = df["spread"].iloc[-1]
        mean = df["spread"].mean()
        vol = df["spread"].std()
        z_score = (last - mean) / vol

        metrics = {
            "Last": f"{last:.2f} bps",
            "Mean": f"{mean:.2f} bps",
            "Vol": f"{vol:.2f} bps",
            "z-score": f"{z_score:.2f}"
        }

        metrics_cards = [
            html.Div([
                html.H5(name, style={"margin": "0"}),
                html.P(value, style={
                    "color": "green" if z_score > 0 else "red",
                    "margin": "0"
                })
            ], className="metric-card") for name, value in metrics.items()
        ]

    else:
        fig = px.line(title=f"No data for {mat1} or {mat2} ({debt})")
        metrics_cards = [html.Div("No data available", className="metric-card")]

    return fig, html.Div(metrics_cards, style={
        "display": "flex",
        "flexDirection": "column",
        "gap": "4px",
        "paddingLeft": "20px"
    })



@callback(
    Output("fly-graph", "figure"),
    Output("fly-metrics", "children"),
    Input("debt-dropdown", "value"),
    Input("fly-maturity1-dropdown", "value"),
    Input("fly-maturity2-dropdown", "value"),
    Input("fly-maturity3-dropdown", "value")
)
def fly_graph(debt: str, mat1: str, mat2: str, mat3: str):

    file1 = os.path.join("GovDatas", f"{debt}_{mat1}.parquet")
    file2 = os.path.join("GovDatas", f"{debt}_{mat2}.parquet")
    file3 = os.path.join("GovDatas", f"{debt}_{mat3}.parquet")

    if all(os.path.exists(f) for f in [file1, file2, file3]):
        df1 = pd.read_parquet(file1)
        df2 = pd.read_parquet(file2)
        df3 = pd.read_parquet(file3)

        for df in [df1, df2, df3]:
            df["date"] = pd.to_datetime(df["date"])

        df = (
            df1[["date", "close"]].rename(columns={"close": f"close_{mat1}"})
            .merge(df2[["date", "close"]].rename(columns={"close": f"close_{mat2}"}), on="date")
            .merge(df3[["date", "close"]].rename(columns={"close": f"close_{mat3}"}), on="date")
        )

        df["fly"] = 2 * df[f"close_{mat2}"] - df[f"close_{mat1}"] - df[f"close_{mat3}"]

        fig = px.line(df, x="date", y="fly",
                      title=f"{debt} Fly ({mat1}, {mat2}, {mat3})",
                      labels={"fly": "Butterfly Spread (bps)"})
        fig.add_hline(y=0, line_dash="dash", line_color="gray")

        last = df["fly"].iloc[-1]
        mean = df["fly"].mean()
        vol = df["fly"].std()
        z_score = (last - mean) / vol

        metrics = {
            "Last": f"{last:.2f} bps",
            "Mean": f"{mean:.2f} bps",
            "Vol": f"{vol:.2f} bps",
            "z-score": f"{z_score:.2f}"
        }

        metrics_cards = [
            html.Div([
                html.H5(name, style={"margin": "0"}),
                html.P(value, style={
                    "color": "green" if z_score > 0 else "red",
                    "margin": "0"
                })
            ], className="metric-card") for name, value in metrics.items()
        ]

    else:
        fig = px.line(title=f"No data for {debt} ({mat1}, {mat2}, {mat3})")
        metrics_cards = [html.Div("No data available", className="metric-card")]

    return fig, html.Div(metrics_cards, style={
        "display": "flex",
        "flexDirection": "column",
        "gap": "4px",
        "paddingLeft": "20px"
    })


debts_ = ["US", "FR", "DE", "IT", "UK", "ES"]
maturities_ = ["2Y", "5Y", "10Y", "30Y"]

# %%%%%%%%%%    Rate Curve Variation Callback   %%%%%%%%%%
@callback(
    Output("rate-curve-variations", "figure"),
    Input("start-date-picker", "start_date"),
    Input("start-date-picker", "end_date")
)
def rate_curve_var_graph(start_date: datetime, end_date: datetime):

    df = pd.DataFrame(index=maturities_, columns=debts_)

    for d in debts_:
        for m in maturities_:
            file_path = os.path.join("GovDatas", f"{d}_{m}.parquet")
            if os.path.exists(file_path):
                eod = pd.read_parquet(file_path)
                eod.index = pd.to_datetime(eod["date"])
                if not eod.empty:
                    start_val = eod['close'].asof(pd.to_datetime(start_date))
                    end_val   = eod['close'].asof(pd.to_datetime(end_date))
                    df.loc[m, d] = start_val - end_val
                else:
                    df.loc[m, d] = None
            else:
                df.loc[m, d] = None

    df = df.astype(float)

    df_long = df.reset_index().melt(id_vars="index", var_name="Country", value_name="Rate")
    df_long.rename(columns={"index": "Maturity"}, inplace=True)

    fig = px.line(df_long, x="Maturity", y="Rate", color="Country",
                  markers=True,
                  title="Government Bond Rate Curves (Last Close)")
    
    return fig