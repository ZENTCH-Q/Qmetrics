import pandas as pd
import numpy as np
import streamlit as st
from monte_carlo import monte_carlo_simulation
from visualize import plot_monte_carlo, display_monte_carlo_metrics

def render_monte_carlo_tab(strategies, portfolio_selection):
    """Render the Monte Carlo Simulation tab in the Streamlit app."""
    st.header("🎲 Monte Carlo Simulation")

    # Strategy selection for simulation
    st.write("### Select Strategies for Monte Carlo Simulation:")
    selected_monte_carlo_strategies = st.multiselect(
        "Choose strategies to run the Monte Carlo simulation on:", 
        options=portfolio_selection, 
        default=portfolio_selection
    )

    if selected_monte_carlo_strategies:
        # Combine selected strategies' trades
        selected_trades = pd.concat([strategies[s] for s in selected_monte_carlo_strategies])

        # Ensure that the 'Entry Date' column is in datetime format
        if 'Entry Date' in selected_trades.columns:
            selected_trades['Entry Date'] = pd.to_datetime(selected_trades['Entry Date'], errors='coerce')

        # Sort the combined trades by 'Entry Date' in chronological order
        selected_trades = selected_trades.sort_values(by='Entry Date')

        initial_balance = st.number_input("Set the initial balance (USD):", min_value=0.0, value=10000.0)

        # Display combined trades
        st.write(f"### Combined Trades for Selected Strategies ({', '.join(selected_monte_carlo_strategies)})")
        st.dataframe(selected_trades)

        # Run Monte Carlo Simulation
        num_simulations = st.number_input("Number of Simulations:", min_value=100, max_value=10000, value=1000, step=100)
        if st.button("Run Monte Carlo Simulation"):
            with st.spinner('Running Monte Carlo Simulation...'):
                simulated_trades = monte_carlo_simulation(selected_trades, num_simulations)
                cumulative_profits = np.cumsum(simulated_trades, axis=1) + initial_balance
                sim_mean_curve = cumulative_profits.mean(axis=0)
                sim_lower = np.percentile(cumulative_profits, 5, axis=0)
                sim_upper = np.percentile(cumulative_profits, 95, axis=0)

                # Ensure the 'Entry Date' is properly used to define the date range
                if not pd.api.types.is_datetime64_any_dtype(selected_trades['Entry Date']):
                    st.error("Error: 'Entry Date' is not in datetime format.")
                    return

                # Use the correct datetime format for simulation dates
                simulation_dates = pd.date_range(start=selected_trades['Entry Date'].min(), periods=len(sim_mean_curve), freq='D')
                simulation_df = pd.DataFrame(cumulative_profits, columns=simulation_dates)

                # Plot Monte Carlo results
                plot_monte_carlo(simulation_df, sim_mean_curve, sim_lower, sim_upper)

                # Display Monte Carlo Metrics Table
                display_monte_carlo_metrics(cumulative_profits, initial_balance)
