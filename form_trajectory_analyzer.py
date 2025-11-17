class FormTrajectoryAnalyzer:
    def __init__(self, team_name, form_data):
        self.team_name = team_name
        self.form_data = form_data

    def analyze(self):
        states = []
        for index in range(1, len(self.form_data)):
            trajectory = self.form_data[index] - self.form_data[index - 1]
            states.append(self.categorize_trajectory(trajectory))
        return states

    def categorize_trajectory(self, trajectory):
        if trajectory > 0:
            return 'Improvement'
        elif trajectory == 0:
            return 'Stable'
        elif trajectory < 0:
            return 'Declining'

    def peak_form(self):
        # Logic to determine peak form based on trajectory analysis
        pass

    def volatile_form(self):
        # Logic to determine volatile form based on data fluctuations
        pass

    def crashed_form(self):
        # Logic to determine if team is in crashed form
        pass

# Test cases
if __name__ == '__main__':
    # Bayern Munich
    bayern_form_data = [1, 3, 2, 3, 4, 6, 5]
    bayern_analyzer = FormTrajectoryAnalyzer('Bayern Munich', bayern_form_data)
    print('Bayern Munich Form Analysis:', bayern_analyzer.analyze())

    # Nottingham Forest
    nottingham_form_data = [3, 2, 2, 1, 2]
    nottingham_analyzer = FormTrajectoryAnalyzer('Nottingham Forest', nottingham_form_data)
    print('Nottingham Forest Form Analysis:', nottingham_analyzer.analyze())

    # Liverpool
    liverpool_form_data = [5, 6, 7, 8, 7, 6, 5]
    liverpool_analyzer = FormTrajectoryAnalyzer('Liverpool', liverpool_form_data)
    print('Liverpool Form Analysis:', liverpool_analyzer.analyze())
