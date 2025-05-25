def identify_option_strategy(group):
    """Identifies option strategies based on a group of option contracts.

    Args:
    group (pd.DataFrame): A DataFrame representing a group of option contracts with
    the columns 'putCall', 'buySell', 'expiry', and 'strike'.

    Returns:
    str: The name of the identified option strategy or None if no
    strategy could be identified.
    """
    if len(group) == 1:
        # Long Call
        if (group["putCall"] == "C").all():
            if (group["buySell"] == "BUY").all():
                return "Long Call"
        # Short Call
        if (group["putCall"] == "C").all():
            if (group["buySell"] == "SELL").all():
                return "Short Call"
        # Long Put
        if (group["putCall"] == "P").all():
            if (group["buySell"] == "BUY").all():
                return "Long Put"
        # Short Put
        if (group["putCall"] == "P").all():
            if (group["buySell"] == "SELL").all():
                return "Short Put"

    elif len(group) == 2:
        if group["expiry"].nunique() == 1:
            # Bull Call Spread and Bear Call Spread
            if (group["putCall"] == "C").all():
                strike_sell = group.loc[group["buySell"] == "SELL", "strike"]
                strike_buy = group.loc[group["buySell"] == "BUY", "strike"]
                if not strike_sell.empty and not strike_buy.empty:
                    strike_sell = strike_sell.iloc[0]
                    strike_buy = strike_buy.iloc[0]
                    if strike_sell < strike_buy:
                        return "Bear Call Spread"
                    else:
                        return "Bull Call Spread"
            # Bull Put Spread and Bear Put Spread
            if (group["putCall"] == "P").all():
                strike_sell = group.loc[group["buySell"] == "SELL", "strike"]
                strike_buy = group.loc[group["buySell"] == "BUY", "strike"]
                if not strike_sell.empty and not strike_buy.empty:
                    strike_sell = strike_sell.iloc[0]
                    strike_buy = strike_buy.iloc[0]
                    if strike_sell < strike_buy:
                        return "Bear Put Spread"
                    else:
                        return "Bull Put Spread"
        # Straddle
        if set(group["putCall"]) == {"P", "C"}:
            if (group["buySell"] == {"BUY"}).all():
                strike_call = group.loc[group["putCall"] == "C", "strike"]
                strike_put = group.loc[group["putCall"] == "P", "strike"]
                if not strike_call.empty and not strike_put.empty:
                    strike_call = strike_call.iloc[0]
                    strike_put = strike_put.iloc[0]
                    if strike_call == strike_put:
                        return "Straddle"
        # Strangle
        if set(group["putCall"]) == {"P", "C"}:
            if (group["buySell"] == {"BUY"}).all():
                strike_call = group.loc[group["putCall"] == "C", "strike"]
                strike_put = group.loc[group["putCall"] == "P", "strike"]
                if not strike_call.empty and not strike_put.empty:
                    strike_call = strike_call.iloc[0]
                    strike_put = strike_put.iloc[0]
                    if strike_call > strike_put:
                        return "Strangle"

        else:
            # Calendar Call Spread
            if (group["putCall"] == "C").all():
                strike_sell = group.loc[group["buySell"] == "SELL", "strike"]
                strike_buy = group.loc[group["buySell"] == "BUY", "strike"]
                if not strike_sell.empty and not strike_buy.empty:
                    strike_sell = strike_sell.iloc[0]
                    strike_buy = strike_buy.iloc[0]
                    if strike_sell == strike_buy:
                        return "Calendar Call Spread"
            # Calendar Put Spread
            if (group["putCall"] == "P").all():
                strike_sell = group.loc[group["buySell"] == "SELL", "strike"]
                strike_buy = group.loc[group["buySell"] == "BUY", "strike"]
                if not strike_sell.empty and not strike_buy.empty:
                    strike_sell = strike_sell.iloc[0]
                    strike_buy = strike_buy.iloc[0]
                    if strike_sell == strike_buy:
                        return "Calendar Put Spread"
            # Diagonal Call Spread
            if (group["putCall"] == "C").all():
                strike_sell = group.loc[group["buySell"] == "SELL", "strike"]
                strike_buy = group.loc[group["buySell"] == "BUY", "strike"]
                if not strike_sell.empty and not strike_buy.empty:
                    strike_sell = strike_sell.iloc[0]
                    strike_buy = strike_buy.iloc[0]
                    if strike_sell > strike_buy:
                        return "Diagonal Call Spread"
            # Diagonal Put Spread
            if (group["putCall"] == "P").all():
                strike_sell = group.loc[group["buySell"] == "SELL", "strike"]
                strike_buy = group.loc[group["buySell"] == "BUY", "strike"]
                if not strike_sell.empty and not strike_buy.empty:
                    strike_sell = strike_sell.iloc[0]
                    strike_buy = strike_buy.iloc[0]
                    if strike_sell < strike_buy:
                        return "Diagonal Put Spread"

    elif len(group) == 4:
        if group["expiry"].nunique() == 1:
            # Iron Condor
            if set(group["putCall"]) == {"P", "C"}:
                if set(group["buySell"]) == {"BUY", "SELL"}:
                    strikes = sorted(group["strike"].tolist())
                    if strikes[0] < strikes[1] < strikes[2] < strikes[3]:
                        return "Iron Condor"
            # Iron Butterfly
            if set(group["putCall"]) == {"P", "C"}:
                if set(group["buySell"]) == {"BUY", "SELL"}:
                    strikes = sorted(group["strike"].tolist())
                    if strikes[1] == strikes[2]:
                        return "Iron Butterfly"
            # Long Put Butterfly
            if (group["putCall"] == "P").all():
                if set(group["buySell"]) == {"BUY", "SELL"}:
                    strikes = sorted(group["strike"].tolist())
                    if strikes[0] < strikes[1] == strikes[2] < strikes[3]:
                        return "Long Put Butterfly"
            # Long Call Butterfly
            if (group["putCall"] == "C").all():
                if set(group["buySell"]) == {"BUY", "SELL"}:
                    strikes = sorted(group["strike"].tolist())
                    if strikes[0] < strikes[1] == strikes[2] < strikes[3]:
                        return "Long Call Butterfly"
            # Box Spread
            if set(group["putCall"]) == {"P", "C"}:
                if set(group["buySell"]) == {"BUY", "SELL"}:
                    strikes = sorted(group["strike"].tolist())
                    if strikes[0] == strikes[1] and strikes[2] == strikes[3]:
                        return "Box Spread"

    return "Other"


def categorize_options_trades(df):
    """
    Categorizes warrants in a DataFrame according to option strategies.

    Args:
    df (pd.DataFrame): A DataFrame representing warrants with the columns
    'dateTime', 'putCall', 'buySell', 'expiry' and 'strike'.
    df2 (pd.DataFrame): A DataFrame with the columns 'description' and 'dateTime'

    Returns:
    pd.DataFrame: A DataFrame with an additional column 'strategy' containing the
    identified option strategy for each group of warrants.
    """

    df_copy = df.copy()

    df_options = df_copy[
        (df_copy["openCloseIndicator"] == "O")
        & (df_copy["assetCategory"].isin(["OPT", "FOP"]))
    ].copy()

    grouped = df_options.groupby("dateTime")

    strategy = grouped.apply(identify_option_strategy, include_groups=False)

    df_options.loc[:, "optionStrategy"] = df_options["dateTime"].map(strategy)

    df_options = df_options.rename(columns={"dateTime": "dateTime_options"})

    df_merged = df.merge(
        df_options[["description", "dateTime_options", "optionStrategy"]],
        left_on=["description", "opendateTime"],
        right_on=["description", "dateTime_options"],
        how="left",
    )

    df_merged.drop(columns=["dateTime_options"], inplace=True)

    return df_merged
