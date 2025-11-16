"""
Advanced Metrics Enhanced

Enhanced metrics for prediction system including DrawClusteringIndex,
DefensiveSuperiorityMultiplier, FormTrendMomentum, and HomeAdvantageContext.
"""

import numpy as np


class DrawClusteringIndex:
    """
    Measures tendency for draws to cluster together in team's recent matches.
    Teams that draw frequently often continue that pattern.
    """
    
    def __init__(self):
        self.lookback_window = 10  # Last 10 matches
        
    def calculate(self, recent_results):
        """
        Calculate draw clustering index.
        
        :param recent_results: List of recent match results ('W', 'D', 'L')
        :return: Index value (0-1), higher = more draw clustering
        """
        if not recent_results or len(recent_results) < 3:
            return 0.5  # Neutral if insufficient data
        
        # Count draws
        draw_count = sum(1 for r in recent_results if r == 'D')
        draw_rate = draw_count / len(recent_results)
        
        # Check for draw clusters (consecutive draws)
        cluster_score = 0
        consecutive_count = 0
        max_consecutive = 0
        
        for result in recent_results:
            if result == 'D':
                consecutive_count += 1
                max_consecutive = max(max_consecutive, consecutive_count)
            else:
                consecutive_count = 0
        
        # Clustering bonus for consecutive draws
        if max_consecutive >= 3:
            cluster_score = 0.3
        elif max_consecutive >= 2:
            cluster_score = 0.15
        
        # Combined index
        index = min(1.0, draw_rate + cluster_score)
        
        return round(index, 3)
    
    def predict_draw_continuation(self, recent_results, current_position):
        """
        Predict likelihood of draw pattern continuing.
        
        :param recent_results: List of recent results
        :param current_position: Current league position/standing
        :return: Continuation probability
        """
        index = self.calculate(recent_results)
        
        # Mid-table teams (positions 8-14 in 18-team league) more likely to continue draws
        if 7 <= current_position <= 14:
            position_factor = 1.2
        else:
            position_factor = 1.0
        
        continuation_prob = index * position_factor
        
        return min(1.0, continuation_prob)


class DefensiveSuperiorityMultiplier:
    """
    Multiplier based on defensive quality difference between teams.
    Strong defense vs weak attack amplifies clean sheet probability.
    """
    
    def __init__(self):
        self.baseline_multiplier = 1.0
        
    def calculate(self, defensive_metrics, opponent_attack_metrics):
        """
        Calculate defensive superiority multiplier.
        
        :param defensive_metrics: Dict with:
            - goals_conceded_avg: Float
            - xg_conceded_avg: Float
            - clean_sheet_rate: Float (0-1)
            - defensive_rating: Float (0-1)
        :param opponent_attack_metrics: Dict with:
            - goals_scored_avg: Float
            - xg_avg: Float
            - shot_accuracy: Float (0-1)
            - attack_rating: Float (0-1)
        :return: Multiplier (0.5-2.0)
        """
        # Defensive strength
        defensive_rating = defensive_metrics.get('defensive_rating', 0.5)
        clean_sheet_rate = defensive_metrics.get('clean_sheet_rate', 0.3)
        xg_conceded = defensive_metrics.get('xg_conceded_avg', 1.5)
        
        # Opponent attack strength
        attack_rating = opponent_attack_metrics.get('attack_rating', 0.5)
        goals_scored = opponent_attack_metrics.get('goals_scored_avg', 1.5)
        xg_for = opponent_attack_metrics.get('xg_avg', 1.5)
        
        # Calculate superiority gap
        defense_score = (defensive_rating * 0.5 + 
                        clean_sheet_rate * 0.3 + 
                        max(0, 1 - xg_conceded / 2.0) * 0.2)
        
        attack_score = (attack_rating * 0.5 + 
                       min(1.0, goals_scored / 2.5) * 0.3 + 
                       min(1.0, xg_for / 2.0) * 0.2)
        
        superiority_gap = defense_score - attack_score
        
        # Convert gap to multiplier
        # Positive gap (defense > attack) = higher multiplier
        # Negative gap (attack > defense) = lower multiplier
        multiplier = self.baseline_multiplier + (superiority_gap * 1.0)
        
        # Clamp to reasonable range
        multiplier = max(0.5, min(2.0, multiplier))
        
        return round(multiplier, 3)
    
    def apply_to_probability(self, base_probability, multiplier):
        """
        Apply multiplier to base probability with normalization.
        
        :param base_probability: Base clean sheet or outcome probability
        :param multiplier: Calculated multiplier
        :return: Adjusted probability
        """
        adjusted = base_probability * multiplier
        
        # Keep in valid probability range
        adjusted = max(0.01, min(0.95, adjusted))
        
        return round(adjusted, 4)


class FormTrendMomentum:
    """
    Analyzes form trends to determine momentum direction and strength.
    Different from simple form - looks at trajectory.
    """
    
    def __init__(self):
        self.window_size = 6  # Last 6 matches for trend
        
    def calculate(self, recent_performances):
        """
        Calculate form trend momentum.
        
        :param recent_performances: List of performance scores (0-3 scale)
            3 = excellent win, 2 = good win, 1 = draw, 0 = loss
        :return: Momentum dict with score and direction
        """
        if not recent_performances or len(recent_performances) < 3:
            return {'momentum_score': 0, 'direction': 'neutral', 'strength': 'weak'}
        
        # Calculate trend using linear regression
        x = np.arange(len(recent_performances))
        y = np.array(recent_performances)
        
        if len(x) >= 2:
            coefficients = np.polyfit(x, y, 1)
            slope = coefficients[0]
        else:
            slope = 0
        
        # Calculate recent average vs overall average
        overall_avg = np.mean(y)
        recent_avg = np.mean(y[-3:]) if len(y) >= 3 else overall_avg
        
        momentum_differential = recent_avg - overall_avg
        
        # Combine slope and differential for momentum score
        momentum_score = (slope * 0.6 + momentum_differential * 0.4)
        
        # Determine direction and strength
        if momentum_score > 0.3:
            direction = 'improving'
            strength = 'strong' if momentum_score > 0.6 else 'moderate'
        elif momentum_score < -0.3:
            direction = 'declining'
            strength = 'strong' if momentum_score < -0.6 else 'moderate'
        else:
            direction = 'neutral'
            strength = 'weak'
        
        return {
            'momentum_score': round(momentum_score, 3),
            'direction': direction,
            'strength': strength,
            'recent_avg': round(recent_avg, 2),
            'overall_avg': round(overall_avg, 2),
            'trend_slope': round(slope, 3)
        }
    
    def predict_continuation(self, momentum_data):
        """
        Predict likelihood of momentum continuing.
        
        :param momentum_data: Output from calculate()
        :return: Continuation probability (0-1)
        """
        score = momentum_data['momentum_score']
        strength = momentum_data['strength']
        
        # Strong momentum more likely to continue
        if strength == 'strong':
            base_continuation = 0.7
        elif strength == 'moderate':
            base_continuation = 0.5
        else:
            base_continuation = 0.3
        
        # Adjust for score magnitude
        adjustment = abs(score) * 0.2
        continuation_prob = base_continuation + adjustment
        
        return min(0.9, continuation_prob)


class HomeAdvantageContext:
    """
    Context-aware home advantage calculation.
    Considers league, team strength, and situational factors.
    """
    
    def __init__(self):
        # Default home advantage by league tier
        self.league_defaults = {
            'top_tier': 0.58,      # ~58% win rate at home
            'second_tier': 0.60,   # Slightly higher
            'third_tier': 0.62     # Even higher
        }
        
    def calculate(self, home_team_data, context_factors):
        """
        Calculate context-aware home advantage.
        
        :param home_team_data: Dict with:
            - home_record: Dict with wins, draws, losses at home
            - overall_strength: Float (0-1)
            - fan_attendance_avg: Int
            - travel_distance_opponents_avg: Float (km)
        :param context_factors: Dict with:
            - league_tier: String ('top_tier', 'second_tier', 'third_tier')
            - is_derby: Bool
            - is_relegation_battle: Bool
            - is_top_of_table: Bool
            - opponent_travel_distance: Float
        :return: Home advantage factor (0.5-1.5)
        """
        # Start with league baseline
        league_tier = context_factors.get('league_tier', 'top_tier')
        base_advantage = self.league_defaults.get(league_tier, 0.58)
        
        # Calculate actual home performance
        home_record = home_team_data.get('home_record', {})
        home_wins = home_record.get('wins', 0)
        home_total = sum(home_record.values()) if home_record else 1
        actual_home_rate = home_wins / home_total if home_total > 0 else 0.5
        
        # Blend actual with baseline (60% actual, 40% baseline for robustness)
        blended_rate = actual_home_rate * 0.6 + base_advantage * 0.4
        
        # Context adjustments
        advantage_factor = blended_rate / 0.5  # Normalize to factor (1.0 = neutral)
        
        # Derby boost
        if context_factors.get('is_derby', False):
            advantage_factor *= 1.15
        
        # Relegation battle (home desperation)
        if context_factors.get('is_relegation_battle', False):
            advantage_factor *= 1.10
        
        # Top of table (less home advantage, quality matters more)
        if context_factors.get('is_top_of_table', False):
            advantage_factor *= 0.95
        
        # Travel distance factor
        travel_distance = context_factors.get('opponent_travel_distance', 0)
        if travel_distance > 500:  # Long distance travel
            advantage_factor *= 1.08
        elif travel_distance > 300:
            advantage_factor *= 1.04
        
        # Attendance factor
        attendance = home_team_data.get('fan_attendance_avg', 0)
        if attendance > 40000:
            advantage_factor *= 1.05
        elif attendance < 10000:
            advantage_factor *= 0.98
        
        # Clamp to reasonable range
        advantage_factor = max(0.5, min(1.5, advantage_factor))
        
        return round(advantage_factor, 3)
    
    def apply_to_probabilities(self, base_probabilities, advantage_factor):
        """
        Apply home advantage to match outcome probabilities.
        
        :param base_probabilities: Dict with home_win, draw, away_win
        :param advantage_factor: Home advantage multiplier
        :return: Adjusted probabilities
        """
        home_win = base_probabilities.get('home_win', 0.33)
        draw = base_probabilities.get('draw', 0.33)
        away_win = base_probabilities.get('away_win', 0.33)
        
        # Apply factor to home win, reduce others proportionally
        if advantage_factor > 1.0:
            # Boost home win
            boost = (advantage_factor - 1.0) * home_win
            home_win += boost
            
            # Reduce draw and away proportionally
            reduction_ratio = boost / (draw + away_win) if (draw + away_win) > 0 else 0
            draw -= draw * reduction_ratio
            away_win -= away_win * reduction_ratio
        else:
            # Reduce home win (weak home advantage)
            reduction = (1.0 - advantage_factor) * home_win
            home_win -= reduction
            
            # Boost draw and away proportionally
            boost_ratio = reduction / 2.0
            draw += boost_ratio
            away_win += boost_ratio
        
        # Normalize
        total = home_win + draw + away_win
        if total > 0:
            home_win /= total
            draw /= total
            away_win /= total
        
        return {
            'home_win': round(home_win, 4),
            'draw': round(draw, 4),
            'away_win': round(away_win, 4)
        }


# Example usage
if __name__ == "__main__":
    # Test DrawClusteringIndex
    dci = DrawClusteringIndex()
    results = ['D', 'D', 'W', 'D', 'L', 'D', 'D', 'W']
    print(f"Draw Clustering Index: {dci.calculate(results)}")
    
    # Test DefensiveSuperiorityMultiplier
    dsm = DefensiveSuperiorityMultiplier()
    defensive = {'defensive_rating': 0.8, 'clean_sheet_rate': 0.5, 'xg_conceded_avg': 1.0}
    attack = {'attack_rating': 0.4, 'goals_scored_avg': 1.0, 'xg_avg': 1.2}
    print(f"Defensive Superiority Multiplier: {dsm.calculate(defensive, attack)}")
    
    # Test FormTrendMomentum
    ftm = FormTrendMomentum()
    performances = [1, 1, 2, 2, 3, 3]  # Improving trend
    momentum = ftm.calculate(performances)
    print(f"Form Trend Momentum: {momentum}")
    
    # Test HomeAdvantageContext
    hac = HomeAdvantageContext()
    home_data = {'home_record': {'wins': 8, 'draws': 3, 'losses': 1}, 'overall_strength': 0.7}
    context = {'league_tier': 'top_tier', 'is_derby': True}
    print(f"Home Advantage Factor: {hac.calculate(home_data, context)}")
