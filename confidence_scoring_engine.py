"""
Confidence Scoring Engine

Provides transparent, formula-based confidence scoring (0-100 scale).
Replaces empirical confidence values with auditable calculations.

Confidence factors:
1. Data completeness (0-20 points)
2. Model agreement (0-25 points)
3. Historical accuracy (0-20 points)
4. Uncertainty metrics (0-20 points)
5. Market coherence (0-15 points)
"""

import numpy as np


class ConfidenceScoringEngine:
    """
    Formula-based confidence scoring with full audit trail.
    """
    
    def __init__(self):
        self.weights = {
            'data_completeness': 20,
            'model_agreement': 25,
            'historical_accuracy': 20,
            'uncertainty_metrics': 20,
            'market_coherence': 15
        }
        
    def calculate_data_completeness_score(self, available_data):
        """
        Score based on data availability.
        
        :param available_data: Dict with boolean flags for data availability
            - has_xg_data (bool)
            - has_possession_data (bool)
            - has_defensive_stats (bool)
            - has_recent_form (bool)
            - has_h2h_history (bool)
        :return: Score 0-20
        """
        if not available_data:
            return 5.0  # Minimal baseline
        
        # Define weights for each data type
        data_weights = {
            'has_xg_data': 5,
            'has_possession_data': 4,
            'has_defensive_stats': 4,
            'has_recent_form': 4,
            'has_h2h_history': 3
        }
        
        score = 0
        for key, weight in data_weights.items():
            if available_data.get(key, False):
                score += weight
        
        return min(20.0, score)
    
    def calculate_model_agreement_score(self, predictions):
        """
        Score based on agreement between different models/methods.
        
        :param predictions: Dict with predictions from different models
            - base_model (dict): {'home_win': 0.4, 'draw': 0.3, 'away_win': 0.3}
            - xg_model (dict): Similar structure
            - tactical_model (dict): Similar structure
        :return: Score 0-25
        """
        if not predictions or len(predictions) < 2:
            return 10.0  # Baseline if only one model
        
        # Extract outcome probabilities from each model
        outcomes = ['home_win', 'draw', 'away_win']
        model_probs = []
        
        for model_name, probs in predictions.items():
            if isinstance(probs, dict):
                model_probs.append([probs.get(o, 0.33) for o in outcomes])
        
        if len(model_probs) < 2:
            return 10.0
        
        # Calculate variance across models for each outcome
        model_probs = np.array(model_probs)
        variances = np.var(model_probs, axis=0)
        avg_variance = np.mean(variances)
        
        # Low variance = high agreement = high score
        # Variance typically 0-0.05 for good agreement
        agreement_score = max(0, 25 - (avg_variance * 500))
        
        return min(25.0, agreement_score)
    
    def calculate_historical_accuracy_score(self, backtest_results):
        """
        Score based on historical prediction accuracy.
        
        :param backtest_results: Dict with backtest metrics
            - accuracy (float): 0-1 scale
            - brier_score (float): Lower is better (0-1)
            - log_loss (float): Lower is better
            - sample_size (int): Number of backtested matches
        :return: Score 0-20
        """
        if not backtest_results:
            return 12.0  # Neutral baseline
        
        accuracy = backtest_results.get('accuracy', 0.5)
        brier_score = backtest_results.get('brier_score', 0.25)
        sample_size = backtest_results.get('sample_size', 0)
        
        # Accuracy component (0-10 points)
        accuracy_points = (accuracy - 0.3) * 25  # 0.3 = baseline, 0.7 = excellent
        accuracy_points = max(0, min(10, accuracy_points))
        
        # Calibration component (0-10 points)
        # Brier score: 0 = perfect, 0.25 = random, 0.5 = worst
        calibration_points = max(0, (0.25 - brier_score) * 40)
        calibration_points = max(0, min(10, calibration_points))
        
        # Sample size penalty if too few examples
        if sample_size < 20:
            penalty = (20 - sample_size) * 0.25
            return max(5, accuracy_points + calibration_points - penalty)
        
        return accuracy_points + calibration_points
    
    def calculate_uncertainty_score(self, uncertainty_metrics):
        """
        Score based on prediction uncertainty (lower uncertainty = higher score).
        
        :param uncertainty_metrics: Dict with uncertainty measures
            - entropy (float): Shannon entropy of probability distribution
            - max_probability (float): Highest probability among outcomes
            - probability_spread (float): Difference between highest and second-highest
        :return: Score 0-20
        """
        if not uncertainty_metrics:
            return 10.0  # Neutral
        
        entropy = uncertainty_metrics.get('entropy', 1.1)
        max_prob = uncertainty_metrics.get('max_probability', 0.4)
        prob_spread = uncertainty_metrics.get('probability_spread', 0.1)
        
        # Entropy component (0-10 points)
        # Shannon entropy: 0 = certain, 1.0986 = maximum (for 3 outcomes)
        entropy_score = max(0, 10 - (entropy * 9))
        
        # Confidence component (0-10 points)
        # Higher max probability = more confident = higher score
        confidence_score = (max_prob - 0.33) * 15  # 0.33 = random, 1.0 = certain
        confidence_score = max(0, min(10, confidence_score))
        
        return entropy_score + confidence_score
    
    def calculate_market_coherence_score(self, prediction, market_odds=None):
        """
        Score based on coherence with betting market (if available).
        
        :param prediction: Dict with model probabilities
        :param market_odds: Optional dict with market implied probabilities
        :return: Score 0-15
        """
        if not market_odds:
            return 10.0  # Neutral baseline when no market data
        
        # Calculate distance between prediction and market
        outcomes = ['home_win', 'draw', 'away_win']
        differences = []
        
        for outcome in outcomes:
            pred_prob = prediction.get(outcome, 0.33)
            market_prob = market_odds.get(outcome, 0.33)
            differences.append(abs(pred_prob - market_prob))
        
        avg_difference = np.mean(differences)
        
        # Low difference = high coherence = high score
        # Typical differences: 0.00-0.15
        coherence_score = max(0, 15 - (avg_difference * 100))
        
        return min(15.0, coherence_score)
    
    def calculate_confidence(self, confidence_inputs):
        """
        Calculate overall confidence score with full audit trail.
        
        :param confidence_inputs: Dict containing all inputs for scoring:
            - available_data (dict)
            - predictions (dict)
            - backtest_results (dict)
            - uncertainty_metrics (dict)
            - market_odds (dict, optional)
        :return: Dict with confidence score and breakdown
        """
        # Calculate component scores
        data_score = self.calculate_data_completeness_score(
            confidence_inputs.get('available_data', {})
        )
        
        model_score = self.calculate_model_agreement_score(
            confidence_inputs.get('predictions', {})
        )
        
        accuracy_score = self.calculate_historical_accuracy_score(
            confidence_inputs.get('backtest_results', {})
        )
        
        uncertainty_score = self.calculate_uncertainty_score(
            confidence_inputs.get('uncertainty_metrics', {})
        )
        
        coherence_score = self.calculate_market_coherence_score(
            confidence_inputs.get('final_prediction', {}),
            confidence_inputs.get('market_odds')
        )
        
        # Total confidence
        total_confidence = (
            data_score +
            model_score +
            accuracy_score +
            uncertainty_score +
            coherence_score
        )
        
        # Create audit breakdown
        breakdown = {
            'total_confidence': round(total_confidence, 1),
            'components': {
                'data_completeness': round(data_score, 1),
                'model_agreement': round(model_score, 1),
                'historical_accuracy': round(accuracy_score, 1),
                'uncertainty_metrics': round(uncertainty_score, 1),
                'market_coherence': round(coherence_score, 1)
            },
            'confidence_level': self._get_confidence_level(total_confidence)
        }
        
        return breakdown
    
    def _get_confidence_level(self, score):
        """Convert numeric score to confidence level string."""
        if score >= 80:
            return "Very High"
        elif score >= 65:
            return "High"
        elif score >= 50:
            return "Moderate"
        elif score >= 35:
            return "Low"
        else:
            return "Very Low"
    
    def print_confidence_report(self, confidence_breakdown):
        """Print formatted confidence report."""
        print("\n" + "="*60)
        print("CONFIDENCE SCORING REPORT")
        print("="*60)
        print(f"\nOverall Confidence: {confidence_breakdown['total_confidence']}/100")
        print(f"Confidence Level: {confidence_breakdown['confidence_level']}")
        print("\nComponent Breakdown:")
        print("-"*60)
        
        for component, score in confidence_breakdown['components'].items():
            max_score = self.weights[component]
            pct = (score / max_score) * 100
            bar = "█" * int(pct / 5)
            print(f"{component:.<30} {score:>4.1f}/{max_score} {bar}")
        
        print("="*60 + "\n")


# Example usage and testing
if __name__ == '__main__':
    engine = ConfidenceScoringEngine()
    
    # Example 1: High confidence scenario
    print("Example 1: High Confidence Scenario")
    print("-" * 60)
    
    inputs_high = {
        'available_data': {
            'has_xg_data': True,
            'has_possession_data': True,
            'has_defensive_stats': True,
            'has_recent_form': True,
            'has_h2h_history': True
        },
        'predictions': {
            'base_model': {'home_win': 0.50, 'draw': 0.30, 'away_win': 0.20},
            'xg_model': {'home_win': 0.52, 'draw': 0.28, 'away_win': 0.20},
            'tactical_model': {'home_win': 0.48, 'draw': 0.32, 'away_win': 0.20}
        },
        'backtest_results': {
            'accuracy': 0.62,
            'brier_score': 0.18,
            'sample_size': 50
        },
        'uncertainty_metrics': {
            'entropy': 0.95,
            'max_probability': 0.50,
            'probability_spread': 0.20
        },
        'final_prediction': {'home_win': 0.50, 'draw': 0.30, 'away_win': 0.20},
        'market_odds': {'home_win': 0.48, 'draw': 0.32, 'away_win': 0.20}
    }
    
    confidence_high = engine.calculate_confidence(inputs_high)
    engine.print_confidence_report(confidence_high)
    
    # Example 2: Low confidence scenario
    print("\nExample 2: Low Confidence Scenario")
    print("-" * 60)
    
    inputs_low = {
        'available_data': {
            'has_xg_data': False,
            'has_possession_data': True,
            'has_defensive_stats': False,
            'has_recent_form': True,
            'has_h2h_history': False
        },
        'predictions': {
            'base_model': {'home_win': 0.35, 'draw': 0.35, 'away_win': 0.30}
        },
        'backtest_results': {
            'accuracy': 0.45,
            'brier_score': 0.28,
            'sample_size': 12
        },
        'uncertainty_metrics': {
            'entropy': 1.08,
            'max_probability': 0.35,
            'probability_spread': 0.05
        },
        'final_prediction': {'home_win': 0.35, 'draw': 0.35, 'away_win': 0.30}
    }
    
    confidence_low = engine.calculate_confidence(inputs_low)
    engine.print_confidence_report(confidence_low)
