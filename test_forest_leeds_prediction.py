"""
Unit tests for Forest vs Leeds Prediction Module
"""

import unittest
from forest_leeds_prediction import ForestLeedsPrediction


class TestForestLeedsPrediction(unittest.TestCase):
    """Test cases for the Forest vs Leeds prediction system"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.predictor = ForestLeedsPrediction()
    
    def test_initialization(self):
        """Test that predictor initializes with correct values"""
        self.assertEqual(self.predictor.home_team, "Nottingham Forest")
        self.assertEqual(self.predictor.away_team, "Leeds United")
        
        # Check base probabilities sum to 1.0
        prob_sum = sum(self.predictor.base_probabilities.values())
        self.assertAlmostEqual(prob_sum, 1.0, places=5)
    
    def test_base_probabilities(self):
        """Test that base probabilities are correct"""
        self.assertEqual(self.predictor.base_probabilities['home_win'], 0.30)
        self.assertEqual(self.predictor.base_probabilities['draw'], 0.40)
        self.assertEqual(self.predictor.base_probabilities['away_win'], 0.30)
    
    def test_form_adjustment(self):
        """Test form analysis adjustment calculation"""
        form_adj = self.predictor.calculate_form_adjustment()
        
        # Check that adjustment is a dict with correct keys
        self.assertIn('home_win', form_adj)
        self.assertIn('draw', form_adj)
        self.assertIn('away_win', form_adj)
        
        # Home unbeaten should increase home_win probability
        self.assertGreater(form_adj['home_win'], 0)
        
        # Away winless should decrease away_win probability
        self.assertLess(form_adj['away_win'], 0)
    
    def test_fatigue_adjustment(self):
        """Test fatigue modeling adjustment calculation"""
        fatigue_adj = self.predictor.calculate_fatigue_adjustment()
        
        # Check that adjustment is a dict with correct keys
        self.assertIn('home_win', fatigue_adj)
        self.assertIn('draw', fatigue_adj)
        self.assertIn('away_win', fatigue_adj)
        
        # Home full rest should increase home_win probability
        self.assertGreater(fatigue_adj['home_win'], 0)
        
        # Away midweek match should decrease away_win probability
        self.assertLess(fatigue_adj['away_win'], 0)
    
    def test_tactical_adjustment(self):
        """Test tactical scenario adjustment calculation"""
        tactical_adj = self.predictor.calculate_tactical_adjustment()
        
        # Check that adjustment is a dict with correct keys
        self.assertIn('home_win', tactical_adj)
        self.assertIn('draw', tactical_adj)
        self.assertIn('away_win', tactical_adj)
        
        # Defensive vs possession should increase draw probability
        self.assertGreater(tactical_adj['draw'], 0)
    
    def test_run_prediction(self):
        """Test complete prediction pipeline"""
        results = self.predictor.run_prediction()
        
        # Check that results contain expected keys
        self.assertIn('final_probabilities', results)
        self.assertIn('audit_trail', results)
        self.assertIn('most_likely_outcome', results)
        self.assertIn('decision_log', results)
        
        # Check final probabilities sum to 1.0
        final_probs = results['final_probabilities']
        prob_sum = sum(final_probs.values())
        self.assertAlmostEqual(prob_sum, 1.0, places=5)
        
        # Check all probabilities are between 0 and 1
        for prob in final_probs.values():
            self.assertGreaterEqual(prob, 0)
            self.assertLessEqual(prob, 1)
    
    def test_form_data_structure(self):
        """Test that form data has correct structure"""
        self.assertIn('unbeaten_streak', self.predictor.home_form)
        self.assertIn('description', self.predictor.home_form)
        self.assertEqual(self.predictor.home_form['unbeaten_streak'], 5)
        
        self.assertIn('winless_streak', self.predictor.away_form)
        self.assertIn('description', self.predictor.away_form)
        self.assertEqual(self.predictor.away_form['winless_streak'], 7)
    
    def test_fatigue_data_structure(self):
        """Test that fatigue data has correct structure"""
        self.assertIn('rest_days', self.predictor.home_fatigue)
        self.assertIn('description', self.predictor.home_fatigue)
        self.assertEqual(self.predictor.home_fatigue['rest_days'], 7)
        
        self.assertIn('midweek_match', self.predictor.away_fatigue)
        self.assertIn('description', self.predictor.away_fatigue)
        self.assertTrue(self.predictor.away_fatigue['midweek_match'])
    
    def test_tactical_data_structure(self):
        """Test that tactical data has correct structure"""
        self.assertIn('possession_team', self.predictor.tactical_scenario)
        self.assertIn('defensive_team', self.predictor.tactical_scenario)
        self.assertIn('description', self.predictor.tactical_scenario)
        self.assertEqual(self.predictor.tactical_scenario['possession_team'], 'Leeds')
        self.assertEqual(self.predictor.tactical_scenario['defensive_team'], 'Forest')
    
    def test_probability_bounds(self):
        """Test that final probabilities stay within valid bounds"""
        results = self.predictor.run_prediction()
        final_probs = results['final_probabilities']
        
        # All probabilities should be non-negative
        for key, prob in final_probs.items():
            self.assertGreaterEqual(prob, 0, 
                f"{key} probability {prob} is negative")
            self.assertLessEqual(prob, 1, 
                f"{key} probability {prob} exceeds 1")
    
    def test_decision_engine_logging(self):
        """Test that decision engine logs adjustments"""
        self.predictor.run_prediction()
        audit_trail = self.predictor.decision_engine.get_audit_trail()
        
        # Should have logged adjustments
        self.assertGreater(len(audit_trail), 0)
        
        # Should include form, fatigue, and tactical adjustments
        audit_str = ' '.join(audit_trail)
        self.assertIn('Form', audit_str)
        self.assertIn('Fatigue', audit_str)
        self.assertIn('Tactical', audit_str)


class TestPredictionConsistency(unittest.TestCase):
    """Test prediction consistency and reproducibility"""
    
    def test_multiple_runs_consistency(self):
        """Test that multiple runs produce consistent results"""
        predictor1 = ForestLeedsPrediction()
        results1 = predictor1.run_prediction()
        
        predictor2 = ForestLeedsPrediction()
        results2 = predictor2.run_prediction()
        
        # Results should be identical
        probs1 = results1['final_probabilities']
        probs2 = results2['final_probabilities']
        
        for key in probs1:
            self.assertAlmostEqual(probs1[key], probs2[key], places=10)


if __name__ == '__main__':
    # Run tests with minimal output for successful tests
    unittest.main(verbosity=2)
