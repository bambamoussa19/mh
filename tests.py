"""Tests for the soccer prediction system modules."""
import math
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))


# ---------------------------------------------------------------------------
# postmatch_analysis
# ---------------------------------------------------------------------------
def test_postmatch_prediction_correct():
    from postmatch_analysis import PostMatchAnalysis
    a = PostMatchAnalysis('Poland', 'Netherlands', 'Away Win', 'Away Win')
    assert a.prediction_correct() is True


def test_postmatch_prediction_incorrect():
    from postmatch_analysis import PostMatchAnalysis
    a = PostMatchAnalysis('Poland', 'Netherlands', 'Draw', 'Away Win')
    assert a.prediction_correct() is False


def test_postmatch_generate_report():
    from postmatch_analysis import PostMatchAnalysis
    a = PostMatchAnalysis('A', 'B', 'Home Win', 'Draw', match_date='2025-01-01')
    a.add_performance_metrics(possession_rate=55.0, shots_on_target=6)
    a.add_influencing_factor('Player Form')
    report = a.generate_report()
    assert report['match'] == 'A vs B'
    assert report['prediction_correct'] is False
    assert report['performance_metrics']['possession_rate'] == 55.0
    assert 'Player Form' in report['influencing_factors']


# ---------------------------------------------------------------------------
# uncertainty_calibration
# ---------------------------------------------------------------------------
def test_predictive_uncertainty_uniform():
    from uncertainty_calibration import predictive_uncertainty
    probs = {'home_win': 1/3, 'draw': 1/3, 'away_win': 1/3}
    entropy = predictive_uncertainty(probs)
    assert abs(entropy - math.log2(3)) < 1e-6


def test_predictive_uncertainty_certain():
    from uncertainty_calibration import predictive_uncertainty
    probs = {'home_win': 1.0, 'draw': 0.0, 'away_win': 0.0}
    entropy = predictive_uncertainty(probs)
    assert entropy == 0.0


def test_upset_detection_true():
    from uncertainty_calibration import upset_detection
    probs = {'home_win': 0.70, 'draw': 0.20, 'away_win': 0.10}
    assert upset_detection(probs, 'away_win') is True


def test_upset_detection_false():
    from uncertainty_calibration import upset_detection
    probs = {'home_win': 0.70, 'draw': 0.20, 'away_win': 0.10}
    assert upset_detection(probs, 'home_win') is False


def test_calibration_error_perfect():
    from uncertainty_calibration import calibration_error
    # Perfect calibration: all predicted ~1.0 and all actually correct
    preds = [0.95] * 10
    actuals = [1] * 10
    ece = calibration_error(preds, actuals)
    assert ece < 0.1


# ---------------------------------------------------------------------------
# advanced_metrics
# ---------------------------------------------------------------------------
def test_draw_clustering_index_no_draws():
    from advanced_metrics import DrawClusteringIndex
    dci = DrawClusteringIndex()
    assert dci.calculate([False, False, False]) == 0.0


def test_draw_clustering_index_all_draws():
    from advanced_metrics import DrawClusteringIndex
    dci = DrawClusteringIndex()
    assert dci.calculate([True, True, True]) == 1.0


def test_defensive_superiority_multiplier():
    from advanced_metrics import DefensiveSuperiorityMultiplier
    dsm = DefensiveSuperiorityMultiplier()
    data = {'goals_conceded_home': 0.5, 'goals_conceded_away': 0.5, 'league_avg_goals_per_match': 2.5}
    result = dsm.calculate(data)
    assert result == 2.5  # league_avg / (2 * avg_conceded) = 2.5 / (2*0.5) = 2.5


def test_home_advantage_context():
    from advanced_metrics import HomeAdvantageContext
    hac = HomeAdvantageContext()
    data = {'home_wins': 15, 'total_home_matches': 20}
    assert hac.calculate(data) == 0.75


def test_home_advantage_context_zero_matches():
    from advanced_metrics import HomeAdvantageContext
    hac = HomeAdvantageContext()
    assert hac.calculate({'home_wins': 0, 'total_home_matches': 0}) == 0.0


def test_pressure_direction_effect():
    from advanced_metrics import PressureDirectionEffect
    pde = PressureDirectionEffect()
    data = {'pressing_intensity': 0.8, 'opposition_errors_forced': 5}
    result = pde.calculate(data)
    assert abs(result - (0.8 * 0.6 + 0.5 * 0.4)) < 1e-9


def test_form_trend_momentum_improving():
    from advanced_metrics import FormTrendMomentum
    ftm = FormTrendMomentum()
    assert ftm.calculate([1, 2, 3, 4]) == 1.0


def test_form_trend_momentum_declining():
    from advanced_metrics import FormTrendMomentum
    ftm = FormTrendMomentum()
    assert ftm.calculate([4, 3, 2, 1]) == -1.0


def test_form_trend_momentum_single():
    from advanced_metrics import FormTrendMomentum
    ftm = FormTrendMomentum()
    assert ftm.calculate([5]) == 0.0


# ---------------------------------------------------------------------------
# main_pipeline_v4 – smoke test (no CSV required)
# ---------------------------------------------------------------------------
def test_main_pipeline_functions_return_data():
    import main_pipeline_v4 as mp
    import pandas as pd
    sample = pd.DataFrame({'col': [1, 2, 3]})
    assert mp.tactical_analysis(sample) is sample
    assert mp.fatigue_modeling(sample) is sample
    assert mp.streak_regression(sample) is sample
    assert mp.draw_threshold_intelligence(sample) is sample


if __name__ == '__main__':
    tests = [v for k, v in list(globals().items()) if k.startswith('test_')]
    passed = failed = 0
    for t in tests:
        try:
            t()
            print(f'  PASS  {t.__name__}')
            passed += 1
        except Exception as exc:
            print(f'  FAIL  {t.__name__}: {exc}')
            failed += 1
    print(f'\n{passed} passed, {failed} failed')
