import time

import streamlit as st

from src.api_utils import get_statement, process_statement_data, send_request
from src.config import load_config
from src.streamlit_dashboard import run_streamlit_dashboard
from src.transformations import transform


@st.cache_data
def load_and_process_data():
    config = load_config()
    reference_code = send_request(config)
    time.sleep(5)
    df = get_statement(config, reference_code)
    df = process_statement_data(df)
    df = transform(df)
    return df


def run_application():
    # Refresh button in the sidebar
    if st.button("🔄 Refresh data"):
        st.cache_data.clear()
        st.rerun()

    # Load data
    df = load_and_process_data()
    run_streamlit_dashboard(df)


if __name__ == "__main__":
    run_application()
