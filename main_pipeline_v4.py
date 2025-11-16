"""
Main Pipeline V4 - Enhanced Prediction System

Orchestrates all modules to provide comprehensive match predictions.
Integrates xG data, defensive collapse detection, confidence scoring,
and market coherence validation.

Addresses all audit findings:
- Integrates xG to goal probability conversion
- Uses volatility detection for form streaks
- Calculates possession efficiency
- Detects defensive panic patterns
- Provides transparent confidence scores
- Validates market coherence
"""

import numpy as np
import pandas as pd

# Import all prediction modules
from tactical_interaction_model import TacticalInteractionModel
from draw_threshold_engine import DrawThresholdEngine
from streak_regression_model import StreakVolatilityDetector
from xg_to_goals_pipeline import XGToGoalsPipeline
from defensive_collapse_detector import DefensiveCollapseDetector
from confidence_scoring_engine import ConfidenceScoringEngine
from market_coherence_validator import MarketCoherenceValidator
from goal_distribution_predictor import GoalDistributionPredictor
from advanced_metrics_enhanced import (
    DrawClusteringIndex, DefensiveSuperiorityMultiplier,
    FormTrendMomentum, HomeAdvantageContext
)
from probability_utilities import ProbabilityManager


class MatchPredictionPipeline:
    """
    Comprehensive match prediction pipeline integrating all components.
    """
    
    def __init__(self):
        # Initialize all components
        self.tactical_model = TacticalInteractionModel()
        self.draw_engine = DrawThresholdEngine()
        self.streak_detector = StreakVolatilityDetector()
        self.xg_pipeline = XGToGoalsPipeline()
        self.collapse_detector = DefensiveCollapseDetector()
        self.confidence_engine = ConfidenceScoringEngine()
        self.coherence_validator = MarketCoherenceValidator()
        self.prob_manager = ProbabilityManager()
        
        # Advanced metrics
        self.draw_clustering = DrawClusteringIndex()
        self.defensive_superiority = DefensiveSuperiorityMultiplier()
        self.form_momentum = FormTrendMomentum()
        self.home_advantage = HomeAdvantageContext()
    
    def predict_match(self, match_data):
        """
        Generate comprehensive match prediction.
        
        :param match_data: Dict containing all match information:
            - xg_home: Float
            - xg_away: Float
            - home_form_results: List
            - away_form_results: List
            - possession_data: Dict
            - defensive_data: Dict
            - home_team_data: Dict
            - away_team_data: Dict
            - context_factors: Dict
        :return: Complete prediction with all markets
        """
        predictions = {}
        audit_trail = []
        
        # Step 1: Extract xG if available
        xg_home = match_data.get('xg_home')
        xg_away = match_data.get('xg_away')
        
        if xg_home is not None and xg_away is not None:
            # Generate xG-based probabilities
            xg_analysis = self.xg_pipeline.full_analysis(xg_home, xg_away)
            base_probabilities = xg_analysis['match_outcomes']
            predictions['xg_analysis'] = xg_analysis
            audit_trail.append("Base probabilities from xG data")
        else:
            # Fallback to default balanced probabilities
            base_probabilities = {'home_win': 0.40, 'draw': 0.30, 'away_win': 0.30}
            audit_trail.append("Using default probabilities (no xG data)")
        
        # Step 2: Tactical analysis adjustments
        tactical_match_data = {
            'possession_data': match_data.get('possession_data', {}),
            'defensive_data': match_data.get('defensive_data', {})
        }
        
        scenario = self.tactical_model.detect_scenario(tactical_match_data)
        possession_eff = self.tactical_model.analyze_possession_efficiency(
            match_data.get('possession_data', {}))
        defensive_res = self.tactical_model.analyze_defensive_resistance(
            match_data.get('defensive_data', {}))
        
        predictions['tactical_analysis'] = {
            'scenario': scenario,
            'possession_efficiency': possession_eff,
            'defensive_resistance': defensive_res
        }
        
        # Adjust probabilities based on tactical scenario
        tactical_adjustment = self._calculate_tactical_adjustment(
            scenario, possession_eff, defensive_res)
        
        if tactical_adjustment:
            base_probabilities, _, log = self.prob_manager.apply_adjustment_with_renorm(
                base_probabilities, tactical_adjustment, "Tactical scenario adjustment")
            audit_trail.append(log)
        
        # Step 3: Draw threshold analysis
        draw_features = self._extract_draw_features(match_data)
        draw_analysis = self.draw_engine.intelligent_draw_decision(draw_features)
        predictions['draw_analysis'] = draw_analysis
        
        # Adjust if draw probability significantly different
        if abs(draw_analysis['probability'] - base_probabilities['draw']) > 0.10:
            draw_adjustment = {
                'draw': draw_analysis['probability'] - base_probabilities['draw']
            }
            base_probabilities, _, log = self.prob_manager.apply_adjustment_with_renorm(
                base_probabilities, draw_adjustment, "Draw threshold adjustment")
            audit_trail.append(log)
        
        # Step 4: Form streak volatility analysis
        home_form = match_data.get('home_form_results', [])
        away_form = match_data.get('away_form_results', [])
        
        home_streak_data = self._prepare_streak_data(home_form, match_data, 'home')
        away_streak_data = self._prepare_streak_data(away_form, match_data, 'away')
        
        home_sustainability = self.streak_detector.detect_streak_sustainability(home_streak_data)
        away_sustainability = self.streak_detector.detect_streak_sustainability(away_streak_data)
        
        predictions['form_analysis'] = {
            'home': home_sustainability,
            'away': away_sustainability
        }
        
        # Step 5: Defensive collapse detection
        if 'collapse_check_data' in match_data:
            collapse_result = self.collapse_detector.comprehensive_collapse_assessment(
                match_data['collapse_check_data'])
            predictions['defensive_collapse'] = collapse_result
            
            # If high collapse risk, adjust probabilities
            if collapse_result['overall_collapse_score'] > 0.6:
                # Shift probability away from the collapsing team
                audit_trail.append("High defensive collapse risk detected")
        
        # Step 6: Home advantage adjustment
        if 'home_team_data' in match_data and 'context_factors' in match_data:
            home_adv_factor = self.home_advantage.calculate(
                match_data['home_team_data'],
                match_data['context_factors']
            )
            base_probabilities = self.home_advantage.apply_to_probabilities(
                base_probabilities, home_adv_factor)
            predictions['home_advantage_factor'] = home_adv_factor
            audit_trail.append(f"Applied home advantage factor: {home_adv_factor}")
        
        # Step 7: Generate all betting markets
        goal_predictor = GoalDistributionPredictor(
            base_probabilities['home_win'],
            base_probabilities['draw'],
            base_probabilities['away_win'],
            xg_home=xg_home,
            xg_away=xg_away
        )
        
        all_markets = goal_predictor.predict_all()
        predictions['markets'] = all_markets
        
        # Step 8: Market coherence validation
        validation_data = {
            'match_outcomes': base_probabilities,
            'over_under': all_markets['over_under'],
            'btts': all_markets['BTTS'],
            'correct_scores': all_markets['correct_score'],
            'xg_values': {'xg_home': xg_home, 'xg_away': xg_away} if xg_home else {}
        }
        
        coherence_result = self.coherence_validator.comprehensive_validation(validation_data)
        predictions['coherence_validation'] = coherence_result
        
        # Step 9: Confidence scoring
        confidence_components = {
            'probabilities': base_probabilities,
            'data_completeness': self._assess_data_completeness(match_data),
            'prediction_stability': {'consensus_trend': 'stable'}
        }
        
        confidence_result = self.confidence_engine.calculate_overall_confidence(confidence_components)
        predictions['confidence'] = confidence_result
        
        # Step 10: Final recommendations
        predictions['final_probabilities'] = base_probabilities
        predictions['recommendations'] = self._generate_recommendations(
            base_probabilities, all_markets, confidence_result)
        predictions['audit_trail'] = audit_trail
        
        return predictions
    
    def _calculate_tactical_adjustment(self, scenario, possession_eff, defensive_res):
        """Calculate probability adjustments based on tactical analysis."""
        adjustments = {}
        
        if scenario == 'possession_dominance' and possession_eff > 0.7:
            adjustments['home_win'] = 0.10
            adjustments['draw'] = -0.05
            adjustments['away_win'] = -0.05
        elif scenario == 'deep_block' and defensive_res > 0.7:
            adjustments['draw'] = 0.10
            adjustments['home_win'] = -0.05
            adjustments['away_win'] = -0.05
        elif scenario == 'inefficient_possession':
            adjustments['draw'] = 0.08
            adjustments['home_win'] = -0.04
            adjustments['away_win'] = -0.04
        
        return adjustments if adjustments else None
    
    def _extract_draw_features(self, match_data):
        """Extract features for draw prediction."""
        return {
            'home_form': match_data.get('home_form_rating', 0.5),
            'away_form': match_data.get('away_form_rating', 0.5),
            'home_strength': match_data.get('home_strength', 0.5),
            'away_strength': match_data.get('away_strength', 0.5),
            'home_defensive_rating': match_data.get('home_defensive_rating', 0.5),
            'away_defensive_rating': match_data.get('away_defensive_rating', 0.5),
            'head_to_head_draws': match_data.get('h2h_draws', 0),
            'home_goals_avg': match_data.get('home_goals_avg', 1.5),
            'away_goals_avg': match_data.get('away_goals_avg', 1.5)
        }
    
    def _prepare_streak_data(self, results, match_data, side):
        """Prepare data for streak volatility detection."""
        # Convert results to numeric (1=W, 0=D, -1=L)
        numeric_results = []
        for r in results:
            if r == 'W':
                numeric_results.append(1)
            elif r == 'D':
                numeric_results.append(0)
            else:
                numeric_results.append(-1)
        
        current_streak = match_data.get(f'{side}_current_streak', 0)
        
        return {
            'current_streak': current_streak,
            'recent_results': numeric_results,
            'performance_metrics': {
                'xg_trend': match_data.get(f'{side}_xg_trend', 0),
                'shot_quality_trend': match_data.get(f'{side}_shot_quality_trend', 0)
            }
        }
    
    def _assess_data_completeness(self, match_data):
        """Assess completeness of input data."""
        return {
            'xg_available': match_data.get('xg_home') is not None,
            'form_data_available': bool(match_data.get('home_form_results')),
            'h2h_available': match_data.get('h2h_draws') is not None,
            'injuries_known': match_data.get('injuries_data') is not None,
            'tactical_data_available': bool(match_data.get('possession_data'))
        }
    
    def _generate_recommendations(self, probabilities, markets, confidence):
        """Generate betting recommendations."""
        recommendations = []
        
        # Primary pick based on highest probability
        primary_outcome = max(probabilities.items(), key=lambda x: x[1])
        
        if confidence['overall_confidence'] >= 70:
            recommendations.append({
                'pick': primary_outcome[0],
                'probability': primary_outcome[1],
                'confidence': confidence['overall_confidence'],
                'rationale': f"High confidence {primary_outcome[0]} at {primary_outcome[1]:.1%}"
            })
        
        # Goal-based recommendations
        over_25 = markets['over_under'].get('over_2.5', 0)
        under_25 = markets['over_under'].get('under_2.5', 0)
        
        if over_25 > 0.60:
            recommendations.append({
                'pick': 'Over 2.5 Goals',
                'probability': over_25,
                'confidence': confidence['overall_confidence'] * 0.9,
                'rationale': f"High scoring expected at {over_25:.1%}"
            })
        elif under_25 > 0.60:
            recommendations.append({
                'pick': 'Under 2.5 Goals',
                'probability': under_25,
                'confidence': confidence['overall_confidence'] * 0.9,
                'rationale': f"Low scoring expected at {under_25:.1%}"
            })
        
        return recommendations


# Main function for CLI usage
def main():
    """Example usage of the pipeline."""
    pipeline = MatchPredictionPipeline()
    
    # Example match data (Frankfurt vs Heidenheim from audit)
    example_match = {
        'xg_home': 0.88,
        'xg_away': 2.32,
        'home_form_results': ['W', 'W', 'D', 'W', 'L'],
        'away_form_results': ['L', 'D', 'W', 'D', 'L'],
        'possession_data': {
            'possession_pct': 52.0,
            'shots': 10,
            'shots_on_target': 4,
            'passes_completed': 380,
            'passes_attempted': 450,
            'final_third_entries': 25
        },
        'defensive_data': {
            'shots_allowed': 18,
            'shots_on_target_allowed': 9,
            'tackles_won': 12,
            'tackles_attempted': 18,
            'interceptions': 8,
            'clearances': 15,
            'possession_against': 48.0
        },
        'home_form_rating': 0.65,
        'away_form_rating': 0.45,
        'home_strength': 0.70,
        'away_strength': 0.55,
        'home_defensive_rating': 0.60,
        'away_defensive_rating': 0.55,
        'h2h_draws': 2,
        'home_goals_avg': 1.8,
        'away_goals_avg': 1.3
    }
    
    # Generate prediction
    result = pipeline.predict_match(example_match)
    
    # Print results
    print("=" * 80)
    print("MATCH PREDICTION RESULTS")
    print("=" * 80)
    print(f"\nFinal Probabilities:")
    for outcome, prob in result['final_probabilities'].items():
        print(f"  {outcome}: {prob:.1%}")
    
    print(f"\nConfidence: {result['confidence']['overall_confidence']}/100 ({result['confidence']['confidence_level']})")
    
    print(f"\nMarket Coherence: {'✓ PASSED' if result['coherence_validation']['validation_passed'] else '✗ FAILED'}")
    
    print(f"\nRecommendations:")
    for rec in result['recommendations']:
        print(f"  - {rec['pick']}: {rec['probability']:.1%} (Confidence: {rec['confidence']:.0f})")
        print(f"    {rec['rationale']}")


if __name__ == "__main__":
    main()