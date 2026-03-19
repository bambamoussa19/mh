"""
Post-Match Analysis Module

Provides tools for analyzing discrepancies between predicted and actual match
outcomes, identifying key contributing factors, and generating improvement
recommendations for the prediction pipeline.
"""


class PostMatchAnalysis:
    """Analyzes a completed match against pre-match predictions."""

    def __init__(self, team_home, team_away, match_date, predicted_result,
                 actual_score, performance_metrics=None):
        """
        :param team_home: str - name of the home team
        :param team_away: str - name of the away team
        :param match_date: str - date of the match (ISO format preferred)
        :param predicted_result: str - predicted result, e.g. 'Home Win', 'Draw', 'Away Win'
        :param actual_score: tuple of (int, int) - actual goals (home, away)
        :param performance_metrics: dict with keys 'possession_rate', 'shots_on_target',
                                    'pass_accuracy' (all floats, 0-100)
        """
        self.team_home = team_home
        self.team_away = team_away
        self.match_date = match_date
        self.predicted_result = predicted_result
        self.actual_score = actual_score
        self.performance_metrics = performance_metrics or {}

    def derive_actual_result(self):
        """Return 'Home Win', 'Draw', or 'Away Win' from actual_score."""
        home_goals, away_goals = self.actual_score
        if home_goals > away_goals:
            return 'Home Win'
        elif home_goals == away_goals:
            return 'Draw'
        else:
            return 'Away Win'

    def prediction_correct(self):
        """Return True if the predicted result matches the actual result."""
        return self.predicted_result == self.derive_actual_result()

    def identify_factors(self):
        """
        Identify key factors that may have influenced the prediction discrepancy.

        :return: list of factor strings
        """
        factors = ['Player Form', 'Historical Data', 'Injuries and Player Absences',
                   'Weather Conditions']
        metrics = self.performance_metrics
        if metrics.get('possession_rate', 50) < 40:
            factors.append('Low Possession')
        if metrics.get('shots_on_target', 5) < 3:
            factors.append('Poor Attacking Output')
        if metrics.get('pass_accuracy', 80) < 70:
            factors.append('Low Pass Accuracy')
        return factors

    def generate_report(self):
        """
        Generate a summary report of the post-match analysis.

        :return: dict containing match summary, prediction accuracy, factors, and recommendations
        """
        actual_result = self.derive_actual_result()
        correct = self.prediction_correct()
        factors = self.identify_factors()

        recommendations = [
            'Incorporate advanced metrics such as player tracking data.',
            'Utilize machine learning models to refine predictions based on historical patterns.',
            'Conduct regular post-match analyses for continuous improvement.',
        ]
        if not correct:
            recommendations.insert(0, f'Review weighting for factors: {", ".join(factors[:2])}.')

        return {
            'match': f'{self.team_home} vs {self.team_away}',
            'date': self.match_date,
            'score': f'{self.actual_score[0]}-{self.actual_score[1]}',
            'predicted_result': self.predicted_result,
            'actual_result': actual_result,
            'prediction_correct': correct,
            'performance_metrics': self.performance_metrics,
            'influencing_factors': factors,
            'recommendations': recommendations,
        }

    def print_report(self):
        """Pretty-print the post-match analysis report."""
        report = self.generate_report()
        print('=' * 60)
        print(f"POST-MATCH ANALYSIS: {report['match']}")
        print('=' * 60)
        print(f"Date:             {report['date']}")
        print(f"Score:            {report['score']}")
        print(f"Predicted Result: {report['predicted_result']}")
        print(f"Actual Result:    {report['actual_result']}")
        print(f"Prediction Correct: {'Yes' if report['prediction_correct'] else 'No'}")
        print()
        if self.performance_metrics:
            print('Performance Metrics:')
            for k, v in report['performance_metrics'].items():
                print(f"  {k}: {v}")
            print()
        print('Influencing Factors:')
        for factor in report['influencing_factors']:
            print(f"  - {factor}")
        print()
        print('Recommendations:')
        for rec in report['recommendations']:
            print(f"  * {rec}")
        print('=' * 60)


if __name__ == '__main__':
    analysis = PostMatchAnalysis(
        team_home='Poland',
        team_away='Netherlands',
        match_date='2025-11-17',
        predicted_result='Away Win',
        actual_score=(1, 2),
        performance_metrics={
            'possession_rate': 42.0,
            'shots_on_target': 4,
            'pass_accuracy': 78.5,
        },
    )
    analysis.print_report()
