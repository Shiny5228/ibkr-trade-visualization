import time

from src.api_utils import get_statement, process_statement_data, send_request
from src.config import load_config
from src.transformations import transform
from src.visualization import create_dashboard


def run_application():
    # Load Environment Variables
    config = load_config()

    # Get Statement from IB via API
    reference_code = send_request(config)

    # Wait for the statement to be generated. Quick fix until more robust solution is implemented.
    time.sleep(5)

    df = get_statement(config, reference_code)

    # Process Data
    df = process_statement_data(df)
    df = transform(df)

    # Create Dashboard
    app = create_dashboard(df)
    app.run(debug=True)


if __name__ == "__main__":
    run_application()
