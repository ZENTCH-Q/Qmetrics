# strategy_comparison_tab.py

import pandas as pd
import streamlit as st
from metrics_calculation import calculate_metrics
from visualize import monthly_performance_table
import plotly.express as px

def render_strategy_comparison_tab(strategies):
    """Render the Strategy Comparison tab in the Streamlit app."""
    st.header("📈 Strategy Comparison")

    if not strategies:
        st.warning("Please upload and select strategies to compare.")
        return

    # Select two strategies to compare
    strategy_names = list(strategies.keys())
    col1, col2 = st.columns(2)
    with col1:
        strategy1_name = st.selectbox("Select the first strategy:", strategy_names, key="strategy1")
    with col2:
        strategy2_name = st.selectbox("Select the second strategy:", strategy_names, key="strategy2")

    if strategy1_name == strategy2_name:
        st.warning("Please select two different strategies to compare.")
        return

    # Retrieve the data for the selected strategies
    strategy1_data = strategies[strategy1_name]
    strategy2_data = strategies[strategy2_name]

    # Determine the date column
    date_columns = ['Entry Date', 'Exit Date', 'Trade Date', 'Date/Time']
    date_column1 = next((col for col in strategy1_data.columns if col in date_columns), None)
    date_column2 = next((col for col in strategy2_data.columns if col in date_columns), None)

    if not date_column1 or not date_column2:
        st.error("One or both strategies do not have a valid date column.")
        return

    # Set initial balance with unique key
    initial_balance = st.number_input(
        "Set the initial balance (USD):",
        min_value=0.0,
        value=10000.0,
        key='strategy_comparison_initial_balance'
    )

    # Calculate metrics for both strategies
    metrics1, equity_curve1 = calculate_metrics(strategy1_data, date_column1, initial_balance)
    metrics2, equity_curve2 = calculate_metrics(strategy2_data, date_column2, initial_balance)

    # Reset index to ensure 'Date' is a column
    equity_curve1.reset_index(inplace=True)
    equity_curve2.reset_index(inplace=True)

    # Display metrics side by side
    st.write("### 📊 Performance Metrics Comparison")
    col1, col2 = st.columns(2)

    # Function to display metrics in a grid
    def display_metrics_grid(metrics_dict):
        metrics_items = list(metrics_dict.items())
        num_metrics = len(metrics_items)
        num_columns = 2  # Adjust this value as needed
        rows = (num_metrics + num_columns - 1) // num_columns

        for row in range(rows):
            cols = st.columns(num_columns)
            for col_index in range(num_columns):
                metric_index = row * num_columns + col_index
                if metric_index < num_metrics:
                    metric_name, metric_value = metrics_items[metric_index]
                    with cols[col_index]:
                        st.metric(metric_name, metric_value)
                else:
                    with cols[col_index]:
                        st.empty()

    with col1:
        st.subheader(f"{strategy1_name}")
        display_metrics_grid(metrics1)

    with col2:
        st.subheader(f"{strategy2_name}")
        display_metrics_grid(metrics2)

    # Display equity curves
    st.write("### 📈 Cumulative Profit Over Time")
    # Merge equity curves on date
    equity_curve1.rename(columns={date_column1: 'Date', 'Cumulative Profit': strategy1_name}, inplace=True)
    equity_curve2.rename(columns={date_column2: 'Date', 'Cumulative Profit': strategy2_name}, inplace=True)
    merged_equity = pd.merge(
        equity_curve1[['Date', strategy1_name]],
        equity_curve2[['Date', strategy2_name]],
        on='Date', how='outer'
    ).sort_values('Date').fillna(method='ffill')

    fig = px.line(
        merged_equity,
        x='Date',
        y=[strategy1_name, strategy2_name],
        labels={'value': 'Cumulative Profit', 'Date': 'Date'},
        title='Cumulative Profit Comparison'
    )
    st.plotly_chart(fig, use_container_width=True)

    # Monthly Performance Tables
    st.write("### 📅 Monthly Performance")
    performance_mode = st.radio("Select the view mode:", ["Dollar ($)", "Percentage (%)"], horizontal=True)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f"{strategy1_name}")
        monthly_performance_table(strategy1_data, date_column1, initial_balance, performance_mode)
    with col2:
        st.subheader(f"{strategy2_name}")
        monthly_performance_table(strategy2_data, date_column2, initial_balance, performance_mode)
