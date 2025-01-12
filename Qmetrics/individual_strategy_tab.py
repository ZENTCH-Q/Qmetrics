# individual_strategy_tab.py

import pandas as pd
import numpy as np
import streamlit as st
from metrics_calculation import calculate_metrics
from visualize import plot_cumulative_profit, plot_monte_carlo, monthly_performance_table, display_monte_carlo_metrics

def render_individual_strategy_tab(strategies):
    """Render the Individual Strategy tab in the Streamlit app."""
    st.header("📊 Individual Strategy Performance")
    selected_strategy = st.selectbox("Select a strategy to view its performance:", options=["None"] + list(strategies.keys()))

    if selected_strategy != "None":
        strategy_trades = strategies[selected_strategy]
        date_column = next((col for col in strategy_trades.columns if col in ['Entry Date', 'Exit Date', 'Trade Date', 'Date/Time']), None)

        if date_column:
            initial_balance = st.number_input(
                f"Set the initial balance for {selected_strategy} (USD):",
                min_value=0.0,
                value=10000.0,
                key=f'individual_strategy_initial_balance_{selected_strategy}'
            )
            metrics, equity_curve = calculate_metrics(strategy_trades, date_column, initial_balance)

            # Display metrics in columns (metrics still appear above the chart)
            cols = st.columns(5)
            for idx, (metric, value) in enumerate(metrics.items()):
                cols[idx % 5].metric(metric, value)

            # Move the view mode toggle **right before the cumulative profit chart**
            st.write("### 📈 Cumulative Profit Over Time")
            view_mode = st.radio("View cumulative profit by:", options=["Time", "Trade"], horizontal=True, key=f'view_mode_individual_{selected_strategy}')

            # Display cumulative profit chart with chosen view mode
            plot_cumulative_profit(equity_curve, date_column, selected_strategy, view_mode)

            # Monthly Performance Table (this can stay as is)
            st.write("### 📅 Monthly Performance ($ / %)")
            performance_mode = st.radio("Select the view mode:", ["Dollar ($)", "Percentage (%)"], horizontal=True, key=f'performance_mode_individual_{selected_strategy}')
            monthly_performance_table(strategy_trades, date_column, initial_balance, performance_mode)
