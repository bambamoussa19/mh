"""
Set Piece Threat Analyzer

Detects and models late-game set-piece goals that often lead to draws.
Addresses the blind spot in predictions where set-piece equalizers weren't considered.
"""

import numpy as np


class SetPieceThreatAnalyzer:
    """
    Analyzes set-piece threat for late-game equalizers and goals.
    """
    
    def __init__(self):
        self.late_game_threshold = 75  # Minutes
        self.set_piece_types = ['corner', 'free_kick', 'penalty']
        
    def calculate_set_piece_threat(self, team_data):
        """
        Calculate overall set-piece threat for a team.
        
        :param team_data: Dict with:
            - set_piece_goals (int): Goals from set pieces this season
            - total_goals (int): Total goals scored
            - corners_per_game (float): Average corners per game
            - set_piece_accuracy (float): 0-1 scale
            - tall_players_count (int): Number of players >185cm
            - set_piece_specialist (bool): Has a known specialist
        :return: Threat score (0-1 scale)
        """
        if not team_data:
            return 0.5
        
        threat_score = 0.0
        
        # Component 1: Set-piece conversion rate
        sp_goals = team_data.get('set_piece_goals', 0)
        total_goals = team_data.get('total_goals', 1)
        conversion_rate = sp_goals / total_goals if total_goals > 0 else 0.25
        
        # High conversion rate = high threat
        threat_score += min(0.30, conversion_rate * 1.2)
        
        # Component 2: Corner frequency
        corners_per_game = team_data.get('corners_per_game', 5.0)
        corner_component = min(0.20, (corners_per_game / 8.0) * 0.20)
        threat_score += corner_component
        
        # Component 3: Set-piece accuracy
        accuracy = team_data.get('set_piece_accuracy', 0.25)
        threat_score += accuracy * 0.25
        
        # Component 4: Aerial presence
        tall_players = team_data.get('tall_players_count', 3)
        aerial_component = min(0.15, (tall_players / 5.0) * 0.15)
        threat_score += aerial_component
        
        # Component 5: Specialist bonus
        if team_data.get('set_piece_specialist', False):
            threat_score += 0.10
        
        # Normalize to 0-1
        threat_score = min(1.0, threat_score)
        
        return threat_score
    
    def calculate_late_game_equalizer_probability(self, match_state, set_piece_threats):
        """
        Calculate probability of late-game equalizer via set piece.
        
        :param match_state: Dict with:
            - current_minute (int): Match minute
            - score_home (int): Home goals
            - score_away (int): Away goals
            - corners_so_far (int): Total corners in match
            - fouls_defensive_third (int): Fouls in dangerous areas
        :param set_piece_threats: Dict with 'home' and 'away' threat scores
        :return: Equalizer probability
        """
        if not match_state or not set_piece_threats:
            return 0.0
        
        minute = match_state.get('current_minute', 45)
        score_home = match_state.get('score_home', 0)
        score_away = match_state.get('score_away', 0)
        score_diff = abs(score_home - score_away)
        
        # Only relevant in late game
        if minute < self.late_game_threshold:
            return 0.0
        
        # Only relevant if one-goal difference or drawing
        if score_diff > 1:
            return 0.0
        
        # Determine which team would equalize
        if score_home > score_away:
            threat = set_piece_threats.get('away', 0.5)
        elif score_away > score_home:
            threat = set_piece_threats.get('home', 0.5)
        else:
            # Already drawing
            return 0.0
        
        # Base probability increases with time
        time_factor = (minute - self.late_game_threshold) / (90 - self.late_game_threshold)
        base_prob = 0.05 + (time_factor * 0.10)  # 5% to 15% based on time
        
        # Adjust by set-piece threat
        equalizer_prob = base_prob * (0.5 + threat)
        
        # Boost for high corner count
        corners = match_state.get('corners_so_far', 8)
        if corners > 10:
            equalizer_prob *= 1.2
        elif corners > 15:
            equalizer_prob *= 1.4
        
        # Boost for fouls in defensive third
        fouls = match_state.get('fouls_defensive_third', 5)
        if fouls > 8:
            equalizer_prob *= 1.15
        
        return min(0.30, equalizer_prob)
    
    def analyze_set_piece_vulnerability(self, defensive_data):
        """
        Analyze defensive vulnerability to set pieces.
        
        :param defensive_data: Dict with:
            - goals_conceded_set_pieces (int): Goals conceded from set pieces
            - total_goals_conceded (int): Total goals conceded
            - aerial_duels_won_pct (float): 0-1 scale
            - goalkeeper_crosses_claimed (int): Crosses claimed by GK
            - zonal_marking (bool): Uses zonal vs man marking
        :return: Vulnerability score (0-1 scale)
        """
        if not defensive_data:
            return 0.5
        
        vulnerability = 0.0
        
        # Component 1: Set-piece goals conceded rate
        sp_conceded = defensive_data.get('goals_conceded_set_pieces', 0)
        total_conceded = defensive_data.get('total_goals_conceded', 1)
        concession_rate = sp_conceded / total_conceded if total_conceded > 0 else 0.25
        
        vulnerability += min(0.40, concession_rate * 1.6)
        
        # Component 2: Aerial duel success (inverse)
        aerial_won = defensive_data.get('aerial_duels_won_pct', 0.50)
        aerial_vulnerability = (1.0 - aerial_won) * 0.30
        vulnerability += aerial_vulnerability
        
        # Component 3: Goalkeeper command (inverse)
        gk_crosses = defensive_data.get('goalkeeper_crosses_claimed', 15)
        gk_vulnerability = max(0, 0.20 - (gk_crosses / 50.0))
        vulnerability += gk_vulnerability
        
        # Component 4: Marking system
        if defensive_data.get('zonal_marking', False):
            vulnerability += 0.10  # Zonal marking often weaker to set pieces
        
        return min(1.0, vulnerability)
    
    def get_set_piece_adjustment(self, home_threat, away_threat, home_vulnerability, away_vulnerability):
        """
        Get probability adjustments based on set-piece analysis.
        
        :param home_threat: Home team threat score
        :param away_threat: Away team threat score
        :param home_vulnerability: Home team vulnerability
        :param away_vulnerability: Away team vulnerability
        :return: Dict with probability adjustments
        """
        # Calculate expected set-piece goals
        home_expected_sp_goals = home_threat * away_vulnerability * 0.5
        away_expected_sp_goals = away_threat * home_vulnerability * 0.5
        
        sp_differential = home_expected_sp_goals - away_expected_sp_goals
        
        # If set pieces favoring draws (both teams capable)
        if abs(sp_differential) < 0.1 and (home_threat + away_threat) > 1.0:
            draw_boost = 0.05
        else:
            draw_boost = 0.02
        
        # Adjust win probabilities based on set-piece advantage
        if sp_differential > 0.1:
            home_boost = sp_differential * 0.15
            away_penalty = -sp_differential * 0.10
        elif sp_differential < -0.1:
            home_penalty = sp_differential * 0.10
            away_boost = -sp_differential * 0.15
        else:
            home_boost = 0
            home_penalty = 0
            away_boost = 0
            away_penalty = 0
        
        return {
            'home_win': home_boost if sp_differential > 0 else home_penalty,
            'draw': draw_boost,
            'away_win': away_boost if sp_differential < 0 else away_penalty
        }
    
    def predict_set_piece_goal_count(self, match_context):
        """
        Predict expected goals from set pieces in the match.
        
        :param match_context: Dict with both teams' set-piece data
        :return: Expected set-piece goals
        """
        home_threat = self.calculate_set_piece_threat(match_context.get('home_team', {}))
        away_threat = self.calculate_set_piece_threat(match_context.get('away_team', {}))
        
        home_vuln = self.analyze_set_piece_vulnerability(match_context.get('away_defense', {}))
        away_vuln = self.analyze_set_piece_vulnerability(match_context.get('home_defense', {}))
        
        # Expected set-piece goals
        home_sp_xg = home_threat * away_vuln * 0.6  # Average ~0.6 goals per team from set pieces
        away_sp_xg = away_threat * home_vuln * 0.6
        
        total_sp_xg = home_sp_xg + away_sp_xg
        
        return {
            'home_set_piece_xg': round(home_sp_xg, 2),
            'away_set_piece_xg': round(away_sp_xg, 2),
            'total_set_piece_xg': round(total_sp_xg, 2),
            'set_piece_percentage': round((total_sp_xg / 3.0) * 100, 1)  # As % of typical 3-goal game
        }


# Example usage and testing
if __name__ == '__main__':
    analyzer = SetPieceThreatAnalyzer()
    
    print("="*70)
    print("SET PIECE THREAT ANALYZER - Module Test")
    print("="*70)
    
    # Test 1: High threat team
    print("\nTest 1: High Set-Piece Threat Team")
    print("-"*70)
    
    high_threat_team = {
        'set_piece_goals': 12,
        'total_goals': 35,
        'corners_per_game': 7.5,
        'set_piece_accuracy': 0.35,
        'tall_players_count': 5,
        'set_piece_specialist': True
    }
    
    threat_score = analyzer.calculate_set_piece_threat(high_threat_team)
    print(f"Set-Piece Threat Score: {threat_score:.3f}")
    print(f"(12/35 = 34% of goals from set pieces + good delivery)")
    
    # Test 2: Vulnerable defense
    print("\n\nTest 2: Set-Piece Vulnerable Defense")
    print("-"*70)
    
    vulnerable_defense = {
        'goals_conceded_set_pieces': 8,
        'total_goals_conceded': 20,
        'aerial_duels_won_pct': 0.42,
        'goalkeeper_crosses_claimed': 10,
        'zonal_marking': True
    }
    
    vulnerability = analyzer.analyze_set_piece_vulnerability(vulnerable_defense)
    print(f"Set-Piece Vulnerability: {vulnerability:.3f}")
    print(f"(8/20 = 40% of goals conceded from set pieces)")
    
    # Test 3: Late game equalizer scenario
    print("\n\nTest 3: Late Game Equalizer Probability")
    print("-"*70)
    
    match_state = {
        'current_minute': 82,
        'score_home': 1,
        'score_away': 0,
        'corners_so_far': 12,
        'fouls_defensive_third': 9
    }
    
    set_piece_threats = {
        'home': threat_score,
        'away': 0.72  # Away team has good set-piece threat
    }
    
    equalizer_prob = analyzer.calculate_late_game_equalizer_probability(
        match_state, set_piece_threats
    )
    print(f"Late Equalizer Probability: {equalizer_prob:.1%}")
    print(f"Context: Minute 82, Away losing 0-1, 12 corners, 9 fouls")
    
    # Test 4: Set-piece goal prediction
    print("\n\nTest 4: Set-Piece Goal Prediction")
    print("-"*70)
    
    match_context = {
        'home_team': high_threat_team,
        'away_team': {
            'set_piece_goals': 8,
            'total_goals': 28,
            'corners_per_game': 6.2,
            'set_piece_accuracy': 0.28,
            'tall_players_count': 4,
            'set_piece_specialist': False
        },
        'home_defense': {
            'goals_conceded_set_pieces': 5,
            'total_goals_conceded': 18,
            'aerial_duels_won_pct': 0.55,
            'goalkeeper_crosses_claimed': 18,
            'zonal_marking': False
        },
        'away_defense': vulnerable_defense
    }
    
    sp_prediction = analyzer.predict_set_piece_goal_count(match_context)
    print(f"Home Set-Piece xG: {sp_prediction['home_set_piece_xg']}")
    print(f"Away Set-Piece xG: {sp_prediction['away_set_piece_xg']}")
    print(f"Total Set-Piece xG: {sp_prediction['total_set_piece_xg']}")
    print(f"Set-Piece % of Total: {sp_prediction['set_piece_percentage']}%")
    
    print("\n" + "="*70)
