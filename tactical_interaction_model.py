"""
Tactical Interaction Model - Production Implementation

Analyzes possession efficiency and defensive resistance to provide
accurate tactical insights for match predictions.

Addresses audit finding: "Possession efficiency not calculated (52% possession 
treated same regardless of shot accuracy)"
"""

import numpy as np


class TacticalInteractionModel:
    def __init__(self):
        # Thresholds for scenario detection
        self.high_possession_threshold = 55.0
        self.low_possession_threshold = 45.0
        self.deep_block_shots_threshold = 15
        
    def analyze_possession_efficiency(self, possession_data):
        """
        Analyze possession efficiency during matches.
        
        Calculates actual conversion of possession into dangerous situations.
        
        :param possession_data: Dict with keys:
            - possession_pct: Float (0-100)
            - shots: Int
            - shots_on_target: Int
            - passes_completed: Int
            - passes_attempted: Int
            - final_third_entries: Int (optional)
        :return: Efficiency score (0.0 - 1.0)
        """
        possession_pct = possession_data.get('possession_pct', 50.0)
        shots = possession_data.get('shots', 0)
        shots_on_target = possession_data.get('shots_on_target', 0)
        passes_completed = possession_data.get('passes_completed', 0)
        passes_attempted = possession_data.get('passes_attempted', 1)
        final_third_entries = possession_data.get('final_third_entries', 0)
        
        # Avoid division by zero
        if possession_pct == 0 or passes_attempted == 0:
            return 0.0
            
        # Shot accuracy component (40% weight)
        shot_accuracy = shots_on_target / shots if shots > 0 else 0
        shot_volume_per_possession = (shots / possession_pct) * 10  # Normalize
        shot_component = min(1.0, (shot_accuracy * 0.6 + 
                                    min(1.0, shot_volume_per_possession / 2) * 0.4))
        
        # Pass completion component (30% weight)
        pass_completion = passes_completed / passes_attempted
        pass_component = pass_completion
        
        # Final third penetration component (30% weight)
        penetration_per_possession = (final_third_entries / possession_pct) * 10
        penetration_component = min(1.0, penetration_per_possession / 3)
        
        # Weighted efficiency score
        efficiency_score = (shot_component * 0.4 + 
                           pass_component * 0.3 + 
                           penetration_component * 0.3)
        
        return round(efficiency_score, 3)

    def analyze_defensive_resistance(self, defensive_data):
        """
        Analyze the effectiveness of defensive strategies.
        
        :param defensive_data: Dict with keys:
            - shots_allowed: Int
            - shots_on_target_allowed: Int
            - tackles_won: Int
            - tackles_attempted: Int
            - interceptions: Int
            - clearances: Int
            - possession_against: Float (0-100)
        :return: Resistance score (0.0 - 1.0)
        """
        shots_allowed = defensive_data.get('shots_allowed', 0)
        shots_on_target_allowed = defensive_data.get('shots_on_target_allowed', 0)
        tackles_won = defensive_data.get('tackles_won', 0)
        tackles_attempted = defensive_data.get('tackles_attempted', 1)
        interceptions = defensive_data.get('interceptions', 0)
        clearances = defensive_data.get('clearances', 0)
        possession_against = defensive_data.get('possession_against', 50.0)
        
        # Shot suppression component (40% weight)
        expected_shots = possession_against / 5  # Rough baseline
        shot_suppression = max(0, 1 - (shots_allowed / max(expected_shots, 1)))
        shot_accuracy_allowed = (shots_on_target_allowed / shots_allowed 
                                 if shots_allowed > 0 else 0)
        shot_component = (shot_suppression * 0.7 + (1 - shot_accuracy_allowed) * 0.3)
        
        # Tackle success component (30% weight)
        tackle_success = tackles_won / tackles_attempted if tackles_attempted > 0 else 0
        tackle_component = tackle_success
        
        # Defensive action volume component (30% weight)
        total_defensive_actions = interceptions + clearances + tackles_won
        action_volume_per_possession = (total_defensive_actions / possession_against) * 10
        action_component = min(1.0, action_volume_per_possession / 4)
        
        # Weighted resistance score
        resistance_score = (shot_component * 0.4 + 
                           tackle_component * 0.3 + 
                           action_component * 0.3)
        
        return round(resistance_score, 3)

    def provide_pick_recommendations(self, scenario):
        """
        Provide pick recommendations based on the scenario.
        
        :param scenario: 'deep_block', 'possession_dominance', 'balanced'
        :return: Dict with recommendations
        """
        recommendations = {
            'deep_block': {
                'primary': 'Under 2.5 Goals',
                'secondary': 'Draw or Low Scoring',
                'reasoning': 'Deep defensive block limits scoring opportunities'
            },
            'possession_dominance': {
                'primary': 'Team Dominant Win',
                'secondary': 'Over 2.5 Goals',
                'reasoning': 'Possession dominance with high efficiency'
            },
            'balanced': {
                'primary': 'Either Team Win',
                'secondary': 'BTTS (Both Teams To Score)',
                'reasoning': 'Balanced tactical battle'
            },
            'inefficient_possession': {
                'primary': 'Draw',
                'secondary': 'Under 2.5 Goals',
                'reasoning': 'High possession but low conversion efficiency'
            }
        }
        return recommendations.get(scenario, recommendations['balanced'])

    def detect_scenario(self, match_data):
        """
        Detect tactical scenario using match data.
        
        :param match_data: Dict with possession_data and defensive_data
        :return: Scenario type
        """
        possession_data = match_data.get('possession_data', {})
        defensive_data = match_data.get('defensive_data', {})
        
        possession_pct = possession_data.get('possession_pct', 50.0)
        efficiency = self.analyze_possession_efficiency(possession_data)
        resistance = self.analyze_defensive_resistance(defensive_data)
        
        # Scenario detection logic
        if possession_pct >= self.high_possession_threshold:
            if efficiency >= 0.6:
                return 'possession_dominance'
            else:
                return 'inefficient_possession'
        elif possession_pct <= self.low_possession_threshold:
            if resistance >= 0.7:
                return 'deep_block'
            else:
                return 'balanced'
        else:
            return 'balanced'