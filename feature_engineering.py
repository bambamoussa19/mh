class FeatureEngineering:
    def __init__(self):
        pass

    def conversion_efficiency(self, attempts, goals):
        """Calculate conversion efficiency."""
        if attempts == 0:
            return 0
        return (goals / attempts) * 100

    def tournament_context(self, matches):
        """Analyze performance in the context of tournaments."""
        # Example calculation
        return sum(match['performance'] for match in matches) / len(matches) if matches else 0

    def defensive_resilience(self, goals_conceded, total_matches):
        """Calculate defensive resilience."""
        if total_matches == 0:
            return 0
        return (1 - (goals_conceded / total_matches))

    def goalkeeper_performance(self, saves, goals_conceded):
        """Evaluate goalkeeper's performance."""
        return saves - goals_conceded

    def enhanced_travel_fatigue(self, travel_distance, matches_played):
        """Calculate fatigue based on travel distance and matches played."""
        return travel_distance / matches_played if matches_played else 0

# Example usage:
feature_engineering = FeatureEngineering()
print(feature_engineering.conversion_efficiency(20, 5))