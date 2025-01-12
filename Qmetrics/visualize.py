# visualize.py

from monte_carlo import calculate_max_drawdown  # Add this import statement

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import random

def plot_cumulative_profit(equity_curve: pd.DataFrame, date_column: str, strategy_name: str, view_mode: str = "Time"):
    """Plot cumulative profit using Plotly, either by time or by trade."""
    
    profit_column = 'Net Profit'  # Change this if the name is different

    if view_mode == "Time":
        # Plot cumulative profit over time (Date)
        fig = px.line(
            equity_curve.reset_index(),
            x=date_column,
            y='Cumulative Profit',
            title=f"Cumulative Profit Over Time for {strategy_name}",
            labels={'Cumulative Profit': 'Cumulative Profit (USD)', date_column: 'Date'},
            template='plotly_dark'
        )
    elif view_mode == "Trade":
        # Reset index to create a clean sequence of trade numbers
        equity_curve = equity_curve.reset_index(drop=True)

        # Calculate cumulative profit by summing profits over each trade
        equity_curve['Cumulative Profit'] = equity_curve[profit_column].cumsum()

        # Create a new 'Trade Number' column for x-axis
        equity_curve['Trade Number'] = equity_curve.index + 1

        # Plot cumulative profit by trade number
        fig = px.line(
            equity_curve,
            x='Trade Number',  # Use trade number as x-axis
            y='Cumulative Profit',
            title=f"Cumulative Profit by Trade for {strategy_name}",
            labels={'Cumulative Profit': 'Cumulative Profit (USD)', 'Trade Number': 'Trade Number'},
            template='plotly_dark'
        )

    # Adding an annotation (bubble box) at the highest cumulative profit point
    max_cumulative_profit = equity_curve['Cumulative Profit'].max()
    max_cumulative_index = equity_curve[equity_curve['Cumulative Profit'] == max_cumulative_profit].index[0]

    fig.add_annotation(
        x=max_cumulative_index, 
        y=max_cumulative_profit,
        text=f"Highest Profit: ${max_cumulative_profit:,.2f}",
        showarrow=True,
        arrowhead=2,
        ax=0,
        ay=-40,
        bgcolor="rgba(0,0,100,0.7)",
        font=dict(size=12)
    )

    # Show the chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)


def plot_monte_carlo(simulation_df: pd.DataFrame, sim_mean_curve, sim_lower, sim_upper):
    """Plot Monte Carlo simulation results with higher opacity."""
    fig_mc = go.Figure()

    # Plot individual simulations with higher opacity and random colors
    for i in range(min(100, len(simulation_df))):
        random_color = f"rgba({random.randint(0,255)},{random.randint(0,255)},{random.randint(0,255)},0.4)"  # Higher opacity
        fig_mc.add_trace(go.Scatter(
            x=simulation_df.columns,
            y=simulation_df.iloc[i],
            mode='lines',
            line=dict(color=random_color, width=1),
            showlegend=False
        ))

    # Plot mean trajectory and confidence interval
    fig_mc.add_trace(go.Scatter(x=simulation_df.columns, y=sim_mean_curve, mode='lines', line=dict(color='red', width=2), name='Mean'))
    fig_mc.add_trace(go.Scatter(x=simulation_df.columns, y=sim_upper, mode='lines', line=dict(color='grey', width=1), name='95th Percentile'))
    fig_mc.add_trace(go.Scatter(x=simulation_df.columns, y=sim_lower, mode='lines', line=dict(color='grey', width=1), fill='tonexty', fillcolor='rgba(128,128,128,0.2)', name='5th Percentile'))

    fig_mc.update_layout(title="Monte Carlo Simulation of Portfolio", xaxis_title="Date", yaxis_title="Cumulative Profit (USD)", template='plotly_dark', height=600)
    st.plotly_chart(fig_mc, use_container_width=True)

def monthly_performance_table(trades: pd.DataFrame, date_column: str, initial_balance: float, mode: str):
    """Display the monthly performance table with a toggle between Dollar and Percentage view."""
    # Ensure the date column is in datetime format
    trades[date_column] = pd.to_datetime(trades[date_column])
    
    # Extract Year, Month, and Month Number
    trades['Year'] = trades[date_column].dt.year.astype(str)  # Convert year to string for grouping
    trades['Month'] = trades[date_column].dt.month_name()    # Full month name for readability
    trades['Month_Num'] = trades[date_column].dt.month       # Numeric month for sorting
    
    # Group by Year and Month_Num to calculate monthly profit
    monthly_performance = trades.groupby(['Year', 'Month_Num', 'Month'])['Profit'].sum().reset_index()
    
    # Pivot the table to have months as columns
    monthly_pivot = monthly_performance.pivot_table(
        index=['Year'],
        columns='Month',
        values='Profit',
        fill_value=0
    )
    
    # Ensure months are ordered correctly
    # Create a list of month names in order
    month_order = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
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
    
    # Display the table using Streamlit
    st.dataframe(
        formatted_performance,
        width=1000,
        height=min(400, len(formatted_performance) * 35 + 40)
    )


def display_monte_carlo_metrics(cumulative_profits: np.ndarray, initial_balance: float):
    """Display Monte Carlo simulation metrics in a table format."""
    # Calculate performance metrics
    confidence_levels = [50, 70, 80, 90, 95, 98, 100]  # Confidence levels for the table
    results = []

    # Calculate Net Profit and other metrics for each confidence level
    for level in confidence_levels:
        max_dd = calculate_max_drawdown(cumulative_profits)
        net_profit = np.percentile(cumulative_profits[:, -1] - initial_balance, level)
        max_drawdown = np.percentile(max_dd, level)
        return_dd_ratio = net_profit / max_drawdown if max_drawdown != 0 else np.inf
        r_expectancy = net_profit / initial_balance  # Simplified R Expectancy
        annual_return = ((net_profit + initial_balance) / initial_balance) ** (1 / len(cumulative_profits)) - 1

        results.append([
            f"{level}%",  # Confidence Level
            f"${net_profit:,.2f}",  # Net Profit
            f"{r_expectancy:.2f} R",  # R Expectancy
            f"{annual_return * 100:.2f}%",  # Annual Return Percentage
            f"${max_drawdown:,.2f}",  # Max Drawdown
            f"{return_dd_ratio:.2f}",  # Return/Drawdown Ratio
        ])

    # Create DataFrame for display
    metrics_df = pd.DataFrame(results, columns=[
        'Confidence Level', 'Net Profit', 'R Exp', 'AR%', 'Max DD', 'Ret/DD'
    ])

    # Display the table in Streamlit
    st.table(metrics_df)
