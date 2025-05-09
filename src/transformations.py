from datetime import datetime, timedelta

import numpy as np
import pandas as pd


def transform(df):
    """
    Filters and groups the given DataFrame based on specified criteria.

    Parameters:
        df (pandas.DataFrame): The DataFrame to filter and group.
        assets_to_include (list, optional): List of asset categories to include, e.g., ["STK", "OPT", "FUT", "FOP"]. Defaults to None.
        symbols_to_include (list, optional): List of underlying symbols to include. Defaults to None.
        dates_to_exclude (list, optional): List of trade dates to exclude. Defaults to None.

    Returns:
        pandas.DataFrame: A grouped DataFrame with calculated PnLRealized.
    """

    # Ensure consistent datetime format for comparison
    current_date = pd.Timestamp(datetime.now().date())
    future_date = pd.Timestamp(datetime.now().date() + timedelta(days=3))

    # Open trades are not included in the PnLRealized calculation and are filtered out in the PnLRealized calculation.
    # If a closed trade is settled fifoPnlRealized is used for the PnLRealized calculation.
    # If a closed trade is not settled, mtmPnl + ibCommission is used for the PnLRealized calculation.
    # That way the PnLRealized is calculated as fast as possible (t+1).
    # Because of weekends and holidays the settlement date is not always t+1 and can be t+2 or t+3.

    condition = (
        (df["tradeDate"] == df["expiry"])
        & (df["fifoPnlRealized"] == 0)
        & (df["settleDateTarget"].between(current_date, future_date))
    )

    # mtmPnL does not include the commission, so we add it to the mtmPnl to get the correct PnLRealized.
    mtmPnl_commission = df["mtmPnl"] + df["ibCommission"]

    # Set PnLRealized to mtmPnl + ibCommission if the condition is met, otherwise use fifoPnlRealized
    df["PnLRealized"] = np.where(condition, mtmPnl_commission, df["fifoPnlRealized"])

    return df


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
