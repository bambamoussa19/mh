"""
Midweek Fatigue Integrator

Integrates midweek fixture congestion into fatigue modeling.
Fixes the issue where fatigue penalty was only -4% for elite teams
playing midweek matches (should be -15 to -20%).
"""

import numpy as np
from datetime import datetime, timedelta


class MidweekFatigueIntegrator:
    """
    Calculates comprehensive midweek fatigue impact on team performance.
    """
    
    def __init__(self):
        # Base fatigue penalties
        self.base_midweek_penalty = 0.15  # 15% base penalty
        self.elite_competition_multiplier = 1.3  # Champions League, etc.
        self.travel_distance_threshold = 1000  # km
        
    def calculate_midweek_impact(self, fixture_data):
        """
        Calculate midweek fatigue impact on performance.
        
        :param fixture_data: Dict with:
            - days_since_last_match (int): Days of rest
            - competition_type (str): 'league', 'champions_league', 'europa_league', 'domestic_cup'
            - travel_distance (float): Travel distance in km
            - rotation_level (float): 0-1, how much squad was rotated
            - injury_count (int): Current injury count
            - match_intensity (float): 0-1, intensity of previous match
        :return: Dict with fatigue impact metrics
        """
        if not fixture_data:
            return {'fatigue_penalty': 0.0, 'impact_level': 'none'}
        
        days_rest = fixture_data.get('days_since_last_match', 7)
        
        # No midweek impact if 5+ days rest
        if days_rest >= 5:
            return {'fatigue_penalty': 0.0, 'impact_level': 'none'}
        
        # Base penalty calculation
        penalty = self._calculate_base_penalty(days_rest)
        
        # Competition type multiplier
        competition = fixture_data.get('competition_type', 'league')
        competition_multiplier = self._get_competition_multiplier(competition)
        penalty *= competition_multiplier
        
        # Travel distance factor
        travel_distance = fixture_data.get('travel_distance', 0)
        travel_factor = self._calculate_travel_factor(travel_distance)
        penalty *= (1 + travel_factor)
        
        # Rotation mitigation
        rotation = fixture_data.get('rotation_level', 0.3)
        rotation_mitigation = rotation * 0.3  # Up to 30% reduction with full rotation
        penalty *= (1 - rotation_mitigation)
        
        # Injury accumulation factor
        injury_count = fixture_data.get('injury_count', 0)
        if injury_count > 3:
            penalty *= 1.15  # 15% worse with injury crisis
        
        # Match intensity factor
        intensity = fixture_data.get('match_intensity', 0.7)
        intensity_factor = 0.8 + (intensity * 0.4)  # 0.8 to 1.2 range
        penalty *= intensity_factor
        
        # Clamp to reasonable range (5% to 25%)
        penalty = max(0.05, min(0.25, penalty))
        
        # Determine impact level
        if penalty >= 0.18:
            impact_level = 'severe'
        elif penalty >= 0.12:
            impact_level = 'high'
        elif penalty >= 0.08:
            impact_level = 'moderate'
        else:
            impact_level = 'low'
        
        return {
            'fatigue_penalty': penalty,
            'impact_level': impact_level,
            'days_rest': days_rest,
            'effective_penalty_pct': f"{penalty*100:.1f}%"
        }
    
    def _calculate_base_penalty(self, days_rest):
        """Calculate base penalty based on days of rest."""
        if days_rest <= 2:
            return 0.20  # Severe: 48 hours or less
        elif days_rest == 3:
            return 0.15  # High: 72 hours
        elif days_rest == 4:
            return 0.10  # Moderate: 96 hours
        else:
            return 0.05  # Low: 5+ days
    
    def _get_competition_multiplier(self, competition_type):
        """Get multiplier based on competition importance."""
        multipliers = {
            'champions_league': 1.3,
            'europa_league': 1.2,
            'europa_conference': 1.15,
            'domestic_cup': 1.0,
            'league': 1.1
        }
        return multipliers.get(competition_type, 1.0)
    
    def _calculate_travel_factor(self, distance_km):
        """Calculate additional fatigue from travel distance."""
        if distance_km < 500:
            return 0.0
        elif distance_km < 1500:
            return 0.1  # 10% additional fatigue
        elif distance_km < 3000:
            return 0.2  # 20% additional
        else:
            return 0.3  # 30% additional for long-haul
    
    def compare_team_fatigue(self, home_fixture_data, away_fixture_data):
        """
        Compare fatigue levels between home and away teams.
        
        :param home_fixture_data: Home team fixture data
        :param away_fixture_data: Away team fixture data
        :return: Dict with comparative analysis
        """
        home_impact = self.calculate_midweek_impact(home_fixture_data)
        away_impact = self.calculate_midweek_impact(away_fixture_data)
        
        fatigue_differential = home_impact['fatigue_penalty'] - away_impact['fatigue_penalty']
        
        # Determine advantage
        if abs(fatigue_differential) < 0.03:
            advantage = 'neutral'
            advantage_team = None
        elif fatigue_differential < 0:
            advantage = 'home'
            advantage_team = 'home'
        else:
            advantage = 'away'
            advantage_team = 'away'
        
        return {
            'home_fatigue': home_impact,
            'away_fatigue': away_impact,
            'fatigue_differential': fatigue_differential,
            'advantage': advantage,
            'advantage_team': advantage_team,
            'significant_gap': abs(fatigue_differential) > 0.08
        }
    
    def apply_fatigue_to_predictions(self, base_predictions, fatigue_comparison):
        """
        Apply fatigue adjustments to probability predictions.
        
        :param base_predictions: Dict {'home_win': p1, 'draw': p2, 'away_win': p3}
        :param fatigue_comparison: Output from compare_team_fatigue()
        :return: Adjusted predictions
        """
        adjusted = base_predictions.copy()
        
        home_penalty = fatigue_comparison['home_fatigue']['fatigue_penalty']
        away_penalty = fatigue_comparison['away_fatigue']['fatigue_penalty']
        
        # Apply penalties to win probabilities
        home_win_adjustment = -home_penalty * 0.5  # Half the penalty to win prob
        away_win_adjustment = -away_penalty * 0.5
        
        # Fatigue increases draw likelihood
        draw_boost = (home_penalty + away_penalty) * 0.25
        
        adjusted['home_win'] = max(0.05, adjusted['home_win'] + home_win_adjustment + away_penalty * 0.3)
        adjusted['away_win'] = max(0.05, adjusted['away_win'] + away_win_adjustment + home_penalty * 0.3)
        adjusted['draw'] = adjusted['draw'] + draw_boost
        
        # Renormalize
        total = sum(adjusted.values())
        adjusted = {k: v / total for k, v in adjusted.items()}
        
        return adjusted
    
    def get_fixture_congestion_rating(self, upcoming_fixtures):
        """
        Rate the congestion level for upcoming fixture period.
        
        :param upcoming_fixtures: List of upcoming matches with dates
        :return: Congestion rating (0-10 scale)
        """
        if not upcoming_fixtures or len(upcoming_fixtures) < 2:
            return 0
        
        # Count matches in next 14 days
        matches_in_14_days = len([f for f in upcoming_fixtures if f.get('days_away', 99) <= 14])
        
        # Count midweek fixtures
        midweek_count = len([f for f in upcoming_fixtures if f.get('is_midweek', False)])
        
        # Calculate rating
        rating = (matches_in_14_days * 1.5) + (midweek_count * 2)
        rating = min(10, rating)
        
        return rating


# Example usage and testing
if __name__ == '__main__':
    integrator = MidweekFatigueIntegrator()
    
    print("="*70)
    print("MIDWEEK FATIGUE INTEGRATOR - Module Test")
    print("="*70)
    
    # Test 1: Elite team with 3 days rest after Champions League
    print("\nTest 1: Elite Team - Champions League Midweek")
    print("-"*70)
    
    fixture_elite = {
        'days_since_last_match': 3,
        'competition_type': 'champions_league',
        'travel_distance': 2000,
        'rotation_level': 0.2,  # Low rotation
        'injury_count': 4,
        'match_intensity': 0.9
    }
    
    impact_elite = integrator.calculate_midweek_impact(fixture_elite)
    print(f"Fatigue Penalty: {impact_elite['effective_penalty_pct']}")
    print(f"Impact Level: {impact_elite['impact_level']}")
    print(f"Expected: 15-20% (was only 4% before)")
    
    # Test 2: Standard midweek domestic match
    print("\n\nTest 2: Standard Midweek Domestic Match")
    print("-"*70)
    
    fixture_standard = {
        'days_since_last_match': 3,
        'competition_type': 'league',
        'travel_distance': 300,
        'rotation_level': 0.5,
        'injury_count': 1,
        'match_intensity': 0.6
    }
    
    impact_standard = integrator.calculate_midweek_impact(fixture_standard)
    print(f"Fatigue Penalty: {impact_standard['effective_penalty_pct']}")
    print(f"Impact Level: {impact_standard['impact_level']}")
    
    # Test 3: Compare two teams
    print("\n\nTest 3: Team Fatigue Comparison")
    print("-"*70)
    
    home_data = {
        'days_since_last_match': 4,
        'competition_type': 'league',
        'travel_distance': 200,
        'rotation_level': 0.4,
        'injury_count': 2,
        'match_intensity': 0.7
    }
    
    away_data = {
        'days_since_last_match': 3,
        'competition_type': 'champions_league',
        'travel_distance': 1800,
        'rotation_level': 0.2,
        'injury_count': 5,
        'match_intensity': 0.95
    }
    
    comparison = integrator.compare_team_fatigue(home_data, away_data)
    print(f"Home Team Fatigue: {comparison['home_fatigue']['effective_penalty_pct']}")
    print(f"Away Team Fatigue: {comparison['away_fatigue']['effective_penalty_pct']}")
    print(f"Advantage: {comparison['advantage_team']}")
    print(f"Significant Gap: {comparison['significant_gap']}")
    
    # Test 4: Apply to predictions
    print("\n\nTest 4: Apply Fatigue to Predictions")
    print("-"*70)
    
    base_pred = {'home_win': 0.45, 'draw': 0.30, 'away_win': 0.25}
    adjusted_pred = integrator.apply_fatigue_to_predictions(base_pred, comparison)
    
    print(f"Base Predictions:     {base_pred}")
    print(f"Adjusted Predictions: {adjusted_pred}")
    print(f"\nNote: Draw probability increased due to both teams' fatigue")
    
    print("\n" + "="*70)
