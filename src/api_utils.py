import time
import xml.etree.ElementTree as ET
from io import StringIO

import pandas as pd
import requests


def send_request(config):
    """
    Send a request to the IB API to generate a statement.

    Args:
        config (dict): Configuration dictionary containing TOKEN, QUERY_ID, FLEX_VERSION, and HEADERS.

    Returns:
        str: Reference code for the generated statement.
    """
    token = config["TOKEN"]
    query_id = config["QUERY_ID"]
    flex_version = config["FLEX_VERSION"]
    headers = config["HEADERS"]

    send_url = "https://ndcdyn.interactivebrokers.com/AccountManagement/FlexWebService/SendRequest"
    send_params = {"t": token, "q": query_id, "v": flex_version}
    response = requests.get(send_url, params=send_params, headers=headers)
    reference_code = ET.fromstring(response.text).findtext("ReferenceCode")

    response.raise_for_status()  # Raise an error for bad responses
    return reference_code


def get_statement(config, reference_code):
    """
    Retrieve the generated statement from the IB API.

    Args:
        config (dict): Configuration dictionary containing TOKEN, FLEX_VERSION, and HEADERS.
        reference_code (str): Reference code for the generated statement.

    Returns:
        pd.DataFrame: DataFrame containing the statement data.
    """
    token = config["TOKEN"]
    flex_version = config["FLEX_VERSION"]
    headers = config["HEADERS"]

    get_url = "https://ndcdyn.interactivebrokers.com/AccountManagement/FlexWebService/GetStatement"
    get_params = {"t": token, "q": reference_code, "v": flex_version}

    max_retries = 5
    retry_delay = 5  # seconds

    for attempt in range(max_retries):
        xml_data = requests.get(get_url, params=get_params, headers=headers).text

        # Check if response contains an error
        try:
            root = ET.fromstring(xml_data)
            error_code = root.findtext("ErrorCode")

            if error_code == "1019":
                # Error 1019: Statement generation in progress
                if attempt < max_retries - 1:
                    print(
                        f"Statement generation in progress. Retrying in {retry_delay} seconds... (attempt {attempt + 1}/{max_retries})"
                    )
                    time.sleep(retry_delay)
                    continue
                else:
                    error_msg = root.findtext(
                        "ErrorMessage",
                        "Statement generation in progress. Maximum retries exceeded.",
                    )
                    raise Exception(f"FlexQuery Error 1019: {error_msg}")
            elif error_code:
                # Other error codes - fail immediately
                error_msg = root.findtext("ErrorMessage", "Unknown error")
                raise Exception(f"FlexQuery Error {error_code}: {error_msg}")
            else:
                # No error code found, assume success
                return pd.read_xml(StringIO(xml_data), xpath=".//Trade")
        except ET.ParseError:
            # If XML parsing fails, it might be a valid response with different structure
            # Return as-is and let the caller handle it
            return pd.read_xml(StringIO(xml_data), xpath=".//Trade")


def process_statement_data(df):
    """
    Processes the statement data by converting date columns to datetime format.

    Args:
        df (pd.DataFrame): The DataFrame containing the statement data.

    Returns:
        pd.DataFrame: The processed DataFrame with date columns converted to datetime.
    """
    df["tradeDate"] = pd.to_datetime(df["tradeDate"], format="%Y%m%d")
    df["settleDateTarget"] = pd.to_datetime(df["settleDateTarget"], format="%Y%m%d")
    df["expiry"] = pd.to_datetime(df["expiry"], format="%Y%m%d")
    df["dateTime"] = pd.to_datetime(df["dateTime"], format="%Y%m%d%H%M%S")

    return df
