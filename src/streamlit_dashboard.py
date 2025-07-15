import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# Helper functions for time filters
def get_weeks(df):
    if df.empty:
        return []
    return sorted(df["tradeDate"].dt.strftime("%Y-W%U").unique())


def get_months(df):
    if df.empty:
        return []
    return sorted(df["tradeDate"].dt.to_period("M").astype(str).unique())


def get_quarters(df):
    if df.empty:
        return []
    return sorted(df["tradeDate"].dt.to_period("Q").astype(str).unique())


def create_indicator_figure(
    value, title, value_format="", prefix="", bgcolor="#2E2E2E", text_color="white"
):
    """Creates a compact indicator figure without border"""
    fig = go.Figure(
        go.Indicator(
            mode="number",
            value=value,
            number={
                "valueformat": value_format,
                "prefix": prefix,
                "font": {"size": 28, "color": text_color},
            },
            title={"text": title, "font": {"size": 14, "color": text_color}},
        )
    )

    # More compact layout without border
    fig.update_layout(
        height=120,
        margin=dict(l=10, r=10, t=30, b=10),
        plot_bgcolor=bgcolor,
        paper_bgcolor=bgcolor,
        font=dict(color=text_color),
    )

    return fig


def run_streamlit_dashboard(df):
    st.set_page_config(page_title="Hebelwerk Dashboard", layout="wide")

    # Custom CSS for better appearance
    st.markdown(
        """
        <style>
        .main > div {
            padding-top: 2rem;
        }
        .stPlotlyChart > div {
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .metric-container {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 8px;
            border: 1px solid #e9ecef;
            margin-bottom: 1rem;
        }
        </style>
    """,
        unsafe_allow_html=True,
    )

    st.title("📊 Hebelwerk Dashboard")

    # Sidebar filters
    st.sidebar.header("🔧 Filter")

    time_filter = st.sidebar.selectbox(
        "Time period:",
        ["Total", "All weeks", "All months", "All quarters"],
        index=0,
    )

    asset_options = sorted(df["assetCategory"].unique())
    selected_assets = st.sidebar.multiselect(
        "Asset Category:", asset_options, default=[]
    )

    symbol_options = (
        sorted(
            df[df["assetCategory"].isin(selected_assets)]["underlyingSymbol"].unique()
        )
        if selected_assets
        else sorted(df["underlyingSymbol"].unique())
    )
    selected_symbols = st.sidebar.multiselect(
        "Underlying Symbol:", symbol_options, default=[]
    )

    # Option Strategy Dropdown
    allowed = {"OPT", "FOP"}
    show_strategy = set(selected_assets).issubset(allowed) and selected_assets
    if show_strategy:
        strategy_options = sorted(
            df[df["assetCategory"].isin(selected_assets)]["optionStrategy"]
            .dropna()
            .unique()
        )
        selected_strategies = st.sidebar.multiselect(
            "Option Strategy:", strategy_options, default=[]
        )
    else:
        selected_strategies = []

    # Time period dropdown
    if time_filter == "All weeks":
        period_options = get_weeks(df)
        selected_periods = st.sidebar.multiselect(
            "Select weeks:", period_options, default=[]
        )
    elif time_filter == "All months":
        period_options = get_months(df)
        selected_periods = st.sidebar.multiselect(
            "Select months:", period_options, default=[]
        )
    elif time_filter == "All quarters":
        period_options = get_quarters(df)
        selected_periods = st.sidebar.multiselect(
            "Select quarters:", period_options, default=[]
        )
    else:
        selected_periods = []

    # Data filtering
    filtered_df = df.copy()
    if selected_assets:
        filtered_df = filtered_df[filtered_df["assetCategory"].isin(selected_assets)]
    if selected_symbols:
        filtered_df = filtered_df[
            filtered_df["underlyingSymbol"].isin(selected_symbols)
        ]
    if show_strategy and selected_strategies:
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
                filtered_df["week_str"] = filtered_df["tradeDate"].dt.strftime("%Y-W%U")
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

    # Calculations
    if not filtered_df.empty:
        trade_pnl_sum = filtered_df.groupby("opendateTime")["PnLRealized"].sum()
        wins = (trade_pnl_sum > 0).sum()
        total_trades = len(trade_pnl_sum)
        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0

        losers = trade_pnl_sum[trade_pnl_sum < 0]
        winners = trade_pnl_sum[trade_pnl_sum > 0]
        avg_loser = losers.mean() if not losers.empty else 0
        avg_winner = winners.mean() if not winners.empty else 0
        max_winner = winners.max() if not winners.empty else 0
        max_loser = losers.min() if not losers.empty else 0
        avg_per_trade = trade_pnl_sum.mean() if not trade_pnl_sum.empty else 0
    else:
        win_rate = wins = total_trades = 0
        avg_loser = avg_winner = max_winner = max_loser = avg_per_trade = 0

    # PCR calculation
    pcr_df = filtered_df[filtered_df["assetCategory"].isin(["FOP", "OPT"])]
    if not pcr_df.empty:
        sum_cost = abs(pcr_df["cost"].sum()).round(2)
        sum_realized = pcr_df["PnLRealized"].sum().round(2)
        pcr = (sum_realized / sum_cost * 100).round(2) if sum_cost != 0 else 0
    else:
        pcr = sum_cost = sum_realized = 0

    # Chart
    if filtered_df.empty:
        st.warning("⚠️ No data available for the selected filters.")
        combined_chart = go.Figure()
    else:
        pnl_per_day = (
            filtered_df.groupby(filtered_df["tradeDate"].dt.date)["PnLRealized"]
            .sum()
            .reset_index()
        )
        pnl_per_day["tradeDate"] = pd.to_datetime(pnl_per_day["tradeDate"])
        pnl_per_day = pnl_per_day.sort_values("tradeDate")
        pnl_per_day["TotalProfit"] = pnl_per_day["PnLRealized"].cumsum()
        pnl_per_day["tradeDateStr"] = pnl_per_day["tradeDate"].dt.strftime("%Y-%m-%d")

        combined_chart = go.Figure()
        combined_chart.add_trace(
            go.Bar(
                x=pnl_per_day["tradeDateStr"],
                y=pnl_per_day["PnLRealized"],
                name="Daily PnL",
                marker_color=[
                    "#DD2C48" if x < 0 else "#00A796"
                    for x in pnl_per_day["PnLRealized"]
                ],
            )
        )
        combined_chart.add_trace(
            go.Scatter(
                x=pnl_per_day["tradeDateStr"],
                y=pnl_per_day["TotalProfit"],
                mode="lines+markers",
                name="Cumulative Total Profit",
                line=dict(color="#B27F1B", width=3),
                marker=dict(size=6),
            )
        )
        combined_chart.update_layout(
            title={
                "text": "📈 Daily PnL and Cumulative Total Profit",
                "font": {"size": 20, "color": "white"},
            },
            xaxis=dict(
                title="Date",
                type="category",
                showgrid=True,
                gridcolor="rgba(128,128,128,0.2)",
                color="white",
                tickangle=-45,
            ),
            yaxis=dict(
                title="Amount ($)",
                showgrid=True,
                gridcolor="rgba(128,128,128,0.2)",
                color="white",
                zerolinecolor="gray",
                zerolinewidth=1,
            ),
            margin=dict(l=60, r=40, t=80, b=100),
            height=500,
            plot_bgcolor="#2E2E2E",
            paper_bgcolor="#2E2E2E",
            font=dict(color="white"),
        )

    # Layout
    st.plotly_chart(combined_chart, use_container_width=True)

    # All metrics summarized
    st.subheader("📊 Trading Metrics")

    # First row: 4 metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        fig = create_indicator_figure(
            sum_cost, "Premium Sold", prefix="$", bgcolor="#2E2E2E"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = create_indicator_figure(
            sum_realized, "Premium Captured", prefix="$", bgcolor="#2E2E2E"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col3:
        fig = create_indicator_figure(
            pcr, "PCR (%)", value_format=".1f", bgcolor="#2E2E2E"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        fig = create_indicator_figure(
            win_rate, "Win Rate (%)", value_format=".1f", bgcolor="#2E2E2E"
        )
        st.plotly_chart(fig, use_container_width=True)

    # Second row: 5 metrics
    col5, col6, col7, col8, col9 = st.columns(5)

    with col5:
        bgcolor = "#00A796" if avg_per_trade >= 0 else "#DD2C48"
        fig = create_indicator_figure(
            avg_per_trade,
            "Avg Per Trade",
            value_format=".2f",
            prefix="$",
            bgcolor=bgcolor,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col6:
        fig = create_indicator_figure(
            avg_winner, "Avg Winner", value_format=".2f", prefix="$", bgcolor="#00A796"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col7:
        fig = create_indicator_figure(
            avg_loser, "Avg Loser", value_format=".2f", prefix="$", bgcolor="#DD2C48"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col8:
        fig = create_indicator_figure(
            max_winner, "Max Winner", value_format=".2f", prefix="$", bgcolor="#00A796"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col9:
        fig = create_indicator_figure(
            max_loser, "Max Loser", value_format=".2f", prefix="$", bgcolor="#DD2C48"
        )
        st.plotly_chart(fig, use_container_width=True)

    # Additional information
    if not filtered_df.empty:
        st.subheader("ℹ️ Additional Information")
        info_col1, info_col2, info_col3 = st.columns(3)

        with info_col1:
            st.metric("Number of Trades", total_trades)
        with info_col2:
            st.metric("Winning Trades", wins)
        with info_col3:
            st.metric("Losing Trades", total_trades - wins)
