"""
Comprehensive Test Suite for Integrated Prediction Pipeline

Tests against known match outcomes to validate:
1. Draw prediction accuracy (Hamburg, Bayern, Heidenheim)
2. High-scoring match detection (St. Pauli)
3. Confidence scoring formula transparency
4. Market coherence validation
"""

import unittest
from integrated_prediction_pipeline import IntegratedPredictionPipeline
from confidence_scoring_engine import ConfidenceScoringEngine
from market_coherence_validator import MarketCoherenceValidator


class TestDrawPredictionAccuracy(unittest.TestCase):
    """Test draw prediction improvements."""
    
    def setUp(self):
        self.pipeline = IntegratedPredictionPipeline()
    
    def test_hamburg_dortmund_draw(self):
        """
        Hamburg 1-1 Dortmund
        Expected: Draw probability ≥ 40% (was 19%)
        """
        match_data = {
            'home_team': 'Hamburg',
            'away_team': 'Dortmund',
            'league': 'bundesliga',
            'home_xg': 1.3,
            'away_xg': 1.5,
            'home_possession': 48,
            'away_possession': 52,
            'home_form': ['D', 'D', 'W', 'D', 'L'],
            'away_form': ['W', 'W', 'D', 'L', 'W'],
            'home_days_rest': 3,
            'away_days_rest': 3,
            'home_midweek_competition': 'league',
            'away_midweek_competition': 'champions_league',
            'home_shots': 11,
            'away_shots': 13,
            'home_shots_on_target': 4,
            'away_shots_on_target': 5,
            'home_tackles': 15,
            'away_tackles': 12,
            'home_set_piece_goals': 6,
            'home_total_goals': 18,
            'away_set_piece_goals': 5,
            'away_total_goals': 22
        }
        
        result = self.pipeline.predict(match_data, verbose=False)
        draw_prob = result['predictions']['result']['draw']
        
        print(f"\n  Hamburg vs Dortmund: Draw probability = {draw_prob:.1%}")
        self.assertGreaterEqual(draw_prob, 0.40, 
            f"Draw probability {draw_prob:.1%} should be ≥ 40%")
    
    def test_bayern_union_draw(self):
        """
        Bayern 2-2 Union Berlin
        Expected: Draw probability ≥ 45% (was 24%)
        """
        match_data = {
            'home_team': 'Bayern Munich',
            'away_team': 'Union Berlin',
            'league': 'bundesliga',
            'home_xg': 2.0,
            'away_xg': 1.8,
            'home_possession': 65,
            'away_possession': 35,
            'home_form': ['W', 'D', 'W', 'D', 'W'],
            'away_form': ['D', 'D', 'D', 'W', 'L'],
            'home_days_rest': 3,
            'away_days_rest': 4,
            'home_midweek_competition': 'champions_league',
            'away_midweek_competition': 'league',
            'home_shots': 18,
            'away_shots': 10,
            'home_shots_on_target': 7,
            'away_shots_on_target': 4,
            'home_tackles': 10,
            'away_tackles': 18,
            'home_set_piece_goals': 7,
            'home_total_goals': 28,
            'away_set_piece_goals': 6,
            'away_total_goals': 16
        }
        
        result = self.pipeline.predict(match_data, verbose=False)
        draw_prob = result['predictions']['result']['draw']
        
        print(f"  Bayern vs Union: Draw probability = {draw_prob:.1%}")
        self.assertGreaterEqual(draw_prob, 0.45,
            f"Draw probability {draw_prob:.1%} should be ≥ 45%")
    
    def test_heidenheim_frankfurt_draw(self):
        """
        Heidenheim 1-1 Frankfurt
        Expected: Draw probability ≥ 45% (was 22%)
        """
        match_data = {
            'home_team': 'Heidenheim',
            'away_team': 'Frankfurt',
            'league': 'bundesliga',
            'home_xg': 1.4,
            'away_xg': 1.6,
            'home_possession': 45,
            'away_possession': 55,
            'home_form': ['D', 'L', 'D', 'W', 'D'],
            'away_form': ['W', 'D', 'D', 'L', 'W'],
            'home_days_rest': 4,
            'away_days_rest': 3,
            'home_midweek_competition': 'league',
            'away_midweek_competition': 'europa_league',
            'home_shots': 10,
            'away_shots': 14,
            'home_shots_on_target': 3,
            'away_shots_on_target': 5,
            'home_tackles': 16,
            'away_tackles': 13,
            'home_set_piece_goals': 4,
            'home_total_goals': 15,
            'away_set_piece_goals': 5,
            'away_total_goals': 20
        }
        
        result = self.pipeline.predict(match_data, verbose=False)
        draw_prob = result['predictions']['result']['draw']
        
        print(f"  Heidenheim vs Frankfurt: Draw probability = {draw_prob:.1%}")
        self.assertGreaterEqual(draw_prob, 0.45,
            f"Draw probability {draw_prob:.1%} should be ≥ 45%")


class TestHighScoringMatches(unittest.TestCase):
    """Test detection of high-scoring matches."""
    
    def setUp(self):
        self.pipeline = IntegratedPredictionPipeline()
    
    def test_st_pauli_gladbach_over(self):
        """
        St. Pauli 0-4 Gladbach
        Expected: Over 2.5 with combined xG ~3.2
        """
        match_data = {
            'home_team': 'St. Pauli',
            'away_team': 'Borussia Monchengladbach',
            'league': 'bundesliga',
            'home_xg': 0.9,
            'away_xg': 2.3,
            'home_possession': 42,
            'away_possession': 58,
            'home_form': ['L', 'L', 'D', 'L', 'L'],
            'away_form': ['W', 'W', 'W', 'D', 'W'],
            'home_days_rest': 4,
            'away_days_rest': 4,
            'home_midweek_competition': 'none',
            'away_midweek_competition': 'none',
            'home_shots': 8,
            'away_shots': 16,
            'home_shots_on_target': 2,
            'away_shots_on_target': 8,
            'home_tackles': 18,
            'away_tackles': 10,
            'home_set_piece_goals': 3,
            'home_total_goals': 12,
            'away_set_piece_goals': 6,
            'away_total_goals': 26
        }
        
        result = self.pipeline.predict(match_data, verbose=False)
        total_xg = result['xg_adjusted']['total']
        over_prob = result['predictions']['over_under_2_5']['Over 2.5 Goals']
        
        print(f"\n  St. Pauli vs Gladbach:")
        print(f"    Total xG: {total_xg}")
        print(f"    Over 2.5 probability: {over_prob:.1%}")
        
        self.assertGreaterEqual(total_xg, 3.0,
            f"Total xG {total_xg} should be ≥ 3.0")
        self.assertGreaterEqual(over_prob, 0.50,
            f"Over 2.5 probability {over_prob:.1%} should be ≥ 50%")


class TestConfidenceScoring(unittest.TestCase):
    """Test confidence scoring formula transparency."""
    
    def setUp(self):
        self.engine = ConfidenceScoringEngine()
    
    def test_formula_based_confidence(self):
        """Verify confidence is formula-based, not empirical."""
        # High quality inputs
        high_quality_inputs = {
            'available_data': {
                'has_xg_data': True,
                'has_possession_data': True,
                'has_defensive_stats': True,
                'has_recent_form': True,
                'has_h2h_history': True
            },
            'predictions': {
                'model_a': {'home_win': 0.50, 'draw': 0.30, 'away_win': 0.20},
                'model_b': {'home_win': 0.52, 'draw': 0.28, 'away_win': 0.20},
                'model_c': {'home_win': 0.48, 'draw': 0.32, 'away_win': 0.20}
            },
            'backtest_results': {
                'accuracy': 0.65,
                'brier_score': 0.17,
                'sample_size': 50
            },
            'uncertainty_metrics': {
                'entropy': 0.90,
                'max_probability': 0.50,
                'probability_spread': 0.22
            },
            'final_prediction': {'home_win': 0.50, 'draw': 0.30, 'away_win': 0.20},
            'market_odds': {'home_win': 0.48, 'draw': 0.32, 'away_win': 0.20}
        }
        
        result_high = self.engine.calculate_confidence(high_quality_inputs)
        
        print(f"\n  High Quality Input:")
        print(f"    Confidence: {result_high['total_confidence']:.1f}/100")
        print(f"    Components: {result_high['components']}")
        
        # Verify score is formula-based
        self.assertIsInstance(result_high['total_confidence'], (int, float))
        self.assertGreaterEqual(result_high['total_confidence'], 60)
        self.assertEqual(len(result_high['components']), 5)
        
        # Low quality inputs
        low_quality_inputs = {
            'available_data': {
                'has_xg_data': False,
                'has_possession_data': True,
                'has_defensive_stats': False,
                'has_recent_form': True,
                'has_h2h_history': False
            },
            'predictions': {
                'model_a': {'home_win': 0.35, 'draw': 0.35, 'away_win': 0.30}
            },
            'backtest_results': {
                'accuracy': 0.42,
                'brier_score': 0.30,
                'sample_size': 10
            },
            'uncertainty_metrics': {
                'entropy': 1.09,
                'max_probability': 0.35,
                'probability_spread': 0.05
            },
            'final_prediction': {'home_win': 0.35, 'draw': 0.35, 'away_win': 0.30}
        }
        
        result_low = self.engine.calculate_confidence(low_quality_inputs)
        
        print(f"\n  Low Quality Input:")
        print(f"    Confidence: {result_low['total_confidence']:.1f}/100")
        print(f"    Components: {result_low['components']}")
        
        # Low quality should score lower
        self.assertLess(result_low['total_confidence'], result_high['total_confidence'])
        self.assertLess(result_low['total_confidence'], 50)
    
    def test_confidence_components_sum(self):
        """Verify confidence components sum correctly."""
        inputs = {
            'available_data': {'has_xg_data': True, 'has_possession_data': True,
                             'has_defensive_stats': True, 'has_recent_form': True,
                             'has_h2h_history': True},
            'predictions': {
                'model_a': {'home_win': 0.45, 'draw': 0.30, 'away_win': 0.25}
            },
            'backtest_results': {'accuracy': 0.55, 'brier_score': 0.22, 'sample_size': 30},
            'uncertainty_metrics': {'entropy': 1.0, 'max_probability': 0.45,
                                  'probability_spread': 0.15},
            'final_prediction': {'home_win': 0.45, 'draw': 0.30, 'away_win': 0.25}
        }
        
        result = self.engine.calculate_confidence(inputs)
        components_sum = sum(result['components'].values())
        
        # Components should sum to total (within rounding tolerance)
        self.assertAlmostEqual(components_sum, result['total_confidence'], delta=0.2)


class TestMarketCoherence(unittest.TestCase):
    """Test market coherence validation."""
    
    def setUp(self):
        self.validator = MarketCoherenceValidator()
    
    def test_coherent_predictions(self):
        """Test that coherent predictions are validated correctly."""
        coherent_package = {
            'result_probs': {'home_win': 0.50, 'draw': 0.30, 'away_win': 0.20},
            'over_under_probs': {'over_2.5': 0.55, 'under_2.5': 0.45},
            'btts_probs': {'yes': 0.60, 'no': 0.40},
            'xg_home': 1.8,
            'xg_away': 1.2
        }
        
        report = self.validator.validate_all_markets(coherent_package)
        
        print(f"\n  Coherent Package:")
        print(f"    Overall Coherent: {report['overall_coherent']}")
        print(f"    Coherence Score: {report['coherence_score']:.2f}")
        print(f"    Issues: {report['total_issues']}")
        
        self.assertTrue(report['overall_coherent'] or report['high_severity_issues'] == 0)
        self.assertGreaterEqual(report['coherence_score'], 0.60)
    
    def test_incoherent_predictions(self):
        """Test that incoherent predictions are flagged."""
        incoherent_package = {
            'result_probs': {'home_win': 0.35, 'draw': 0.45, 'away_win': 0.20},
            'over_under_probs': {'over_2.5': 0.70, 'under_2.5': 0.30},
            'btts_probs': {'yes': 0.25, 'no': 0.75},
            'xg_home': 1.6,
            'xg_away': 1.4
        }
        
        report = self.validator.validate_all_markets(incoherent_package)
        
        print(f"\n  Incoherent Package:")
        print(f"    Overall Coherent: {report['overall_coherent']}")
        print(f"    Coherence Score: {report['coherence_score']:.2f}")
        print(f"    Issues: {report['total_issues']}")
        
        # Should detect inconsistencies
        self.assertGreater(report['total_issues'], 0)


class TestFatigueCorrections(unittest.TestCase):
    """Test that fatigue corrections are properly applied."""
    
    def setUp(self):
        self.pipeline = IntegratedPredictionPipeline()
    
    def test_midweek_fatigue_impact(self):
        """Test that midweek fatigue significantly impacts predictions."""
        # Match with no midweek fatigue
        rested_match = {
            'home_team': 'Team A',
            'away_team': 'Team B',
            'home_xg': 1.5,
            'away_xg': 1.5,
            'home_possession': 50,
            'away_possession': 50,
            'home_days_rest': 7,
            'away_days_rest': 7,
            'home_midweek_competition': 'none',
            'away_midweek_competition': 'none'
        }
        
        # Same match but with severe midweek fatigue
        fatigued_match = rested_match.copy()
        fatigued_match.update({
            'home_days_rest': 3,
            'away_days_rest': 3,
            'home_midweek_competition': 'champions_league',
            'away_midweek_competition': 'champions_league'
        })
        
        result_rested = self.pipeline.predict(rested_match, verbose=False)
        result_fatigued = self.pipeline.predict(fatigued_match, verbose=False)
        
        draw_prob_rested = result_rested['predictions']['result']['draw']
        draw_prob_fatigued = result_fatigued['predictions']['result']['draw']
        
        print(f"\n  Rested teams: Draw = {draw_prob_rested:.1%}")
        print(f"  Fatigued teams: Draw = {draw_prob_fatigued:.1%}")
        
        # Fatigue should increase draw probability
        self.assertGreater(draw_prob_fatigued, draw_prob_rested,
            "Midweek fatigue should increase draw probability")


def run_all_tests():
    """Run all test suites with formatted output."""
    print("\n" + "="*80)
    print("COMPREHENSIVE VALIDATION TEST SUITE")
    print("="*80)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestDrawPredictionAccuracy))
    suite.addTests(loader.loadTestsFromTestCase(TestHighScoringMatches))
    suite.addTests(loader.loadTestsFromTestCase(TestConfidenceScoring))
    suite.addTests(loader.loadTestsFromTestCase(TestMarketCoherence))
    suite.addTests(loader.loadTestsFromTestCase(TestFatigueCorrections))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✓ ALL TESTS PASSED")
    else:
        print("\n✗ SOME TESTS FAILED")
    
    print("="*80)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_all_tests()
    exit(0 if success else 1)
