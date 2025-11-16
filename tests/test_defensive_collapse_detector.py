"""
Unit tests for Defensive Collapse Detector
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from defensive_collapse_detector import DefensiveCollapseDetector


class TestDefensiveCollapseDetector(unittest.TestCase):
    
    def setUp(self):
        self.detector = DefensiveCollapseDetector()
    
    def test_detect_panic_fouls_high_cards(self):
        """Test panic foul detection with high yellow cards"""
        card_data = {
            'yellow_cards': 4,
            'yellow_cards_first_half': 2,
            'fouls_committed': 18,
            'tactical_fouls': 3
        }
        
        result = self.detector.detect_panic_fouls(card_data)
        
        self.assertIn('panic_score', result)
        self.assertIn('risk_level', result)
        self.assertIn('indicators', result)
        
        # High yellow cards should result in high panic score
        self.assertGreater(result['panic_score'], 0.4)
        self.assertIn(result['risk_level'], ['High', 'Critical'])
    
    def test_detect_panic_fouls_normal(self):
        """Test panic foul detection with normal cards"""
        card_data = {
            'yellow_cards': 1,
            'yellow_cards_first_half': 0,
            'fouls_committed': 12,
            'tactical_fouls': 5
        }
        
        result = self.detector.detect_panic_fouls(card_data)
        
        # Normal cards should result in low panic score
        self.assertLess(result['panic_score'], 0.3)
        self.assertEqual(result['risk_level'], 'Low')
    
    def test_detect_shot_suppression_failure(self):
        """Test shot suppression failure detection"""
        defensive_stats = {
            'shots_allowed': 22,
            'shots_on_target_allowed': 12,
            'xg_allowed': 2.8,
            'blocks': 4,
            'clearances': 18
        }
        
        result = self.detector.detect_shot_suppression_failure(defensive_stats)
        
        self.assertIn('failure_score', result)
        self.assertIn('risk_level', result)
        
        # High shots allowed should indicate failure
        self.assertGreater(result['failure_score'], 0.3)
    
    def test_detect_defensive_deterioration(self):
        """Test defensive deterioration detection"""
        time_series_data = [
            {'time_period': '0-15', 'shots_allowed': 3, 'defensive_actions': 12},
            {'time_period': '15-30', 'shots_allowed': 5, 'defensive_actions': 10},
            {'time_period': '30-45', 'shots_allowed': 7, 'defensive_actions': 8},
            {'time_period': '45-60', 'shots_allowed': 8, 'defensive_actions': 7}
        ]
        
        result = self.detector.detect_defensive_deterioration(time_series_data)
        
        self.assertIn('deterioration_score', result)
        self.assertIn('trend', result)
        
        # Increasing shots should indicate deterioration
        self.assertEqual(result['trend'], 'Worsening')
        self.assertGreater(result['deterioration_score'], 0.3)
    
    def test_comprehensive_collapse_assessment(self):
        """Test comprehensive collapse assessment"""
        match_data = {
            'card_data': {
                'yellow_cards': 4,
                'yellow_cards_first_half': 2,
                'fouls_committed': 18,
                'tactical_fouls': 3
            },
            'defensive_stats': {
                'shots_allowed': 22,
                'shots_on_target_allowed': 12,
                'xg_allowed': 2.8,
                'blocks': 4,
                'clearances': 18
            },
            'time_series_data': [
                {'time_period': '0-15', 'shots_allowed': 3, 'defensive_actions': 12},
                {'time_period': '15-30', 'shots_allowed': 5, 'defensive_actions': 10},
                {'time_period': '30-45', 'shots_allowed': 7, 'defensive_actions': 8}
            ],
            'current_score_deficit': 2
        }
        
        result = self.detector.comprehensive_collapse_assessment(match_data)
        
        self.assertIn('overall_collapse_score', result)
        self.assertIn('risk_level', result)
        self.assertIn('blowout_risk', result)
        self.assertIn('components', result)
        self.assertIn('recommendation', result)
        
        # With high cards, shots, and deficit, should be high collapse risk
        self.assertGreater(result['overall_collapse_score'], 0.5)


if __name__ == '__main__':
    unittest.main()
