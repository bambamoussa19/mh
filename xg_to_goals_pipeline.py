"""
Expected Goals (xG) to Goal Probability Pipeline

Converts expected goals data into goal probability distributions.
Addresses audit finding: "xG data (0.88 vs 2.32) was available but not 
converted to goal probability"
"""

import numpy as np
from scipy.stats import poisson, skellam


class XGToGoalsPipeline:
    """
    Converts xG values into realistic goal probability distributions
    using Poisson and adjusted models.
    """
    
    def __init__(self):
        self.max_goals = 8  # Maximum goals to consider in distribution
        
    def xg_to_poisson_lambda(self, xg_value, adjustment_factor=0.95):
        """
        Convert xG to Poisson lambda parameter.
        
        xG slightly overestimates goals in practice, so we apply adjustment.
        
        :param xg_value: Expected goals value
        :param adjustment_factor: Calibration factor (0.9-1.0)
        :return: Lambda for Poisson distribution
        """
        return xg_value * adjustment_factor
    
    def calculate_goal_distribution(self, xg_home, xg_away):
        """
        Calculate probability distribution for exact goal counts.
        
        :param xg_home: Home team xG
        :param xg_away: Away team xG
        :return: Dict with goal probabilities
        """
        lambda_home = self.xg_to_poisson_lambda(xg_home)
        lambda_away = self.xg_to_poisson_lambda(xg_away)
        
        # Calculate probability for each goal count (0 to max_goals)
        home_dist = {}
        away_dist = {}
        
        for goals in range(self.max_goals + 1):
            home_dist[goals] = poisson.pmf(goals, lambda_home)
            away_dist[goals] = poisson.pmf(goals, lambda_away)
        
        return {
            'home_goals_distribution': home_dist,
            'away_goals_distribution': away_dist,
            'home_expected': lambda_home,
            'away_expected': lambda_away
        }
    
    def calculate_match_outcome_probabilities(self, xg_home, xg_away):
        """
        Calculate win/draw/loss probabilities from xG.
        
        Uses Skellam distribution (difference of two Poisson variables).
        
        :param xg_home: Home team xG
        :param xg_away: Away team xG
        :return: Dict with outcome probabilities
        """
        lambda_home = self.xg_to_poisson_lambda(xg_home)
        lambda_away = self.xg_to_poisson_lambda(xg_away)
        
        # Home win: goal difference > 0
        home_win_prob = 0.0
        for diff in range(1, self.max_goals + 1):
            home_win_prob += skellam.pmf(diff, lambda_home, lambda_away)
        
        # Draw: goal difference = 0
        draw_prob = skellam.pmf(0, lambda_home, lambda_away)
        
        # Away win: goal difference < 0
        away_win_prob = 0.0
        for diff in range(-self.max_goals, 0):
            away_win_prob += skellam.pmf(diff, lambda_home, lambda_away)
        
        # Normalize to ensure sum = 1.0
        total = home_win_prob + draw_prob + away_win_prob
        if total > 0:
            home_win_prob /= total
            draw_prob /= total
            away_win_prob /= total
        
        return {
            'home_win': round(home_win_prob, 4),
            'draw': round(draw_prob, 4),
            'away_win': round(away_win_prob, 4)
        }
    
    def calculate_over_under_probabilities(self, xg_home, xg_away, lines=[0.5, 1.5, 2.5, 3.5, 4.5]):
        """
        Calculate over/under goal line probabilities.
        
        :param xg_home: Home team xG
        :param xg_away: Away team xG
        :param lines: List of goal lines to calculate
        :return: Dict with over/under probabilities
        """
        lambda_home = self.xg_to_poisson_lambda(xg_home)
        lambda_away = self.xg_to_poisson_lambda(xg_away)
        
        # Calculate probability of each total goals scoreline
        total_goals_dist = {}
        for home_goals in range(self.max_goals + 1):
            for away_goals in range(self.max_goals + 1):
                total = home_goals + away_goals
                prob = (poisson.pmf(home_goals, lambda_home) * 
                       poisson.pmf(away_goals, lambda_away))
                total_goals_dist[total] = total_goals_dist.get(total, 0) + prob
        
        # Calculate over/under for each line
        over_under = {}
        for line in lines:
            over_prob = sum(prob for goals, prob in total_goals_dist.items() 
                          if goals > line)
            under_prob = sum(prob for goals, prob in total_goals_dist.items() 
                           if goals < line)
            
            over_under[f'over_{line}'] = round(over_prob, 4)
            over_under[f'under_{line}'] = round(under_prob, 4)
        
        return over_under
    
    def calculate_btts_probability(self, xg_home, xg_away):
        """
        Calculate Both Teams To Score (BTTS) probability.
        
        :param xg_home: Home team xG
        :param xg_away: Away team xG
        :return: Dict with BTTS probabilities
        """
        lambda_home = self.xg_to_poisson_lambda(xg_home)
        lambda_away = self.xg_to_poisson_lambda(xg_away)
        
        # P(Home scores) = 1 - P(Home 0 goals)
        home_scores_prob = 1 - poisson.pmf(0, lambda_home)
        
        # P(Away scores) = 1 - P(Away 0 goals)
        away_scores_prob = 1 - poisson.pmf(0, lambda_away)
        
        # BTTS = both score (independent events)
        btts_yes = home_scores_prob * away_scores_prob
        btts_no = 1 - btts_yes
        
        return {
            'btts_yes': round(btts_yes, 4),
            'btts_no': round(btts_no, 4)
        }
    
    def calculate_correct_score_probabilities(self, xg_home, xg_away, top_n=10):
        """
        Calculate most likely correct scores.
        
        :param xg_home: Home team xG
        :param xg_away: Away team xG
        :param top_n: Number of top scores to return
        :return: List of (score, probability) tuples
        """
        lambda_home = self.xg_to_poisson_lambda(xg_home)
        lambda_away = self.xg_to_poisson_lambda(xg_away)
        
        scores = []
        for home_goals in range(self.max_goals + 1):
            for away_goals in range(self.max_goals + 1):
                prob = (poisson.pmf(home_goals, lambda_home) * 
                       poisson.pmf(away_goals, lambda_away))
                scores.append(((home_goals, away_goals), prob))
        
        # Sort by probability and return top N
        scores.sort(key=lambda x: x[1], reverse=True)
        
        results = {}
        for (home, away), prob in scores[:top_n]:
            results[f'{home}-{away}'] = round(prob, 4)
        
        return results
    
    def full_analysis(self, xg_home, xg_away):
        """
        Perform complete xG to probability conversion.
        
        :param xg_home: Home team xG
        :param xg_away: Away team xG
        :return: Comprehensive probability analysis
        """
        return {
            'input': {
                'xg_home': xg_home,
                'xg_away': xg_away
            },
            'goal_distributions': self.calculate_goal_distribution(xg_home, xg_away),
            'match_outcomes': self.calculate_match_outcome_probabilities(xg_home, xg_away),
            'over_under': self.calculate_over_under_probabilities(xg_home, xg_away),
            'btts': self.calculate_btts_probability(xg_home, xg_away),
            'top_correct_scores': self.calculate_correct_score_probabilities(xg_home, xg_away, top_n=10)
        }


# Example usage
if __name__ == "__main__":
    pipeline = XGToGoalsPipeline()
    
    # Example from audit: Frankfurt xG 0.88 vs Heidenheim xG 2.32
    result = pipeline.full_analysis(0.88, 2.32)
    
    print("xG Analysis: Home 0.88 vs Away 2.32")
    print(f"Match Outcome Probabilities:")
    print(f"  Home Win: {result['match_outcomes']['home_win']:.1%}")
    print(f"  Draw: {result['match_outcomes']['draw']:.1%}")
    print(f"  Away Win: {result['match_outcomes']['away_win']:.1%}")
    print(f"\nOver/Under 2.5:")
    print(f"  Over: {result['over_under']['over_2.5']:.1%}")
    print(f"  Under: {result['over_under']['under_2.5']:.1%}")
