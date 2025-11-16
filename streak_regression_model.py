import numpy as np
import pandas as pd
import statsmodels.api as sm

def clean_sheet_streak_probability(streaks):
    """
    Calculate clean sheet streak regression probability curves.

    Parameters:
    streaks (list): List of clean sheet streaks.

    Returns:
    np.array: Probability curves for clean sheet streaks.
    """
    # Example implementation
    likelihoods = [1 / (streak + 1) for streak in streaks]
    return np.array(likelihoods) / sum(likelihoods)

def adjust_streak_logic(streak_count):
    """
    Logic for adjusting streaks based on historical data.
    
    Parameters:
    streak_count (int): The current streak count.

    Returns:
    int: Adjusted streak count.
    """
    # Example adjustment logic
    if streak_count > 5:
        return streak_count * 0.9  # Reduce streak for normalization
    return streak_count

def regression_warnings(model):
    """
    Provide warnings for regression model analysis.

    Parameters:
    model (statsmodels regression model): The regression model object.

    Returns:
    str: Warnings regarding the regression model.
    """
    if model.pvalues.max() > 0.05:
        return "Warning: Some predictors may not be statistically significant."
    return "Model appears to be statistically significant."

# Example usage
if __name__ == "__main__":
    # Example streak data
    streak_data = [0, 1, 2, 3, 4, 5]
    probabilities = clean_sheet_streak_probability(streak_data)
    print("Clean Sheet Streak Probabilities:", probabilities)
    
    adjusted_streak = adjust_streak_logic(6)
    print("Adjusted Streak Count:", adjusted_streak)

    # Example regression model (dummy data)
    X = np.random.rand(100, 2)  # Dummy features
    y = np.random.rand(100)      # Dummy target
    X = sm.add_constant(X)       # Add constant to model
    model = sm.OLS(y, X).fit()
    print(regression_warnings(model))
