# IBKR Trade Visualization

A tool for visualizing trade data from Interactive Brokers (IBKR). This project helps traders analyze their trading performance through intuitive and interactive visualizations in a dash web app. Currently only working for data exported via IBKR Activity Flex Query.

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

- Import trade data from IBKR via Activity Flex Query Web Service.
- Generate various visualizations to analyze trading performance.
- User-friendly interface made with dash for exploring trade metrics.
- Filter for time period, assets and symbols.

<p align="center">
    <img src="https://github.com/user-attachments/assets/14ffebc5-bec2-4d34-8724-3e745d151d93" width="700">
</p>

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
2. Configure .env with token and query id from IBKR.
3. Explore the visualizations made with plotly in a dash web app to gain insights into your trading performance.

## Generating IB Reports

To generate the required IBKR Flex Query report:

1. Log in to your IBKR account.
2. Navigate to **Reports > Flex Queries**.
3. Create a new Flex Query with the following fields in **Trades**:
   - **Execution** At the top of the report
   - **Account ID**
   - **Description** 
   - **Asset Class**
   - **Underlying Symbol**
   - **Put/Call**
   - **Buy/Sell**
   - **Strike**
   - **Date/Time**
   - **Trade Date**
   - **Settle Date**
   - **Expiry**
   - **Open/Close**
   - **Notes**
   - **Cost Basis**
   - **Realized PnL**
   - **MTM P/L**
   - **IB Commission**
   - **FX Rate**
   - **Level of Detail**
4. At Delivery Configuration select **Format: XML** and **Period: Year to Date**.
5. Set decimal for dates to **None (no separator)**
6. Save the query and note the `Query ID`.
7. Activate Web Services, see here: [IBKR Web Services](https://www.ibkrguides.com/clientportal/performanceandstatements/flex-web-service.htm).
8. Configure the `TOKEN`, `QUERY_ID`, and other required environment variables in a `.env` file.
9. Run main.py

## Contributing

Contributions are welcome! 

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For questions or feedback, please open an issue in the repository.
