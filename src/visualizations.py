import plotly.graph_objects as go

def generate_buttons(df, get_filtered_data):
    """
    Generate buttons for different time periods (week, month, quarter, year, total).

    Args:
        df (DataFrame): The grouped DataFrame containing trade data.
        get_filtered_data (callable): A function to filter the DataFrame by a specific column and value.

    Returns:
        list: A list of button dictionaries for use in visualizations.
    """
    buttons = []

    # Create Buttons for every week (1-52)
    for w in sorted(df["week"].unique()):
        filtered = get_filtered_data(df, "week", w)
        buttons.append(
            dict(
                label=f"Woche {w}",
                method="update",
                args=[
                    {
                        "x": [
                            filtered["tradeDate"].astype(str),
                            filtered["tradeDate"].astype(str),
                        ],
                        "y": [filtered["TotalProfit"], filtered["PnLRealized"]],
                    },
                    {
                        "title": f"0DTE IF PnL in $ - Woche {w}",
                        "xaxis": {"type": "category"},
                    },
                ],
            )
        )

    # Create Buttons for every month (1-12)
    for m in sorted(df["month"].unique()):
        filtered = get_filtered_data(df, "month", m)
        buttons.append(
            dict(
                label=f"Monat {m}",
                method="update",
                args=[
                    {
                        "x": [
                            filtered["tradeDate"].astype(str),
                            filtered["tradeDate"].astype(str),
                        ],
                        "y": [filtered["TotalProfit"], filtered["PnLRealized"]],
                    },
                    {
                        "title": f"0DTE IF PnL in $ - Monat {m}",
                        "xaxis": {"type": "category"},
                    },
                ],
            )
        )

    # Create Buttons for every quarter (1-4)
    for q in sorted(df["quarter"].unique()):
        filtered = get_filtered_data(df, "quarter", q)
        buttons.append(
            dict(
                label=f"Quartal {q}",
                method="update",
                args=[
                    {
                        "x": [
                            filtered["tradeDate"].astype(str),
                            filtered["tradeDate"].astype(str),
                        ],
                        "y": [filtered["TotalProfit"], filtered["PnLRealized"]],
                    },
                    {
                        "title": f"0DTE IF PnL in $ - Quartal {q}",
                        "xaxis": {"type": "category"},
                    },
                ],
            )
        )

    # Create Buttons for every year
    for y in sorted(df["year"].unique()):
        filtered = get_filtered_data(df, "year", y)
        buttons.append(
            dict(
                label=f"Jahr {y}",
                method="update",
                args=[
                    {
                        "x": [
                            filtered["tradeDate"].astype(str),
                            filtered["tradeDate"].astype(str),
                        ],
                        "y": [filtered["TotalProfit"], filtered["PnLRealized"]],
                    },
                    {
                        "title": f"0DTE IF PnL in $ - Jahr {y}",
                        "xaxis": {"type": "category"},
                    },
                ],
            )
        )

    # Create Total Button
    buttons.append(
        dict(
            label="Total",
            method="update",
            args=[
                {
                    "x": [
                        df["tradeDate"].astype(str),
                        df["tradeDate"].astype(str),
                    ],
                    "y": [df["TotalProfit"], df["PnLRealized"]],
                },
                {"title": "0DTE IF PnL in $ - Total", "xaxis": {"type": "category"}},
            ],
        )
    )

    return buttons


def create_initial_plot(df, buttons):
    """
    Create the initial plot with the "Total" view and add buttons for interactivity.

    Args:
        df (DataFrame): The grouped DataFrame containing trade data.
        buttons (list): A list of button dictionaries for use in the plot.

    Returns:
        plotly.graph_objects.Figure: The created figure.
    """
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["tradeDate"].astype(str),
            y=df["TotalProfit"],
            mode="lines",
            name="Total Profit",
            line=dict(color="red"),
        )
    )
    fig.add_bar(
        x=df["tradeDate"].astype(str),
        y=df["PnLRealized"],
        name="PnL Daily",
        marker_color="green",
    )

    fig.update_layout(
        updatemenus=[
            dict(
                active=len(buttons) - 1,  # "Total" is the last button
                buttons=buttons,
                direction="down",
            )
        ],
        title="0DTE IF PnL in $ - Total",
        xaxis_title="tradeDate",
        yaxis_title="PnL Realized",
        autosize=True
    )
    fig.update_xaxes(type="category")
    fig.layout.template = "plotly_dark"

    return fig