# Qmetrics

![GitHub license](https://img.shields.io/github/license/Zentch-Q/Qmetrics.svg)

**Qmetrics** is a comprehensive TradingView analyzer designed to evaluate and enhance your trading strategies. By analyzing your list of trades exported from TradingView, Qmetrics provides insightful metrics and visualizations to help you make informed trading decisions.

## Table of Contents

- [Features](#features)
- [Supported Data Formats](#supported-data-formats)
- [Installation](#installation)
- [Usage](#usage)
- [Supported Data Frame Structure](#supported-data-frame-structure)
- [Dependencies](#dependencies)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Features

Qmetrics offers a range of functionalities tailored to evaluate and improve your trading strategies:

1. **Individual Strategy Performance**
   - Analyze the performance metrics of individual trading strategies.
   - Visualize cumulative profits over time or by trade.
   - Examine monthly performance in both dollar and percentage terms.

2. **Portfolio Performance**
   - Aggregate multiple strategies into a single portfolio.
   - Adjust risk per trade for each strategy to optimize portfolio performance.
   - View combined performance metrics and equity curves.
   - Conduct monthly performance analysis for the entire portfolio.

3. **Monte Carlo Simulation** (Currently Testing)
   - Assess the robustness of trading strategies through simulations.
   - Generate multiple trade sequences to understand potential outcomes.
   - Visualize simulation results with interactive charts and metrics.

4. **Strategy Correlation Analysis**
   - Examine the correlations between different trading strategies.
   - Visualize correlations through heatmaps and correlation matrices.
   - Interpret correlation coefficients to inform diversification strategies.

5. **Strategy Comparison**
   - Compare the performance metrics of two selected trading strategies side by side.
   - Analyze cumulative profits and monthly performances concurrently.
   - Make informed decisions based on comparative insights.

6. **Robustness Test**
   - Test the resilience of strategies under various market conditions.
   - Set thresholds for out-of-sample (OOS) performance metrics.
   - Evaluate strategies based on predefined robustness criteria.

## Supported Data Formats

Qmetrics currently supports the following file formats for importing trading data:

- **CSV (`.csv`)**
- **Excel (`.xlsx`)**

> **Note:** Qmetrics is specifically built to work with trade exports from TradingView. However, it may also work with other trading platforms that export data with similar column formats. Ensure that your exported data includes the required columns as outlined in the [Supported Data Frame Structure](#supported-data-frame-structure) section.

## Installation

Follow these steps to set up Qmetrics on your local machine:

1. **Clone the Repository**

   ```bash
   git clone https://github.com/Zentch-Q/Qmetrics.git
   cd Qmetrics
