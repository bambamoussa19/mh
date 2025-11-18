"""
Unit tests for the Intelligent Prediction Module
"""

import unittest
import numpy as np
from intelligent_prediction_module import (
    IntelligentPredictionModule,
    rank_predictions,
    format_predictions_report
)


class TestIntelligentPredictionModule(unittest.TestCase):
    """Test cases for IntelligentPredictionModule"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.predictor = IntelligentPredictionModule()
        
    def test_initialization(self):
        """Test that module initializes correctly"""
        self.assertIsNotNone(self.predictor.fatigue_model)
        self.assertIsNotNone(self.predictor.tactical_model)
        self.assertIsNotNone(self.predictor.probability_manager)
        
    def test_integrate_fatigue_insights(self):
        """Test fatigue integration logic"""
        result = self.predictor.integrate_fatigue_insights(3, 5)
        
        self.assertIn('home_adjustment', result)
        self.assertIn('away_adjustment', result)
        self.assertIn('draw_adjustment', result)
        
        # Check that adjustments are reasonable floats
        self.assertIsInstance(result['home_adjustment'], float)
        self.assertIsInstance(result['away_adjustment'], float)
        self.assertIsInstance(result['draw_adjustment'], float)
        
    def test_integrate_fatigue_insights_edge_cases(self):
        """Test fatigue integration with edge cases"""
        # Zero fatigue
        result = self.predictor.integrate_fatigue_insights(0, 0)
        self.assertIsInstance(result['draw_adjustment'], float)
        
        # Max fatigue
        result = self.predictor.integrate_fatigue_insights(10, 10)
        self.assertIsInstance(result['draw_adjustment'], float)
        
    def test_integrate_tactical_insights(self):
        """Test tactical integration"""
        match_data = {'formation': '4-4-2', 'style': 'possession'}
        result = self.predictor.integrate_tactical_insights(match_data)
        
        self.assertIn('home_adjustment', result)
        self.assertIn('away_adjustment', result)
        self.assertIn('draw_adjustment', result)
        
    def test_integrate_draw_threshold(self):
        """Test draw threshold calculation"""
        base_probs = {'home_win': 0.45, 'draw': 0.30, 'away_win': 0.25}
        result = self.predictor.integrate_draw_threshold(base_probs, 30)
        
        self.assertIsInstance(result, float)
        self.assertGreaterEqual(result, 0.0)
        self.assertLessEqual(result, 0.1)  # Cap at 10%
        
    def test_integrate_streak_regression(self):
        """Test streak regression logic"""
        result = self.predictor.integrate_streak_regression(5, 2)
        
        self.assertIn('home_adjustment', result)
        self.assertIn('away_adjustment', result)
        self.assertIn('draw_adjustment', result)
        
        # Long streak should have negative adjustment (regression)
        self.assertLess(result['home_adjustment'], 0.0)
        
    def test_calculate_match_result_probabilities(self):
        """Test match result probability calculation"""
        result = self.predictor.calculate_match_result_probabilities(
            base_home_win=0.45,
            base_draw=0.30,
            base_away_win=0.25,
            fatigue_home=3,
            fatigue_away=5
        )
        
        self.assertIn('home_win', result)
        self.assertIn('draw', result)
        self.assertIn('away_win', result)
        
        # Probabilities should sum to approximately 1.0
        total = sum(result.values())
        self.assertAlmostEqual(total, 1.0, places=5)
        
        # All probabilities should be between 0 and 1
        for prob in result.values():
            self.assertGreaterEqual(prob, 0.0)
            self.assertLessEqual(prob, 1.0)
            
    def test_calculate_goals_market_probabilities(self):
        """Test goals market probability calculation"""
        match_result_probs = {
            'home_win': 0.45,
            'draw': 0.30,
            'away_win': 0.25
        }
        
        result = self.predictor.calculate_goals_market_probabilities(
            match_result_probs,
            fatigue_home=2,
            fatigue_away=3
        )
        
        self.assertIn('over_under', result)
        self.assertIn('btts', result)
        
        # Check over/under markets
        self.assertIn('over_2.5', result['over_under'])
        self.assertIn('under_2.5', result['over_under'])
        
        # Check BTTS markets
        self.assertIn('yes', result['btts'])
        self.assertIn('no', result['btts'])
        
        # Over/Under should sum to 1.0
        over_25 = result['over_under']['over_2.5']
        under_25 = result['over_under']['under_2.5']
        self.assertAlmostEqual(over_25 + under_25, 1.0, places=5)
        
        # BTTS should sum to 1.0
        btts_yes = result['btts']['yes']
        btts_no = result['btts']['no']
        self.assertAlmostEqual(btts_yes + btts_no, 1.0, places=5)
        
    def test_calculate_correct_score_probabilities(self):
        """Test correct score probability calculation"""
        match_result_probs = {
            'home_win': 0.45,
            'draw': 0.30,
            'away_win': 0.25
        }
        
        goals_market_probs = {
            'over_under': {
                'over_2.5': 0.5,
                'under_2.5': 0.5
            },
            'btts': {
                'yes': 0.5,
                'no': 0.5
            }
        }
        
        result = self.predictor.calculate_correct_score_probabilities(
            match_result_probs,
            goals_market_probs
        )
        
        # Check that common scores are present
        self.assertIn('1-0', result)
        self.assertIn('0-0', result)
        self.assertIn('1-1', result)
        self.assertIn('2-1', result)
        
        # All probabilities should be valid
        for prob in result.values():
            self.assertGreaterEqual(prob, 0.0)
            self.assertLessEqual(prob, 1.0)
            
        # Probabilities should sum to approximately 1.0
        total = sum(result.values())
        self.assertAlmostEqual(total, 1.0, places=5)
        
    def test_calculate_confidence_score(self):
        """Test confidence score calculation"""
        # High probability should give high confidence
        high_conf = self.predictor.calculate_confidence_score(0.8, 'match_result')
        self.assertGreater(high_conf, 60.0)
        
        # Low probability should give low confidence
        low_conf = self.predictor.calculate_confidence_score(0.3, 'match_result')
        self.assertLess(low_conf, 40.0)
        
        # Confidence should be between 0 and 100
        for prob in [0.1, 0.3, 0.5, 0.7, 0.9]:
            conf = self.predictor.calculate_confidence_score(prob, 'match_result')
            self.assertGreaterEqual(conf, 0.0)
            self.assertLessEqual(conf, 100.0)
            
    def test_generate_predictions_all_markets(self):
        """Test comprehensive prediction generation"""
        result = self.predictor.generate_predictions(
            base_home_win=0.45,
            base_draw=0.30,
            base_away_win=0.25,
            fatigue_home=3,
            fatigue_away=5,
            tactical_data={'formation': '4-4-2'},
            home_streak=4,
            away_streak=1
        )
        
        # All market types should be present
        self.assertIn('match_result', result)
        self.assertIn('goals', result)
        self.assertIn('correct_score', result)
        
        # Each market should have probabilities and confidence
        for market in ['match_result', 'goals', 'correct_score']:
            self.assertIn('probabilities', result[market])
            self.assertIn('confidence', result[market])
            
    def test_generate_predictions_specific_market(self):
        """Test prediction generation for specific markets"""
        # Test match_result only
        result = self.predictor.generate_predictions(
            base_home_win=0.45,
            base_draw=0.30,
            base_away_win=0.25,
            markets=['match_result']
        )
        
        self.assertIn('match_result', result)
        self.assertNotIn('goals', result)
        self.assertNotIn('correct_score', result)
        
        # Test goals only
        result = self.predictor.generate_predictions(
            base_home_win=0.45,
            base_draw=0.30,
            base_away_win=0.25,
            markets=['goals']
        )
        
        self.assertIn('goals', result)
        self.assertNotIn('match_result', result)
        self.assertNotIn('correct_score', result)
        
    def test_generate_predictions_multiple_markets(self):
        """Test prediction generation for multiple specific markets"""
        result = self.predictor.generate_predictions(
            base_home_win=0.45,
            base_draw=0.30,
            base_away_win=0.25,
            markets=['match_result', 'goals']
        )
        
        self.assertIn('match_result', result)
        self.assertIn('goals', result)
        self.assertNotIn('correct_score', result)


class TestRankPredictions(unittest.TestCase):
    """Test cases for rank_predictions function"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.predictor = IntelligentPredictionModule()
        
    def test_rank_predictions_basic(self):
        """Test basic ranking functionality"""
        predictions = self.predictor.generate_predictions(
            base_home_win=0.45,
            base_draw=0.30,
            base_away_win=0.25
        )
        
        ranked = rank_predictions(predictions, top_n=5)
        
        # Should return top 5 predictions
        self.assertEqual(len(ranked), 5)
        
        # Each prediction should be a tuple with 4 elements
        for pred in ranked:
            self.assertEqual(len(pred), 4)
            market, outcome, prob, conf = pred
            self.assertIsInstance(market, str)
            self.assertIsInstance(outcome, str)
            self.assertIsInstance(prob, float)
            self.assertIsInstance(conf, float)
            
    def test_rank_predictions_ordering(self):
        """Test that predictions are properly ordered by confidence"""
        predictions = self.predictor.generate_predictions(
            base_home_win=0.6,
            base_draw=0.25,
            base_away_win=0.15
        )
        
        ranked = rank_predictions(predictions, top_n=10)
        
        # Confidence should be in descending order
        confidences = [pred[3] for pred in ranked]
        self.assertEqual(confidences, sorted(confidences, reverse=True))
        
    def test_rank_predictions_empty(self):
        """Test ranking with empty prediction set"""
        empty_predictions = {}
        ranked = rank_predictions(empty_predictions)
        self.assertEqual(len(ranked), 0)
        
    def test_rank_predictions_variable_top_n(self):
        """Test ranking with different top_n values"""
        predictions = self.predictor.generate_predictions(
            base_home_win=0.45,
            base_draw=0.30,
            base_away_win=0.25
        )
        
        # Test different top_n values
        for n in [1, 5, 10, 20]:
            ranked = rank_predictions(predictions, top_n=n)
            self.assertLessEqual(len(ranked), n)


class TestFormatPredictionsReport(unittest.TestCase):
    """Test cases for format_predictions_report function"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.predictor = IntelligentPredictionModule()
        
    def test_format_predictions_report_basic(self):
        """Test basic report formatting"""
        predictions = self.predictor.generate_predictions(
            base_home_win=0.45,
            base_draw=0.30,
            base_away_win=0.25
        )
        
        ranked = rank_predictions(predictions, top_n=5)
        report = format_predictions_report(predictions, ranked)
        
        # Report should be a string
        self.assertIsInstance(report, str)
        
        # Report should contain key sections
        self.assertIn('INTELLIGENT PREDICTION MODULE', report)
        self.assertIn('MATCH RESULT PROBABILITIES', report)
        self.assertIn('GOALS MARKET PROBABILITIES', report)
        self.assertIn('TOP CONFIDENT PREDICTIONS', report)
        
    def test_format_predictions_report_content(self):
        """Test that report contains actual prediction data"""
        predictions = self.predictor.generate_predictions(
            base_home_win=0.45,
            base_draw=0.30,
            base_away_win=0.25
        )
        
        ranked = rank_predictions(predictions, top_n=5)
        report = format_predictions_report(predictions, ranked)
        
        # Report should contain outcome labels
        self.assertIn('home_win', report)
        self.assertIn('draw', report)
        self.assertIn('away_win', report)
        
        # Report should contain confidence indicators
        self.assertIn('Confidence:', report)


class TestIntegrationScenarios(unittest.TestCase):
    """Integration tests for real-world scenarios"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.predictor = IntelligentPredictionModule()
        
    def test_high_home_favorite_scenario(self):
        """Test scenario with strong home favorite"""
        predictions = self.predictor.generate_predictions(
            base_home_win=0.65,
            base_draw=0.20,
            base_away_win=0.15,
            fatigue_home=1,
            fatigue_away=6,
            home_streak=0,
            away_streak=0
        )
        
        # Home win should have high probability
        home_prob = predictions['match_result']['probabilities']['home_win']
        self.assertGreater(home_prob, 0.5)
        
    def test_balanced_match_scenario(self):
        """Test scenario with balanced teams"""
        predictions = self.predictor.generate_predictions(
            base_home_win=0.35,
            base_draw=0.35,
            base_away_win=0.30,
            fatigue_home=3,
            fatigue_away=3,
            home_streak=0,
            away_streak=0
        )
        
        # Probabilities should be relatively balanced
        probs = predictions['match_result']['probabilities']
        max_diff = max(probs.values()) - min(probs.values())
        self.assertLess(max_diff, 0.4)
        
    def test_tired_teams_scenario(self):
        """Test scenario with both teams fatigued"""
        predictions = self.predictor.generate_predictions(
            base_home_win=0.45,
            base_draw=0.30,
            base_away_win=0.25,
            fatigue_home=8,
            fatigue_away=8,
            tactical_data={'style': 'defensive'}
        )
        
        # Under goals should be more likely with tired teams
        under_25 = predictions['goals']['probabilities']['over_under']['under_2.5']
        over_25 = predictions['goals']['probabilities']['over_under']['over_2.5']
        self.assertGreater(under_25, over_25)
        
    def test_long_streak_regression_scenario(self):
        """Test scenario with long winning streak"""
        predictions = self.predictor.generate_predictions(
            base_home_win=0.55,
            base_draw=0.25,
            base_away_win=0.20,
            home_streak=8,  # Very long streak
            away_streak=0
        )
        
        # Streak regression should reduce home win probability slightly
        home_prob = predictions['match_result']['probabilities']['home_win']
        self.assertLess(home_prob, 0.60)  # Should be adjusted down from extreme


if __name__ == '__main__':
    unittest.main(verbosity=2)
