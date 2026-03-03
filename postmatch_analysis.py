class PostMatchAnalysis:
    """Analyze actual match outcomes versus predictions and identify discrepancies."""

    def __init__(self, home_team, away_team, predicted_result, actual_result, match_date=None):
        self.home_team = home_team
        self.away_team = away_team
        self.predicted_result = predicted_result
        self.actual_result = actual_result
        self.match_date = match_date
        self.performance_metrics = {}
        self.influencing_factors = []

    def add_performance_metrics(self, possession_rate=None, shots_on_target=None, pass_accuracy=None):
        """Record key performance metrics for the match."""
        if possession_rate is not None:
            self.performance_metrics['possession_rate'] = possession_rate
        if shots_on_target is not None:
            self.performance_metrics['shots_on_target'] = shots_on_target
        if pass_accuracy is not None:
            self.performance_metrics['pass_accuracy'] = pass_accuracy

    def add_influencing_factor(self, factor):
        """Record a factor that may have influenced the match outcome."""
        self.influencing_factors.append(factor)

    def prediction_correct(self):
        """Return True if the predicted result matches the actual result."""
        return self.predicted_result == self.actual_result

    def generate_report(self):
        """Generate a post-match analysis report."""
        report = {
            'match': f"{self.home_team} vs {self.away_team}",
            'date': self.match_date,
            'predicted_result': self.predicted_result,
            'actual_result': self.actual_result,
            'prediction_correct': self.prediction_correct(),
            'performance_metrics': self.performance_metrics,
            'influencing_factors': self.influencing_factors,
        }
        return report

    def summarize(self):
        """Print a summary of the post-match analysis."""
        correct = self.prediction_correct()
        status = "CORRECT" if correct else "INCORRECT"
        print(f"Match: {self.home_team} vs {self.away_team}")
        if self.match_date:
            print(f"Date: {self.match_date}")
        print(f"Predicted: {self.predicted_result} | Actual: {self.actual_result} [{status}]")
        if self.performance_metrics:
            print("Performance Metrics:")
            for key, value in self.performance_metrics.items():
                print(f"  {key}: {value}")
        if self.influencing_factors:
            print("Influencing Factors:")
            for factor in self.influencing_factors:
                print(f"  - {factor}")


if __name__ == '__main__':
    analysis = PostMatchAnalysis(
        home_team='Poland',
        away_team='Netherlands',
        predicted_result='Draw',
        actual_result='Away Win',
        match_date='2025-11-15',
    )
    analysis.add_performance_metrics(possession_rate=45.0, shots_on_target=4, pass_accuracy=78.5)
    analysis.add_influencing_factor('Player Form')
    analysis.add_influencing_factor('Injuries and Player Absences')
    analysis.summarize()

