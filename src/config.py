import json
import os
from pathlib import Path

from dotenv import load_dotenv


def load_config() -> dict:
    project_root = Path(__file__).resolve().parent.parent
    dotenv_path = project_root / ".env"

    # load_dotenv() loads environment variables from a .env file
    load_dotenv(dotenv_path=dotenv_path)

    config = {
        "TOKEN": os.getenv("TOKEN"),
        "QUERY_ID": os.getenv("QUERY_ID"),
        "FLEX_VERSION": os.getenv("FLEX_VERSION"),
        "HEADERS": os.getenv("HEADERS"),
    }

    # Validation for required environment variables
    if not config["TOKEN"]:
        raise ValueError("Please set the TOKEN environment variable.")
    if not config["QUERY_ID"]:
        raise ValueError("Please set the QUERY_ID environment variable.")
    if not config["FLEX_VERSION"]:
        raise ValueError("Please set the FLEX_VERSION environment variable.")
    if not config["HEADERS"]:
        raise ValueError("Please set the HEADERS environment variable.")

    # Convert HEADERS from JSON string to dictionary
    try:
        config["HEADERS"] = json.loads(config["HEADERS"])
    except json.JSONDecodeError:
        raise ValueError("HEADERS must be a valid JSON string.")

    return config
