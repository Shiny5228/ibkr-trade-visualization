from datetime import datetime, timedelta

import numpy as np
import pandas as pd


def transform(df):
    """
    Filters and groups the given DataFrame based on specified criteria.

    Parameters:
        df (pandas.DataFrame): The DataFrame to filter and group.

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

    # Initialize the new column with empty values
    df["opendateTime"] = pd.NaT
    df["opendateTime"] = df["opendateTime"].astype("datetime64[ns]")

    # Group by 'description'
    grouped = df.groupby("description")
    for name, group in grouped:
        if len(group) == 1 and group["openCloseIndicator"].iloc[0] == "O":
            df.loc[df["description"] == name, "opendateTime"] = group["dateTime"].iloc[
                0
            ]
        else:
            if "O" in group["openCloseIndicator"].values:
                open_datetime = group[group["openCloseIndicator"] == "O"][
                    "dateTime"
                ].iloc[0]
                df.loc[
                    (df["description"] == name) & (df["openCloseIndicator"] == "C"),
                    "opendateTime",
                ] = open_datetime
            else:
                open_datetime = group["dateTime"].iloc[0]
                df.loc[
                    (df["description"] == name) & (df["openCloseIndicator"] == "C"),
                    "opendateTime",
                ] = open_datetime

    # Filter for closed trades except for the ones that are not settled yet, like 0DTE options
    df = df[
        (df["openCloseIndicator"] == "C")
        | (
            (df["settleDateTarget"].between(current_date, future_date))
            & (df["PnLRealized"] != 0)
        )
    ]

    return df
