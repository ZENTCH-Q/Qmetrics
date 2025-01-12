# monte_carlo.py

import numpy as np
import pandas as pd

def monte_carlo_simulation(
    trades: pd.DataFrame,
    num_simulations: int = 1000,
    num_trades: int = None,
    method: str = "random_choice",
    seed: int = None
) -> np.ndarray:

    if 'Profit' not in trades.columns:
        raise KeyError("The input DataFrame must contain a 'Profit' column.")

    profits = trades['Profit'].values
    total_trades_available = len(profits)

    if num_trades is None:
        num_trades = total_trades_available

    if method not in ["random_choice", "randomized_shuffling"]:
        raise ValueError(f"Unknown method: {method}. Choose either 'random_choice' or 'randomized_shuffling'.")

    if method == "randomized_shuffling" and num_trades > total_trades_available:
        raise ValueError(
            f"For 'randomized_shuffling', num_trades ({num_trades}) cannot exceed the total number of available trades ({total_trades_available})."
        )

    # Set seed for reproducibility if provided
    if seed is not None:
        np.random.seed(seed)

    if method == "random_choice":
        # Sample trades with replacement
        simulated_trades = np.random.choice(profits, size=(num_simulations, num_trades), replace=True)
    elif method == "randomized_shuffling":
        # Sample trades without replacement by shuffling
        # Initialize an empty array to store simulations
        simulated_trades = np.empty((num_simulations, num_trades))
        # Shuffle profits once and tile them if num_trades == total_trades_available
        # Otherwise, perform shuffling per simulation
        for i in range(num_simulations):
            shuffled_profits = np.random.permutation(profits)
            simulated_trades[i, :] = shuffled_profits[:num_trades]
    
    return simulated_trades


def calculate_max_drawdown(cumulative_profits: np.ndarray, as_percentage: bool = False) -> np.ndarray:

    if not isinstance(cumulative_profits, np.ndarray):
        raise TypeError("cumulative_profits must be a NumPy array.")

    if cumulative_profits.ndim == 1:
        cumulative_profits = cumulative_profits.reshape(1, -1)
    elif cumulative_profits.ndim != 2:
        raise ValueError("cumulative_profits must be a 1D or 2D array.")

    # Compute the rolling maximum for each simulation
    roll_max = np.maximum.accumulate(cumulative_profits, axis=1)
    # Compute drawdowns
    drawdowns = roll_max - cumulative_profits
    if as_percentage:
        # Avoid division by zero by setting zero peaks to one (no drawdown possible)
        safe_roll_max = np.where(roll_max == 0, 1, roll_max)
        drawdowns = (drawdowns / safe_roll_max) * 100  # Percentage drawdown

    # Return the maximum drawdown per simulation
    return drawdowns.max(axis=1)


def calculate_max_consecutive_losing_trades(simulated_trades: np.ndarray) -> np.ndarray:

    if simulated_trades.ndim != 2:
        raise ValueError("simulated_trades must be a 2D array.")

    losing = simulated_trades < 0
    max_streaks = np.zeros(losing.shape[0], dtype=int)
    current_streak = np.zeros(losing.shape[0], dtype=int)

    for i in range(losing.shape[1]):
        # Increment streak where losing, reset where not
        current_streak = np.where(losing[:, i], current_streak + 1, 0)
        # Update max streaks
        max_streaks = np.maximum(max_streaks, current_streak)

    return max_streaks

def calculate_max_consecutive_winning_trades(simulated_trades: np.ndarray) -> np.ndarray:

    if simulated_trades.ndim != 2:
        raise ValueError("simulated_trades must be a 2D array.")

    winning = simulated_trades > 0
    max_streaks = np.zeros(winning.shape[0], dtype=int)
    current_streak = np.zeros(winning.shape[0], dtype=int)

    for i in range(winning.shape[1]):
        # Increment streak where winning, reset where not
        current_streak = np.where(winning[:, i], current_streak + 1, 0)
        # Update max streaks
        max_streaks = np.maximum(max_streaks, current_streak)

    return max_streaks
