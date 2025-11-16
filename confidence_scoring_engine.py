"""
Confidence Scoring Engine

Provides transparent formula-based confidence scores (0-100) for predictions.
Makes confidence calculation auditable and explainable.
"""

import numpy as np


class ConfidenceScoringEngine:
    """
    Calculate confidence scores based on multiple factors with
    transparent, formula-based methodology.
    """
    
    def __init__(self):
        # Component weights (sum to 1.0)
        self.weights = {
            'probability_margin': 0.30,     # How clear the favorite is
            'data_quality': 0.20,           # Completeness of input data
            'model_agreement': 0.20,        # Different models agreeing
            'historical_accuracy': 0.15,    # Past performance in similar scenarios
            'volatility': 0.15              # Stability of predictions
        }
    
    def calculate_probability_margin_score(self, probabilities):
        """
        Score based on how decisive the prediction is.
        
        :param probabilities: Dict with outcome probabilities
        :return: Score 0-100
        """
        probs = list(probabilities.values())
        if not probs:
            return 0
        
        # Sort probabilities
        probs_sorted = sorted(probs, reverse=True)
        
        # Get highest probability
        max_prob = probs_sorted[0]
        
        # Get margin over second choice
        if len(probs_sorted) > 1:
            margin = max_prob - probs_sorted[1]
        else:
            margin = max_prob
        
        # Convert to 0-100 scale
        # High probability + large margin = high confidence
        score = (max_prob * 70 + margin * 30) * 100
        
        return min(100, max(0, score))
    
    def calculate_data_quality_score(self, data_completeness):
        """
        Score based on input data quality and completeness.
        
        :param data_completeness: Dict with:
            - xg_available: Bool
            - form_data_available: Bool
            - h2h_available: Bool
            - injuries_known: Bool
            - tactical_data_available: Bool
        :return: Score 0-100
        """
        # Check availability of key data
        available_count = sum(1 for v in data_completeness.values() if v)
        total_count = len(data_completeness)
        
        if total_count == 0:
            return 50  # Neutral if no data specified
        
        completeness_ratio = available_count / total_count
        
        # Convert to 0-100 scale
        score = completeness_ratio * 100
        
        # Bonus for having critical data (xG, form)
        if data_completeness.get('xg_available', False):
            score = min(100, score + 5)
        if data_completeness.get('form_data_available', False):
            score = min(100, score + 5)
        
        return score
    
    def calculate_model_agreement_score(self, model_predictions):
        """
        Score based on agreement between multiple prediction models.
        
        :param model_predictions: List of prediction dicts from different models
            Each dict has outcome probabilities
        :return: Score 0-100
        """
        if len(model_predictions) < 2:
            return 70  # Default moderate confidence if single model
        
        # Find consensus winner across models
        winners = []
        for pred in model_predictions:
            winner = max(pred.items(), key=lambda x: x[1])[0]
            winners.append(winner)
        
        # Calculate agreement rate
        most_common = max(set(winners), key=winners.count)
        agreement_rate = winners.count(most_common) / len(winners)
        
        # Calculate probability variance for the consensus outcome
        if most_common in model_predictions[0]:
            probs = [pred.get(most_common, 0) for pred in model_predictions]
            prob_std = np.std(probs)
            consistency_score = max(0, 1 - prob_std * 2)  # Lower std = higher consistency
        else:
            consistency_score = 0.5
        
        # Combined score
        score = (agreement_rate * 0.6 + consistency_score * 0.4) * 100
        
        return score
    
    def calculate_historical_accuracy_score(self, scenario_stats):
        """
        Score based on historical accuracy in similar scenarios.
        
        :param scenario_stats: Dict with:
            - similar_matches_count: Int
            - correct_predictions: Int
            - average_confidence: Float (0-1)
        :return: Score 0-100
        """
        similar_count = scenario_stats.get('similar_matches_count', 0)
        correct = scenario_stats.get('correct_predictions', 0)
        
        if similar_count == 0:
            return 60  # Neutral confidence if no historical data
        
        accuracy = correct / similar_count
        
        # Adjust based on sample size
        if similar_count < 10:
            reliability_factor = similar_count / 10
        else:
            reliability_factor = 1.0
        
        # Score combines accuracy with reliability
        score = accuracy * reliability_factor * 100
        
        return score
    
    def calculate_volatility_score(self, prediction_stability):
        """
        Score based on prediction stability (inverse of volatility).
        
        :param prediction_stability: Dict with:
            - probability_changes: List of probability changes over time
            - consensus_trend: String ('stable', 'trending', 'volatile')
        :return: Score 0-100
        """
        prob_changes = prediction_stability.get('probability_changes', [])
        trend = prediction_stability.get('consensus_trend', 'stable')
        
        if not prob_changes:
            # No volatility data, assume moderate stability
            return 65
        
        # Calculate volatility (standard deviation of changes)
        volatility = np.std(prob_changes)
        
        # Convert to stability score (inverse relationship)
        stability_score = max(0, 1 - volatility * 5)  # High volatility reduces score
        
        # Adjust based on trend
        trend_multipliers = {
            'stable': 1.0,
            'trending': 0.9,
            'volatile': 0.7
        }
        multiplier = trend_multipliers.get(trend, 0.85)
        
        score = stability_score * multiplier * 100
        
        return max(0, min(100, score))
    
    def calculate_overall_confidence(self, components):
        """
        Calculate overall confidence score from all components.
        
        :param components: Dict with:
            - probabilities: Dict of outcome probabilities
            - data_completeness: Dict of data availability
            - model_predictions: List of model prediction dicts (optional)
            - scenario_stats: Dict of historical stats (optional)
            - prediction_stability: Dict of stability metrics (optional)
        :return: Dict with overall score and breakdown
        """
        # Calculate component scores
        scores = {}
        
        # 1. Probability margin
        scores['probability_margin'] = self.calculate_probability_margin_score(
            components.get('probabilities', {}))
        
        # 2. Data quality
        scores['data_quality'] = self.calculate_data_quality_score(
            components.get('data_completeness', {}))
        
        # 3. Model agreement
        model_preds = components.get('model_predictions', None)
        if model_preds and len(model_preds) > 1:
            scores['model_agreement'] = self.calculate_model_agreement_score(model_preds)
        else:
            scores['model_agreement'] = 70  # Default
        
        # 4. Historical accuracy
        scenario_stats = components.get('scenario_stats', {})
        scores['historical_accuracy'] = self.calculate_historical_accuracy_score(scenario_stats)
        
        # 5. Volatility
        stability = components.get('prediction_stability', {})
        scores['volatility'] = self.calculate_volatility_score(stability)
        
        # Calculate weighted overall score
        overall_score = sum(scores[key] * self.weights[key] 
                          for key in self.weights.keys())
        
        # Round to integer
        overall_score = round(overall_score)
        
        # Classify confidence level
        confidence_level = self._classify_confidence(overall_score)
        
        return {
            'overall_confidence': overall_score,
            'confidence_level': confidence_level,
            'component_scores': scores,
            'weights': self.weights,
            'formula': self._generate_formula_explanation(scores)
        }
    
    def _classify_confidence(self, score):
        """Classify numeric confidence into category."""
        if score >= 85:
            return 'Very High'
        elif score >= 70:
            return 'High'
        elif score >= 55:
            return 'Moderate'
        elif score >= 40:
            return 'Low'
        else:
            return 'Very Low'
    
    def _generate_formula_explanation(self, scores):
        """Generate human-readable formula explanation."""
        explanation = []
        for component, weight in self.weights.items():
            score = scores.get(component, 0)
            contribution = score * weight
            explanation.append(
                f"{component}: {score:.1f} × {weight:.2f} = {contribution:.1f}"
            )
        return explanation
    
    def quick_confidence(self, prediction_probability, data_available_count=3, total_data_points=5):
        """
        Quick confidence calculation for simple cases.
        
        :param prediction_probability: Float (0-1) - probability of predicted outcome
        :param data_available_count: Int - number of data sources available
        :param total_data_points: Int - total possible data sources
        :return: Confidence score 0-100
        """
        # Simple formula: weighted combination of probability and data quality
        prob_score = prediction_probability * 100
        data_quality = (data_available_count / total_data_points) * 100
        
        confidence = prob_score * 0.7 + data_quality * 0.3
        
        return round(confidence)


# Example usage
if __name__ == "__main__":
    engine = ConfidenceScoringEngine()
    
    # Example: Frankfurt vs Heidenheim prediction
    components = {
        'probabilities': {
            'home_win': 0.782,
            'draw': 0.128,
            'away_win': 0.090
        },
        'data_completeness': {
            'xg_available': True,
            'form_data_available': True,
            'h2h_available': True,
            'injuries_known': False,
            'tactical_data_available': True
        },
        'model_predictions': [
            {'home_win': 0.782, 'draw': 0.128, 'away_win': 0.090},
            {'home_win': 0.750, 'draw': 0.150, 'away_win': 0.100},
            {'home_win': 0.800, 'draw': 0.120, 'away_win': 0.080}
        ],
        'scenario_stats': {
            'similar_matches_count': 15,
            'correct_predictions': 10,
            'average_confidence': 0.75
        },
        'prediction_stability': {
            'probability_changes': [0.02, -0.01, 0.01, 0.00],
            'consensus_trend': 'stable'
        }
    }
    
    result = engine.calculate_overall_confidence(components)
    
    print(f"Overall Confidence: {result['overall_confidence']}/100 ({result['confidence_level']})")
    print("\nComponent Breakdown:")
    for component, score in result['component_scores'].items():
        print(f"  {component}: {score:.1f}")
    print("\nFormula:")
    for line in result['formula']:
        print(f"  {line}")
