import pandas as pd
import numpy as np
import streamlit as st
import statsmodels.api as sm
from utils import interpret_sqn

DEFAULT_RISK_FREE_RATE = 0.02  # 2% annual risk-free rate.

def max_consecutive_losses(profits):
    max_loss_streak = 0
    current_loss_streak = 0
    for profit in profits:
        if profit < 0:
            current_loss_streak += 1
            if current_loss_streak > max_loss_streak:
                max_loss_streak = current_loss_streak
        else:
            current_loss_streak = 0
    return max_loss_streak

def max_consecutive_wins(profits):
    max_win_streak = 0
    current_win_streak = 0
    for profit in profits:
        if profit > 0:
            current_win_streak += 1
            if current_win_streak > max_win_streak:
                max_win_streak = current_win_streak
        else:
            current_win_streak = 0
    return max_win_streak

def calculate_stability(equity_curve):
    """
    Calculate the stability (R^2) of the equity curve using linear regression.
    """
    if len(equity_curve) < 2:
        return np.nan

    if equity_curve.nunique() == 1:
        return 1.0

    X = np.arange(len(equity_curve))  # time index
    y = equity_curve.values
    X = sm.add_constant(X)
    model = sm.OLS(y, X).fit()
    return model.rsquared

def max_drawdown_period(cumulative_profit):
    """
    Calculate the maximum drawdown period (in days) from the cumulative profit series.
    """
    rolling_max = cumulative_profit.cummax()
    in_drawdown = cumulative_profit < rolling_max

    max_dd_period = 0
    current_dd_period = 0

    for drawdown in in_drawdown:
        if drawdown:
            current_dd_period += 1
            if current_dd_period > max_dd_period:
                max_dd_period = current_dd_period
        else:
            current_dd_period = 0

    return max_dd_period

def calculate_buy_and_hold(trades, date_column, initial_balance=10000.0):
    """
    Calculate the equity curve for a buy-and-hold position held throughout the test period.
    """
    trades = trades.copy()
    trades[date_column] = pd.to_datetime(trades[date_column])

    trades_sorted = trades.sort_values(by=date_column)
    trades_sorted = trades_sorted.drop_duplicates(subset=[date_column])

    # Identify first entry price and date
    first_trade = trades_sorted.iloc[0]
    buy_price = first_trade['Entry Price']

    # Determine last date in test period
    last_date = trades_sorted[date_column].max().date()
    first_date = trades_sorted[date_column].min().date()

    date_range = pd.date_range(start=first_date, end=last_date, freq='D')
    trades_sorted = trades_sorted.set_index(date_column)

    # If the index isn't unique, remove duplicates
    if not trades_sorted.index.is_unique:
        trades_sorted = trades_sorted[~trades_sorted.index.duplicated()]

    daily_prices = trades_sorted['Entry Price'].resample('D').ffill().reindex(date_range, method='ffill')
    daily_prices = daily_prices.fillna(buy_price)

    daily_prices = daily_prices.reset_index()
    daily_prices.columns = ['Date', 'Entry Price']

    daily_prices['Daily Return'] = (daily_prices['Entry Price'] - buy_price) / buy_price
    daily_prices['Cumulative Profit'] = (1 + daily_prices['Daily Return']) * initial_balance

    final_balance = daily_prices['Cumulative Profit'].iloc[-1]
    buy_and_hold_return_dollar = final_balance - initial_balance
    buy_and_hold_return_pct = (buy_and_hold_return_dollar / initial_balance) * 100

    buy_and_hold_curve = daily_prices.set_index('Date')
    return buy_and_hold_curve, buy_and_hold_return_dollar, buy_and_hold_return_pct

@st.cache_data
def calculate_metrics(
    trades,
    date_column,
    initial_balance=10000.0,
    risk_free_rate=DEFAULT_RISK_FREE_RATE,
    include_buy_and_hold=True
):
    """
    Calculate performance metrics. 
    """
    metrics = {}

    trades = trades.copy()
    trades[date_column] = pd.to_datetime(trades[date_column])
    trades.sort_values(by=date_column, inplace=True)

    total_profit = trades['Net Profit'].sum()
    number_of_trades = len(trades)
    winning_trades = len(trades[trades['Net Profit'] > 0])
    winning_percentage = (winning_trades / number_of_trades) * 100 if number_of_trades > 0 else 0
    average_win = trades[trades['Net Profit'] > 0]['Net Profit'].mean() or 0
    average_loss = trades[trades['Net Profit'] < 0]['Net Profit'].mean() or 0

    risk_reward_ratio = abs(average_loss) / average_win if average_win != 0 else np.inf

    profits = trades['Net Profit'].values
    max_consec_losses = max_consecutive_losses(profits)
    max_consec_wins = max_consecutive_wins(profits)

    total_net_profit = total_profit
    total_net_profit_pct = (total_net_profit / initial_balance) * 100 if initial_balance != 0 else 0

    daily_profit = trades.groupby(date_column)['Net Profit'].sum().reset_index()
    daily_profit['Cumulative Profit'] = daily_profit['Net Profit'].cumsum() + initial_balance

    equity_curve = daily_profit.set_index(date_column)

    # -- FIX #1: replace `.fillna(method='ffill')` with pure `.ffill()`:
    equity_curve = equity_curve.resample('D').ffill()  # forward-fill daily frequency
    # (No second fill needed unless you really want it repeated)
    
    equity_curve['Daily Return'] = equity_curve['Cumulative Profit'].pct_change().fillna(0)

    # Worst 5% of daily returns
    worst_5_percent = equity_curve['Daily Return'].nsmallest(int(len(equity_curve) * 0.05))
    expected_shortfall = worst_5_percent.mean()

    trades_std_dev = trades['Net Profit'].std()
    expectancy = trades['Net Profit'].mean()
    sqn = (expectancy / trades_std_dev) * np.sqrt(number_of_trades) if trades_std_dev != 0 else 0

    mean_daily_return = equity_curve['Daily Return'].mean()
    std_daily_return = equity_curve['Daily Return'].std()
    sharpe_ratio = 0
    if std_daily_return != 0:
        sharpe_ratio = ((mean_daily_return - (risk_free_rate / 252)) / std_daily_return) * np.sqrt(252)

    negative_returns = equity_curve['Daily Return'][equity_curve['Daily Return'] < (risk_free_rate / 252)]
    downside_deviation = negative_returns.std() if len(negative_returns) > 0 else 0
    sortino_ratio = 0
    if downside_deviation != 0:
        sortino_ratio = ((mean_daily_return - (risk_free_rate / 252)) / downside_deviation) * np.sqrt(252)

    start_date = trades[date_column].min()
    end_date = trades[date_column].max()
    days = (end_date - start_date).days
    years = days / 365.25 if days > 0 else 1
    ending_balance = initial_balance + total_profit
    cagr = (ending_balance / initial_balance) ** (1 / years) - 1 if ending_balance > 0 and initial_balance > 0 and years > 0 else 0

    annual_volatility = std_daily_return * np.sqrt(252)
    annual_return_dollar = total_profit / years if years > 0 else 0
    annual_return_pct = cagr * 100

    cumulative_profit = equity_curve['Cumulative Profit']
    rolling_max = cumulative_profit.cummax()
    drawdown = rolling_max - cumulative_profit
    max_drawdown = drawdown.max()
    percentage_drawdown = (max_drawdown / initial_balance) * 100 if initial_balance != 0 else 0

    from_date = trades[date_column].min().date() if not trades.empty else None
    to_date = trades[date_column].max().date() if not trades.empty else None
    dd_period = max_drawdown_period(cumulative_profit)

    # If user wants buy & hold
    if include_buy_and_hold:
        bah_curve, bah_dollar, bah_pct = calculate_buy_and_hold(trades, date_column, initial_balance)
        metrics.update({
            'Buy and Hold Return ($)': f"${bah_dollar:,.2f}",
            'Buy and Hold Return (%)': f"{bah_pct:.2f}%"
        })

    metrics.update({
        '# of Trades': number_of_trades,
        'Win Rate (%)': f"{winning_percentage:.2f}%",
        'Risk-Reward Ratio': f"{risk_reward_ratio:.2f}",
        'Total Net Profit ($)': f"${total_net_profit:,.2f}",
        'Total Net Profit (%)': f"{total_net_profit_pct:.2f}%",
        'Max Drawdown ($)': f"${max_drawdown:,.2f}",
        'Max Drawdown (%)': f"{percentage_drawdown:.2f}%",
        'Max Drawdown Period (days)': dd_period,
        'Expected Shortfall (5%)': f"{expected_shortfall:.4f}",
        'Strategy Quality Number': f"{round(sqn, 2)} ({interpret_sqn(sqn)})",
        'Sharpe Ratio': round(sharpe_ratio, 2),
        'Sortino Ratio': round(sortino_ratio, 2),
        'CAGR': f"{annual_return_pct:.2f}%",
        'Annualized Return ($)': f"${annual_return_dollar:,.2f}",
        'Volatility (Annualized)': f"{annual_volatility:.2f}%",
        'Max Consecutive Losses': max_consec_losses,
        'Max Consecutive Wins': max_consec_wins,
    })

    return metrics, equity_curve
