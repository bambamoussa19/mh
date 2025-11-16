"""
Unit tests for Market Coherence Validator
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from market_coherence_validator import MarketCoherenceValidator


class TestMarketCoherenceValidator(unittest.TestCase):
    
    def setUp(self):
        self.validator = MarketCoherenceValidator()
    
    def test_validate_win_goals_coherence_valid(self):
        """Test coherent win and goals predictions"""
        match_outcomes = {'home_win': 0.65, 'draw': 0.20, 'away_win': 0.15}
        over_under = {'over_2.5': 0.55, 'under_2.5': 0.45, 'under_1.5': 0.20}
        
        result = self.validator.validate_win_goals_coherence(match_outcomes, over_under)
        
        self.assertIn('coherent', result)
        self.assertIn('issues', result)
        self.assertTrue(result['coherent'])
        self.assertEqual(len(result['issues']), 0)
    
    def test_validate_win_goals_coherence_contradiction(self):
        """Test contradictory win and goals predictions"""
        match_outcomes = {'home_win': 0.80, 'draw': 0.12, 'away_win': 0.08}
        over_under = {'over_2.5': 0.30, 'under_2.5': 0.70, 'under_1.5': 0.65}
        
        result = self.validator.validate_win_goals_coherence(match_outcomes, over_under)
        
        self.assertFalse(result['coherent'])
        self.assertGreater(len(result['issues']), 0)
        
        # Should flag high win with low goals
        issue_types = [i['type'] for i in result['issues']]
        self.assertIn('win_low_goals_contradiction', issue_types)
    
    def test_validate_btts_outcome_coherence_valid(self):
        """Test coherent BTTS predictions"""
        btts = {'btts_yes': 0.55, 'btts_no': 0.45}
        match_outcomes = {'home_win': 0.50, 'draw': 0.30, 'away_win': 0.20}
        over_under = {'over_2.5': 0.60, 'under_2.5': 0.40, 'under_1.5': 0.15}
        
        result = self.validator.validate_btts_outcome_coherence(btts, match_outcomes, over_under)
        
        self.assertTrue(result['coherent'])
        self.assertEqual(len([i for i in result['issues'] if i['severity'] in ['critical', 'high']]), 0)
    
    def test_validate_btts_outcome_coherence_contradiction(self):
        """Test contradictory BTTS and goals"""
        btts = {'btts_yes': 0.75, 'btts_no': 0.25}
        match_outcomes = {'home_win': 0.50, 'draw': 0.30, 'away_win': 0.20}
        over_under = {'over_2.5': 0.30, 'under_2.5': 0.70, 'under_1.5': 0.55}
        
        result = self.validator.validate_btts_outcome_coherence(btts, match_outcomes, over_under)
        
        self.assertFalse(result['coherent'])
        
        # Should flag BTTS yes with low total goals
        high_severity = [i for i in result['issues'] if i['severity'] == 'high']
        self.assertGreater(len(high_severity), 0)
    
    def test_validate_correct_score_coherence_valid(self):
        """Test coherent correct score predictions"""
        correct_scores = {
            '2-1': 0.15,
            '2-0': 0.12,
            '1-0': 0.10,
            '1-1': 0.08,
            '0-1': 0.06
        }
        match_outcomes = {'home_win': 0.50, 'draw': 0.25, 'away_win': 0.25}
        
        result = self.validator.validate_correct_score_coherence(correct_scores, match_outcomes)
        
        self.assertIn('aggregated_scores', result)
        
        # Aggregated scores should be close to outcomes
        home_win_diff = abs(result['aggregated_scores']['home_win'] - match_outcomes['home_win'])
        self.assertLess(home_win_diff, 0.20)
    
    def test_validate_xg_outcome_coherence_aligned(self):
        """Test xG aligned with outcomes"""
        xg_values = {'xg_home': 2.0, 'xg_away': 1.0}
        match_outcomes = {'home_win': 0.65, 'draw': 0.20, 'away_win': 0.15}
        
        result = self.validator.validate_xg_outcome_coherence(xg_values, match_outcomes)
        
        self.assertTrue(result['coherent'])
        self.assertEqual(result['xg_difference'], 1.0)
    
    def test_validate_xg_outcome_coherence_misaligned(self):
        """Test xG misaligned with outcomes"""
        xg_values = {'xg_home': 0.5, 'xg_away': 2.5}  # Away much better
        match_outcomes = {'home_win': 0.70, 'draw': 0.20, 'away_win': 0.10}  # Home favored
        
        result = self.validator.validate_xg_outcome_coherence(xg_values, match_outcomes)
        
        # Should flag mismatch
        self.assertGreater(len(result['issues']), 0)
    
    def test_comprehensive_validation_all_pass(self):
        """Test comprehensive validation with coherent data"""
        prediction_data = {
            'match_outcomes': {'home_win': 0.55, 'draw': 0.25, 'away_win': 0.20},
            'over_under': {'over_2.5': 0.50, 'under_2.5': 0.50, 'under_1.5': 0.25},
            'btts': {'btts_yes': 0.50, 'btts_no': 0.50},
            'xg_values': {'xg_home': 1.6, 'xg_away': 1.3},
            'correct_scores': {
                '2-1': 0.12,
                '1-0': 0.10,
                '1-1': 0.10,
                '2-0': 0.08
            }
        }
        
        result = self.validator.comprehensive_validation(prediction_data)
        
        self.assertIn('overall_coherent', result)
        self.assertIn('validation_passed', result)
        self.assertIn('total_issues', result)
        self.assertIn('validations', result)
        
        # Should have low number of issues
        self.assertLess(result['critical_issues'], 1)
    
    def test_comprehensive_validation_with_issues(self):
        """Test comprehensive validation with incoherent data"""
        prediction_data = {
            'match_outcomes': {'home_win': 0.85, 'draw': 0.10, 'away_win': 0.05},
            'over_under': {'over_2.5': 0.20, 'under_2.5': 0.80, 'under_1.5': 0.70},
            'btts': {'btts_yes': 0.70, 'btts_no': 0.30},
            'xg_values': {'xg_home': 0.5, 'xg_away': 2.5},
            'correct_scores': {}
        }
        
        result = self.validator.comprehensive_validation(prediction_data)
        
        # Should find contradictions
        self.assertFalse(result['overall_coherent'])
        self.assertGreater(result['total_issues'], 0)


if __name__ == '__main__':
    unittest.main()
