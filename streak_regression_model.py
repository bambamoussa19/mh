import numpy as np
import pandas as pd
import statsmodels.api as sm

def clean_sheet_streak_probability(streaks):
    """
    Calculate clean sheet streak regression probability curves.
    Corrected: Longer streaks = LOWER probability (regression to mean).

    Parameters:
    streaks (list): List of clean sheet streaks.

    Returns:
    np.array: Probability curves for clean sheet streaks.
    """
    if not streaks or len(streaks) == 0:
        return np.array([1.0])
    
    # Correct implementation: longer streaks should have lower continuation probability
    # Using exponential decay: P(continue) = base_prob * exp(-decay_rate * streak)
    base_prob = 0.6  # Base probability for streak length 0
    decay_rate = 0.15
    
    likelihoods = [base_prob * np.exp(-decay_rate * streak) for streak in streaks]
    total = sum(likelihoods)
    
    if total == 0:
        return np.ones(len(streaks)) / len(streaks)
    
    return np.array(likelihoods) / total

def calculate_streak_volatility(streak_count):
    """
    Calculate volatility associated with a streak.
    CORRECTED: Longer streaks = HIGHER volatility (more likely to break).
    
    Parameters:
    streak_count (int): The current streak count.

    Returns:
    float: Volatility score (0-1 scale, higher = more volatile)
    """
    if streak_count <= 0:
        return 0.1  # Low volatility baseline
    
    # Correct logic: volatility INCREASES with streak length
    # Using logarithmic growth to avoid extreme values
    volatility = min(0.95, 0.1 + 0.15 * np.log1p(streak_count))
    
    return volatility

def adjust_streak_logic(streak_count):
    """
    Logic for adjusting predictions based on streaks.
    Longer streaks increase the chance of regression to the mean.
    
    Parameters:
    streak_count (int): The current streak count.

    Returns:
    dict: Adjustment factors for predictions.
    """
    if streak_count <= 0:
        return {'continuation_probability': 0.50, 'break_probability': 0.50, 'volatility': 0.1}
    
    # Streak continuation probability decreases with length
    base_continuation = 0.6
    decay_factor = 0.12
    continuation_prob = max(0.1, base_continuation * np.exp(-decay_factor * streak_count))
    
    # Break probability is complement
    break_prob = 1.0 - continuation_prob
    
    # Volatility increases with streak
    volatility = calculate_streak_volatility(streak_count)
    
    return {
        'continuation_probability': continuation_prob,
        'break_probability': break_prob,
        'volatility': volatility,
        'streak_count': streak_count
    }

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

def apply_streak_adjustment_to_predictions(base_predictions, streak_info):
    """
    Apply streak-based adjustments to predictions.
    
    Parameters:
    base_predictions (dict): Base predictions (e.g., {'clean_sheet': 0.4})
    streak_info (dict): Output from adjust_streak_logic()
    
    Returns:
    dict: Adjusted predictions
    """
    adjusted = base_predictions.copy()
    
    if 'clean_sheet' in adjusted:
        # Apply streak continuation probability
        original_prob = adjusted['clean_sheet']
        streak_adjustment = streak_info['continuation_probability']
        
        # Blend original prediction with streak-based expectation
        adjusted['clean_sheet'] = (original_prob * 0.6 + streak_adjustment * 0.4)
        
        # Add volatility warning
        if streak_info['volatility'] > 0.7:
            adjusted['high_volatility_warning'] = True
    
    return adjusted

# Example usage
if __name__ == "__main__":
    # Example streak data
    streak_data = [0, 1, 2, 3, 4, 5, 6]
    probabilities = clean_sheet_streak_probability(streak_data)
    print("Clean Sheet Streak Probabilities:", probabilities)
    print("(Note: Probabilities DECREASE with longer streaks - correct behavior)\n")
    
    # Test volatility for different streak lengths
    print("Streak Volatility Analysis:")
    for streak in [0, 1, 3, 5, 8, 10]:
        volatility = calculate_streak_volatility(streak)
        print(f"Streak {streak}: Volatility = {volatility:.3f}")
    print()
    
    # Test adjustment logic
    print("Streak Adjustment Logic:")
    for streak in [0, 2, 5, 8]:
        adjustment = adjust_streak_logic(streak)
        print(f"Streak {streak}: {adjustment}")
    print()
    
    # Example with predictions
    base_pred = {'clean_sheet': 0.45, 'concede': 0.55}
    streak_5_info = adjust_streak_logic(5)
    adjusted_pred = apply_streak_adjustment_to_predictions(base_pred, streak_5_info)
    print("Base predictions:", base_pred)
    print("After 5-game clean sheet streak:", adjusted_pred)
