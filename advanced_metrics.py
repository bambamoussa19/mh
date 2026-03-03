class DrawClusteringIndex:
    def __init__(self):
        self.draw_results = []

    def add_result(self, is_draw):
        """Record a match result (True = draw, False = non-draw)."""
        self.draw_results.append(bool(is_draw))

    def calculate(self, data=None):
        """
        Calculate the Draw Clustering Index.

        Returns the ratio of consecutive draw pairs to the total number of
        consecutive match pairs, indicating whether draws tend to cluster.
        A value > expected draw rate suggests clustering.
        """
        results = data if data is not None else self.draw_results
        if len(results) < 2:
            return 0.0
        consecutive_draws = sum(
            1 for i in range(len(results) - 1) if results[i] and results[i + 1]
        )
        return consecutive_draws / (len(results) - 1)

class DefensiveSuperiorityMultiplier:
    def __init__(self):
        self.base_multiplier = 1.0

    def calculate(self, data):
        """
        Calculate the Defensive Superiority Multiplier.

        Parameters:
        data (dict): Expected keys: 'goals_conceded_home', 'goals_conceded_away',
                     'league_avg_goals_per_match'.

        Returns:
        float: Multiplier > 1 indicates defensive superiority; < 1 is inferior.
        """
        league_avg = data.get('league_avg_goals_per_match', 2.5)
        goals_conceded_home = data.get('goals_conceded_home', league_avg / 2)
        goals_conceded_away = data.get('goals_conceded_away', league_avg / 2)
        avg_conceded = (goals_conceded_home + goals_conceded_away) / 2
        if avg_conceded == 0:
            return 2.0
        return league_avg / (2 * avg_conceded)

class HomeAdvantageContext:
    def __init__(self):
        self.home_wins = 0
        self.total_matches = 0

    def calculate(self, data):
        """
        Calculate the Home Advantage Context score.

        Parameters:
        data (dict): Expected keys: 'home_wins', 'total_home_matches'.

        Returns:
        float: Home win rate (0.0 – 1.0).
        """
        home_wins = data.get('home_wins', self.home_wins)
        total = data.get('total_home_matches', self.total_matches)
        if total == 0:
            return 0.0
        return home_wins / total

class PressureDirectionEffect:
    def __init__(self):
        self.high_pressure_score = 0.0

    def calculate(self, data):
        """
        Calculate the Pressure Direction Effect on match outcome.

        Parameters:
        data (dict): Expected keys: 'pressing_intensity' (0–1),
                     'opposition_errors_forced' (count).

        Returns:
        float: Pressure effect score (higher = more dominant pressing).
        """
        pressing = data.get('pressing_intensity', 0.0)
        errors_forced = data.get('opposition_errors_forced', 0)
        return pressing * 0.6 + min(errors_forced / 10.0, 1.0) * 0.4

class FormTrendMomentum:
    def __init__(self):
        self.form_points = []

    def calculate(self, data):
        """
        Calculate Form Trend Momentum as the average change in form over recent matches.

        Parameters:
        data (list of float): Sequence of form scores across recent matches.

        Returns:
        float: Average momentum (positive = improving, negative = declining).
        """
        points = data if data is not None else self.form_points
        if len(points) < 2:
            return 0.0
        deltas = [points[i] - points[i - 1] for i in range(1, len(points))]
        return sum(deltas) / len(deltas)
