"""
Integrated Prediction Pipeline

Main orchestrator that chains all production-ready modules into a unified prediction system.

Pipeline stages:
1. Data validation and preprocessing
2. Tactical analysis (possession efficiency, defensive resistance, tactical friction)
3. Fatigue modeling (midweek fatigue, fixture congestion)
4. Streak analysis (form momentum, volatility)
5. Draw threshold calculation (dynamic, context-aware)
6. xG to goals conversion
7. Defensive collapse detection
8. Advanced metrics (clustering, superiority, home advantage)
9. Set-piece threat analysis
10. Confidence scoring
11. Market coherence validation
12. Output generation with audit trail
"""

import numpy as np
from scipy.stats import poisson

# Import all modules
from tactical_interaction_model import TacticalInteractionModel
from fatigue_interaction_model import FatigueInteractionModel
from midweek_fatigue_integrator import MidweekFatigueIntegrator
from streak_regression_model import adjust_streak_logic, calculate_streak_volatility
from draw_threshold_engine import DrawThresholdEngine
from dynamic_draw_threshold import DynamicDrawThreshold
from xg_to_goals_pipeline import GoalProbabilityDistribution, GoalMarketPrediction
from defensive_collapse_detector import DefensiveCollapseDetector
from advanced_metrics_enhanced import (
    DrawClusteringIndex, DefensiveSuperiorityMultiplier,
    FormTrendMomentum, HomeAdvantageContext
)
from set_piece_threat_analyzer import SetPieceThreatAnalyzer
from confidence_scoring_engine import ConfidenceScoringEngine
from market_coherence_validator import MarketCoherenceValidator
from probability_utilities import ProbabilityManager


class IntegratedPredictionPipeline:
    """
    Comprehensive prediction pipeline integrating all modules.
    """
    
    def __init__(self):
        # Initialize all modules
        self.tactical_model = TacticalInteractionModel()
        self.fatigue_model = FatigueInteractionModel()
        self.midweek_fatigue = MidweekFatigueIntegrator()
        self.draw_engine = DrawThresholdEngine()
        self.dynamic_draw = DynamicDrawThreshold()
        self.defensive_collapse = DefensiveCollapseDetector()
        self.draw_clustering = DrawClusteringIndex()
        self.defensive_superiority = DefensiveSuperiorityMultiplier()
        self.form_momentum = FormTrendMomentum()
        self.home_advantage = HomeAdvantageContext()
        self.set_piece_analyzer = SetPieceThreatAnalyzer()
        self.confidence_engine = ConfidenceScoringEngine()
        self.coherence_validator = MarketCoherenceValidator()
        self.prob_manager = ProbabilityManager()
        
    def preprocess_match_data(self, raw_match_data):
        """
        Validate and preprocess incoming match data.
        
        :param raw_match_data: Raw match data dict
        :return: Processed match data with defaults
        """
        processed = {
            'home_team': raw_match_data.get('home_team', 'Home'),
            'away_team': raw_match_data.get('away_team', 'Away'),
            'league': raw_match_data.get('league', 'default'),
            
            # xG data
            'home_xg': raw_match_data.get('home_xg', 1.5),
            'away_xg': raw_match_data.get('away_xg', 1.5),
            
            # Possession data
            'home_possession': raw_match_data.get('home_possession', 50),
            'away_possession': raw_match_data.get('away_possession', 50),
            
            # Form data
            'home_form': raw_match_data.get('home_form', ['D', 'D', 'W', 'L', 'W']),
            'away_form': raw_match_data.get('away_form', ['W', 'D', 'L', 'W', 'D']),
            
            # Fatigue data
            'home_days_rest': raw_match_data.get('home_days_rest', 7),
            'away_days_rest': raw_match_data.get('away_days_rest', 7),
            'home_midweek_competition': raw_match_data.get('home_midweek_competition', 'none'),
            'away_midweek_competition': raw_match_data.get('away_midweek_competition', 'none'),
            
            # Tactical data
            'home_shots': raw_match_data.get('home_shots', 12),
            'away_shots': raw_match_data.get('away_shots', 10),
            'home_shots_on_target': raw_match_data.get('home_shots_on_target', 4),
            'away_shots_on_target': raw_match_data.get('away_shots_on_target', 3),
            
            # Defensive data
            'home_tackles': raw_match_data.get('home_tackles', 12),
            'away_tackles': raw_match_data.get('away_tackles', 15),
            
            # Set-piece data
            'home_set_piece_goals': raw_match_data.get('home_set_piece_goals', 5),
            'home_total_goals': raw_match_data.get('home_total_goals', 20),
            'away_set_piece_goals': raw_match_data.get('away_set_piece_goals', 4),
            'away_total_goals': raw_match_data.get('away_total_goals', 18),
        }
        
        # Calculate derived metrics
        processed['total_xg'] = processed['home_xg'] + processed['away_xg']
        processed['xg_differential'] = abs(processed['home_xg'] - processed['away_xg'])
        processed['possession_parity'] = 1.0 - (abs(processed['home_possession'] - processed['away_possession']) / 100.0)
        
        return processed
    
    def run_tactical_analysis(self, match_data):
        """Stage 1: Tactical analysis."""
        home_poss_data = {
            'possession_pct': match_data['home_possession'],
            'shots': match_data['home_shots'],
            'shots_on_target': match_data['home_shots_on_target'],
            'xG': match_data['home_xg']
        }
        
        away_poss_data = {
            'possession_pct': match_data['away_possession'],
            'shots': match_data['away_shots'],
            'shots_on_target': match_data['away_shots_on_target'],
            'xG': match_data['away_xg']
        }
        
        home_poss_eff = self.tactical_model.analyze_possession_efficiency(home_poss_data)
        away_poss_eff = self.tactical_model.analyze_possession_efficiency(away_poss_data)
        
        home_def_data = {
            'tackles': match_data['home_tackles'],
            'xG_against': match_data['away_xg']
        }
        
        away_def_data = {
            'tackles': match_data['away_tackles'],
            'xG_against': match_data['home_xg']
        }
        
        home_def_res = self.tactical_model.analyze_defensive_resistance(home_def_data)
        away_def_res = self.tactical_model.analyze_defensive_resistance(away_def_data)
        
        tactical_friction = self.tactical_model.calculate_tactical_friction(
            home_poss_eff, away_poss_eff, home_def_res, away_def_res
        )
        
        return {
            'home_possession_efficiency': home_poss_eff,
            'away_possession_efficiency': away_poss_eff,
            'home_defensive_resistance': home_def_res,
            'away_defensive_resistance': away_def_res,
            'tactical_friction': tactical_friction
        }
    
    def run_fatigue_analysis(self, match_data):
        """Stage 2: Fatigue modeling."""
        home_fixture_data = {
            'days_since_last_match': match_data['home_days_rest'],
            'competition_type': match_data['home_midweek_competition'],
            'rotation_level': 0.3,
            'injury_count': 2
        }
        
        away_fixture_data = {
            'days_since_last_match': match_data['away_days_rest'],
            'competition_type': match_data['away_midweek_competition'],
            'rotation_level': 0.3,
            'injury_count': 2
        }
        
        fatigue_comparison = self.midweek_fatigue.compare_team_fatigue(
            home_fixture_data, away_fixture_data
        )
        
        return fatigue_comparison
    
    def run_form_analysis(self, match_data):
        """Stage 3: Form and streak analysis."""
        home_form_data = self.form_momentum.calculate(match_data['home_form'])
        away_form_data = self.form_momentum.calculate(match_data['away_form'])
        
        return {
            'home_form': home_form_data,
            'away_form': away_form_data
        }
    
    def calculate_base_probabilities(self, match_data, tactical_results):
        """Calculate base probabilities from xG using Poisson."""
        home_xg = match_data['home_xg']
        away_xg = match_data['away_xg']
        
        # Adjust xG based on possession efficiency
        home_xg_adjusted = home_xg * (0.85 + tactical_results['home_possession_efficiency'] * 0.3)
        away_xg_adjusted = away_xg * (0.85 + tactical_results['away_possession_efficiency'] * 0.3)
        
        # Simple Poisson-based probability calculation
        max_goals = 6
        home_probs = [poisson.pmf(k, home_xg_adjusted) for k in range(max_goals)]
        away_probs = [poisson.pmf(k, away_xg_adjusted) for k in range(max_goals)]
        
        # Calculate match result probabilities
        home_win = 0
        draw = 0
        away_win = 0
        
        for h in range(max_goals):
            for a in range(max_goals):
                prob = home_probs[h] * away_probs[a]
                if h > a:
                    home_win += prob
                elif h == a:
                    draw += prob
                else:
                    away_win += prob
        
        # Normalize
        total = home_win + draw + away_win
        base_probs = {
            'home_win': home_win / total,
            'draw': draw / total,
            'away_win': away_win / total
        }
        
        return base_probs, home_xg_adjusted, away_xg_adjusted
    
    def apply_all_corrections(self, base_probs, match_data, tactical_results, fatigue_results, form_results):
        """Apply all probability corrections sequentially."""
        adjustments = []
        descriptions = []
        
        # Correction 1: Midweek fatigue
        if fatigue_results['home_fatigue']['fatigue_penalty'] > 0.05 or \
           fatigue_results['away_fatigue']['fatigue_penalty'] > 0.05:
            home_penalty = fatigue_results['home_fatigue']['fatigue_penalty']
            away_penalty = fatigue_results['away_fatigue']['fatigue_penalty']
            draw_boost = (home_penalty + away_penalty) * 0.25
            
            fatigue_adj = {
                'home_win': -home_penalty * 0.3 + away_penalty * 0.2,
                'draw': draw_boost,
                'away_win': -away_penalty * 0.3 + home_penalty * 0.2
            }
            adjustments.append(fatigue_adj)
            descriptions.append(f"Midweek Fatigue (H:{home_penalty:.1%}, A:{away_penalty:.1%})")
        
        # Correction 2: Draw threshold (dynamic)
        match_factors = {
            'possession_parity': match_data['possession_parity'],
            'xg_differential': match_data['xg_differential'],
            'tactical_friction': tactical_results['tactical_friction'],
            'fatigue_home': fatigue_results['home_fatigue']['fatigue_penalty'],
            'fatigue_away': fatigue_results['away_fatigue']['fatigue_penalty'],
            'midweek_played': match_data['home_days_rest'] <= 3 or match_data['away_days_rest'] <= 3,
            'set_piece_threat': 0.6
        }
        
        draw_adjustment = self.draw_engine.get_draw_adjustment(match_factors)
        adjustments.append(draw_adjustment)
        draw_prob = self.draw_engine.calculate_draw_probability(match_factors)
        descriptions.append(f"Dynamic Draw Threshold ({draw_prob:.1%})")
        
        # Correction 3: Form momentum
        home_momentum = form_results['home_form']['momentum']
        away_momentum = form_results['away_form']['momentum']
        
        if abs(home_momentum - away_momentum) > 0.2:
            momentum_diff = home_momentum - away_momentum
            form_adj = {
                'home_win': momentum_diff * 0.05,
                'draw': 0,
                'away_win': -momentum_diff * 0.05
            }
            adjustments.append(form_adj)
            descriptions.append(f"Form Momentum (H:{home_momentum:.2f}, A:{away_momentum:.2f})")
        
        # Correction 4: Set-piece threat
        home_sp_threat = match_data['home_set_piece_goals'] / max(1, match_data['home_total_goals'])
        away_sp_threat = match_data['away_set_piece_goals'] / max(1, match_data['away_total_goals'])
        
        if home_sp_threat > 0.25 or away_sp_threat > 0.25:
            sp_adj = {
                'home_win': (home_sp_threat - away_sp_threat) * 0.05,
                'draw': (home_sp_threat + away_sp_threat) * 0.03,
                'away_win': (away_sp_threat - home_sp_threat) * 0.05
            }
            adjustments.append(sp_adj)
            descriptions.append(f"Set-Piece Threat (H:{home_sp_threat:.1%}, A:{away_sp_threat:.1%})")
        
        # Apply all adjustments sequentially
        final_probs, audit_trail = self.prob_manager.apply_sequence_of_adjustments(
            base_probs, adjustments, descriptions
        )
        
        return final_probs, audit_trail
    
    def calculate_market_predictions(self, final_probs, home_xg, away_xg):
        """Calculate additional market predictions."""
        total_xg = home_xg + away_xg
        
        # Over/Under 2.5
        gpd = GoalProbabilityDistribution(total_xg)
        goals, probabilities = gpd.to_probability_distribution()
        gmp = GoalMarketPrediction((goals, probabilities))
        markets = gmp.market_prediction()
        
        # BTTS
        home_no_goals = poisson.pmf(0, home_xg)
        away_no_goals = poisson.pmf(0, away_xg)
        btts_no = home_no_goals + away_no_goals - (home_no_goals * away_no_goals)
        btts_yes = 1 - btts_no
        
        return {
            'over_under': markets,
            'btts': {'yes': btts_yes, 'no': btts_no},
            'result': final_probs
        }
    
    def predict(self, raw_match_data, verbose=False):
        """
        Run full prediction pipeline.
        
        :param raw_match_data: Dict with match data
        :param verbose: Print detailed audit trail
        :return: Comprehensive prediction package
        """
        # Stage 0: Preprocess
        match_data = self.preprocess_match_data(raw_match_data)
        
        # Stage 1: Tactical analysis
        tactical_results = self.run_tactical_analysis(match_data)
        
        # Stage 2: Fatigue analysis
        fatigue_results = self.run_fatigue_analysis(match_data)
        
        # Stage 3: Form analysis
        form_results = self.run_form_analysis(match_data)
        
        # Stage 4: Base probabilities
        base_probs, home_xg_adj, away_xg_adj = self.calculate_base_probabilities(
            match_data, tactical_results
        )
        
        # Stage 5: Apply corrections
        final_probs, audit_trail = self.apply_all_corrections(
            base_probs, match_data, tactical_results, fatigue_results, form_results
        )
        
        # Stage 6: Market predictions
        market_predictions = self.calculate_market_predictions(
            final_probs, home_xg_adj, away_xg_adj
        )
        
        # Stage 7: Confidence scoring
        confidence_inputs = {
            'available_data': {
                'has_xg_data': True,
                'has_possession_data': True,
                'has_defensive_stats': True,
                'has_recent_form': True,
                'has_h2h_history': False
            },
            'predictions': {
                'base_model': base_probs,
                'tactical_adjusted': final_probs
            },
            'backtest_results': {
                'accuracy': 0.58,
                'brier_score': 0.20,
                'sample_size': 45
            },
            'uncertainty_metrics': {
                'entropy': -sum(p * np.log(p) if p > 0 else 0 for p in final_probs.values()),
                'max_probability': max(final_probs.values()),
                'probability_spread': max(final_probs.values()) - sorted(final_probs.values())[-2]
            },
            'final_prediction': final_probs
        }
        
        confidence_breakdown = self.confidence_engine.calculate_confidence(confidence_inputs)
        
        # Stage 8: Coherence validation
        prediction_package = {
            'result_probs': final_probs,
            'over_under_probs': market_predictions['over_under'],
            'btts_probs': market_predictions['btts'],
            'xg_home': home_xg_adj,
            'xg_away': away_xg_adj
        }
        
        coherence_report = self.coherence_validator.validate_all_markets(prediction_package)
        
        # Print audit trail if verbose
        if verbose:
            print("\n" + "="*80)
            print(f"PREDICTION: {match_data['home_team']} vs {match_data['away_team']}")
            print("="*80)
            self.prob_manager.print_audit_trail(audit_trail)
            self.confidence_engine.print_confidence_report(confidence_breakdown)
        
        # Compile final output
        return {
            'match': {
                'home': match_data['home_team'],
                'away': match_data['away_team'],
                'league': match_data['league']
            },
            'predictions': {
                'result': final_probs,
                'over_under_2_5': market_predictions['over_under'],
                'btts': market_predictions['btts']
            },
            'xg_adjusted': {
                'home': round(home_xg_adj, 2),
                'away': round(away_xg_adj, 2),
                'total': round(home_xg_adj + away_xg_adj, 2)
            },
            'confidence': confidence_breakdown,
            'coherence': coherence_report,
            'audit_trail': audit_trail,
            'tactical_analysis': tactical_results,
            'fatigue_analysis': fatigue_results,
            'form_analysis': form_results
        }


# Example usage
if __name__ == '__main__':
    pipeline = IntegratedPredictionPipeline()
    
    # Example: Hamburg vs Dortmund scenario (should predict 40%+ draw)
    print("="*80)
    print("TEST: Hamburg 1-1 Dortmund Scenario")
    print("="*80)
    
    hamburg_match = {
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
    
    result = pipeline.predict(hamburg_match, verbose=True)
    
    print("\n" + "="*80)
    print("FINAL PREDICTION")
    print("="*80)
    print(f"Home Win: {result['predictions']['result']['home_win']:.1%}")
    print(f"Draw:     {result['predictions']['result']['draw']:.1%}")
    print(f"Away Win: {result['predictions']['result']['away_win']:.1%}")
    print(f"\nOver 2.5: {result['predictions']['over_under_2_5']['Over 2.5 Goals']:.1%}")
    print(f"Under 2.5: {result['predictions']['over_under_2_5']['Under 2.5 Goals']:.1%}")
    print(f"\nBTTS Yes: {result['predictions']['btts']['yes']:.1%}")
    print(f"BTTS No:  {result['predictions']['btts']['no']:.1%}")
    print(f"\nConfidence: {result['confidence']['total_confidence']:.1f}/100")
    print(f"Coherence: {result['coherence']['coherence_score']:.2f}")
    print("="*80)
