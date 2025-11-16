class DefensiveCollapseDetector:
    def __init__(self):
        self.yellow_cards = 0
        self.fouls = 0
        self.clearances = 0
        self.form_streaks = []

    def update_stats(self, yellow_cards, fouls, clearances):
        self.yellow_cards += yellow_cards
        self.fouls += fouls
        self.clearances += clearances

    def add_form_streak(self, streak):
        self.form_streaks.append(streak)

    def assess_blowout_risk(self):
        risk_factor = 0

        # Analyze yellow cards and fouls
        if self.yellow_cards > 3:
            risk_factor += 1
        if self.fouls > 10:
            risk_factor += 1

        # Analyze clearances
        if self.clearances < 5:
            risk_factor += 1

        # Analyze form streaks
        if self.form_streaks and len(self.form_streaks) > 3:
            if sum(self.form_streaks[-3:]) < 1:
                risk_factor += 2  # Poor form streak

        # Determine risk level
        if risk_factor >= 3:
            return "High Risk of Blowout"
        elif risk_factor == 2:
            return "Moderate Risk of Blowout"
        else:
            return "Low Risk of Blowout"