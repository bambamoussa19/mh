class TacticalInteractionModel:
    def __init__(self):
        self.tactical_friction_threshold = 0.3
        self.possession_parity_threshold = 5.0

    def analyze_possession_efficiency(self, possession_data):
        """
        Analyze possession efficiency during matches.
        :param possession_data: Dict with keys 'possession_pct', 'shots', 'shots_on_target', 'xG'
        :return: Efficiency score (0-1 scale).
        """
        if not possession_data or 'possession_pct' not in possession_data:
            return 0.5
        
        possession_pct = possession_data.get('possession_pct', 50)
        shots = possession_data.get('shots', 10)
        shots_on_target = possession_data.get('shots_on_target', 3)
        xG = possession_data.get('xG', 1.0)
        
        # Calculate efficiency: xG per possession percentage
        if possession_pct == 0:
            return 0.0
        
        # Efficiency ratio: how much threat generated per possession unit
        xg_per_possession = xG / (possession_pct / 100)
        
        # Shot accuracy
        shot_accuracy = shots_on_target / shots if shots > 0 else 0.5
        
        # Combine metrics: normalized efficiency score
        efficiency_score = min(1.0, (xg_per_possession * 0.7 + shot_accuracy * 0.3))
        
        return efficiency_score

    def analyze_defensive_resistance(self, defensive_data):
        """
        Analyze the effectiveness of defensive strategies against different formations.
        :param defensive_data: Dict with keys 'tackles', 'interceptions', 'blocks', 'clearances', 'xG_against'
        :return: Resistance score (0-1 scale).
        """
        if not defensive_data:
            return 0.5
        
        tackles = defensive_data.get('tackles', 10)
        interceptions = defensive_data.get('interceptions', 5)
        blocks = defensive_data.get('blocks', 3)
        clearances = defensive_data.get('clearances', 10)
        xG_against = defensive_data.get('xG_against', 1.5)
        
        # Defensive action index
        defensive_actions = tackles + interceptions + blocks + clearances
        
        # Resistance = high defensive actions + low xG conceded
        # Normalize: typical match has ~30 defensive actions and 1.5 xG against
        action_score = min(1.0, defensive_actions / 30)
        xg_resistance = max(0.0, 1.0 - (xG_against / 3.0))  # Lower xG_against = higher resistance
        
        resistance_score = (action_score * 0.4 + xg_resistance * 0.6)
        
        return resistance_score

    def calculate_tactical_friction(self, home_possession_eff, away_possession_eff, 
                                     home_defensive_res, away_defensive_res):
        """
        Calculate tactical friction between teams.
        High friction = both teams strong defensively, low scoring expected
        :return: Friction score (0-1 scale)
        """
        # Friction is high when both defenses are strong relative to opponent attacks
        home_friction = home_defensive_res / (away_possession_eff + 0.1)
        away_friction = away_defensive_res / (home_possession_eff + 0.1)
        
        # Normalize and average
        avg_friction = (home_friction + away_friction) / 2
        friction_score = min(1.0, avg_friction)
        
        return friction_score

    def detect_possession_parity(self, home_possession, away_possession):
        """
        Detect if possession is evenly matched (indicator of draw potential).
        :param home_possession: Home team possession percentage
        :param away_possession: Away team possession percentage
        :return: Boolean and parity score
        """
        possession_diff = abs(home_possession - away_possession)
        is_parity = possession_diff < self.possession_parity_threshold
        parity_score = max(0, 1.0 - (possession_diff / 20.0))  # 20% diff = 0 score
        
        return is_parity, parity_score

    def provide_pick_recommendations(self, scenario):
        """
        Provide primary and secondary pick recommendations based on the scenario.
        :param scenario: Type of match scenario detected.
        :return: Recommendations list.
        """
        recommendations = {
            'deep_block': ['Under 2.5 Goals', 'Draw', 'BTTS No'],
            'high_possession': ['Over 2.5 Goals', 'Home Win', 'BTTS Yes'],
            'tactical_friction': ['Draw', 'Under 2.5 Goals', 'Exact Score 1-1'],
            'possession_parity': ['Draw', 'Under 2.5 Goals', '1-1 or 0-0'],
        }
        return recommendations.get(scenario, ['Standard Analysis Required'])

    def detect_scenario(self, match_data):
        """
        Detect match scenario using tactical and possession data.
        :param match_data: Dict with home/away possession and defensive metrics.
        :return: Scenario type string.
        """
        if not match_data:
            return 'unknown'
        
        home_poss = match_data.get('home_possession', 50)
        away_poss = match_data.get('away_possession', 50)
        
        is_parity, parity_score = self.detect_possession_parity(home_poss, away_poss)
        
        if is_parity:
            return 'possession_parity'
        elif home_poss > 60 or away_poss > 60:
            return 'high_possession'
        elif home_poss < 40 or away_poss < 40:
            return 'deep_block'
        else:
            return 'balanced'