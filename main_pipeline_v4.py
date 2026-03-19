# main_pipeline_v4.py

import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.linear_model import LinearRegression

from tactical_interaction_model import TacticalInteractionModel
from fatigue_interaction_model import FatigueInteractionModel
from streak_regression_model import clean_sheet_streak_probability, adjust_streak_logic
from dynamic_draw_threshold import calculate_draw_probability
from feature_engineering import FeatureEngineering
from decision_engine import DecisionEngine


# Tactical Analysis
def tactical_analysis(data):
    """
    Perform tactical analysis on match data.

    :param data: pd.DataFrame with match metrics per row, including columns for
                 'home_possession', 'away_possession', 'home_shots', 'away_shots',
                 'shots_on_target', 'goals', 'tackles_won', 'interceptions',
                 'goals_conceded', 'shots_faced'.
    :return: pd.DataFrame with additional tactical analysis columns appended.
    """
    model = TacticalInteractionModel()
    results = []
    for _, row in data.iterrows():
        possession_data = {
            'possession_pct': row.get('home_possession', 50),
            'shots': row.get('home_shots', 0),
            'goals': row.get('home_goals', 0),
        }
        defensive_data = {
            'tackles_won': row.get('tackles_won', 0),
            'interceptions': row.get('interceptions', 0),
            'goals_conceded': row.get('goals_conceded', 0),
            'shots_faced': row.get('shots_faced', 1),
        }
        match_data = {
            'home_possession': row.get('home_possession', 50),
            'away_possession': row.get('away_possession', 50),
            'home_shots': row.get('home_shots', 0),
            'away_shots': row.get('away_shots', 0),
        }
        results.append({
            'possession_efficiency': model.analyze_possession_efficiency(possession_data),
            'defensive_resistance': model.analyze_defensive_resistance(defensive_data),
            'scenario': model.detect_scenario(match_data),
        })
    analyzed_data = data.copy()
    analyzed_data = pd.concat(
        [analyzed_data, pd.DataFrame(results, index=data.index)], axis=1
    )
    return analyzed_data


# Fatigue Modeling
def fatigue_modeling(data):
    """
    Model fatigue impact on team performance for each row of match data.

    :param data: pd.DataFrame with a 'fatigue_level' column (0-10 scale).
    :return: pd.DataFrame with additional 'fatigue_performance' column appended.
    """
    fatigue_model = FatigueInteractionModel()
    performances = []
    for _, row in data.iterrows():
        fatigue_model.set_fatigue_level(row.get('fatigue_level', 0))
        performances.append(fatigue_model.calculate_performance())
    modeled_fatigue = data.copy()
    modeled_fatigue['fatigue_performance'] = performances
    return modeled_fatigue


# Streak Regression
def streak_regression(data):
    """
    Perform clean sheet streak regression analysis on match data.

    :param data: pd.DataFrame with a 'clean_sheet_streak' column.
    :return: pd.DataFrame with additional 'streak_probability' and
             'adjusted_streak' columns appended.
    """
    streaks = (
        data['clean_sheet_streak'].tolist()
        if 'clean_sheet_streak' in data.columns
        else [0] * len(data)
    )
    probabilities = clean_sheet_streak_probability(streaks)
    adjusted = [adjust_streak_logic(s) for s in streaks]
    regression_results = data.copy()
    regression_results['streak_probability'] = probabilities
    regression_results['adjusted_streak'] = adjusted
    return regression_results


# Draw Threshold Intelligence
def draw_threshold_intelligence(data):
    """
    Calculate draw probability using dynamic threshold intelligence for each match row.

    :param data: pd.DataFrame with columns for 'possession_parity', 'xg_difference',
                 'tactical_friction', 'fatigue', 'midweek_factor', 'set_piece_threat'.
    :return: pd.DataFrame with additional 'draw_probability' column appended.
    """
    draw_probs = []
    for _, row in data.iterrows():
        prob = calculate_draw_probability(
            possession_parity=row.get('possession_parity', 0.5),
            xG_difference=row.get('xg_difference', 0.0),
            tactical_friction=row.get('tactical_friction', 0.0),
            fatigue=row.get('fatigue', 0.0),
            midweek_factor=row.get('midweek_factor', 0.0),
            set_piece_threat=row.get('set_piece_threat', 0.0),
        )
        draw_probs.append(prob)
    draw_threshold_results = data.copy()
    draw_threshold_results['draw_probability'] = draw_probs
    return draw_threshold_results


# Main function to integrate and run all aspects of the pipeline
def main():
    # Load data
    data = pd.read_csv('data.csv')  # Update with actual data source
    analyzed_data = tactical_analysis(data)
    modeled_fatigue = fatigue_modeling(analyzed_data)
    regression_results = streak_regression(modeled_fatigue)
    draw_threshold_results = draw_threshold_intelligence(regression_results)

    # Output or save results
    print(draw_threshold_results)


if __name__ == "__main__":
    main()
