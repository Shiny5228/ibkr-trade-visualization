import pandas as pd


def filter_and_group_data(
    df,
    assets_to_include=None,
    symbols_to_include=None,
    notes_to_exclude=None,
    dates_to_exclude=None,
):
    """
    Filters and groups the given DataFrame based on specified criteria.

    Parameters:
        df (pandas.DataFrame): The DataFrame to filter and group.
        assets_to_include (list, optional): List of asset categories to include, e.g., ["STK", "OPT", "FUT", "FOP"]. Defaults to None.
        symbols_to_include (list, optional): List of underlying symbols to include. Defaults to None.
        notes_to_exclude (list, optional): List of notes to exclude. Defaults to None.
        dates_to_exclude (list, optional): List of trade dates to exclude. Defaults to None.

    Returns:
        pandas.DataFrame: A grouped DataFrame with calculated PnLRealized.
    """

    # Set default values if parameters are None
    if assets_to_include is None:
        assets_to_include = df["assetCategory"].unique()
    if symbols_to_include is None:
        symbols_to_include = df["underlyingSymbol"].unique()
    if notes_to_exclude is None:
        notes_to_exclude = []
    if dates_to_exclude is None:
        dates_to_exclude = []

    # tradeDate is in datetime format and dates_to_exclude is converted to datetime
    dates_to_exclude = pd.to_datetime(
        dates_to_exclude, format="%Y%m%d", errors="coerce"
    )

    filtered_df = df[
        (df["assetCategory"].isin(assets_to_include))
        & (df["underlyingSymbol"].isin(symbols_to_include))
        & (~df["notes"].isin(notes_to_exclude))
        & (~df["tradeDate"].isin(dates_to_exclude))
    ]

    # mtmPnl is used because fifoPnlRealized is only available one day after settlement (t+2)
    # and we want to calculate the PnLRealized as fast as possible (t+0 or t+1).
    # That why assigned and excercised options are excluded in the notebook
    filtered_df["PnLRealized"] = filtered_df["mtmPnl"] + filtered_df["ibCommission"]

    grouped_df = (
        filtered_df.groupby(["tradeDate", "settleDateTarget"])["PnLRealized"]
        .sum()
        .reset_index()
    )
    return filtered_df, grouped_df


def add_cum_sum_rows(df):
    """
    Adds cumulative sum columns to the DataFrame for different time periods.

    Parameters:
        df (pandas.DataFrame): The DataFrame to which cumulative sum columns will be added.

    Returns:
        pandas.DataFrame: The modified DataFrame with additional cumulative sum columns.
    """

    # cumulative sum
    df["TotalProfit"] = df["PnLRealized"].cumsum()

    # cumulative sum per calendarweek
    df["ProfitWeek"] = df.groupby(df["tradeDate"].dt.isocalendar().week)[
        "PnLRealized"
    ].cumsum()

    # cumulative sum per month
    df["ProfitMonth"] = df.groupby(df["tradeDate"].dt.to_period("M"))[
        "PnLRealized"
    ].cumsum()

    # cumulative sum per quarter
    df["ProfitQuarter"] = df.groupby(df["tradeDate"].dt.to_period("Q"))[
        "PnLRealized"
    ].cumsum()

    df["week"] = df["tradeDate"].dt.isocalendar().week
    df["month"] = df["tradeDate"].dt.month_name()
    df["quarter"] = df["tradeDate"].dt.quarter
    df["year"] = df["tradeDate"].dt.year

    return df


# Prepare data for visualization
def get_filtered_data(df, period, value=None):
    """
    Filters a DataFrame based on a specified time period and value.

    Parameters:
        df (pandas.DataFrame): The DataFrame to filter. It is expected to have columns
                               such as 'week', 'month', 'quarter', and 'year'.
        period (str): The time period to filter by. Accepted values are "week", "month",
                      "quarter", or "year".
        value (optional): The value to filter the specified period by. If None, the
                          function returns the original DataFrame.

    Returns:
        pandas.DataFrame: A filtered DataFrame containing rows that match the specified
                          period and value. If the period is not recognized, the original
                          DataFrame is returned.
    """
    if period == "week":
        return df[df["week"] == value]
    elif period == "month":
        return df[df["month"] == value]
    elif period == "quarter":
        return df[df["quarter"] == value]
    elif period == "year":
        return df[df["year"] == value]
    else:
        return df


def get_filtered_pcr(df, period, value=None):
    """
    Filters a DataFrame based on a specified time period and calculates the Premium Capture Rate (PCR).

    Parameters:
        df (pandas.DataFrame): The DataFrame to filter. It must contain the columns 'tradeDate', 'cost', and 'PnLRealized'.
        period (str): The time period to filter by. Accepted values are "week", "month", "quarter", or "year".
        value (optional): The value to filter the specified period by. If None, the function processes the entire DataFrame.

    Returns:
        None: Prints the premium received, premium captured, and premium capture rate.
    """
    # Ensure the DataFrame has the necessary columns
    required_columns = {"tradeDate", "cost", "PnLRealized"}
    if not required_columns.issubset(df.columns):
        raise ValueError(
            f"The DataFrame must contain the following columns: {required_columns}"
        )

    # Zeitspalten erzeugen
    df["week"] = df["tradeDate"].dt.isocalendar().week
    df["month"] = df["tradeDate"].dt.month_name()
    df["quarter"] = df["tradeDate"].dt.quarter
    df["year"] = df["tradeDate"].dt.year

    # Nach Zeitraum filtern
    if period == "week":
        filtered_df = df[df["week"] == value]
    elif period == "month":
        filtered_df = df[df["month"] == value]
    elif period == "quarter":
        filtered_df = df[df["quarter"] == value]
    elif period == "year":
        filtered_df = df[df["year"] == value]
    else:
        filtered_df = df

    # Nur verkaufte Optionen filtern (cost < 0)
    df_pcr = filtered_df[filtered_df["cost"] < 0]

    # Summen berechnen
    sum_cost = abs(df_pcr["cost"].sum()).round(2)
    sum_realized = df_pcr["PnLRealized"].sum().round(2)

    # Premium Capture Rate berechnen
    premium_capture_rate = (
        ((sum_realized / sum_cost) * 100).round(2) if sum_cost != 0 else 0.0
    )

    print(f"Premium received: {sum_cost}")
    print(f"Premium captured: {sum_realized}")
    print(f"Premium capture rate: {premium_capture_rate}")
