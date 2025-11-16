"""
Unit tests for Streak Regression Model with Volatility Detection
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from streak_regression_model import StreakVolatilityDetector, clean_sheet_streak_probability, adjust_streak_logic


class TestStreakVolatilityDetector(unittest.TestCase):
    
    def setUp(self):
        self.detector = StreakVolatilityDetector()
    
    def test_calculate_streak_volatility_stable(self):
        """Test volatility calculation for stable results"""
        stable_results = [1, 1, 1, 1, 1]  # All wins
        volatility = self.detector.calculate_streak_volatility(stable_results)
        
        # Stable results should have low volatility
        self.assertLess(volatility, 0.3)
    
    def test_calculate_streak_volatility_volatile(self):
        """Test volatility calculation for volatile results"""
        volatile_results = [1, -1, 1, -1, 1, -1]  # Win-loss oscillation
        volatility = self.detector.calculate_streak_volatility(volatile_results)
        
        # Oscillating results should have high volatility
        self.assertGreater(volatility, 0.6)
    
    def test_calculate_streak_volatility_mixed(self):
        """Test volatility calculation for mixed results"""
        mixed_results = [1, 1, 0, -1, 1, 0]  # Mixed
        volatility = self.detector.calculate_streak_volatility(mixed_results)
        
        # Mixed results should have moderate volatility
        self.assertGreater(volatility, 0.3)
        self.assertLess(volatility, 0.7)
    
    def test_calculate_streak_volatility_insufficient_data(self):
        """Test volatility with insufficient data"""
        short_results = [1, -1]
        volatility = self.detector.calculate_streak_volatility(short_results)
        
        # Should return neutral volatility
        self.assertEqual(volatility, 0.5)
    
    def test_detect_streak_sustainability_sustainable_winning(self):
        """Test sustainability of sustainable winning streak"""
        streak_data = {
            'current_streak': 5,
            'recent_results': [1, 1, 1, 1, 1],
            'performance_metrics': {
                'xg_trend': 0.2,
                'shot_quality_trend': 0.15
            }
        }
        
        result = self.detector.detect_streak_sustainability(streak_data)
        
        self.assertIn('sustainability_score', result)
        self.assertIn('volatility', result)
        self.assertIn('regression_risk', result)
        
        # Sustainable winning streak with positive metrics
        self.assertGreater(result['sustainability_score'], 0.6)
        self.assertEqual(result['regression_risk'], 'Low')
    
    def test_detect_streak_sustainability_lucky_wins(self):
        """Test sustainability of lucky winning streak"""
        streak_data = {
            'current_streak': 4,
            'recent_results': [1, 1, 1, 1],
            'performance_metrics': {
                'xg_trend': -0.3,  # Negative xG trend = lucky wins
                'shot_quality_trend': -0.2
            }
        }
        
        result = self.detector.detect_streak_sustainability(streak_data)
        
        # Lucky wins should have low or moderate sustainability
        self.assertLessEqual(result['sustainability_score'], 0.5)
        # Recommendation should show caution (monitor or regression)
        self.assertIn('monitor', result['recommendation'].lower())
    
    def test_detect_streak_sustainability_volatile_streak(self):
        """Test sustainability of volatile streak"""
        streak_data = {
            'current_streak': 2,
            'recent_results': [1, -1, 1, -1, 1, 1],  # Volatile then wins
            'performance_metrics': {
                'xg_trend': 0.1,
                'shot_quality_trend': 0.05
            }
        }
        
        result = self.detector.detect_streak_sustainability(streak_data)
        
        # Volatile pattern should indicate regression risk
        self.assertEqual(result['regression_risk'], 'High')


class TestStreakUtilityFunctions(unittest.TestCase):
    
    def test_clean_sheet_streak_probability(self):
        """Test clean sheet streak probability calculation"""
        streaks = [0, 1, 2, 3, 4, 5]
        probs = clean_sheet_streak_probability(streaks)
        
        # Should return probabilities for each streak
        self.assertEqual(len(probs), len(streaks))
        
        # Probabilities should sum to 1
        self.assertAlmostEqual(sum(probs), 1.0, places=2)
        
        # Longer streaks should have lower probability
        self.assertGreater(probs[0], probs[-1])
    
    def test_clean_sheet_streak_probability_empty(self):
        """Test clean sheet probability with empty input"""
        probs = clean_sheet_streak_probability([])
        self.assertEqual(len(probs), 1)
    
    def test_adjust_streak_logic_no_volatility(self):
        """Test streak adjustment without volatility"""
        adjusted = adjust_streak_logic(3)
        self.assertGreater(adjusted, 0)
        self.assertLessEqual(adjusted, 3)
    
    def test_adjust_streak_logic_with_volatility(self):
        """Test streak adjustment with volatility"""
        # High volatility should reduce streak weight
        high_vol_adjusted = adjust_streak_logic(5, volatility=0.8)
        low_vol_adjusted = adjust_streak_logic(5, volatility=0.2)
        
        self.assertLess(high_vol_adjusted, low_vol_adjusted)
    
    def test_adjust_streak_logic_long_streak(self):
        """Test adjustment of long streak"""
        long_streak = adjust_streak_logic(7)
        short_streak = adjust_streak_logic(3)
        
        # Long streaks get diminishing returns
        self.assertLess(long_streak / 7, short_streak / 3)


if __name__ == '__main__':
    unittest.main()
