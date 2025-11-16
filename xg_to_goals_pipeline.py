import numpy as np
from scipy.stats import poisson

class GoalProbabilityDistribution:
    def __init__(self, expected_goals):
        self.expected_goals = expected_goals

    def to_probability_distribution(self):
        # Calculate probabilities for scoring 0 to 5 goals
        goals = np.arange(0, 6)
        probabilities = poisson.pmf(goals, self.expected_goals)
        return goals, probabilities

class GoalMarketPrediction:
    def __init__(self, prob_dist):
        self.prob_dist = prob_dist

    def market_prediction(self):
        # Sample logic for market predictions
        predictions = {
            'Over 2.5 Goals': np.sum(self.prob_dist[1][3:]),  # P(Over 2.5)
            'Under 2.5 Goals': np.sum(self.prob_dist[1][:3]),  # P(Under 2.5)
            'Exact 2 Goals': self.prob_dist[1][2]             # P(Exactly 2 Goals)
        }
        return predictions

if __name__ == '__main__':
    xg = 1.5  # Example expected goals
    gpd = GoalProbabilityDistribution(xg)
    goals, probabilities = gpd.to_probability_distribution()
    print('Goal Probability Distribution:', list(zip(goals, probabilities)))
    gmp = GoalMarketPrediction((goals, probabilities))
    predictions = gmp.market_prediction()
    print('Goal Market Predictions:', predictions)