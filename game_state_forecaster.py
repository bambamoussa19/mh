# Game State Forecaster Module
# This module provides intelligent diagnosis of the tactical nature of a football match
# before a prediction is made.

# Grind threshold constant - matches with grind_score below this are considered "OPEN_PLAY"
GRIND_THRESHOLD = 7


def calculate_grind_score(team_a_data, team_b_data):
    """
    Calculate the "Grind Score" based on tactical matchup, goalkeeper form, and fortress factor.
    
    :param team_a_data: Dictionary containing home team's tactical and performance data
                        Expected keys: 'formation', 'fortress_rating', 'style_archetype', 'name'
    :param team_b_data: Dictionary containing away team's tactical and performance data
                        Expected keys: 'formation', 'goalkeeper_form', 'style_archetype', 'name'
    :return: Integer grind score representing the likelihood of a grinding match
    """
    grind_score = 0
    
    # Tactical Matchup: Add +5 if formations cause tactical clash
    # Known tactical clashes (examples)
    tactical_clashes = [
        ('4-4-2 deep block', '4-3-3 overloads'),
        ('5-3-2 defensive', '4-3-3 possession'),
        ('4-5-1 counter', '3-4-3 attacking')
    ]
    
    team_a_formation = team_a_data.get('formation', '')
    team_b_formation = team_b_data.get('formation', '')
    
    # Check if this combination is a tactical clash
    for clash_pair in tactical_clashes:
        if (team_a_formation == clash_pair[0] and team_b_formation == clash_pair[1]) or \
           (team_a_formation == clash_pair[1] and team_b_formation == clash_pair[0]):
            grind_score += 5
            break
    
    # Goalkeeper Form: Add points based on away team's goalkeeper form rating
    goalkeeper_form = team_b_data.get('goalkeeper_form', 0)
    if goalkeeper_form >= 7.5:
        grind_score += 3
    elif goalkeeper_form >= 6.5:
        grind_score += 1
    
    # Fortress Factor: Add points based on home team's stadium fortress rating
    fortress_rating = team_a_data.get('fortress_rating', 0)
    if fortress_rating >= 8:
        grind_score += 3
    elif fortress_rating >= 6:
        grind_score += 1
    
    return grind_score


def forecast_game_state(team_a_data, team_b_data):
    """
    Main entry point for the Game State Forecaster module.
    Forecasts the game state based on evidence-first hierarchy and symmetric/asymmetric logic.
    
    :param team_a_data: Dictionary containing home team's tactical and performance data
                        Expected keys: 'formation', 'fortress_rating', 'style_archetype', 'name'
    :param team_b_data: Dictionary containing away team's tactical and performance data
                        Expected keys: 'formation', 'goalkeeper_form', 'style_archetype', 'name'
    :return: Dictionary with scenario type and optional winner_bias
             Possible scenarios: 'OPEN_PLAY', 'SYMMETRIC_GRIND', 'ASYMMETRIC_GRIND'
    """
    # Step 1: Calculate grind score
    grind_score = calculate_grind_score(team_a_data, team_b_data)
    
    # Step 2: Evidence-First Hierarchy
    # If grind_score is below threshold, return OPEN_PLAY scenario
    if grind_score < GRIND_THRESHOLD:
        return {'scenario': 'OPEN_PLAY'}
    
    # Step 3: Symmetric vs. Asymmetric Logic
    # If grind_score is above threshold, analyze playing styles
    team_a_style = team_a_data.get('style_archetype', '')
    team_b_style = team_b_data.get('style_archetype', '')
    
    # Check if both teams are Passive Blockers (symmetric grind)
    if team_a_style == 'Passive Blocker' and team_b_style == 'Passive Blocker':
        return {'scenario': 'SYMMETRIC_GRIND'}
    
    # Check for asymmetric grind (one passive, one proactive)
    if team_a_style == 'Passive Blocker' and team_b_style == 'Proactive Presser':
        # Proactive team (away team) has bias
        return {
            'scenario': 'ASYMMETRIC_GRIND',
            'winner_bias': team_b_data.get('name', 'team_b')
        }
    elif team_a_style == 'Proactive Presser' and team_b_style == 'Passive Blocker':
        # Proactive team (home team) has bias
        return {
            'scenario': 'ASYMMETRIC_GRIND',
            'winner_bias': team_a_data.get('name', 'team_a')
        }
    
    # Placeholder for Execution Score logic (to be implemented later)
    # This section will further refine the prediction based on execution quality
    # For now, default to OPEN_PLAY if no clear pattern is detected
    return {'scenario': 'OPEN_PLAY'}


# Example usage and testing
if __name__ == '__main__':
    # Example 1: Open play scenario (low grind score)
    team_a = {
        'name': 'Home United',
        'formation': '4-3-3 attacking',
        'fortress_rating': 5,
        'style_archetype': 'Proactive Presser'
    }
    team_b = {
        'name': 'Away City',
        'formation': '4-4-2 standard',
        'goalkeeper_form': 6.0,
        'style_archetype': 'Balanced'
    }
    
    print("Example 1 - Low Grind Score:")
    print(f"Grind Score: {calculate_grind_score(team_a, team_b)}")
    print(f"Forecast: {forecast_game_state(team_a, team_b)}")
    print()
    
    # Example 2: Symmetric grind scenario
    team_a = {
        'name': 'Defensive FC',
        'formation': '5-3-2 defensive',
        'fortress_rating': 8,
        'style_archetype': 'Passive Blocker'
    }
    team_b = {
        'name': 'Counter United',
        'formation': '4-3-3 possession',
        'goalkeeper_form': 7.8,
        'style_archetype': 'Passive Blocker'
    }
    
    print("Example 2 - Symmetric Grind:")
    print(f"Grind Score: {calculate_grind_score(team_a, team_b)}")
    print(f"Forecast: {forecast_game_state(team_a, team_b)}")
    print()
    
    # Example 3: Asymmetric grind scenario
    team_a = {
        'name': 'Fortress Stadium',
        'formation': '4-4-2 deep block',
        'fortress_rating': 9,
        'style_archetype': 'Passive Blocker'
    }
    team_b = {
        'name': 'Press Masters',
        'formation': '4-3-3 overloads',
        'goalkeeper_form': 7.5,
        'style_archetype': 'Proactive Presser'
    }
    
    print("Example 3 - Asymmetric Grind:")
    print(f"Grind Score: {calculate_grind_score(team_a, team_b)}")
    print(f"Forecast: {forecast_game_state(team_a, team_b)}")
