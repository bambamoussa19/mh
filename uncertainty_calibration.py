"""
Uncertainty Calibration

This module implements prediction uncertainty quantification and upset detection
for the football match prediction system.
"""

import numpy as np


def predictive_uncertainty(predictions, actuals=None):
    """
    Evaluate the uncertainty of predictions made by the prediction system.

    :param predictions: dict mapping outcome labels to predicted probabilities,
                        e.g. {'home_win': 0.5, 'draw': 0.3, 'away_win': 0.2}
    :param actuals: optional dict mapping outcome labels to actual probabilities
                    or observed frequencies for calibration comparison.
    :return: dict with uncertainty metrics including entropy, confidence,
             and calibration error (if actuals provided).
    """
    probs = list(predictions.values())
    if not probs:
        return {'entropy': 0.0, 'confidence': 0.0, 'calibration_error': None}

    # Shannon entropy as measure of uncertainty (higher = more uncertain)
    entropy = -sum(p * np.log(p + 1e-9) for p in probs if p > 0)

    # Max probability as confidence measure
    confidence = max(probs)

    result = {
        'entropy': round(entropy, 4),
        'confidence': round(confidence, 4),
        'calibration_error': None,
    }

    if actuals is not None:
        # Mean Absolute Calibration Error across outcomes
        errors = []
        for outcome in predictions:
            if outcome in actuals:
                errors.append(abs(predictions[outcome] - actuals[outcome]))
        if errors:
            result['calibration_error'] = round(sum(errors) / len(errors), 4)

    return result


def upset_detection(uncertainty_results, entropy_threshold=0.9, confidence_threshold=0.45):
    """
    Identify anomalies and deviations in predictions that may indicate systemic
    problems or unexpected upset potential.

    :param uncertainty_results: dict as returned by predictive_uncertainty().
    :param entropy_threshold: float; predictions with entropy above this value
                              are flagged as high-uncertainty.
    :param confidence_threshold: float; predictions with max confidence below
                                 this value are flagged as potential upsets.
    :return: dict with upset flags and a summary message.
    """
    entropy = uncertainty_results.get('entropy', 0.0)
    confidence = uncertainty_results.get('confidence', 1.0)
    calibration_error = uncertainty_results.get('calibration_error')

    flags = []

    if entropy > entropy_threshold:
        flags.append('high_entropy')

    if confidence < confidence_threshold:
        flags.append('low_confidence')

    if calibration_error is not None and calibration_error > 0.15:
        flags.append('poor_calibration')

    upset_likely = len(flags) >= 2

    return {
        'flags': flags,
        'upset_likely': upset_likely,
        'summary': (
            'Potential upset detected: ' + ', '.join(flags)
            if flags else 'Prediction appears well-calibrated'
        ),
    }


if __name__ == '__main__':
    sample_predictions = {'home_win': 0.38, 'draw': 0.32, 'away_win': 0.30}
    sample_actuals = {'home_win': 0.40, 'draw': 0.30, 'away_win': 0.30}

    results = predictive_uncertainty(sample_predictions, sample_actuals)
    print('Uncertainty Results:', results)

    upsets = upset_detection(results)
    print('Upset Detection:', upsets)
