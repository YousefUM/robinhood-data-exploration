# robinhood-data-exploration
An initial data science project to explore personal Robinhood trading history. Focuses on data cleaning, basic P/L calculation, and early performance insights. (Future iterations planned!)
## Version 1 Accomplishments: Core Trading Analysis

This initial version focuses on extracting and analyzing realized profit/loss from personal Robinhood trading history.

**Key achievements include:**

* **Data Ingestion & Robust Cleaning:** Processed raw CSV transaction data, handling inconsistencies and converting messy strings (e.g., "$12.34", "($5.00)") into clean numeric and datetime formats.
* **Core Trading Data Isolation:** Systematically filtered raw transactions to focus exclusively on `Buy` and `Sell` orders. This was crucial because other transaction codes (like `CDIV` for dividends, `INT` for interest, or `ACH` for transfers) contain `NaN` values for `Quantity` and `Price`, as they don't represent security trades, and including them would distort trade-specific performance metrics.
* **FIFO Profit/Loss Calculation:** Implemented a First-In, First-Out (FIFO) methodology to accurately match buy and sell orders, calculating `realized_profit_loss`, `cost_basis`, and `holding_period_days` for every closed position.
* **Key Performance Metrics:** Derived overall trading performance (e.g., total P/L, win rate, average holding periods) and identified top/bottom performing instruments.
* **Visualizations:** Generated essential plots, including cumulative P/L over time, instrument performance breakdowns, and holding period distributions (notably, observing longer holds for losing trades).
* **Interactive Dashboard (Streamlit):** Packaged all insights into a deployable, interactive web application, making the analysis accessible and shareable.
