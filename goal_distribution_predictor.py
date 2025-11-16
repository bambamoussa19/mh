"""
Goal Distribution Predictor - Enhanced with xG Integration

Predicts goal distributions and betting market outcomes using both
traditional probabilities and xG data.

Addresses audit finding: Integrate xG data for more accurate predictions.
"""

import numpy as np
from scipy.stats import poisson


class GoalDistributionPredictor:
    def __init__(self, home_win_prob, draw_prob, away_win_prob, xg_home=None, xg_away=None):
        """
        Initialize predictor with win probabilities and optional xG data.
        
        :param home_win_prob: Home win probability
        :param draw_prob: Draw probability
        :param away_win_prob: Away win probability
        :param xg_home: Optional expected goals for home team
        :param xg_away: Optional expected goals for away team
        """
        self.home_win_prob = home_win_prob
        self.draw_prob = draw_prob
        self.away_win_prob = away_win_prob
        self.total_prob = home_win_prob + draw_prob + away_win_prob
        
        # xG data for enhanced predictions
        self.xg_home = xg_home
        self.xg_away = xg_away
        self.xg_available = xg_home is not None and xg_away is not None

    def normalize_probabilities(self):
        """Normalize probabilities to sum to 1.0"""
        if self.total_prob != 1.0:
            self.home_win_prob /= self.total_prob
            self.draw_prob /= self.total_prob
            self.away_win_prob /= self.total_prob
            self.total_prob = 1.0

    def _infer_goals_from_probs(self):
        """
        Infer expected goals from win probabilities if xG not available.
        This is a rough estimation method.
        """
        # Rough estimation: higher win prob suggests more goals
        home_expected = 1.3 + (self.home_win_prob - 0.33) * 1.5
        away_expected = 1.3 + (self.away_win_prob - 0.33) * 1.5
        
        return max(0.3, home_expected), max(0.3, away_expected)

    def calculate_over_under(self):
        """
        Calculate over/under betting markets using xG if available.
        Enhanced with Poisson distribution when xG available.
        """
        if self.xg_available:
            # Use xG-based Poisson model
            lambda_home = self.xg_home * 0.95  # Slight adjustment
            lambda_away = self.xg_away * 0.95
        else:
            # Fallback to inference from probabilities
            lambda_home, lambda_away = self._infer_goals_from_probs()
        
        # Calculate probability distribution for total goals
        total_goals_prob = {}
        for home_goals in range(7):
            for away_goals in range(7):
                total = home_goals + away_goals
                prob = (poisson.pmf(home_goals, lambda_home) * 
                       poisson.pmf(away_goals, lambda_away))
                total_goals_prob[total] = total_goals_prob.get(total, 0) + prob
        
        # Calculate over/under for common lines
        result = {}
        for line in [0.5, 1.5, 2.5, 3.5, 4.5]:
            over = sum(prob for goals, prob in total_goals_prob.items() if goals > line)
            under = sum(prob for goals, prob in total_goals_prob.items() if goals < line)
            result[f'over_{line}'] = round(over, 4)
            result[f'under_{line}'] = round(under, 4)
        
        return result

    def calculate_BTTS(self):
        """
        Calculate Both Teams To Score using xG-enhanced model.
        """
        if self.xg_available:
            lambda_home = self.xg_home * 0.95
            lambda_away = self.xg_away * 0.95
        else:
            lambda_home, lambda_away = self._infer_goals_from_probs()
        
        # P(home scores) = 1 - P(home 0 goals)
        home_scores = 1 - poisson.pmf(0, lambda_home)
        away_scores = 1 - poisson.pmf(0, lambda_away)
        
        # BTTS = both score
        btts_yes = home_scores * away_scores
        btts_no = 1 - btts_yes
        
        return {
            'BTTS_yes': round(btts_yes, 4),
            'BTTS_no': round(btts_no, 4),
        }

    def calculate_asian_handicaps(self):
        """
        Calculate Asian Handicaps using win probabilities and xG.
        """
        if self.xg_available:
            xg_diff = self.xg_home - self.xg_away
            
            # Adjust probabilities based on xG difference
            if xg_diff > 0.5:
                home_boost = min(0.15, xg_diff * 0.1)
            elif xg_diff < -0.5:
                home_boost = max(-0.15, xg_diff * 0.1)
            else:
                home_boost = 0
            
            home_handicap = min(0.95, max(0.05, self.home_win_prob + home_boost))
            away_handicap = min(0.95, max(0.05, self.away_win_prob - home_boost))
        else:
            home_handicap = self.home_win_prob
            away_handicap = self.away_win_prob
        
        return {
            'home_-0.5': round(home_handicap, 4),
            'away_+0.5': round(1 - home_handicap, 4),
            'home_-1.5': round(home_handicap * 0.6, 4),
            'away_+1.5': round(1 - home_handicap * 0.6, 4),
        }

    def correct_score_predictions(self):
        """
        Predict correct scores using xG-based Poisson model.
        """
        if self.xg_available:
            lambda_home = self.xg_home * 0.95
            lambda_away = self.xg_away * 0.95
        else:
            lambda_home, lambda_away = self._infer_goals_from_probs()
        
        # Calculate probabilities for most likely scores
        scores = {}
        for home_goals in range(6):
            for away_goals in range(6):
                prob = (poisson.pmf(home_goals, lambda_home) * 
                       poisson.pmf(away_goals, lambda_away))
                scores[f'{home_goals}-{away_goals}'] = round(prob, 4)
        
        # Return top 10 most likely scores
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_scores[:10])

    def goal_margin_predictions(self):
        """
        Predict goal margin distributions.
        """
        if self.xg_available:
            lambda_home = self.xg_home * 0.95
            lambda_away = self.xg_away * 0.95
        else:
            lambda_home, lambda_away = self._infer_goals_from_probs()
        
        # Calculate margin probabilities
        margins = {}
        for home_goals in range(7):
            for away_goals in range(7):
                margin = home_goals - away_goals
                prob = (poisson.pmf(home_goals, lambda_home) * 
                       poisson.pmf(away_goals, lambda_away))
                margins[margin] = margins.get(margin, 0) + prob
        
        result = {}
        for margin, prob in margins.items():
            if margin > 0:
                result[f'home_by_{margin}'] = round(prob, 4)
            elif margin < 0:
                result[f'away_by_{abs(margin)}'] = round(prob, 4)
            else:
                result['draw'] = round(prob, 4)
        
        return result

    def predict_all(self):
        """
        Generate all predictions with xG integration.
        """
        self.normalize_probabilities()
        
        predictions = {
            'match_outcome': {
                'home_win': round(self.home_win_prob, 4),
                'draw': round(self.draw_prob, 4),
                'away_win': round(self.away_win_prob, 4)
            },
            'over_under': self.calculate_over_under(),
            'BTTS': self.calculate_BTTS(),
            'asian_handicaps': self.calculate_asian_handicaps(),
            'correct_score': self.correct_score_predictions(),
            'goal_margin': self.goal_margin_predictions(),
        }
        
        # Add xG info if available
        if self.xg_available:
            predictions['xg_data'] = {
                'xg_home': self.xg_home,
                'xg_away': self.xg_away,
                'xg_difference': round(self.xg_home - self.xg_away, 2)
            }
        
        return predictions
