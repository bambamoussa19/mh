import math


def predictive_uncertainty(probabilities):
    """
    Quantify predictive uncertainty using entropy.

    Parameters:
    probabilities (dict): A dict mapping outcome labels to their predicted probabilities.
                          Values should sum to 1.0.

    Returns:
    float: Entropy-based uncertainty score (higher = more uncertain).
    """
    entropy = 0.0
    for p in probabilities.values():
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy


def upset_detection(predicted_probs, actual_outcome, upset_threshold=0.25):
    """
    Detect whether an actual match outcome constitutes an upset.

    An upset is defined as the actual outcome having a predicted probability
    below ``upset_threshold``.

    Parameters:
    predicted_probs (dict): Predicted probabilities for each outcome label.
    actual_outcome (str): The outcome that actually occurred.
    upset_threshold (float): Probability threshold below which a result is an upset.

    Returns:
    bool: True if the result is classified as an upset, False otherwise.
    """
    actual_prob = predicted_probs.get(actual_outcome, 0.0)
    return actual_prob < upset_threshold


def calibration_error(predicted_probs_list, actual_outcomes, n_bins=10):
    """
    Compute the Expected Calibration Error (ECE) across a set of predictions.

    Parameters:
    predicted_probs_list (list of float): Predicted probability for the positive/chosen outcome.
    actual_outcomes (list of int): Binary ground truth labels (1 = correct, 0 = incorrect).
    n_bins (int): Number of equally-spaced probability bins.

    Returns:
    float: Expected Calibration Error.
    """
    bin_size = 1.0 / n_bins
    ece = 0.0
    n = len(predicted_probs_list)

    for b in range(n_bins):
        lower = b * bin_size
        upper = lower + bin_size
        indices = [i for i, p in enumerate(predicted_probs_list) if lower <= p < upper]
        if not indices:
            continue
        avg_confidence = sum(predicted_probs_list[i] for i in indices) / len(indices)
        avg_accuracy = sum(actual_outcomes[i] for i in indices) / len(indices)
        ece += (len(indices) / n) * abs(avg_confidence - avg_accuracy)

    return ece


if __name__ == '__main__':
    probs = {'home_win': 0.55, 'draw': 0.25, 'away_win': 0.20}
    uncertainty = predictive_uncertainty(probs)
    print(f"Predictive uncertainty (entropy): {uncertainty:.4f}")

    is_upset = upset_detection(probs, actual_outcome='away_win')
    print(f"Upset detected: {is_upset}")
