class BTTSAnalyzer:
    def __init__(self):
        self.striker_stats = {}
        self.locked_scenarios = []
        self.edge_cases = []

    def add_striker_profile(self, striker_id, goals, shots, assists, minutes_played):
        """
        Adds a striker profile for analysis.
        
        :param striker_id: Unique identifier for the striker
        :param goals: Number of goals scored
        :param shots: Number of shots taken
        :param assists: Number of assists made
        :param minutes_played: Total minutes played
        """
        self.striker_stats[striker_id] = {
            'goals': goals,
            'shots': shots,
            'assists': assists,
            'minutes_played': minutes_played
        }

    def detect_locked_scenario(self, scenario_description):
        """
        Detects impossible lock scenarios based on predefined criteria.
        
        :param scenario_description: Description of the scenario to analyze
        """
        # Example criteria
        if "team_no_scoring" in scenario_description:
            self.locked_scenarios.append(scenario_description)

    def handle_edge_case(self, edge_case_description):
        """
        Handles unusual cases that may affect the outcome.
        
        :param edge_case_description: Description of the edge case
        """
        self.edge_cases.append(edge_case_description)

    def compute_final_probability(self):
        """
        Computes the probability of both teams scoring based on the analyzed data.
        
        :return: Computed probability score
        """
        # Simple scoring logic for demonstration
        total_goals = sum(striker['goals'] for striker in self.striker_stats.values())
        total_shots = sum(striker['shots'] for striker in self.striker_stats.values())

        if total_shots == 0:
            return 0  # Avoid division by zero
        probability = total_goals / total_shots

        return probability * 100  # Convert to percentage

    def analyze(self):
        # Run analysis
        probability = self.compute_final_probability()
        if probability >= 85:
            print(f"Analysis Result: High probability of both teams scoring: {probability}%")
        else:
            print(f"Analysis Result: Low probability of both teams scoring: {probability}%")

# Example of using the BTTSAnalyzer
if __name__ == '__main__':
    analyzer = BTTSAnalyzer()
    analyzer.add_striker_profile('striker1', 20, 100, 10, 900)
    analyzer.add_striker_profile('striker2', 15, 80, 8, 800)
    analyzer.detect_locked_scenario('team_no_scoring')
    analyzer.handle_edge_case('injured_player')
    analyzer.analyze()