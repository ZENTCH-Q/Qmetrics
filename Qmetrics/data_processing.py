# data_processing.py
import pandas as pd
import streamlit as st

@st.cache_data
def format_trade_data(trade_data: pd.DataFrame, input_filename: str) -> pd.DataFrame:

    try:

        final_format_cols = [
            'Trade #', 'Type', 'lots', 'Entry Date', 'Exit Date', 
            'Entry Price', 'Exit Price', 'Profit', 'Total Commission', 'Net Profit'
        ]
        
        if all(col in trade_data.columns for col in final_format_cols):

            trade_data['Entry Date'] = pd.to_datetime(trade_data['Entry Date'], errors='coerce')
            trade_data['Exit Date'] = pd.to_datetime(trade_data['Exit Date'], errors='coerce')
            
            return trade_data[final_format_cols].copy()
        
        required_columns = ['Type', 'Trade #', 'Date/Time', 'Contracts']
        for column in required_columns:
            if column not in trade_data.columns:
                raise ValueError(
                    f"Column '{column}' not found in file: {input_filename}. "
                    "If your file is in final format, make sure all final columns exist."
                )

        # Dynamically identify the price and profit columns
        price_column = next((col for col in trade_data.columns if col.startswith('Price')), None)
        if price_column is None:
            raise ValueError(
                f"No 'Price' column found in file: {input_filename}. "
                "Make sure your file has a column starting with 'Price', or it's already in final format."
            )

        profit_column = next((col for col in trade_data.columns if 'Profit' in col), None)
        if profit_column is None:
            raise ValueError(
                f"Unable to detect correct 'Profit' column in file: {input_filename}."
            )

        # ~~~ existing old logic for pairing ~~~
        trade_data['Lots'] = trade_data['Contracts'] / 100000  # example
        trade_data['Commission'] = trade_data['Lots'] * 4.0     # example

        entries = trade_data[trade_data['Type'].str.contains('Entry', case=False, na=False)]
        exits = trade_data[trade_data['Type'].str.contains('Exit', case=False, na=False)]

        if entries.empty or exits.empty:
            raise ValueError(f"File {input_filename} must contain both 'Entry' and 'Exit' trades, or be in final format.")

        paired_trades = pd.merge(
            entries[['Trade #', 'Date/Time', price_column, 'Contracts', 'Commission']],
            exits[['Trade #', 'Date/Time', price_column, profit_column, 'Contracts']],
            on='Trade #',
            suffixes=('_Entry', '_Exit')
        )

        paired_trades['Type'] = entries.iloc[0]['Type'] if not entries.empty else 'N/A'

        formatted_trades = paired_trades.rename(columns={
            'Date/Time_Entry': 'Entry Date',
            'Date/Time_Exit': 'Exit Date',
            f'{price_column}_Entry': 'Entry Price',
            f'{price_column}_Exit': 'Exit Price',
            'Contracts_Entry': 'Contracts',
            profit_column: 'Profit',
            'Commission_Entry': 'Commission'
        })

        formatted_trades['Total Commission'] = formatted_trades['Commission']
        formatted_trades['Net Profit'] = formatted_trades['Profit'] - formatted_trades['Total Commission']
        formatted_trades = formatted_trades[
            ['Trade #', 'Type', 'Contracts', 'Entry Date', 'Exit Date', 
             'Entry Price', 'Exit Price', 'Profit', 'Total Commission', 'Net Profit']
        ]
        return formatted_trades

    except Exception as e:
        st.error(f"An error occurred while processing file {input_filename}: {e}")
        return None
