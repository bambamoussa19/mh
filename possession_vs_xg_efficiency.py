class PossessionEfficiencyAnalyzer:
    def __init__(self, match_data):
        self.match_data = match_data

    def detect_possession_paradoxes(self):
        # Logic to detect possession paradoxes goes here
        print("Detecting possession paradoxes...")
        # Simulated logic for demonstration
        paradoxes = []
        for match, data in self.match_data.items():
            if data['possession'] < 50 and data['expected_goals'] > 1:
                paradoxes.append(match)
        return paradoxes

    def calculate_efficiency_ratios(self):
        # Logic to calculate efficiency ratios goes here
        efficiencies = {}
        for match, data in self.match_data.items():
            efficiency_ratio = data['expected_goals'] / (data['possession'] / 100)
            efficiencies[match] = efficiency_ratio
        return efficiencies

    def draw_upset_probability_adjustments(self):
        # Logic to assess probability adjustments goes here
        adjustments = {}
        for match, data in self.match_data.items():
            if data['expected_goals'] >= 1:
                adjustments[match] = "Possible upset"
            else:
                adjustments[match] = "Draw likelihood"
        return adjustments

# Example Matches
match_scenarios = {
    "Liverpool 1-0 Real Madrid": {"possession": 45, "expected_goals": 1.5},
    "Napoli 0-0 Frankfurt": {"possession": 60, "expected_goals": 0.8},
    "Benfica 0-1 Leverkusen": {"possession": 55, "expected_goals": 1.2},
}

# Example Usage
analyzer = PossessionEfficiencyAnalyzer(match_scenarios)
paradoxes = analyzer.detect_possession_paradoxes()
efficiencies = analyzer.calculate_efficiency_ratios()
adjustments = analyzer.draw_upset_probability_adjustments()

print("Possession Paradoxes:", paradoxes)
print("Efficiency Ratios:", efficiencies)
print("Probability Adjustments:", adjustments)