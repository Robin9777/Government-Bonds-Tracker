from dash import callback, Output, Input
import os
import pandas as pd
import plotly.express as px


@callback(
    Output("gov-graph", "figure"),
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
    else:
        fig = px.line(title=f"No data for {country} {maturity}")
    
    return fig


@callback(
    Output("credit-graph", "figure"),
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
    else:
        fig = px.line(title=f"No data for {country1} or {country2} ({maturity})")

    return fig


@callback(
    Output("curve-spread-graph", "figure"),
    Input("debt-dropdown", "value"),
    Input("curve-spread-maturity1-dropdown", "value"),
    Input("curve-spread-maturity2-dropdown", "value")
)
def curve_spread_graph(debt: str, mat1: str, mat2:str):

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
                      title=f"Credit Spread: {mat1} - {mat2} ({debt})",
                      labels={"spread": "Yield Spread (bps)"})
    else:
        fig = px.line(title=f"No data for {mat1} or {mat2} ({debt})")

    return fig

@callback(
    Output("fly-graph", "figure"),
    Input("debt-dropdown", "value"),
    Input("fly-maturity1-dropdown", "value"),
    Input("fly-maturity2-dropdown", "value"),
    Input("fly-maturity3-dropdown", "value")
)
def fly_graph(debt: str, mat1: str, mat2: str, mat3: str):
    """
    Calcule le Butterfly Spread = 2 * mat2 - mat1 - mat3
    """
    file1 = os.path.join("GovDatas", f"{debt}_{mat1}.parquet")
    file2 = os.path.join("GovDatas", f"{debt}_{mat2}.parquet")
    file3 = os.path.join("GovDatas", f"{debt}_{mat3}.parquet")

    if all(os.path.exists(f) for f in [file1, file2, file3]):
        df1 = pd.read_parquet(file1)
        df2 = pd.read_parquet(file2)
        df3 = pd.read_parquet(file3)

        for df in [df1, df2, df3]:
            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"])

        df1 = df1[["date", "close"]].rename(columns={"close": f"close_{mat1}"})
        df2 = df2[["date", "close"]].rename(columns={"close": f"close_{mat2}"})
        df3 = df3[["date", "close"]].rename(columns={"close": f"close_{mat3}"})

        df = df1.merge(df2, on="date").merge(df3, on="date")

        df["fly"] = 2 * df[f"close_{mat2}"] - df[f"close_{mat1}"] - df[f"close_{mat3}"]

        fig = px.line(
            df,
            x="date",
            y="fly",
            title=f"{debt} Fly ({mat1}, {mat2}, {mat3})",
            labels={"fly": "Butterfly Spread (bps)"}
        )

        fig.add_hline(y=0, line_dash="dash", line_color="gray")

    else:
        fig = px.line(title=f"No data for {debt} ({mat1}, {mat2}, {mat3})")

    return fig
