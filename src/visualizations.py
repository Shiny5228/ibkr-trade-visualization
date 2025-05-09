import pandas as pd
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
                        "y": [filtered["ProfitWeek"], filtered["PnLRealized"]],
                    },
                    {
                        "title": f"PnL in $ - Week {w}",
                        "xaxis": {"type": "category"},
                    },
                ],
            )
        )

    # Create Buttons for every month (1-12)
    months_order = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]
    df["month"] = pd.Categorical(df["month"], categories=months_order, ordered=True)

    for m in df["month"].cat.categories:
        if m in df["month"].unique():
            filtered = get_filtered_data(df, "month", m)
            buttons.append(
                dict(
                    label=m,
                    method="update",
                    args=[
                        {
                            "x": [
                                filtered["tradeDate"].astype(str),
                                filtered["tradeDate"].astype(str),
                            ],
                            "y": [filtered["ProfitMonth"], filtered["PnLRealized"]],
                        },
                        {
                            "title": f"PnL in $ - Month {m}",
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
                        "y": [filtered["ProfitQuarter"], filtered["PnLRealized"]],
                    },
                    {
                        "title": f"PnL in $ - Quarter {q}",
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
                        "title": f"PnL in $ - Year {y}",
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
                {"title": "PnL in $ - Total", "xaxis": {"type": "category"}},
            ],
        )
    )

    # Button 2: Filter by assetCategory (multi-select)
    asset_categories = sorted(df["assetCategory"].unique())
    buttons_asset = []

    # Add "Alle" button
    buttons_asset.append(
        dict(
            label="Alle",
            method="update",
            args=[
                {
                    "x": [
                        df["tradeDate"].astype(str),
                        df["tradeDate"].astype(str),
                    ],
                    "y": [df["PnLRealized"], df["PnLRealized"]],
                },
                {
                    "title": "PnL in $ - Alle Asset Kategorien",
                    "xaxis": {"type": "category"},
                },
            ],
        )
    )

    for asset in asset_categories:
        buttons_asset.append(
            dict(
                label=f"Asset: {asset}",
                method="update",
                args=[
                    {
                        "x": [
                            df[df["assetCategory"] == asset]["tradeDate"].astype(str),
                            df[df["assetCategory"] == asset]["tradeDate"].astype(str),
                        ],
                        "y": [
                            df[df["assetCategory"] == asset]["PnLRealized"],
                            df[df["assetCategory"] == asset]["PnLRealized"],
                        ],
                    },
                    {
                        "title": f"PnL in $ - Asset: {asset}",
                        "xaxis": {"type": "category"},
                    },
                ],
            )
        )

    # Button 3: Filter by underlyingSymbol (multi-select)
    underlying_symbols = sorted(df["underlyingSymbol"].unique())
    buttons_symbol = []

    # Add "Alle" button
    buttons_symbol.append(
        dict(
            label="Alle",
            method="update",
            args=[
                {
                    "x": [
                        df["tradeDate"].astype(str),
                        df["tradeDate"].astype(str),
                    ],
                    "y": [df["PnLRealized"], df["PnLRealized"]],
                },
                {
                    "title": "PnL in $ - Alle Symbole",
                    "xaxis": {"type": "category"},
                },
            ],
        )
    )

    for symbol in underlying_symbols:
        buttons_symbol.append(
            dict(
                label=f"Symbol: {symbol}",
                method="update",
                args=[
                    {
                        "x": [
                            df[df["underlyingSymbol"] == symbol]["tradeDate"].astype(
                                str
                            ),
                            df[df["underlyingSymbol"] == symbol]["tradeDate"].astype(
                                str
                            ),
                        ],
                        "y": [
                            df[df["underlyingSymbol"] == symbol]["PnLRealized"],
                            df[df["underlyingSymbol"] == symbol]["PnLRealized"],
                        ],
                    },
                    {
                        "title": f"PnL in $ - Symbol: {symbol}",
                        "xaxis": {"type": "category"},
                    },
                ],
            )
        )

    return buttons, buttons_asset, buttons_symbol


def create_initial_plot(df, buttons1, buttons2, buttons3):
    """
    Create the initial plot with the "Total" view and add buttons for interactivity.

    Args:
        df (DataFrame): The grouped DataFrame containing trade data.
        buttons1 (list): A list of button dictionaries for year filtering.
        buttons2 (list): A list of button dictionaries for asset category filtering.
        buttons3 (list): A list of button dictionaries for underlying symbol filtering.

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

    # Ensure updatemenus is correctly structured
    fig.update_layout(
        updatemenus=[
            dict(
                active=len(buttons1) - 1,  # "Total" is the last button
                buttons=buttons1,
                direction="down",
                showactive=True,
                x=0.1,
                y=1.15,
            ),  # Adjust position if necessary
            dict(
                active=0,
                buttons=buttons2,
                direction="down",
                showactive=True,
                x=0.5,
                y=1.15,
            ),  # Adjust position if necessary
            dict(
                active=0,
                buttons=buttons3,
                direction="down",
                showactive=True,
                x=0.9,
                y=1.15,
            ),  # Adjust position if necessary
        ],
        title="PnL in $ - Total",
        xaxis_title="tradeDate",
        yaxis_title="PnL Realized",
        autosize=True,
    )
    fig.update_xaxes(type="category")
    fig.layout.template = "plotly_dark"

    return fig
