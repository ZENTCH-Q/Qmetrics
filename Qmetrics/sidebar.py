# sidebar.py

import streamlit as st
import os
import pickle  # For saving the whole DataFrame as binary
from metrics_calculation import calculate_metrics

SAVE_FOLDER_PATH = './saved_strategies'

# Save selected strategies to individual files
def save_selected_strategies(selected_strategies, strategies):
    os.makedirs(SAVE_FOLDER_PATH, exist_ok=True)
    for strategy_name in selected_strategies:
        file_path = os.path.join(SAVE_FOLDER_PATH, f"{strategy_name}.pkl")
        try:
            with open(file_path, 'wb') as f:
                pickle.dump(strategies[strategy_name], f)
        except Exception as e:
            st.error(f"Error saving strategy {strategy_name}: {e}")
    st.success("Selected strategies saved successfully!")

def render_sidebar(strategies):
    """Render sidebar for selecting and viewing strategies."""
    st.sidebar.header("🔧 Strategy Selection")

    # Checkbox to filter out strategies with SQN < 2
    filter_by_sqn = st.sidebar.checkbox("Auto-deselect strategies with SQN < 2")

    # Initialize session state for checkboxes
    for filename in strategies.keys():
        if f"checkbox_{filename}" not in st.session_state:
            st.session_state[f"checkbox_{filename}"] = True

    # Sidebar: "Select All" Checkbox
    if "select_all" not in st.session_state:
        st.session_state.select_all = False

    def toggle_select_all():
        select_all = st.session_state.select_all
        for filename in strategies.keys():
            st.session_state[f"checkbox_{filename}"] = select_all

    def update_select_all():
        all_checked = all(st.session_state[f"checkbox_{filename}"] for filename in strategies.keys())
        st.session_state.select_all = all_checked

    st.sidebar.checkbox("Select All", key="select_all", on_change=toggle_select_all)

        # Automatically deselect strategies with SQN < 2 if the filter is enabled
    if filter_by_sqn:
        for filename in strategies.keys():
            # Calculate the SQN of each strategy
            strategy_metrics, _ = calculate_metrics(strategies[filename], 'Entry Date', initial_balance=10000)
            sqn_value = float(strategy_metrics['Strategy Quality Number'].split()[0])  # Extract SQN value

            # Deselect strategies with SQN < 1
            if sqn_value < 2:
                st.session_state[f"checkbox_{filename}"] = False

    # Sidebar: Individual Strategy Checkboxes
    for filename in strategies.keys():
        st.sidebar.checkbox(
            filename,
            key=f"checkbox_{filename}",
            on_change=update_select_all
        )

    # Save Selection Button
    if st.sidebar.button("Save Strategy Selection"):
        selected_strategies = [filename for filename in strategies.keys() if st.session_state[f"checkbox_{filename}"]]
        save_selected_strategies(selected_strategies, strategies)

    # Get selected strategies
    portfolio_selection = [filename for filename in strategies.keys() if st.session_state[f"checkbox_{filename}"]]
    return portfolio_selection
