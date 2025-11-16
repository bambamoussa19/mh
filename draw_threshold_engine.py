class DrawThresholdEngine:
    """
    Dynamic draw threshold engine based on 6 key factors:
    1. Possession parity
    2. xG differential
    3. Tactical friction
    4. Fatigue levels
    5. Midweek factor
    6. Set-piece threat
    """
    def __init__(self):
        self.base_draw_threshold = 0.25
        self.possession_parity_weight = 0.15
        self.xg_diff_weight = 0.20
        self.tactical_friction_weight = 0.20
        self.fatigue_weight = 0.15
        self.midweek_weight = 0.15
        self.set_piece_weight = 0.15

    def calculate_draw_probability(self, match_factors):
        """
        Calculate dynamic draw probability based on multiple factors.
        
        :param match_factors: Dict with keys:
            - possession_parity (0-1): 1 = equal possession, 0 = one-sided
            - xg_differential (float): Absolute difference in xG
            - tactical_friction (0-1): Defensive strength indicator
            - fatigue_home (0-1): 0 = rested, 1 = exhausted
            - fatigue_away (0-1): 0 = rested, 1 = exhausted
            - midweek_played (bool): True if midweek matches played
            - set_piece_threat (0-1): Likelihood of late set-piece goals
        :return: Draw probability (0-1 scale)
        """
        if not match_factors:
            return self.base_draw_threshold
        
        # Factor 1: Possession Parity (higher = more likely draw)
        possession_parity = match_factors.get('possession_parity', 0.5)
        possession_contribution = possession_parity * self.possession_parity_weight
        
        # Factor 2: xG Differential (smaller diff = more likely draw)
        xg_diff = match_factors.get('xg_differential', 0.5)
        xg_contribution = max(0, (1.0 - min(1.0, xg_diff / 1.5))) * self.xg_diff_weight
        
        # Factor 3: Tactical Friction (higher friction = more likely draw)
        tactical_friction = match_factors.get('tactical_friction', 0.5)
        friction_contribution = tactical_friction * self.tactical_friction_weight
        
        # Factor 4: Fatigue (both teams fatigued = more likely draw)
        fatigue_home = match_factors.get('fatigue_home', 0.0)
        fatigue_away = match_factors.get('fatigue_away', 0.0)
        avg_fatigue = (fatigue_home + fatigue_away) / 2
        fatigue_contribution = avg_fatigue * self.fatigue_weight
        
        # Factor 5: Midweek Factor (both played midweek = more likely draw)
        midweek_played = match_factors.get('midweek_played', False)
        midweek_contribution = (0.1 if midweek_played else 0.0)
        
        # Factor 6: Set-piece Threat (high threat = late equalizers more likely)
        set_piece_threat = match_factors.get('set_piece_threat', 0.5)
        set_piece_contribution = set_piece_threat * self.set_piece_weight
        
        # Calculate total draw probability
        draw_probability = (
            self.base_draw_threshold +
            possession_contribution +
            xg_contribution +
            friction_contribution +
            fatigue_contribution +
            midweek_contribution +
            set_piece_contribution
        )
        
        # Clamp between reasonable bounds (10% to 60%)
        draw_probability = max(0.10, min(0.60, draw_probability))
        
        return draw_probability

    def intelligent_draw(self, match_factors=None):
        """
        Determine if draw is predicted based on intelligent analysis.
        
        :param match_factors: Dict of match factors
        :return: String describing draw prediction
        """
        draw_prob = self.calculate_draw_probability(match_factors)
        
        if draw_prob >= 0.40:
            return f'High Draw Probability: {draw_prob:.1%}'
        elif draw_prob >= 0.30:
            return f'Moderate Draw Probability: {draw_prob:.1%}'
        else:
            return f'Low Draw Probability: {draw_prob:.1%}'
    
    def get_draw_adjustment(self, match_factors):
        """
        Get probability adjustment to apply to outcome distribution.
        
        :return: Dict with outcome adjustments
        """
        draw_prob = self.calculate_draw_probability(match_factors)
        base_draw = 0.25
        
        draw_boost = draw_prob - base_draw
        
        # Redistribute from home/away wins to draw
        return {
            'home_win': -draw_boost * 0.5,
            'draw': draw_boost,
            'away_win': -draw_boost * 0.5
        }

# Usage example:
if __name__ == '__main__':
    engine = DrawThresholdEngine()
    
    # Example: Hamburg 1-1 Dortmund scenario
    match_factors = {
        'possession_parity': 0.9,  # Very even possession
        'xg_differential': 0.3,    # Small xG difference
        'tactical_friction': 0.8,  # High defensive resistance
        'fatigue_home': 0.4,
        'fatigue_away': 0.5,
        'midweek_played': True,
        'set_piece_threat': 0.7
    }
    
    result = engine.intelligent_draw(match_factors)
    draw_prob = engine.calculate_draw_probability(match_factors)
    print(result)
    print(f"Calculated Draw Probability: {draw_prob:.1%}")