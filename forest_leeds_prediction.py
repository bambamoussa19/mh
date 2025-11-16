"""
Forest vs. Leeds Prediction Module

This module implements an intelligent prediction query for the upcoming match
between Nottingham Forest (Home) and Leeds United (Away).

It integrates:
- Base probability adjustments
- Form analysis (streaks)
- Fatigue modeling
- Tactical scenario analysis
"""

import numpy as np
from probability_utilities import ProbabilityManager
from fatigue_interaction_model import FatigueInteractionModel
from tactical_interaction_model import TacticalInteractionModel
from streak_regression_model import adjust_streak_logic
from decision_engine import DecisionEngine


class ForestLeedsPrediction:
    """Main prediction class for Forest vs Leeds match"""
    
    def __init__(self):
        self.home_team = "Nottingham Forest"
        self.away_team = "Leeds United"
        
        # Base probabilities
        self.base_probabilities = {
            'home_win': 0.30,
            'draw': 0.40,
            'away_win': 0.30
        }
        
        # Form data
        self.home_form = {
            'unbeaten_streak': 5,
            'description': 'Unbeaten at Home (5 Matches)'
        }
        
        self.away_form = {
            'winless_streak': 7,
            'description': '7 Matches Without a Win'
        }
        
        # Fatigue data
        self.home_fatigue = {
            'rest_days': 7,
            'description': 'Full-rest (+7 days recovery)'
        }
        
        self.away_fatigue = {
            'midweek_match': True,
            'description': 'Midweek Match (-Recovery Factor)'
        }
        
        # Tactical scenario
        self.tactical_scenario = {
            'possession_team': 'Leeds',
            'defensive_team': 'Forest',
            'description': 'Possession (Leeds), Forest defensive'
        }
        
        # Initialize models
        self.fatigue_model = FatigueInteractionModel()
        self.tactical_model = TacticalInteractionModel()
        self.decision_engine = DecisionEngine()
        
        # Store adjustments for audit trail
        self.adjustments_list = []
        self.descriptions_list = []
    
    def calculate_form_adjustment(self):
        """
        Calculate probability adjustments based on team form
        
        Home team unbeaten streak boosts home win probability
        Away team winless streak reduces away win probability
        """
        adjustment = {'home_win': 0, 'draw': 0, 'away_win': 0}
        
        # Home unbeaten streak adjustment
        # Each match in the unbeaten streak adds confidence
        home_streak_factor = min(self.home_form['unbeaten_streak'] * 0.02, 0.10)
        adjustment['home_win'] += home_streak_factor
        adjustment['draw'] += home_streak_factor * 0.5  # Partial boost to draw
        
        # Away winless streak adjustment
        # Reduces away win probability
        away_streak_factor = min(self.away_form['winless_streak'] * 0.015, 0.10)
        adjustment['away_win'] -= away_streak_factor
        
        self.decision_engine.apply_adjustment(
            f"Form: Home unbeaten {self.home_form['unbeaten_streak']}, "
            f"Away winless {self.away_form['winless_streak']}"
        )
        
        return adjustment
    
    def calculate_fatigue_adjustment(self):
        """
        Calculate probability adjustments based on fatigue levels
        
        Home team with full rest has advantage
        Away team with midweek match has disadvantage
        """
        adjustment = {'home_win': 0, 'draw': 0, 'away_win': 0}
        
        # Calculate home team fatigue (well-rested)
        home_rest_days = self.home_fatigue['rest_days']
        if home_rest_days >= 7:
            # Full rest advantage
            rest_bonus = 0.05
            adjustment['home_win'] += rest_bonus
            self.fatigue_model.set_fatigue_level(0)  # No fatigue
        else:
            self.fatigue_model.set_fatigue_level(max(0, 7 - home_rest_days))
        
        # Calculate away team fatigue (midweek match)
        if self.away_fatigue['midweek_match']:
            # Midweek match fatigue penalty
            fatigue_penalty = 0.08
            adjustment['away_win'] -= fatigue_penalty
            adjustment['draw'] += fatigue_penalty * 0.3  # Slightly increases draw
            # Set high fatigue level for away team
            away_fatigue_level = 6
            self.fatigue_model.set_fatigue_level(away_fatigue_level)
        
        self.decision_engine.apply_adjustment(
            f"Fatigue: Home {home_rest_days} days rest, Away midweek match"
        )
        
        return adjustment
    
    def calculate_tactical_adjustment(self):
        """
        Calculate probability adjustments based on tactical scenarios
        
        Leeds prefers possession, Forest plays defensively
        This setup typically favors defensive teams (draws or counter-attacks)
        """
        adjustment = {'home_win': 0, 'draw': 0, 'away_win': 0}
        
        if (self.tactical_scenario['possession_team'] == 'Leeds' and 
            self.tactical_scenario['defensive_team'] == 'Forest'):
            
            # Defensive teams against possession-heavy teams tend to:
            # 1. Increase draw probability (organized defense)
            # 2. Increase home win slightly (counter-attack potential)
            # 3. Reduce away win (harder to break down organized defense)
            
            adjustment['draw'] += 0.06
            adjustment['home_win'] += 0.03  # Counter-attack potential
            adjustment['away_win'] -= 0.04
            
            self.decision_engine.apply_adjustment(
                f"Tactical: {self.tactical_scenario['description']}"
            )
        
        return adjustment
    
    def run_prediction(self):
        """
        Run the complete prediction pipeline
        
        Returns:
            dict: Final probabilities and audit trail
        """
        print("="*80)
        print(f"MATCH PREDICTION: {self.home_team} vs {self.away_team}")
        print("="*80)
        print()
        
        print("Initial Setup:")
        print(f"  Home Team: {self.home_team}")
        print(f"  Away Team: {self.away_team}")
        print(f"  Base Probabilities: {self.base_probabilities}")
        print()
        
        print("Form Analysis:")
        print(f"  Home: {self.home_form['description']}")
        print(f"  Away: {self.away_form['description']}")
        print()
        
        print("Fatigue Analysis:")
        print(f"  Home: {self.home_fatigue['description']}")
        print(f"  Away: {self.away_fatigue['description']}")
        print()
        
        print("Tactical Scenario:")
        print(f"  {self.tactical_scenario['description']}")
        print()
        
        # Calculate adjustments
        form_adj = self.calculate_form_adjustment()
        fatigue_adj = self.calculate_fatigue_adjustment()
        tactical_adj = self.calculate_tactical_adjustment()
        
        # Prepare adjustment sequence
        adjustments_list = [form_adj, fatigue_adj, tactical_adj]
        descriptions_list = [
            "Form Analysis (Home unbeaten 5, Away winless 7)",
            "Fatigue Modeling (Home full rest, Away midweek)",
            "Tactical Scenario (Leeds possession vs Forest defensive)"
        ]
        
        # Apply sequential adjustments using ProbabilityManager
        final_probabilities, audit_trail = ProbabilityManager.apply_sequence_of_adjustments(
            self.base_probabilities,
            adjustments_list,
            descriptions_list
        )
        
        # Print audit trail
        ProbabilityManager.print_audit_trail(audit_trail)
        
        # Print final results
        print("="*80)
        print("FINAL PREDICTION")
        print("="*80)
        print()
        print(f"Home Win ({self.home_team}): {final_probabilities['home_win']:.1%}")
        print(f"Draw: {final_probabilities['draw']:.1%}")
        print(f"Away Win ({self.away_team}): {final_probabilities['away_win']:.1%}")
        print()
        
        # Determine most likely outcome
        max_outcome = max(final_probabilities, key=final_probabilities.get)
        max_prob = final_probabilities[max_outcome]
        
        outcome_names = {
            'home_win': f'{self.home_team} Win',
            'draw': 'Draw',
            'away_win': f'{self.away_team} Win'
        }
        
        print(f"Most Likely Outcome: {outcome_names[max_outcome]} ({max_prob:.1%})")
        print()
        
        # Decision engine audit trail
        print("Decision Engine Audit Trail:")
        for adjustment in self.decision_engine.get_audit_trail():
            print(f"  - {adjustment}")
        print()
        
        return {
            'final_probabilities': final_probabilities,
            'audit_trail': audit_trail,
            'most_likely_outcome': outcome_names[max_outcome],
            'decision_log': self.decision_engine.get_audit_trail()
        }


def main():
    """Main execution function"""
    predictor = ForestLeedsPrediction()
    results = predictor.run_prediction()
    
    print("="*80)
    print("Prediction completed successfully!")
    print("="*80)
    
    return results


if __name__ == "__main__":
    main()
