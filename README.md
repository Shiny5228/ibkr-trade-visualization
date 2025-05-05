# IBKR Trade Visualization

A tool for visualizing trade data from Interactive Brokers (IBKR). This project helps traders analyze their trading performance through intuitive and interactive visualizations. It is optimized for use with option trade data, especially 0DTE, exported from IBKR's trading platform.

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
- Generate various visualizations to analyze trading performance.
- User-friendly interface for exploring trade metrics.

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

1. Export your trade data from IBKR in the supported format.
2. Upload the data through the application's interface.
3. Explore the visualizations to gain insights into your trading performance.

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
