class DrawClusteringIndex:
    def __init__(self):
        self.index = 0.0

    def calculate(self, data):
        """
        Calculate Draw Clustering Index based on recent draw frequency.

        :param data: dict with keys 'draws' (int) and 'total_matches' (int)
        :return: float index in [0, 1] representing draw clustering tendency
        """
        draws = data.get('draws', 0)
        total_matches = data.get('total_matches', 1)
        if total_matches == 0:
            self.index = 0.0
        else:
            self.index = draws / total_matches
        return self.index


class DefensiveSuperiorityMultiplier:
    def __init__(self):
        self.multiplier = 1.0

    def calculate(self, data):
        """
        Calculate Defensive Superiority Multiplier based on goals conceded vs league average.

        :param data: dict with keys 'goals_conceded' (float) and 'league_avg_goals_conceded' (float)
        :return: float multiplier where > 1.0 indicates defensive superiority
        """
        goals_conceded = data.get('goals_conceded', 1.0)
        league_avg = data.get('league_avg_goals_conceded', 1.0)
        if goals_conceded == 0:
            self.multiplier = 2.0
        elif league_avg == 0:
            self.multiplier = 1.0
        else:
            self.multiplier = league_avg / goals_conceded
        return self.multiplier


class HomeAdvantageContext:
    def __init__(self):
        self.advantage_score = 0.0

    def calculate(self, data):
        """
        Calculate Home Advantage Context score.

        :param data: dict with keys 'home_wins' (int), 'home_draws' (int), 'home_losses' (int)
        :return: float score in [0, 1] representing home advantage strength
        """
        home_wins = data.get('home_wins', 0)
        home_draws = data.get('home_draws', 0)
        home_losses = data.get('home_losses', 0)
        total = home_wins + home_draws + home_losses
        if total == 0:
            self.advantage_score = 0.0
        else:
            self.advantage_score = (home_wins + 0.5 * home_draws) / total
        return self.advantage_score


class PressureDirectionEffect:
    def __init__(self):
        self.effect_score = 0.0

    def calculate(self, data):
        """
        Calculate Pressure Direction Effect based on shots on target and fouls.

        :param data: dict with keys 'shots_on_target' (int) and 'fouls_committed' (int)
        :return: float effect score representing attacking pressure direction
        """
        shots_on_target = data.get('shots_on_target', 0)
        fouls_committed = data.get('fouls_committed', 0)
        total_actions = shots_on_target + fouls_committed
        if total_actions == 0:
            self.effect_score = 0.0
        else:
            self.effect_score = shots_on_target / total_actions
        return self.effect_score


class FormTrendMomentum:
    def __init__(self):
        self.momentum = 0.0

    def calculate(self, data):
        """
        Calculate Form Trend Momentum based on recent match points.

        :param data: dict with key 'recent_points' (list of int, most recent last)
        :return: float momentum score; positive = improving, negative = declining
        """
        recent_points = data.get('recent_points', [])
        if len(recent_points) < 2:
            self.momentum = 0.0
            return self.momentum
        n = len(recent_points)
        # Linear weighting (1, 2, …, n) gives more recent results greater influence
        # while remaining simple and interpretable (vs. exponential decay).
        weighted_sum = sum((i + 1) * p for i, p in enumerate(recent_points))
        simple_sum = sum(recent_points)
        weight_total = n * (n + 1) / 2
        weighted_avg = weighted_sum / weight_total if weight_total else 0
        simple_avg = simple_sum / n if n else 0
        self.momentum = weighted_avg - simple_avg
        return self.momentum
