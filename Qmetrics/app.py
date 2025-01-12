# app.py

import pandas as pd
import streamlit as st
import os
import pickle
from config import configure_page, inject_custom_css
from data_processing import format_trade_data
from sidebar import render_sidebar
from individual_strategy_tab import render_individual_strategy_tab
from portfolio_tab import render_portfolio_tab
from monte_carlo_tab import render_monte_carlo_tab
from strategy_correlation_tab import render_strategy_correlation_tab
from strategy_comparison_tab import render_strategy_comparison_tab
from styles import custom_css

SAVE_FOLDER_PATH = './saved_strategies'

# Ensure save folder exists
os.makedirs(SAVE_FOLDER_PATH, exist_ok=True)

# Load previously saved strategies
def load_saved_strategies():
    strategies = {}
    if os.path.exists(SAVE_FOLDER_PATH):
        for file_name in os.listdir(SAVE_FOLDER_PATH):
            file_path = os.path.join(SAVE_FOLDER_PATH, file_name)
            try:
                with open(file_path, 'rb') as f:
                    data = pickle.load(f)
                    strategies[file_name] = data
            except Exception as e:
                st.error(f"Error loading strategy {file_name}: {e}")
    return strategies

# Display saved strategies in a styled box
def display_saved_strategies(strategies):
    if strategies:
        st.markdown(
            """
            <style>
            .strategy-box {
                border-radius: 8px;
                padding: 15px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.15);
                background-color: #262730;
                margin-bottom: 20px;
            }
            .strategy-title {
                font-weight: bold;
                margin-bottom: 10px;
                font-size: 1.1em;
            }
            .strategy-item {
                background-color: #0E1117;
                padding: 10px;
                margin: 5px 0;
                border-radius: 5px;
                font-size: 0.9em;
            }
            </style>
            """, 
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="strategy-box">'
            '<div class="strategy-title">Strategy</div>' +
            ''.join([f'<div class="strategy-item">{name}</div>' for name in strategies.keys()]) +
            '</div>',
            unsafe_allow_html=True
        )

# Configure and style the Streamlit page
configure_page()
inject_custom_css()
st.title("📈 Professional Trading Performance Metrics Dashboard")
saved_strategies = load_saved_strategies()
display_saved_strategies(saved_strategies)
uploaded_files = st.sidebar.file_uploader(
    "📂 Upload your trading CSV/XLSX files",
    type=["csv", "xlsx"],  # <-- now includes XLSX
    accept_multiple_files=True,
    help="Upload one or more CSV or XLSX files containing your trading data."
)

# Process and store uploaded strategies
if uploaded_files:
    strategies = {**saved_strategies}  # Start with saved strategies
    for uploaded_file in uploaded_files:
        try:
            # 1) Conditionally read CSV or XLSX
            if uploaded_file.name.lower().endswith('.csv'):
                raw_trades = pd.read_csv(uploaded_file)
            elif uploaded_file.name.lower().endswith('.xlsx'):
                raw_trades = pd.read_excel(uploaded_file, engine='openpyxl')
            else:
                raise ValueError("Unsupported file format. Please upload .csv or .xlsx")

            # 2) Pass to format_trade_data as before
            formatted_trades = format_trade_data(raw_trades, uploaded_file.name)
            if formatted_trades is not None:
                strategies[uploaded_file.name] = formatted_trades
        except Exception as e:
            st.error(f"An error occurred while processing file {uploaded_file.name}: {e}")
else:
    strategies = saved_strategies

if strategies:
    portfolio_selection = render_sidebar(strategies)

    # Create Tabs for Each Section
    tabs = st.tabs([
        "Individual Strategy",
        "Portfolio",
        "Monte Carlo Simulation",
        "Strategy Correlation",
        "Strategy Comparison",
    ])

    # Individual Strategy Tab
    with tabs[0]:
        render_individual_strategy_tab(strategies)

    with tabs[1]:
        render_portfolio_tab(strategies, portfolio_selection)

    with tabs[2]:
        render_monte_carlo_tab(strategies, portfolio_selection)

    with tabs[3]:
        render_strategy_correlation_tab(strategies)

    with tabs[4]:
        render_strategy_comparison_tab(strategies)

