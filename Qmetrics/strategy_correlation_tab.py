import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
from metrics_calculation import calculate_metrics
from visualize import plot_cumulative_profit, monthly_performance_table

def render_strategy_correlation_tab(strategies, initial_balance=100000):
    """
    Render the Strategy Correlation tab in the Streamlit app.

    Parameters:
    - strategies (dict): A dictionary where keys are strategy names and values are pandas DataFrames containing
                         at least 'Entry Date' and 'Profit' columns.
    - initial_balance (float): The initial capital to calculate cumulative equity curves.
    """
    st.header("📊 Strategy Correlation Analysis")

    if not strategies:
        st.warning("Please upload and select strategies to view correlation analysis.")
        return

    # Display a multi-select box to choose strategies for correlation analysis
    selected_strategies = st.multiselect(
        "Choose strategies to analyze correlation:",
        options=list(strategies.keys()),
        default=list(strategies.keys())
    )

    if len(selected_strategies) < 2:
        st.warning("Please select at least two strategies to view correlation.")
        return

    # Initialize a dictionary to store cumulative returns for each strategy
    cumulative_returns = {}

    for strategy_name in selected_strategies:
        strategy_data = strategies[strategy_name].copy()

        # Ensure the date column is in datetime format
        if 'Entry Date' not in strategy_data.columns:
            st.error(f"Strategy '{strategy_name}' does not contain 'Entry Date' column.")
            return

        strategy_data['Entry Date'] = pd.to_datetime(strategy_data['Entry Date'])

        # Sort by date to ensure proper cumulative calculation
        strategy_data = strategy_data.sort_values('Entry Date')

        # Calculate cumulative profit
        strategy_data['Cumulative Profit'] = strategy_data['Profit'].cumsum()

        # Calculate cumulative equity curve
        strategy_data['Equity Curve'] = initial_balance + strategy_data['Cumulative Profit']

        # Calculate daily returns based on equity curve
        strategy_data['Daily Return'] = strategy_data['Equity Curve'].pct_change().fillna(0)

        # Set 'Entry Date' as the index
        strategy_data.set_index('Entry Date', inplace=True)

        # Store the daily returns
        cumulative_returns[strategy_name] = strategy_data['Daily Return']

    # Combine all strategies' daily returns into a single DataFrame
    combined_returns = pd.concat(cumulative_returns, axis=1, join='outer')

    # Sort the index to ensure chronological order
    combined_returns = combined_returns.sort_index()

    # Forward-fill missing values to maintain continuity
    combined_returns.fillna(method='ffill', inplace=True)

    # Replace any remaining NaNs with zeros (if any)
    combined_returns.fillna(0, inplace=True)

    # Calculate the correlation matrix
    correlation_matrix = combined_returns.corr()

    # Display correlation matrix as a table
    st.write("### Correlation Matrix")
    st.dataframe(correlation_matrix.style.background_gradient(cmap='RdBu', axis=1))

    # Add interpretation of correlation coefficients
    st.write("""
    **Interpretation of Correlation Coefficients:**

    - **+1.0 to +0.7**: Strong positive correlation _(less desirable for diversification)_
    - **+0.7 to +0.3**: Moderate positive correlation
    - **+0.3 to -0.3**: Weak or no correlation _(desirable for diversification)_
    - **-0.3 to -0.7**: Moderate negative correlation
    - **-0.7 to -1.0**: Strong negative correlation _(most desirable for diversification)_
    """)

    # Interactive heatmap using Plotly
    st.write("### Interactive Correlation Heatmap")
    fig = px.imshow(
        correlation_matrix,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="RdBu",
        origin="upper",
        labels={"color": "Correlation"},
        title="Strategy Correlation Heatmap",
        zmin=-1, zmax=1
    )

    # Add hover information for better interactivity
    fig.update_traces(
        hovertemplate="Strategy 1: %{x}<br>Strategy 2: %{y}<br>Correlation: %{z:.2f}"
    )

    fig.update_layout(
        xaxis_title="Strategies",
        yaxis_title="Strategies",
        coloraxis_colorbar=dict(title="Correlation Coefficient")
    )

    st.plotly_chart(fig, use_container_width=True)

def render_strategy_comparison_tab(strategies):
    """
    Render the Strategy Comparison tab in the Streamlit app.
    """
    st.header("📈 Strategy Comparison")

    if not strategies:
        st.warning("Please upload and select strategies to compare.")
        return

    # Select two strategies to compare
    strategy_names = list(strategies.keys())
    col1, col2 = st.columns(2)
    with col1:
        strategy1_name = st.selectbox("Select the first strategy:", ["None"] + strategy_names, key="strategy1")
    with col2:
        strategy2_name = st.selectbox("Select the second strategy:", ["None"] + strategy_names, key="strategy2")

    if "None" in [strategy1_name, strategy2_name]:
        st.warning("Please select two strategies to compare.")
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

    # Set initial balances
    initial_balance = st.number_input("Set the initial balance (USD):", min_value=0.0, value=10000.0)

    # Calculate metrics for both strategies
    metrics1, equity_curve1 = calculate_metrics(strategy1_data, date_column1, initial_balance)
    metrics2, equity_curve2 = calculate_metrics(strategy2_data, date_column2, initial_balance)

    # Display metrics side by side
    st.write("### 📊 Performance Metrics Comparison")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f"{strategy1_name}")
        for metric, value in metrics1.items():
            st.metric(metric, value)
    with col2:
        st.subheader(f"{strategy2_name}")
        for metric, value in metrics2.items():
            st.metric(metric, value)

    # Display equity curves
    st.write("### 📈 Cumulative Profit Over Time")
    fig = px.line(
        pd.DataFrame({
            date_column1: equity_curve1[date_column1],
            strategy1_name: equity_curve1['Cumulative Profit'],
            strategy2_name: equity_curve2['Cumulative Profit']
        }).set_index(date_column1),
        y=[strategy1_name, strategy2_name],
        labels={'value': 'Cumulative Profit', 'index': 'Date'},
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
