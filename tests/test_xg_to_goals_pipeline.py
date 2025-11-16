"""
Unit tests for xG to Goals Pipeline
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from xg_to_goals_pipeline import XGToGoalsPipeline


class TestXGToGoalsPipeline(unittest.TestCase):
    
    def setUp(self):
        self.pipeline = XGToGoalsPipeline()
    
    def test_xg_to_poisson_lambda(self):
        """Test xG to Poisson lambda conversion"""
        lambda_val = self.pipeline.xg_to_poisson_lambda(1.5)
        self.assertAlmostEqual(lambda_val, 1.425, places=3)
        
    def test_match_outcome_probabilities(self):
        """Test match outcome probability calculation"""
        result = self.pipeline.calculate_match_outcome_probabilities(1.5, 1.0)
        
        # Check all outcomes present
        self.assertIn('home_win', result)
        self.assertIn('draw', result)
        self.assertIn('away_win', result)
        
        # Check probabilities sum to ~1.0
        total = result['home_win'] + result['draw'] + result['away_win']
        self.assertAlmostEqual(total, 1.0, places=2)
        
        # Higher xG should mean higher win probability
        self.assertGreater(result['home_win'], result['away_win'])
    
    def test_over_under_probabilities(self):
        """Test over/under calculation"""
        result = self.pipeline.calculate_over_under_probabilities(1.5, 1.5)
        
        # Check over/under for 2.5 line
        self.assertIn('over_2.5', result)
        self.assertIn('under_2.5', result)
        
        # Over + under should be close to 1.0
        total_25 = result['over_2.5'] + result['under_2.5']
        self.assertAlmostEqual(total_25, 1.0, places=1)
    
    def test_btts_probability(self):
        """Test BTTS calculation"""
        result = self.pipeline.calculate_btts_probability(1.5, 1.5)
        
        self.assertIn('btts_yes', result)
        self.assertIn('btts_no', result)
        
        # Should sum to 1.0
        total = result['btts_yes'] + result['btts_no']
        self.assertAlmostEqual(total, 1.0, places=3)
        
        # With reasonable xG, btts_yes should be likely
        self.assertGreater(result['btts_yes'], 0.3)
    
    def test_correct_score_probabilities(self):
        """Test correct score calculation"""
        result = self.pipeline.calculate_correct_score_probabilities(1.5, 1.0, top_n=5)
        
        # Should return 5 scores
        self.assertEqual(len(result), 5)
        
        # All probabilities should be positive and < 1
        for score, prob in result.items():
            self.assertGreater(prob, 0)
            self.assertLess(prob, 1.0)
    
    def test_full_analysis(self):
        """Test complete analysis pipeline"""
        result = self.pipeline.full_analysis(0.88, 2.32)
        
        # Check all components present
        self.assertIn('input', result)
        self.assertIn('goal_distributions', result)
        self.assertIn('match_outcomes', result)
        self.assertIn('over_under', result)
        self.assertIn('btts', result)
        self.assertIn('top_correct_scores', result)
        
        # Input should match
        self.assertEqual(result['input']['xg_home'], 0.88)
        self.assertEqual(result['input']['xg_away'], 2.32)
        
        # Away win should be more likely (higher xG)
        outcomes = result['match_outcomes']
        self.assertGreater(outcomes['away_win'], outcomes['home_win'])


if __name__ == '__main__':
    unittest.main()
