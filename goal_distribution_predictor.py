import numpy as np

class GoalDistributionPredictor:
    def __init__(self, home_win_prob, draw_prob, away_win_prob):
        self.home_win_prob = home_win_prob
        self.draw_prob = draw_prob
        self.away_win_prob = away_win_prob
        self.total_prob = home_win_prob + draw_prob + away_win_prob

    def normalize_probabilities(self):
        # Normalize probabilities if not summing to 1
        if self.total_prob != 1.0:
            self.home_win_prob /= self.total_prob
            self.draw_prob /= self.total_prob
            self.away_win_prob /= self.total_prob

    def calculate_over_under(self):
        # Example calculation for over/under betting markets
        return {
            'over_2.5_goals': self.home_win_prob * 0.6,
            'under_2.5_goals': self.home_win_prob * 0.4
        }

    def calculate_BTTS(self):
        # Example calculation for Both Teams To Score (BTTS)
        return {
            'BTTS_yes': 0.5,
            'BTTS_no': 0.5,
        }

    def calculate_asian_handicaps(self):
        # Example calculation for Asian Handicaps
        return {
            'home_win_0.5': self.home_win_prob * 0.55,
            'away_win_0.5': self.away_win_prob * 0.45,
        }

    def correct_score_predictions(self):
        # Example predictions for correct scores
        return {
            '1-0': self.home_win_prob * 0.3,
            '2-1': self.home_win_prob * 0.2
        }

    def goal_margin_predictions(self):
        # Example goal margin predictions
        return {
            'margin_1': self.home_win_prob * 0.4,
            'margin_2': self.home_win_prob * 0.6,
        }

    def predict_all(self):
        self.normalize_probabilities()
        predictions = {
            'over_under': self.calculate_over_under(),
            'BTTS': self.calculate_BTTS(),
            'asian_handicaps': self.calculate_asian_handicaps(),
            'correct_score': self.correct_score_predictions(),
            'goal_margin': self.goal_margin_predictions(),
        }
        return predictions
