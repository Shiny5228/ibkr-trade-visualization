import pandas as pd
import plotly.graph_objs as go
from dash import Dash, Input, Output, dcc, html


# Helper functions for time filters
def get_weeks(df):
    """
    Get unique weeks from the DataFrame.

    Parameters:
    df (pd.DataFrame): DataFrame containing the data to be filtered.

    Returns:
    list: List of unique weeks in the format "YYYY-WW".
    """
    if df.empty:
        return []
    return sorted(df["tradeDate"].dt.strftime("%Y-W%U").unique())


def get_months(df):
    """
    Get unique months from the DataFrame.

    Parameters:
    df (pd.DataFrame): DataFrame containing the data to be filtered.

    Returns:
    list: List of unique months in the format "YYYY-MM".
    """
    if df.empty:
        return []
    return sorted(df["tradeDate"].dt.to_period("M").astype(str).unique())


def get_quarters(df):
    """
    Get unique quarters from the DataFrame.

    Parameters:
    df (pd.DataFrame): DataFrame containing the data to be filtered.

    Returns:
    list: List of unique quarters in the format "YYYY-Q".
    """
    if df.empty:
        return []
    return sorted(df["tradeDate"].dt.to_period("Q").astype(str).unique())


def create_dashboard(df):
    """
    Create a dashboard using Dash and Plotly.

    Parameters:
    df (pd.DataFrame): DataFrame containing the data to be visualized.

    Returns:
    Dash app: A Dash app instance.
    """
    # Dash App
    app = Dash(__name__, suppress_callback_exceptions=True)

    # Layout with dark mode CSS styles
    app.layout = html.Div(
        style={
            "backgroundColor": "#2f2f2f",
            "color": "white",
            "font-family": "Arial, sans-serif",
            "padding": "20px",
        },
        children=[
            html.H1("Hebelwerk Dashboard", style={"textAlign": "center"}),
            html.Div(
                style={
                    "display": "flex",
                    "flexDirection": "row",
                    "gap": "20px",
                    "marginBottom": "20px",
                },
                children=[
                    html.Div(
                        [
                            html.Label("Select period:"),
                            dcc.Dropdown(
                                id="time-filter",
                                options=[
                                    {"label": "Total", "value": "Total"},
                                    {"label": "All weeks", "value": "All weeks"},
                                    {"label": "All months", "value": "All months"},
                                    {"label": "All quarters", "value": "All quarters"},
                                ],
                                value="Total",
                                clearable=False,
                                style={"width": "400px", "color": "#000"},
                            ),
                        ]
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
                                value=[],
                                multi=True,
                                style={"width": "400px", "color": "#000"},
                            ),
                        ]
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
                                value=[],
                                multi=True,
                                style={"width": "400px", "color": "#000"},
                            ),
                        ]
                    ),
                    html.Div(
                        [
                            html.Label("Option Strategy Filter:"),
                            dcc.Dropdown(
                                id="optionStrategy-filter",
                                options=[],
                                value=[],
                                multi=True,
                                placeholder="Select option strategy",
                                style={"width": "400px", "color": "#000"},
                                disabled=True,
                            ),
                        ],
                        id="optionStrategy-dropdown-wrapper",
                        style={"display": "none", "marginLeft": "20px"},
                    ),
                ],
            ),
            # Wrapper for dynamic time period dropdown
            html.Div(
                id="time-period-dropdown-wrapper",
                style={"display": "none", "marginBottom": 20},
                children=[
                    dcc.Dropdown(
                        id="time-period-dropdown",
                        multi=True,
                        value=[],
                        placeholder="Select period",
                        style={"width": "400px", "color": "#000"},
                    )
                ],
            ),
            dcc.Graph(id="combined-chart"),
            html.Div(
                style={
                    "display": "flex",
                    "flexDirection": "row",
                    "gap": "20px",
                    "marginTop": "20px",
                },
                children=[
                    dcc.Graph(id="win-rate-indicator", style={"width": "50%"}),
                    dcc.Graph(id="pcr-indicator", style={"width": "50%"}),
                ],
            ),
        ],
    )

    # Callback for managing the visibility and options of the time-period-dropdown
    @app.callback(
        [
            Output("time-period-dropdown-wrapper", "style"),
            Output("time-period-dropdown", "options"),
            Output("time-period-dropdown", "value"),
            Output("time-period-dropdown", "placeholder"),
        ],
        [Input("time-filter", "value")],
    )
    def manage_time_period_dropdown(selected_time_filter):
        style = {"display": "none", "marginBottom": 20}
        options = []
        value = []
        placeholder = ""

        if selected_time_filter == "All weeks":
            options = [{"label": w, "value": w} for w in get_weeks(df)]
            placeholder = "Select one or more weeks"
            style = {"display": "block", "marginBottom": 20}
        elif selected_time_filter == "All months":
            options = [{"label": m, "value": m} for m in get_months(df)]
            placeholder = "Select one or more months"
            style = {"display": "block", "marginBottom": 20}
        elif selected_time_filter == "All quarters":
            options = [{"label": q, "value": q} for q in get_quarters(df)]
            placeholder = "Select one or more quarters"
            style = {"display": "block", "marginBottom": 20}  # Show
        return style, options, value, placeholder

    # Callback for visibility and options of the option strategy dropdown
    @app.callback(
        [
            Output("optionStrategy-dropdown-wrapper", "style"),
            Output("optionStrategy-filter", "options"),
            Output("optionStrategy-filter", "disabled"),
            Output("optionStrategy-filter", "value"),
        ],
        [Input("asset-filter", "value")],
        prevent_initial_call=True,
    )
    def update_option_strategy_dropdown(selected_assets):
        # Only show if exclusively OPT and/or FOP are selected
        allowed = {"OPT", "FOP"}
        selected_set = set(selected_assets)
        show = selected_set and selected_set.issubset(allowed)
        # Disable if other asset categories are selected
        disabled = not show or not selected_set
        style = (
            {"display": "block", "marginLeft": "20px"}
            if show
            else {"display": "none", "marginLeft": "20px"}
        )
        # Set options
        if show:
            filtered_df = df[df["assetCategory"].isin(selected_assets)]
            strategies = sorted(filtered_df["optionStrategy"].dropna().unique())
            options = [{"label": s, "value": s} for s in strategies]
        else:
            options = []
        return style, options, disabled, []

    # Callback for dynamically updating the symbol options based on asset filter
    @app.callback(
        [
            Output("symbol-filter", "options"),
            Output("symbol-filter", "value"),
        ],
        [Input("asset-filter", "value")],
        prevent_initial_call=True,
    )
    def update_symbol_options_and_reset(selected_assets):
        if not selected_assets:
            symbols = sorted(df["underlyingSymbol"].unique())
        else:
            symbols = sorted(
                df[df["assetCategory"].isin(selected_assets)][
                    "underlyingSymbol"
                ].unique()
            )
        options = [{"label": i, "value": i} for i in symbols]

        return options, []

    # Callback for updating the combined chart and indicators
    @app.callback(
        [
            Output("combined-chart", "figure"),
            Output("win-rate-indicator", "figure"),
            Output("pcr-indicator", "figure"),
        ],
        [
            Input("time-filter", "value"),
            Input("asset-filter", "value"),
            Input("symbol-filter", "value"),
            Input("time-period-dropdown", "value"),
            Input("optionStrategy-filter", "value"),
        ],
    )
    def update_combined_chart_and_indicators(
        time_filter,
        selected_assets,
        selected_symbols,
        selected_periods,
        selected_strategies,
    ):
        filtered_df = df.copy()

        if selected_assets:
            filtered_df = filtered_df[
                filtered_df["assetCategory"].isin(selected_assets)
            ]
        if selected_symbols:
            filtered_df = filtered_df[
                filtered_df["underlyingSymbol"].isin(selected_symbols)
            ]
        # Filter by Option Strategy, if dropdown is active and selection made
        allowed = {"OPT", "FOP"}
        if set(selected_assets).issubset(allowed) and selected_strategies:
            filtered_df = filtered_df[
                filtered_df["optionStrategy"].isin(selected_strategies)
            ]

        if time_filter == "Total":
            pass
        elif time_filter in ["All weeks", "All months", "All quarters"]:
            if not selected_periods:
                filtered_df = pd.DataFrame(columns=df.columns)
            else:
                if time_filter == "All weeks":
                    filtered_df["week_str"] = filtered_df["tradeDate"].dt.strftime(
                        "%Y-W%U"
                    )
                    filtered_df = filtered_df[
                        filtered_df["week_str"].isin(selected_periods)
                    ]
                elif time_filter == "All months":
                    filtered_df["month_str"] = (
                        filtered_df["tradeDate"].dt.to_period("M").astype(str)
                    )
                    filtered_df = filtered_df[
                        filtered_df["month_str"].isin(selected_periods)
                    ]
                elif time_filter == "All quarters":
                    filtered_df["quarter_str"] = (
                        filtered_df["tradeDate"].dt.to_period("Q").astype(str)
                    )
                    filtered_df = filtered_df[
                        filtered_df["quarter_str"].isin(selected_periods)
                    ]

        # Win rate calculation
        if not filtered_df.empty:
            trade_pnl_sum = filtered_df.groupby("opendateTime")["PnLRealized"].sum()
            wins = (trade_pnl_sum > 0).sum()
            total_trades = len(trade_pnl_sum)
            win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
        else:
            win_rate = 0
            wins = 0
            total_trades = 0

        win_rate_figure = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=win_rate,
                title={"text": "Win Rate (%)"},
                gauge={
                    "axis": {
                        "range": [0, 100],
                        "tickcolor": "white",
                        "tickwidth": 1,
                    },
                    "bordercolor": "white",
                    "borderwidth": 1,
                },
            )
        )
        win_rate_figure.update_layout(
            plot_bgcolor="#3f3f3f",
            paper_bgcolor="#3f3f3f",
            font=dict(color="white"),
        )

        # PCR calculation
        pcr_df = filtered_df[filtered_df["assetCategory"].isin(["FOP", "OPT"])]
        if not pcr_df.empty:
            sum_cost = abs(pcr_df["cost"].sum()).round(2)
            sum_realized = pcr_df["PnLRealized"].sum().round(2)
            pcr = (sum_realized / sum_cost * 100).round(2) if sum_cost != 0 else 0
        else:
            pcr = 0

        pcr_figure = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=pcr,
                title={"text": "PCR (%)"},
                gauge={
                    "axis": {
                        "range": [0, 100],
                        "tickcolor": "white",
                        "tickwidth": 1,
                    },
                    "bordercolor": "white",
                    "borderwidth": 1,
                },
            )
        )
        pcr_figure.update_layout(
            plot_bgcolor="#3f3f3f", paper_bgcolor="#3f3f3f", font=dict(color="white")
        )

        # Chart calculation
        if filtered_df.empty:
            combined_chart = {
                "data": [],
                "layout": go.Layout(
                    title="No data for the selected filters",
                    plot_bgcolor="#3f3f3f",
                    paper_bgcolor="#3f3f3f",
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
        else:
            pnl_per_day = (
                filtered_df.groupby(filtered_df["tradeDate"].dt.date)["PnLRealized"]
                .sum()
                .reset_index()
            )
            pnl_per_day["tradeDate"] = pd.to_datetime(pnl_per_day["tradeDate"])
            pnl_per_day = pnl_per_day.sort_values("tradeDate")
            pnl_per_day["TotalProfit"] = pnl_per_day["PnLRealized"].cumsum()
            pnl_per_day["tradeDateStr"] = pnl_per_day["tradeDate"].dt.strftime(
                "%Y-%m-%d"
            )

            combined_chart = go.Figure()
            combined_chart.add_trace(
                go.Bar(
                    x=pnl_per_day["tradeDateStr"],
                    y=pnl_per_day["PnLRealized"],
                    name="Daily PnL",
                    marker_color=[
                        "red" if x < 0 else "green" for x in pnl_per_day["PnLRealized"]
                    ],
                )
            )
            combined_chart.add_trace(
                go.Scatter(
                    x=pnl_per_day["tradeDateStr"],
                    y=pnl_per_day["TotalProfit"],
                    mode="lines+markers",
                    name="Cumulative Total Profit",
                    line=dict(color="orange", width=2),
                    marker=dict(size=5),
                )
            )
            combined_chart.update_layout(
                title="Daily PnL and Cumulative Total Profit",
                xaxis=dict(
                    title="Date",
                    type="category",
                    showgrid=True,
                    gridcolor="rgba(128,128,128,0.2)",
                    color="white",
                    tickangle=-45,
                ),
                yaxis=dict(
                    title="Amount",
                    showgrid=True,
                    gridcolor="rgba(128,128,128,0.2)",
                    color="white",
                    zerolinecolor="gray",
                    zerolinewidth=1,
                ),
                plot_bgcolor="#3f3f3f",
                paper_bgcolor="#3f3f3f",
                font=dict(color="white"),
                legend=dict(
                    bgcolor="#3f3f3f",
                    bordercolor="gray",
                    font=dict(color="white"),
                ),
                margin=dict(l=60, r=40, t=80, b=100),
            )

        return combined_chart, win_rate_figure, pcr_figure

    return app
