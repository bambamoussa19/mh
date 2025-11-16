def calculate_draw_probability(possession_parity, xG_difference, tactical_friction, fatigue, midweek_factor, set_piece_threat):
    """
    Calculate draw probability based on various match conditions.

    Parameters:
    possession_parity (float): Ratio of possession between teams.
    xG_difference (float): Expected goals difference between teams.
    tactical_friction (float): Tactical adjustments affecting the game.
    fatigue (float): Fatigue level of the teams.
    midweek_factor (float): Influence of midweek matches.
    set_piece_threat (float): Threat from set-pieces.

    Returns:
    float: Calculated probability of a draw.
    """
    # Example logic to calculate draw probability
    base_probability = 0.2  # Base chance of draw
    possession_effect = possession_parity * 0.1
    xg_effect = -xG_difference * 0.05
    tactical_effect = tactical_friction * 0.1
    fatigue_effect = -fatigue * 0.1
    midweek_effect = midweek_factor * 0.05
    set_piece_effect = set_piece_threat * 0.1
    
    draw_probability = base_probability + possession_effect + xg_effect + tactical_effect + fatigue_effect + midweek_effect + set_piece_effect
    
    # Ensure the probability is within the range [0, 1]
    return max(0, min(1, draw_probability))

# Example usage:
# draw_prob = calculate_draw_probability(0.5, 0.3, 0.2, 0.1, 0.4, 0.3)
# print("Draw probability:", draw_prob)