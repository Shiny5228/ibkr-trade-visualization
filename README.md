# IBKR Trade Visualization

A tool for visualizing trade data from Interactive Brokers (IBKR). This project helps traders analyze their trading performance through intuitive and interactive visualizations. Currently **only working for 0DTE Option trades** exported via IBKR IBKR Flex Query.

## Table of Contents
- [IBKR Trade Visualization](#ibkr-trade-visualization)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Generating IB Reports](#generating-ib-reports)
  - [Contributing](#contributing)
  - [License](#license)
  - [Contact](#contact)

## Features

- Import trade data from IBKR.
- Generate various visualizations to analyze 0DTE trading performance.
- User-friendly interface made with plotly for exploring trade metrics.

![ibkr_trade_gif](https://github.com/user-attachments/assets/d860927f-395f-49e9-a93a-8b9b9e379531)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/ibkr-trade-visualization.git
   cd ibkr-trade-visualization
   ```

2. Install dependencies using `pyproject.toml`:
   ```bash
   uv sync
   ```

## Usage

1. Generate IBKR Flex Query report.
2. Configure .env and load data with notebook.
3. Explore the visualizations made with plotly to gain insights into your 0DTE trading performance.

## Generating IB Reports

To generate the required IBKR Flex Query report:

1. Log in to your IBKR account.
2. Navigate to **Reports > Flex Queries**.
3. Create a new Flex Query with the following fields in **Trades**:
   - **Execution** At the top of the report
   - **Account ID**
   - **Asset Class**
   - **Description** 
   - **Underlying Symbol**
   - **Trade Date**
   - **Settle Date**
   - **Put/Call**
   - **Buy/Sell**
   - **Notes**
   - **Cost Basis**
   - **Realized PnL**
   - **MTM P/L**
   - **IB Commission**
   - **Level of Detail**
4. At Delivery Configuration select **Format: XML** and **Period: Year to Date**.
5. Save the query and note the `Query ID`.
6. Activate Web Services, see here: [IBKR Web Services](https://www.ibkrguides.com/clientportal/performanceandstatements/flex-web-service.htm).
7. Configure the `TOKEN`, `QUERY_ID`, and other required environment variables in a `.env` file.

## Contributing

Contributions are welcome! 

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For questions or feedback, please open an issue in the repository.
