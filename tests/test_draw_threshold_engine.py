"""
Unit tests for Draw Threshold Engine
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from draw_threshold_engine import DrawThresholdEngine


class TestDrawThresholdEngine(unittest.TestCase):
    
    def setUp(self):
        self.engine = DrawThresholdEngine()
    
    def test_calculate_draw_probability_even_match(self):
        """Test draw probability for evenly matched teams"""
        features = {
            'home_form': 0.50,
            'away_form': 0.50,
            'home_strength': 0.50,
            'away_strength': 0.50,
            'home_defensive_rating': 0.70,
            'away_defensive_rating': 0.70,
            'head_to_head_draws': 2,
            'home_goals_avg': 1.3,
            'away_goals_avg': 1.3,
            'league_draw_rate': 0.27
        }
        
        prob = self.engine.calculate_draw_probability(features)
        
        # Evenly matched with good defense should have higher draw probability
        self.assertGreater(prob, 0.35)
        self.assertLessEqual(prob, 0.70)
    
    def test_calculate_draw_probability_mismatch(self):
        """Test draw probability for mismatched teams"""
        features = {
            'home_form': 0.80,
            'away_form': 0.30,
            'home_strength': 0.75,
            'away_strength': 0.35,
            'home_defensive_rating': 0.50,
            'away_defensive_rating': 0.40,
            'head_to_head_draws': 0,
            'home_goals_avg': 2.5,
            'away_goals_avg': 1.0,
            'league_draw_rate': 0.27
        }
        
        prob = self.engine.calculate_draw_probability(features)
        
        # Mismatched teams should have lower draw probability
        self.assertLess(prob, 0.30)
    
    def test_calculate_draw_probability_defensive_match(self):
        """Test draw probability for defensive match"""
        features = {
            'home_form': 0.55,
            'away_form': 0.50,
            'home_strength': 0.52,
            'away_strength': 0.50,
            'home_defensive_rating': 0.85,
            'away_defensive_rating': 0.80,
            'head_to_head_draws': 3,
            'home_goals_avg': 1.1,
            'away_goals_avg': 1.0,
            'league_draw_rate': 0.27
        }
        
        prob = self.engine.calculate_draw_probability(features)
        
        # Strong defenses + low scoring should increase draw likelihood
        self.assertGreater(prob, 0.40)
    
    def test_intelligent_draw_decision_high_confidence(self):
        """Test draw decision with high confidence"""
        features = {
            'home_form': 0.50,
            'away_form': 0.50,
            'home_strength': 0.50,
            'away_strength': 0.50,
            'home_defensive_rating': 0.75,
            'away_defensive_rating': 0.75,
            'head_to_head_draws': 3,
            'home_goals_avg': 1.2,
            'away_goals_avg': 1.2,
            'league_draw_rate': 0.27
        }
        
        result = self.engine.intelligent_draw_decision(features)
        
        self.assertIn('prediction', result)
        self.assertIn('probability', result)
        self.assertIn('confidence', result)
        self.assertIn('details', result)
        
        # Should predict draw with high confidence
        self.assertEqual(result['prediction'], 'Draw')
        self.assertIn(result['confidence'], ['Medium', 'High'])
    
    def test_intelligent_draw_decision_low_confidence(self):
        """Test draw decision with low confidence"""
        features = {
            'home_form': 0.80,
            'away_form': 0.30,
            'home_strength': 0.75,
            'away_strength': 0.35,
            'home_defensive_rating': 0.50,
            'away_defensive_rating': 0.40,
            'head_to_head_draws': 0,
            'home_goals_avg': 2.5,
            'away_goals_avg': 1.0,
            'league_draw_rate': 0.27
        }
        
        result = self.engine.intelligent_draw_decision(features)
        
        # Should predict no draw
        self.assertEqual(result['prediction'], 'No Draw')
        self.assertGreater(result['probability'], 0)
    
    def test_probability_bounds(self):
        """Test that probabilities stay within valid bounds"""
        # Extreme values
        features = {
            'home_form': 1.0,
            'away_form': 0.0,
            'home_strength': 1.0,
            'away_strength': 0.0,
            'home_defensive_rating': 1.0,
            'away_defensive_rating': 0.0,
            'head_to_head_draws': 10,
            'home_goals_avg': 5.0,
            'away_goals_avg': 0.0,
            'league_draw_rate': 0.27
        }
        
        prob = self.engine.calculate_draw_probability(features)
        
        # Should be within bounds
        self.assertGreaterEqual(prob, 0.0)
        self.assertLessEqual(prob, 1.0)


if __name__ == '__main__':
    unittest.main()
