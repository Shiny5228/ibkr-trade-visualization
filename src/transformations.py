from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from src.options import categorize_options_trades


def consolidate_trades(df):
    """
    Consolidates partial trades in the DataFrame by summing up their values.
    Partial trades are identified by the 'notes' column having the value 'P'.
    The function groups the DataFrame by relevant columns and sums up the values
    of 'ibCommission', 'cost', 'fifoPnlRealized', and 'mtmPnl' for partial trades.

    Parameters:
        df (pandas.DataFrame): The DataFrame containing trade data.
    Returns:
        pandas.DataFrame: A new DataFrame with consolidated trades.
    """

    partial_trades_df = df[df["notes"] == "P"].copy()
    other_trades_df = df[df["notes"] != "P"].copy()

    group_cols = [
        col
        for col in partial_trades_df.columns
        if col not in ["ibCommission", "cost", "fifoPnlRealized", "mtmPnl", "notes"]
    ]

    if not partial_trades_df.empty:
        consolidated_partials_df = partial_trades_df.groupby(
            group_cols, as_index=False, dropna=False
        ).agg(
            {
                "ibCommission": "sum",
                "cost": "sum",
                "fifoPnlRealized": "sum",
                "mtmPnl": "sum",
            }
        )
        consolidated_partials_df["notes"] = "P"
    else:
        consolidated_partials_df = pd.DataFrame(columns=df.columns)

    consolidated_partials_df = consolidated_partials_df.reindex(columns=df.columns)

    final_trades_df = pd.concat(
        [other_trades_df, consolidated_partials_df], ignore_index=True
    )

    final_trades_df = final_trades_df.sort_values(
        by=["assetCategory", "description", "dateTime"], ascending=[False, True, True]
    ).reset_index(drop=True)

    return final_trades_df


def filter_group_general(group):
    """
    Filters a group of trades to keep only the relevant entries.
    This function checks if there are any closed trades in the group.
    If there are, it keeps the closed trades and all open trades that occur after the last closed trade.

    Parameters:
        group (pandas.DataFrame): A group of trades.

    Returns:
        pandas.DataFrame: The filtered group.
    """
    closed_trades = group[group["openCloseIndicator"] == "C"]
    if not closed_trades.empty:
        last_close_time = closed_trades["dateTime"].max()
        later_open_trades = group[
            (group["openCloseIndicator"] == "O") & (group["dateTime"] > last_close_time)
        ]
        return pd.concat([closed_trades, later_open_trades])
    else:
        return group


def transform(df):
    """
    Filters and groups the given DataFrame based on specified criteria.

    Parameters:
        df (pandas.DataFrame): The DataFrame to filter and group.

    Returns:
        pandas.DataFrame: A grouped DataFrame with calculated PnLRealized.
    """
    df_copy = df.copy()
    if "tradeID" in df_copy.columns:
        df_copy = df_copy.drop(columns=["tradeID"], errors="ignore")

    df_copy = consolidate_trades(df_copy)

    # Initialize the new column with empty values
    df_copy["opendateTime"] = pd.NaT
    df_copy["opendateTime"] = df_copy["opendateTime"].astype("datetime64[ns]")

    # Group by 'description'
    grouped = df_copy.groupby("description")
    for name, group in grouped:
        if "O" in group["openCloseIndicator"].values:
            open_datetime = group[group["openCloseIndicator"] == "O"]["dateTime"].iloc[
                0
            ]
        else:
            open_datetime = group["dateTime"].iloc[0]
        df_copy.loc[df_copy["description"] == name, "opendateTime"] = open_datetime

    df_copy_opt = categorize_options_trades(df_copy)

    # Ensure consistent datetime format for comparison
    current_date = pd.Timestamp(datetime.now().date())
    if current_date.weekday() == 5:  # Saturday
        current_date = current_date - timedelta(days=1)
    elif current_date.weekday() == 6:  # Sunday
        current_date = current_date - timedelta(days=2)

    future_date = pd.Timestamp(datetime.now().date() + timedelta(days=3))

    # Open trades are not included in the PnLRealized calculation and are filtered out in the PnLRealized calculation.
    # If a closed trade is settled fifoPnlRealized is used for the PnLRealized calculation.
    # If a closed trade is not settled, mtmPnl + ibCommission is used for the PnLRealized calculation.
    # That way the PnLRealized is calculated as fast as possible (t+1).
    # Because of weekends and holidays the settlement date is not always t+1 and can be t+2 or t+3.

    condition = (
        (df_copy_opt["tradeDate"] == df_copy_opt["expiry"])
        & (df_copy_opt["fifoPnlRealized"] == 0)
        & (df_copy_opt["settleDateTarget"].between(current_date, future_date))
    )

    # mtmPnL does not include the commission, so we add it to the mtmPnl to get the correct PnLRealized.
    mtmPnl_commission = df_copy_opt["mtmPnl"] + df_copy_opt["ibCommission"]

    # Set PnLRealized to mtmPnl + ibCommission if the condition is met, otherwise use fifoPnlRealized
    df_copy_opt["PnLRealized"] = np.where(
        condition, mtmPnl_commission, df_copy_opt["fifoPnlRealized"]
    )

    # Filter for closed trades except for the ones that are not settled yet, like 0DTE options
    df_copy_opt = df_copy_opt[
        (df_copy_opt["openCloseIndicator"] == "C")
        | (
            (df_copy_opt["settleDateTarget"].between(current_date, future_date))
            & (df_copy_opt["PnLRealized"] != 0)
        )
    ]

    # Remove duplicates based on 'description' and 'tradeDate'.
    # Some 0DTE trades can be counted twice, if the position is closed on the same day and the position is not settled yet.
    grouped = df_copy_opt.groupby(["description", "tradeDate"])

    df_no_dupes = grouped.apply(
        filter_group_general, include_groups=False
    ).reset_index()

    return df_no_dupes
