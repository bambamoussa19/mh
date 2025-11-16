"""
Draw Threshold Engine - Production Implementation

Uses predictive modeling instead of random number generation to
determine draw likelihood based on match characteristics.

Addresses audit finding: "draw_threshold_engine.py uses random.randint, not predictive"
"""

import numpy as np


class DrawThresholdEngine:
    def __init__(self):
        # Base draw probability in football is ~25-28%
        self.base_draw_probability = 0.27
        
        # Thresholds for draw indicators
        self.form_difference_threshold = 0.15  # Similar form teams
        self.strength_parity_threshold = 0.10  # Similar strength
        self.defensive_solidity_threshold = 0.70  # Both defensive
        
    def calculate_draw_probability(self, match_features):
        """
        Calculate draw probability using match features.
        
        :param match_features: Dict with keys:
            - home_form: Float (0-1)
            - away_form: Float (0-1)
            - home_strength: Float (0-1)
            - away_strength: Float (0-1)
            - home_defensive_rating: Float (0-1)
            - away_defensive_rating: Float (0-1)
            - head_to_head_draws: Int (recent H2H draws)
            - home_goals_avg: Float
            - away_goals_avg: Float
            - league_draw_rate: Float (0-1, optional)
        :return: Draw probability (0-1)
        """
        home_form = match_features.get('home_form', 0.5)
        away_form = match_features.get('away_form', 0.5)
        home_strength = match_features.get('home_strength', 0.5)
        away_strength = match_features.get('away_strength', 0.5)
        home_defensive = match_features.get('home_defensive_rating', 0.5)
        away_defensive = match_features.get('away_defensive_rating', 0.5)
        h2h_draws = match_features.get('head_to_head_draws', 0)
        home_goals_avg = match_features.get('home_goals_avg', 1.5)
        away_goals_avg = match_features.get('away_goals_avg', 1.5)
        league_draw_rate = match_features.get('league_draw_rate', self.base_draw_probability)
        
        # Start with league baseline
        draw_prob = league_draw_rate
        
        # 1. Form parity adjustment (±15%)
        form_diff = abs(home_form - away_form)
        if form_diff < self.form_difference_threshold:
            # Similar form increases draw likelihood
            parity_boost = (self.form_difference_threshold - form_diff) / self.form_difference_threshold
            draw_prob += 0.15 * parity_boost
        else:
            # Large form difference decreases draw likelihood
            draw_prob -= 0.10 * min(1.0, (form_diff - self.form_difference_threshold) / 0.3)
        
        # 2. Strength parity adjustment (±12%)
        strength_diff = abs(home_strength - away_strength)
        if strength_diff < self.strength_parity_threshold:
            parity_boost = (self.strength_parity_threshold - strength_diff) / self.strength_parity_threshold
            draw_prob += 0.12 * parity_boost
        else:
            draw_prob -= 0.08 * min(1.0, (strength_diff - self.strength_parity_threshold) / 0.3)
        
        # 3. Defensive solidity adjustment (±20%)
        avg_defensive_rating = (home_defensive + away_defensive) / 2
        if avg_defensive_rating >= self.defensive_solidity_threshold:
            # Both teams defensive = more draws
            defensive_boost = (avg_defensive_rating - self.defensive_solidity_threshold) / (1 - self.defensive_solidity_threshold)
            draw_prob += 0.20 * defensive_boost
        
        # 4. Low scoring tendency adjustment (±10%)
        total_goals_avg = home_goals_avg + away_goals_avg
        if total_goals_avg < 2.3:  # Low scoring match expected
            draw_prob += 0.10 * (2.3 - total_goals_avg) / 2.3
        elif total_goals_avg > 3.0:  # High scoring reduces draws
            draw_prob -= 0.08 * min(1.0, (total_goals_avg - 3.0) / 2.0)
        
        # 5. Head-to-head history (±8%)
        if h2h_draws >= 3:
            draw_prob += 0.08
        elif h2h_draws >= 2:
            draw_prob += 0.05
        
        # Ensure probability is in valid range [0, 1]
        draw_prob = max(0.05, min(0.70, draw_prob))
        
        return round(draw_prob, 4)
    
    def intelligent_draw_decision(self, match_features, confidence_threshold=0.35):
        """
        Make a draw prediction with confidence assessment.
        
        :param match_features: Match feature dict
        :param confidence_threshold: Minimum probability to predict draw
        :return: Dict with decision and details
        """
        draw_prob = self.calculate_draw_probability(match_features)
        
        # Determine confidence level
        if draw_prob >= 0.45:
            confidence = 'High'
        elif draw_prob >= confidence_threshold:
            confidence = 'Medium'
        else:
            confidence = 'Low'
        
        is_draw_prediction = draw_prob >= confidence_threshold
        
        return {
            'prediction': 'Draw' if is_draw_prediction else 'No Draw',
            'probability': draw_prob,
            'confidence': confidence,
            'details': self._get_decision_factors(match_features, draw_prob)
        }
    
    def _get_decision_factors(self, match_features, draw_prob):
        """Extract key factors influencing the draw decision."""
        factors = []
        
        home_form = match_features.get('home_form', 0.5)
        away_form = match_features.get('away_form', 0.5)
        form_diff = abs(home_form - away_form)
        
        if form_diff < self.form_difference_threshold:
            factors.append(f"Similar form (diff: {form_diff:.2f})")
        
        home_strength = match_features.get('home_strength', 0.5)
        away_strength = match_features.get('away_strength', 0.5)
        strength_diff = abs(home_strength - away_strength)
        
        if strength_diff < self.strength_parity_threshold:
            factors.append(f"Evenly matched (diff: {strength_diff:.2f})")
        
        avg_defensive = (match_features.get('home_defensive_rating', 0.5) + 
                        match_features.get('away_defensive_rating', 0.5)) / 2
        if avg_defensive >= self.defensive_solidity_threshold:
            factors.append(f"Strong defenses (avg: {avg_defensive:.2f})")
        
        total_goals = (match_features.get('home_goals_avg', 1.5) + 
                      match_features.get('away_goals_avg', 1.5))
        if total_goals < 2.3:
            factors.append(f"Low scoring trend ({total_goals:.2f} goals/match)")
        
        return factors if factors else ["Standard match profile"]