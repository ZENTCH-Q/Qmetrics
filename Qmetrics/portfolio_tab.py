# portfolio_tab.py

import pandas as pd
import numpy as np
import streamlit as st
from metrics_calculation import calculate_metrics
from monte_carlo import monte_carlo_simulation
from visualize import (
    plot_cumulative_profit,
    plot_monte_carlo,
    display_monte_carlo_metrics
)

def import_portfolio_file():
    """Handles file upload and returns a DataFrame."""
    uploaded_file = st.file_uploader("Upload Portfolio Export File", type=["csv"])
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.success("File uploaded successfully!")
            return df
        except Exception as e:
            st.error(f"Error loading file: {e}")
    return None

def calculate_portfolio_sharpe_ratio(combined_portfolio_trades, initial_balance=10000, annual_risk_free_rate=0.02):
    combined_portfolio_trades['Entry Date'] = pd.to_datetime(combined_portfolio_trades['Entry Date'])
    daily_profit = combined_portfolio_trades.groupby('Entry Date', observed=False)['Net Profit'].sum().reset_index()
    # FIX #2: explicitly specify `observed=False` if you rely on old grouping behavior 
    #   (the future default will be True)
    
    daily_profit['Cumulative Profit'] = daily_profit['Net Profit'].cumsum() + initial_balance
    daily_profit['Daily Return'] = daily_profit['Cumulative Profit'].pct_change().fillna(0)
    daily_risk_free_rate = annual_risk_free_rate / 252
    daily_profit['Excess Daily Return'] = daily_profit['Daily Return'] - daily_risk_free_rate
    mean_excess_return = daily_profit['Excess Daily Return'].mean()
    std_excess_return = daily_profit['Excess Daily Return'].std()
    sharpe_ratio = (mean_excess_return / std_excess_return) * np.sqrt(252) if std_excess_return != 0 else 0
    return sharpe_ratio, daily_profit

def adjust_risk_per_trade(portfolio_trades, strategies, initial_balance, default_risk_per_trade=100.0):
    st.markdown("## Risk Management Settings")
    st.markdown("Adjust the risk per trade for each strategy below:")

    adjusted_trades_list = []
    for strategy in strategies:
        with st.expander(f"Strategy: {strategy}"):
            risk_option = st.selectbox(
                f"Risk Adjustment for {strategy}:",
                options=["Fixed Amount ($)", "Percentage (%)"],
                key=f"risk_option_{strategy}"
            )
            if risk_option == "Fixed Amount ($)":
                desired_risk = st.number_input(
                    f"Desired risk per trade for {strategy} (USD):",
                    min_value=0.0,
                    value=default_risk_per_trade,
                    key=f"fixed_risk_{strategy}"
                )
                scaling_factor = desired_risk / default_risk_per_trade if default_risk_per_trade != 0 else 1.0
            else:
                desired_risk_pct = st.number_input(
                    f"Desired risk per trade for {strategy} (% of initial balance):",
                    min_value=0.0,
                    max_value=100.0,
                    value=1.0,
                    key=f"pct_risk_{strategy}"
                )
                desired_risk = initial_balance * (desired_risk_pct / 100.0)
                scaling_factor = desired_risk / default_risk_per_trade if default_risk_per_trade != 0 else 1.0

            strategy_trades = portfolio_trades[portfolio_trades['Strategy'] == strategy].copy()
            strategy_trades['Net Profit'] = strategy_trades['Net Profit'] * scaling_factor
            adjusted_trades_list.append(strategy_trades)

    if adjusted_trades_list:
        adjusted_portfolio_trades = pd.concat(adjusted_trades_list, ignore_index=True)
    else:
        adjusted_portfolio_trades = portfolio_trades.copy()

    return adjusted_portfolio_trades

def monthly_performance_table(df, date_column, initial_balance, mode="Dollar ($)"):
    """Display the monthly performance table with a toggle between Dollar and Percentage view."""
    # Ensure the date column is in datetime format
    df[date_column] = pd.to_datetime(df[date_column])
    
    # Extract Year, Month, and Month Number
    df['Year'] = df[date_column].dt.year.astype(str)  # Convert year to string for grouping
    df['Month'] = df[date_column].dt.month_name().str.slice(stop=3)    # Short month name for readability
    df['Month_Num'] = df[date_column].dt.month       # Numeric month for sorting
    
    # Group by Year and Month_Num to calculate monthly profit
    monthly_profit = df.groupby(['Year', 'Month_Num', 'Month'])['Net Profit'].sum().reset_index()
    
    # Pivot the table to have months as columns
    monthly_pivot = monthly_profit.pivot_table(
        index=['Year'],
        columns='Month',
        values='Net Profit',
        fill_value=0
    )
    
    # Ensure months are ordered correctly
    # Create a list of month names in order
    month_order = [
        'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
    ]
    # Reindex the columns to ensure correct order
    monthly_pivot = monthly_pivot.reindex(columns=month_order, fill_value=0)
    
    # Calculate YTD (Year-to-Date) performance for each year
    monthly_pivot['YTD'] = monthly_pivot.sum(axis=1)
    
    # Convert to percentage if selected
    if mode == "Percentage (%)":
        monthly_pivot = (monthly_pivot / initial_balance) * 100
    
    # Reset index to turn 'Year' back into a column
    monthly_pivot = monthly_pivot.reset_index()
    
    # Format the values for display
    if mode == "Dollar ($)":
        formatted_performance = monthly_pivot.copy()
        for col in formatted_performance.columns:
            if col != 'Year':
                formatted_performance[col] = formatted_performance[col].apply(lambda x: f"${x:,.2f}")
    else:
        formatted_performance = monthly_pivot.copy()
        for col in formatted_performance.columns:
            if col != 'Year':
                formatted_performance[col] = formatted_performance[col].apply(lambda x: f"{x:.2f}%")
    
    # Display the table using st.dataframe for size control
    st.dataframe(
        formatted_performance,
        width=1000,
        height=min(400, len(formatted_performance) * 35 + 40)
    )

def render_portfolio_tab(strategies, portfolio_selection):
    """Render the Portfolio tab in the Streamlit app."""
    st.header("📊 Portfolio Performance Overview")
    portfolio_file = import_portfolio_file()

    if portfolio_file is not None:
        st.subheader("🔍 Imported Portfolio Data")
        st.dataframe(portfolio_file)

        initial_balance = st.number_input(
            "💰 Set the Initial Balance for the Portfolio (USD):",
            min_value=0.0,
            value=10000.0,
            key='portfolio_initial_balance'
        )

        if 'Strategy' not in portfolio_file.columns:
            st.error("❌ The uploaded portfolio file must contain a 'Strategy' column.")
            return

        unique_strategies = portfolio_file['Strategy'].unique().tolist()
        adjusted_portfolio_trades = adjust_risk_per_trade(
            portfolio_trades=portfolio_file,
            strategies=unique_strategies,
            initial_balance=initial_balance
        )

        st.subheader("✅ Adjusted Portfolio Data")
        st.dataframe(adjusted_portfolio_trades)

        metrics, equity_curve = calculate_metrics(
            adjusted_portfolio_trades,
            'Entry Date',
            initial_balance,
            include_buy_and_hold=False
        )
        sharpe_ratio, daily_profit = calculate_portfolio_sharpe_ratio(
            adjusted_portfolio_trades,
            initial_balance
        )
        st.metric("📈 Sharpe Ratio (Adjusted Portfolio)", f"{sharpe_ratio:.2f}")

        st.subheader("📊 Performance Metrics")
        metrics_cols = st.columns(5)
        for idx, (metric, value) in enumerate(metrics.items()):
            if isinstance(value, (int, float, np.number)):
                display_value = f"{value:.2f}"
            else:
                display_value = str(value)
            metrics_cols[idx % 5].metric(metric, display_value)

        st.subheader("📈 Cumulative Profit Over Time/Trade (Adjusted Portfolio)")
        view_mode = st.radio(
            "📊 View Cumulative Profit By:",
            options=["Time", "Trade"],
            horizontal=True,
            key="imported_view_mode"
        )
        plot_cumulative_profit(equity_curve, 'Entry Date', "Adjusted Portfolio", view_mode)

        st.subheader("📅 Monthly Performance (Adjusted Portfolio)")
        performance_mode = st.radio(
            "🔍 Select the View Mode:",
            ["Dollar ($)", "Percentage (%)"],
            horizontal=True,
            key="imported_performance_mode"
        )
        monthly_performance_table(
            adjusted_portfolio_trades,
            'Entry Date',
            initial_balance,
            performance_mode
        )

    if portfolio_selection:
        st.subheader("🎯 Selected Strategies in the Portfolio")
        combined_trades = [strategies[s].copy().assign(Strategy=s) for s in portfolio_selection]
        selected_portfolio_trades = pd.concat(combined_trades, ignore_index=True)
        selected_portfolio_trades['Entry Date'] = pd.to_datetime(selected_portfolio_trades['Entry Date'], errors='coerce')
        selected_portfolio_trades.sort_values(by='Entry Date', inplace=True)

        csv = selected_portfolio_trades.to_csv(index=False).encode('utf-8')
        st.download_button(label="📥 Download Combined Strategy", data=csv, file_name='combined_strategy.csv')

        initial_balance_selected = st.number_input(
            "💰 Set the Initial Balance for the Portfolio (USD):",
            min_value=0.0,
            value=10000.0,
            key="selected_initial_balance"
        )

        if 'Strategy' not in selected_portfolio_trades.columns:
            st.error("❌ The selected portfolio trades must contain a 'Strategy' column.")
            return

        unique_strategies_selected = selected_portfolio_trades['Strategy'].unique().tolist()
        adjusted_selected_trades = adjust_risk_per_trade(
            portfolio_trades=selected_portfolio_trades,
            strategies=unique_strategies_selected,
            initial_balance=initial_balance_selected
        )

        st.subheader("✅ Adjusted Selected Portfolio Data")
        st.dataframe(adjusted_selected_trades)

        metrics_selected, equity_curve_selected = calculate_metrics(
            adjusted_selected_trades,
            'Entry Date',
            initial_balance_selected,
            include_buy_and_hold=False
        )
        sharpe_ratio_selected, daily_profit_selected = calculate_portfolio_sharpe_ratio(
            adjusted_selected_trades,
            initial_balance_selected
        )
        st.metric("📈 Sharpe Ratio (Adjusted Selected Portfolio)", f"{sharpe_ratio_selected:.2f}")

        st.subheader("📊 Performance Metrics")
        metrics_selected_cols = st.columns(5)
        for idx, (metric, value) in enumerate(metrics_selected.items()):
            if isinstance(value, (int, float, np.number)):
                display_value = f"{value:.2f}"
            else:
                display_value = str(value)
            metrics_selected_cols[idx % 5].metric(metric, display_value)

        st.subheader("📈 Cumulative Profit Over Time/Trade (Adjusted Selected Portfolio)")
        view_mode_selected = st.radio(
            "📊 View Cumulative Profit By:",
            options=["Time", "Trade"],
            horizontal=True,
            key="selected_view_mode"
        )
        plot_cumulative_profit(equity_curve_selected, 'Entry Date', "Adjusted Selected Portfolio", view_mode_selected)

        st.subheader("📅 Monthly Performance (Adjusted Selected Portfolio)")
        performance_mode_selected = st.radio(
            "🔍 Select the View Mode:",
            ["Dollar ($)", "Percentage (%)"],
            horizontal=True,
            key="selected_performance_mode"
        )
        monthly_performance_table(
            adjusted_selected_trades,
            'Entry Date',
            initial_balance_selected,
            performance_mode_selected
        )
