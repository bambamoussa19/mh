class TacticalInteractionModel:
    def __init__(self):
        pass

    def analyze_possession_efficiency(self, possession_data):
        """
        Analyze possession efficiency during matches.
        :param possession_data: dict with keys 'possession_pct' (float 0-100),
                                'shots' (int), and 'goals' (int).
        :return: Efficiency score as float in [0, 1].
        """
        possession_pct = possession_data.get('possession_pct', 50)
        shots = possession_data.get('shots', 0)
        goals = possession_data.get('goals', 0)
        if possession_pct == 0 or shots == 0:
            return 0.0
        # Shots per unit of possession (possession expressed as decimal 0-1).
        # Normalised by EXPECTED_SHOT_CREATION_RATE (shots per full possession unit
        # observed in typical matches, empirically ~20 for a team with 100% possession).
        EXPECTED_SHOT_CREATION_RATE = 20
        shot_creation_rate = shots / (possession_pct / 100)
        conversion_rate = goals / shots if shots > 0 else 0
        efficiency_score = min(1.0, (shot_creation_rate / EXPECTED_SHOT_CREATION_RATE) * 0.5 + conversion_rate * 0.5)
        return round(efficiency_score, 4)

    def analyze_defensive_resistance(self, defensive_data):
        """
        Analyze the effectiveness of defensive strategies against different formations.
        :param defensive_data: dict with keys 'tackles_won' (int), 'interceptions' (int),
                               'goals_conceded' (int), and 'shots_faced' (int).
        :return: Resistance score as float in [0, 1].
        """
        tackles_won = defensive_data.get('tackles_won', 0)
        interceptions = defensive_data.get('interceptions', 0)
        goals_conceded = defensive_data.get('goals_conceded', 0)
        shots_faced = defensive_data.get('shots_faced', 1)
        defensive_actions = tackles_won + interceptions
        save_rate = 1 - (goals_conceded / shots_faced) if shots_faced > 0 else 0
        resistance_score = min(1.0, (defensive_actions / 30) * 0.5 + save_rate * 0.5)
        return round(resistance_score, 4)

    def provide_pick_recommendations(self, scenario):
        """
        Provide primary and secondary pick recommendations based on the scenario.
        :param scenario: Type of match scenario detected (possession vs deep block).
        :return: Recommendations list.
        """
        recommendations = []
        if scenario == 'deep_block':
            recommendations = ['Under 2.5 Goals', 'Draw or Away Win']
        elif scenario == 'possession':
            recommendations = ['Home Win', 'Over 1.5 Goals']
        elif scenario == 'open_play':
            recommendations = ['Both Teams to Score', 'Over 2.5 Goals']
        return recommendations

    def detect_scenario(self, match_data):
        """
        Detect possession vs deep block scenario using match data.
        :param match_data: dict with keys 'home_possession' (float), 'away_possession' (float),
                           'home_shots' (int), 'away_shots' (int).
        :return: Scenario type (e.g., 'possession', 'deep_block', 'open_play').
        """
        home_possession = match_data.get('home_possession', 50)
        away_possession = match_data.get('away_possession', 50)
        home_shots = match_data.get('home_shots', 0)
        away_shots = match_data.get('away_shots', 0)
        possession_gap = abs(home_possession - away_possession)
        total_shots = home_shots + away_shots
        if possession_gap >= 20:
            return 'deep_block'
        elif total_shots >= 20:
            return 'open_play'
        else:
            return 'possession'

# Example usage
# model = TacticalInteractionModel()
# efficiency = model.analyze_possession_efficiency(possession_data)
# resistance = model.analyze_defensive_resistance(defensive_data)
# recommendations = model.provide_pick_recommendations(model.detect_scenario(match_data))