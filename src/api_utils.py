import xml.etree.ElementTree as ET
from io import StringIO

import pandas as pd
import requests


def send_request(token, query_id, flex_version, headers):
    """
    Sends a request to the Interactive Brokers Flex Web Service to generate a statement.

    Args:
        token (str): The API token for authentication.
        query_id (str): The query ID for the Flex report.
        flex_version (str): The version of the Flex Web Service.
        headers (dict): Additional headers for the HTTP request.

    Returns:
        str: The reference code for the generated statement.
    """
    send_url = "https://ndcdyn.interactivebrokers.com/AccountManagement/FlexWebService/SendRequest"
    send_params = {"t": token, "q": query_id, "v": flex_version}
    response = requests.get(send_url, params=send_params, headers=headers)
    reference_code = ET.fromstring(response.text).findtext("ReferenceCode")

    return reference_code


def get_statement(token, reference_code, flex_version, headers):
    """
    Retrieves the statement data from the Interactive Brokers Flex Web Service.

    Args:
        token (str): The API token for authentication.
        reference_code (str): The reference code for the generated statement.
        flex_version (str): The version of the Flex Web Service.
        headers (dict): Additional headers for the HTTP request.

    Returns:
        pd.DataFrame: A DataFrame containing the statement data filtered by the specified XPath.
    """
    get_url = "https://ndcdyn.interactivebrokers.com/AccountManagement/FlexWebService/GetStatement"
    get_params = {"t": token, "q": reference_code, "v": flex_version}
    xml_data = requests.get(get_url, params=get_params, headers=headers).text

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
