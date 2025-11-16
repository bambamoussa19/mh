"""
Streak Regression Model - Production Implementation with Volatility Detection

Detects volatility patterns in form streaks instead of simple mean reversion.
Addresses audit finding: "Form streaks treated as 'mean reversion = draw' 
instead of volatility detector"
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm


class StreakVolatilityDetector:
    """
    Detects volatility in team performance streaks to identify
    unstable form vs. sustainable trends.
    """
    
    def __init__(self):
        self.high_volatility_threshold = 0.6
        self.sustainable_streak_length = 4
        
    def calculate_streak_volatility(self, recent_results):
        """
        Calculate volatility in recent results.
        
        :param recent_results: List of recent match results (1=win, 0=draw, -1=loss)
        :return: Volatility score (0=stable, 1=highly volatile)
        """
        if len(recent_results) < 3:
            return 0.5  # Insufficient data, assume moderate volatility
        
        results_array = np.array(recent_results)
        
        # Calculate standard deviation normalized by result range
        volatility = np.std(results_array) / 2.0  # Max std is 2 for [-1, 1] range
        
        # Check for oscillating pattern (win-loss-win-loss)
        if len(recent_results) >= 4:
            changes = np.diff(results_array)
            sign_changes = np.sum(np.abs(np.diff(np.sign(changes))))
            if sign_changes >= len(changes) - 1:
                # High frequency oscillation detected
                volatility = min(1.0, volatility * 1.5)
        
        return round(volatility, 3)
    
    def detect_streak_sustainability(self, streak_data):
        """
        Determine if a winning/losing streak is sustainable or due to variance.
        
        :param streak_data: Dict with:
            - current_streak: Int (positive for wins, negative for losses)
            - recent_results: List of results
            - performance_metrics: Dict with xG, shots, possession trends
        :return: Sustainability assessment
        """
        current_streak = streak_data.get('current_streak', 0)
        recent_results = streak_data.get('recent_results', [])
        metrics = streak_data.get('performance_metrics', {})
        
        volatility = self.calculate_streak_volatility(recent_results)
        
        # Check underlying performance metrics
        xg_trend = metrics.get('xg_trend', 0)  # Positive = improving
        shot_quality_trend = metrics.get('shot_quality_trend', 0)
        
        # Sustainability scoring
        sustainability_score = 0.5  # Neutral baseline
        
        # Long streaks with low volatility = sustainable
        if abs(current_streak) >= self.sustainable_streak_length:
            if volatility < self.high_volatility_threshold:
                sustainability_score += 0.3
            else:
                sustainability_score -= 0.2  # Long but volatile = regression likely
        
        # Performance metrics alignment
        if current_streak > 0:  # Winning streak
            if xg_trend > 0 and shot_quality_trend > 0:
                sustainability_score += 0.2  # Performance backing results
            elif xg_trend < -0.1:
                sustainability_score -= 0.3  # Lucky wins, not sustainable
        elif current_streak < 0:  # Losing streak
            if xg_trend < 0 and shot_quality_trend < 0:
                sustainability_score -= 0.2  # Performance declining
            elif xg_trend > 0.1:
                sustainability_score += 0.3  # Unlucky losses, improvement expected
        
        sustainability_score = max(0.0, min(1.0, sustainability_score))
        
        return {
            'sustainability_score': round(sustainability_score, 3),
            'volatility': volatility,
            'regression_risk': 'High' if volatility > self.high_volatility_threshold else 'Low',
            'recommendation': self._get_recommendation(sustainability_score, current_streak)
        }
    
    def _get_recommendation(self, sustainability, streak):
        """Generate betting recommendation based on sustainability."""
        if streak > 0:  # Winning streak
            if sustainability > 0.7:
                return "Continue backing team, sustainable form"
            elif sustainability < 0.4:
                return "Regression likely, consider draw/opposition"
            else:
                return "Moderate confidence, monitor closely"
        elif streak < 0:  # Losing streak
            if sustainability < 0.3:
                return "Improvement expected, bounce-back opportunity"
            elif sustainability > 0.6:
                return "Continued struggles likely, back opposition"
            else:
                return "Uncertain trajectory, wait for clearer signal"
        else:
            return "No clear trend"


def clean_sheet_streak_probability(streaks):
    """
    Calculate clean sheet streak regression probability with volatility adjustment.

    Parameters:
    streaks (list): List of clean sheet streaks.

    Returns:
    np.array: Probability curves for clean sheet streaks.
    """
    if not streaks or len(streaks) == 0:
        return np.array([1.0])
    
    # Base probabilities with diminishing returns for longer streaks
    likelihoods = []
    for streak in streaks:
        # Longer streaks are less likely to continue (regression to mean)
        # But not linear - uses exponential decay
        if streak == 0:
            base_prob = 0.4  # 40% chance of clean sheet if no current streak
        else:
            base_prob = 0.6 * np.exp(-0.15 * streak)  # Exponential decay
        likelihoods.append(base_prob)
    
    # Normalize to probability distribution
    likelihoods = np.array(likelihoods)
    return likelihoods / likelihoods.sum() if likelihoods.sum() > 0 else likelihoods


def adjust_streak_logic(streak_count, volatility=None):
    """
    Adjust streaks based on volatility and historical patterns.
    
    Parameters:
    streak_count (int): The current streak count.
    volatility (float): Optional volatility measure (0-1)

    Returns:
    float: Adjusted streak weight for predictions
    """
    if volatility is None:
        volatility = 0.5  # Default moderate volatility
    
    # Base adjustment - longer streaks get diminishing weight
    if streak_count > 5:
        base_adjustment = streak_count * 0.85
    elif streak_count > 3:
        base_adjustment = streak_count * 0.95
    else:
        base_adjustment = streak_count
    
    # Volatility adjustment - high volatility reduces streak reliability
    volatility_factor = 1.0 - (volatility * 0.4)
    
    adjusted = base_adjustment * volatility_factor
    
    return round(adjusted, 2)


def regression_warnings(model):
    """
    Provide warnings for regression model analysis.

    Parameters:
    model (statsmodels regression model): The regression model object.

    Returns:
    dict: Warnings and model diagnostics
    """
    warnings = []
    
    # Check p-values
    if hasattr(model, 'pvalues'):
        if model.pvalues.max() > 0.05:
            warnings.append("Warning: Some predictors may not be statistically significant.")
            insignificant = model.pvalues[model.pvalues > 0.05].index.tolist()
            warnings.append(f"Insignificant variables: {insignificant}")
    
    # Check R-squared
    if hasattr(model, 'rsquared') and model.rsquared < 0.3:
        warnings.append(f"Low R-squared: {model.rsquared:.3f} - model has limited explanatory power")
    
    # Check for multicollinearity
    if hasattr(model, 'condition_number') and model.condition_number > 30:
        warnings.append(f"High condition number: {model.condition_number:.1f} - possible multicollinearity")
    
    if not warnings:
        return {"status": "OK", "message": "Model appears statistically sound"}
    
    return {"status": "WARNING", "warnings": warnings}
