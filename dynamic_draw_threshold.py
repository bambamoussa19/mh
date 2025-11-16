"""
Dynamic Draw Threshold Module

Fixes draw prediction blindness by dynamically adjusting draw probabilities
based on real match factors instead of using fixed thresholds.

This module works in conjunction with draw_threshold_engine.py to provide
comprehensive draw analysis.
"""

import numpy as np


class DynamicDrawThreshold:
    """
    Dynamic draw threshold calculator with context-aware adjustments.
    """
    
    def __init__(self):
        self.league_draw_rates = {
            'bundesliga': 0.26,
            'premier_league': 0.25,
            'la_liga': 0.24,
            'serie_a': 0.27,
            'ligue_1': 0.26,
            'default': 0.25
        }
        
    def calculate_contextual_draw_threshold(self, match_context):
        """
        Calculate dynamic draw threshold based on match context.
        
        :param match_context: Dict with match-specific factors:
            - league (str): League identifier
            - home_recent_draws (int): Recent draw count for home team
            - away_recent_draws (int): Recent draw count for away team
            - possession_expected_parity (bool): Expected even possession
            - xg_expected_close (bool): Expected close xG
            - tactical_styles_matched (bool): Similar tactical approaches
            - importance_level (str): 'high', 'medium', 'low'
        :return: Dynamic threshold (0-1 scale)
        """
        if not match_context:
            return 0.25
        
        # Start with league baseline
        league = match_context.get('league', 'default').lower()
        threshold = self.league_draw_rates.get(league, 0.25)
        
        # Adjustment 1: Recent draw history
        home_draws = match_context.get('home_recent_draws', 0)
        away_draws = match_context.get('away_recent_draws', 0)
        avg_recent_draws = (home_draws + away_draws) / 2
        
        if avg_recent_draws >= 3:  # In last 5 games
            threshold += 0.08
        elif avg_recent_draws >= 2:
            threshold += 0.05
        elif avg_recent_draws >= 1:
            threshold += 0.02
        
        # Adjustment 2: Expected possession parity
        if match_context.get('possession_expected_parity', False):
            threshold += 0.06
        
        # Adjustment 3: Expected close xG
        if match_context.get('xg_expected_close', False):
            threshold += 0.07
        
        # Adjustment 4: Matched tactical styles
        if match_context.get('tactical_styles_matched', False):
            threshold += 0.05
        
        # Adjustment 5: Match importance (less important = more draws)
        importance = match_context.get('importance_level', 'medium')
        if importance == 'low':
            threshold += 0.03
        elif importance == 'high':
            threshold -= 0.02
        
        # Clamp to reasonable range
        threshold = max(0.15, min(0.55, threshold))
        
        return threshold
    
    def apply_late_game_draw_adjustment(self, current_probs, game_state):
        """
        Apply late-game adjustments for draw probability.
        Accounts for set-pieces, fatigue, and game management.
        
        :param current_probs: Current probability distribution
        :param game_state: Dict with:
            - minute (int): Current match minute
            - score_difference (int): Goal difference
            - set_piece_count_recent (int): Set pieces in last 15 min
            - fatigue_level (float): 0-1 scale
        :return: Adjusted probabilities
        """
        if not game_state:
            return current_probs
        
        minute = game_state.get('minute', 90)
        score_diff = game_state.get('score_difference', 0)
        
        # Late game draw scenarios (75+ minutes)
        if minute >= 75:
            # Close game scenarios increase draw likelihood
            if score_diff == 0:
                # Already drawing, likelihood increases
                draw_boost = 0.05
            elif abs(score_diff) == 1:
                # One-goal game, equalizer possible
                set_pieces = game_state.get('set_piece_count_recent', 0)
                fatigue = game_state.get('fatigue_level', 0.5)
                
                # More set pieces + fatigue = higher draw chance
                draw_boost = 0.02 + (set_pieces * 0.01) + (fatigue * 0.02)
            else:
                # Multi-goal difference, unlikely to draw
                draw_boost = 0.0
            
            # Apply boost
            adjusted = current_probs.copy()
            adjusted['draw'] = min(0.60, adjusted.get('draw', 0.25) + draw_boost)
            
            # Renormalize
            total = sum(adjusted.values())
            adjusted = {k: v / total for k, v in adjusted.items()}
            
            return adjusted
        
        return current_probs
    
    def get_draw_clustering_boost(self, team_draw_history):
        """
        Calculate boost for teams that show draw clustering patterns.
        
        :param team_draw_history: Dict with:
            - recent_sequence (list): Recent results ['W', 'D', 'D', 'L']
            - seasonal_draw_rate (float): 0-1 scale
            - h2h_draw_rate (float): Head-to-head draw rate
        :return: Boost value (0-0.15)
        """
        if not team_draw_history:
            return 0.0
        
        boost = 0.0
        
        # Check for consecutive draws
        sequence = team_draw_history.get('recent_sequence', [])
        consecutive_draws = 0
        for result in reversed(sequence):
            if result == 'D':
                consecutive_draws += 1
            else:
                break
        
        boost += min(0.08, consecutive_draws * 0.03)
        
        # Check seasonal draw rate
        seasonal_rate = team_draw_history.get('seasonal_draw_rate', 0.25)
        if seasonal_rate > 0.35:
            boost += 0.05
        elif seasonal_rate > 0.30:
            boost += 0.03
        
        # Check H2H history
        h2h_rate = team_draw_history.get('h2h_draw_rate', 0.25)
        if h2h_rate > 0.40:
            boost += 0.04
        
        return min(0.15, boost)
    
    def predict_draw_scenario_type(self, match_factors):
        """
        Classify the type of draw scenario expected.
        
        :param match_factors: Dict with match characteristics
        :return: Dict with scenario type and characteristics
        """
        xg_diff = match_factors.get('xg_differential', 0.5)
        possession_parity = match_factors.get('possession_parity', 0.5)
        tactical_friction = match_factors.get('tactical_friction', 0.5)
        
        # Scenario classification
        if xg_diff < 0.3 and possession_parity > 0.8:
            scenario_type = 'tactical_stalemate'
            expected_score = '0-0 or 1-1'
            confidence = 0.75
        elif tactical_friction > 0.7:
            scenario_type = 'defensive_battle'
            expected_score = '0-0 or 1-1'
            confidence = 0.70
        elif xg_diff < 0.4 and match_factors.get('fatigue_both_high', False):
            scenario_type = 'fatigue_draw'
            expected_score = '1-1 or 2-2'
            confidence = 0.65
        elif match_factors.get('set_piece_threat', 0) > 0.7:
            scenario_type = 'late_equalizer'
            expected_score = '1-1 or 2-2'
            confidence = 0.60
        else:
            scenario_type = 'neutral'
            expected_score = 'varied'
            confidence = 0.50
        
        return {
            'scenario_type': scenario_type,
            'expected_score': expected_score,
            'confidence': confidence,
            'description': self._get_scenario_description(scenario_type)
        }
    
    def _get_scenario_description(self, scenario_type):
        """Get human-readable description of scenario."""
        descriptions = {
            'tactical_stalemate': 'Teams cancel each other out with similar tactics',
            'defensive_battle': 'Both defenses dominate, low scoring expected',
            'fatigue_draw': 'Both teams fatigued, leading to conservative play',
            'late_equalizer': 'High chance of late set-piece equalizer',
            'neutral': 'Standard match dynamics'
        }
        return descriptions.get(scenario_type, 'Unknown scenario')


# Example usage and testing
if __name__ == '__main__':
    ddt = DynamicDrawThreshold()
    
    print("="*70)
    print("DYNAMIC DRAW THRESHOLD - Module Test")
    print("="*70)
    
    # Test 1: Hamburg vs Dortmund scenario (should predict high draw)
    print("\nTest 1: Hamburg 1-1 Dortmund Scenario")
    print("-"*70)
    
    hamburg_context = {
        'league': 'bundesliga',
        'home_recent_draws': 2,
        'away_recent_draws': 1,
        'possession_expected_parity': True,
        'xg_expected_close': True,
        'tactical_styles_matched': True,
        'importance_level': 'medium'
    }
    
    threshold = ddt.calculate_contextual_draw_threshold(hamburg_context)
    print(f"Dynamic Draw Threshold: {threshold:.1%}")
    print(f"Expected: 40%+ (was 19% with old logic)")
    
    match_factors = {
        'xg_differential': 0.2,
        'possession_parity': 0.95,
        'tactical_friction': 0.8,
        'fatigue_both_high': False,
        'set_piece_threat': 0.7
    }
    
    scenario = ddt.predict_draw_scenario_type(match_factors)
    print(f"\nScenario Type: {scenario['scenario_type']}")
    print(f"Expected Score: {scenario['expected_score']}")
    print(f"Confidence: {scenario['confidence']:.1%}")
    print(f"Description: {scenario['description']}")
    
    # Test 2: Bayern vs Union scenario
    print("\n\nTest 2: Bayern 2-2 Union Scenario")
    print("-"*70)
    
    bayern_context = {
        'league': 'bundesliga',
        'home_recent_draws': 1,
        'away_recent_draws': 3,
        'possession_expected_parity': False,
        'xg_expected_close': True,
        'tactical_styles_matched': False,
        'importance_level': 'medium'
    }
    
    threshold2 = ddt.calculate_contextual_draw_threshold(bayern_context)
    print(f"Dynamic Draw Threshold: {threshold2:.1%}")
    print(f"Expected: 45%+ (was 24% with old logic)")
    
    # Test late game adjustment
    print("\n\nTest 3: Late Game Draw Adjustment")
    print("-"*70)
    
    current = {'home_win': 0.40, 'draw': 0.35, 'away_win': 0.25}
    game_state = {
        'minute': 80,
        'score_difference': 0,
        'set_piece_count_recent': 4,
        'fatigue_level': 0.7
    }
    
    adjusted = ddt.apply_late_game_draw_adjustment(current, game_state)
    print(f"Before adjustment: {current}")
    print(f"After late game adjustment: {adjusted}")
    
    print("\n" + "="*70)
