import calendar  # noqa: F401
import json
import os
from datetime import datetime, timedelta  # noqa: F401

import pandas as pd
import plotly.graph_objs as go
from dash import Dash, Input, Output, dcc, html
from dotenv import load_dotenv

from src.api_utils import get_statement, process_statement_data, send_request
from src.transformations import transform

# HINWEIS: Ersetzen Sie diesen Dummy-DataFrame durch Ihren tatsächlichen DataFrame.
# Stellen Sie sicher, dass Ihr DataFrame 'df' heißt und die Spalten
# 'tradeDate' (als datetime), 'PnLRealized', 'assetCategory' und 'underlyingSymbol' enthält.

load_dotenv()
token = os.getenv("TOKEN")
if token is None:
    raise ValueError("Please set the TOKEN environment variable.")
query_id = os.getenv("QUERY_ID")
if query_id is None:
    raise ValueError("Please set the QUERY_ID environment variable.")
flex_version = os.getenv("FLEX_VERSION")
if flex_version is None:
    raise ValueError("Please set the FLEX_VERSION environment variable.")
headers_str = os.getenv("HEADERS")
if headers_str is None:
    raise ValueError("Please set the HEADERS environment variable.")
headers = json.loads(headers_str)
### Get Statement from IB via API
# API Calls
reference_code = send_request(token, query_id, flex_version, headers)
df = get_statement(token, reference_code, flex_version, headers)

# Process Data
df = process_statement_data(df)
df = transform(df)


# Hilfsfunktionen für Zeitfilter
def get_weeks(df_source):
    if df_source.empty:
        return []
    return sorted(df_source["tradeDate"].dt.strftime("%Y-W%U").unique())


def get_months(df_source):
    if df_source.empty:
        return []
    return sorted(df_source["tradeDate"].dt.to_period("M").astype(str).unique())


def get_quarters(df_source):
    if df_source.empty:
        return []
    return sorted(df_source["tradeDate"].dt.to_period("Q").astype(str).unique())


# Dash App
# suppress_callback_exceptions kann weiterhin nützlich sein, ist aber für dieses spezielle Problem
# mit dem neuen Ansatz möglicherweise nicht mehr zwingend erforderlich.
app = Dash(__name__, suppress_callback_exceptions=True)

# Layout mit Darkmode CSS Styles
app.layout = html.Div(
    style={
        "backgroundColor": "#1e1e1e",
        "color": "white",
        "font-family": "Arial, sans-serif",
        "padding": "20px",
    },
    children=[
        html.H1("Trade-Visualisierung", style={"textAlign": "center"}),
        html.Div(
            [
                html.Label("Zeitraumfilter:"),
                dcc.Dropdown(
                    id="time-filter",
                    options=[
                        {"label": "Gesamt", "value": "Total"},
                        {"label": "Alle Wochen", "value": "Alle Wochen"},
                        {"label": "Alle Monate", "value": "Alle Monate"},
                        {"label": "Alle Quartale", "value": "Alle Quartale"},
                    ],
                    value="Total",
                    clearable=False,
                    style={"width": "50%", "color": "#000"},
                ),
            ],
            style={"marginBottom": 20},
        ),
        # Wrapper für den dynamischen Dropdown, initial versteckt
        html.Div(
            id="time-period-dropdown-wrapper",
            style={"display": "none", "marginBottom": 20},
            children=[
                dcc.Dropdown(
                    id="time-period-dropdown",
                    multi=True,
                    value=[],  # Initial leer für multi-select
                    placeholder="Zeitraum auswählen",  # Allgemeiner initialer Platzhalter
                    style={"width": "50%", "color": "#000"},
                )
            ],
        ),
        html.Div(
            [
                html.Label("Asset Category Filter:"),
                dcc.Dropdown(
                    id="asset-filter",
                    options=[
                        {"label": i, "value": i}
                        for i in sorted(df["assetCategory"].unique())
                    ],
                    value=df["assetCategory"].unique().tolist(),
                    multi=True,
                    style={"width": "50%", "color": "#000"},
                ),
            ],
            style={"marginBottom": 20},
        ),
        html.Div(
            [
                html.Label("Underlying Symbol Filter:"),
                dcc.Dropdown(
                    id="symbol-filter",
                    options=[
                        {"label": i, "value": i}
                        for i in sorted(df["underlyingSymbol"].unique())
                    ],
                    value=df["underlyingSymbol"].unique().tolist(),
                    multi=True,
                    style={"width": "50%", "color": "#000"},
                ),
            ],
            style={"marginBottom": 20},
        ),
        dcc.Graph(id="combined-chart"),
    ],
)


# Callback zur Steuerung der Sichtbarkeit und Optionen des time-period-dropdown
@app.callback(
    [
        Output("time-period-dropdown-wrapper", "style"),
        Output("time-period-dropdown", "options"),
        Output(
            "time-period-dropdown", "value"
        ),  # Wert zurücksetzen, wenn Filtertyp ändert
        Output("time-period-dropdown", "placeholder"),
    ],
    [Input("time-filter", "value")],
)
def manage_time_period_dropdown(selected_time_filter):
    style = {"display": "none", "marginBottom": 20}  # Standard: versteckt
    options = []
    value = []  # Für multi-select, immer auf leere Liste zurücksetzen, wenn Hauptfilter ändert
    placeholder = ""

    if selected_time_filter == "Alle Wochen":
        options = [{"label": w, "value": w} for w in get_weeks(df)]
        placeholder = "Wähle eine oder mehrere Wochen"
        style = {"display": "block", "marginBottom": 20}  # Anzeigen
    elif selected_time_filter == "Alle Monate":
        options = [{"label": m, "value": m} for m in get_months(df)]
        placeholder = "Wähle einen oder mehrere Monate"
        style = {"display": "block", "marginBottom": 20}  # Anzeigen
    elif selected_time_filter == "Alle Quartale":
        options = [{"label": q, "value": q} for q in get_quarters(df)]
        placeholder = "Wähle ein oder mehrere Quartale"
        style = {"display": "block", "marginBottom": 20}  # Anzeigen

    return style, options, value, placeholder


# Callback zur Aktualisierung des kombinierten Graphen
@app.callback(
    Output("combined-chart", "figure"),
    [
        Input("time-filter", "value"),
        Input("asset-filter", "value"),
        Input("symbol-filter", "value"),
        Input("time-period-dropdown", "value"),
    ],  # Dieser Input ist jetzt immer gültig
)
def update_combined_chart(
    time_filter, selected_assets, selected_symbols, selected_periods
):
    filtered_df = df.copy()

    if selected_assets:
        filtered_df = filtered_df[filtered_df["assetCategory"].isin(selected_assets)]
    if selected_symbols:
        filtered_df = filtered_df[
            filtered_df["underlyingSymbol"].isin(selected_symbols)
        ]

    if time_filter == "Total":
        pass
    elif time_filter in ["Alle Wochen", "Alle Monate", "Alle Quartale"]:
        # selected_periods ist [] wenn nichts ausgewählt oder Dropdown gerade erst sichtbar wurde/Filtertyp änderte
        if not selected_periods:
            filtered_df = pd.DataFrame(columns=df.columns)
            if "tradeDate" in filtered_df.columns:
                filtered_df["tradeDate"] = pd.to_datetime(filtered_df["tradeDate"])
        else:
            if time_filter == "Alle Wochen":
                filtered_df["week_str"] = filtered_df["tradeDate"].dt.strftime("%Y-W%U")
                filtered_df = filtered_df[
                    filtered_df["week_str"].isin(selected_periods)
                ]
            elif time_filter == "Alle Monate":
                filtered_df["month_str"] = (
                    filtered_df["tradeDate"].dt.to_period("M").astype(str)
                )
                filtered_df = filtered_df[
                    filtered_df["month_str"].isin(selected_periods)
                ]
            elif time_filter == "Alle Quartale":
                filtered_df["quarter_str"] = (
                    filtered_df["tradeDate"].dt.to_period("Q").astype(str)
                )
                filtered_df = filtered_df[
                    filtered_df["quarter_str"].isin(selected_periods)
                ]

    if filtered_df.empty:
        return {
            "data": [],
            "layout": go.Layout(
                title="Keine Daten für die ausgewählten Filter",
                plot_bgcolor="#1e1e1e",
                paper_bgcolor="#1e1e1e",
                font=dict(color="white"),
                xaxis=dict(
                    showgrid=False,
                    zeroline=False,
                    showticklabels=False,
                    type="category",
                ),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            ),
        }

    pnl_per_day = (
        filtered_df.groupby(filtered_df["tradeDate"].dt.date)["PnLRealized"]
        .sum()
        .reset_index()
    )
    pnl_per_day["tradeDate"] = pd.to_datetime(pnl_per_day["tradeDate"])
    pnl_per_day = pnl_per_day.sort_values("tradeDate")
    pnl_per_day["TotalProfit"] = pnl_per_day["PnLRealized"].cumsum()
    pnl_per_day["tradeDateStr"] = pnl_per_day["tradeDate"].dt.strftime("%Y-%m-%d")

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=pnl_per_day["tradeDateStr"],
            y=pnl_per_day["PnLRealized"],
            name="Gewinn/Verlust pro Tag",
            marker_color=[
                "crimson" if x < 0 else "lightseagreen"
                for x in pnl_per_day["PnLRealized"]
            ],
        )
    )
    fig.add_trace(
        go.Scatter(
            x=pnl_per_day["tradeDateStr"],
            y=pnl_per_day["TotalProfit"],
            mode="lines+markers",
            name="Kumulierter TotalProfit",
            line=dict(color="orange", width=2),
            marker=dict(size=5),
        )
    )
    fig.update_layout(
        title="Gewinn/Verlust pro Tag und kumulierter TotalProfit",
        xaxis=dict(
            title="Datum",
            type="category",
            showgrid=True,
            gridcolor="rgba(128,128,128,0.2)",
            color="white",
            tickangle=-45,
        ),
        yaxis=dict(
            title="Betrag",
            showgrid=True,
            gridcolor="rgba(128,128,128,0.2)",
            color="white",
            zerolinecolor="gray",
            zerolinewidth=1,
        ),
        plot_bgcolor="#1e1e1e",
        paper_bgcolor="#1e1e1e",
        font=dict(color="white"),
        legend=dict(
            bgcolor="rgba(30,30,30,0.7)", bordercolor="gray", font=dict(color="white")
        ),
        margin=dict(l=60, r=40, t=80, b=100),
    )
    return fig


if __name__ == "__main__":
    app.run(debug=True)
