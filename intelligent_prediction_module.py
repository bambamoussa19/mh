"""
Intelligent Prediction Module

This module evaluates all available markets and generates the best predictions 
across multiple markets based on key probabilities and confidence ratings.

Key Features:
- Integrates insights from fatigue, tactical, draw threshold, and streak regression models
- Evaluates Match Result, Goals (BTTS, Over/Under), and Correct Score markets
- Ranks predictions by confidence levels
- Supports modular market queries
- Optimized for real-time predictions
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from fatigue_interaction_model import FatigueInteractionModel
from tactical_interaction_model import TacticalInteractionModel
from draw_threshold_engine import DrawThresholdEngine
from streak_regression_model import clean_sheet_streak_probability, adjust_streak_logic
from goal_distribution_predictor import GoalDistributionPredictor
from probability_utilities import ProbabilityManager


class IntelligentPredictionModule:
    """
    Main class for intelligent multi-market prediction analysis.
    """
    
    def __init__(self):
        """Initialize the prediction module with all sub-modules."""
        self.fatigue_model = FatigueInteractionModel()
        self.tactical_model = TacticalInteractionModel()
        self.probability_manager = ProbabilityManager()
        
    def integrate_fatigue_insights(self, home_fatigue_level: int, away_fatigue_level: int) -> Dict[str, float]:
        """
        Integrate fatigue impact into predictions.
        
        Args:
            home_fatigue_level: Fatigue level for home team (0-10)
            away_fatigue_level: Fatigue level for away team (0-10)
            
        Returns:
            Dictionary with performance adjustments
        """
        self.fatigue_model.set_fatigue_level(home_fatigue_level)
        home_performance = self.fatigue_model.calculate_performance()
        
        self.fatigue_model.set_fatigue_level(away_fatigue_level)
        away_performance = self.fatigue_model.calculate_performance()
        
        # Calculate relative performance impact
        total_performance = home_performance + away_performance
        if total_performance == 0:
            return {'home_adjustment': 0.0, 'away_adjustment': 0.0, 'draw_adjustment': 0.0}
            
        home_factor = home_performance / total_performance
        away_factor = away_performance / total_performance
        
        # Fatigue increases draw probability slightly
        fatigue_delta = abs(home_fatigue_level - away_fatigue_level)
        draw_boost = min(0.05, fatigue_delta * 0.01)
        
        return {
            'home_adjustment': (home_factor - 0.5) * 0.1,
            'away_adjustment': (away_factor - 0.5) * 0.1,
            'draw_adjustment': draw_boost
        }
    
    def integrate_tactical_insights(self, match_data: Dict) -> Dict[str, float]:
        """
        Integrate tactical interaction analysis.
        
        Args:
            match_data: Dictionary containing match tactical data
            
        Returns:
            Dictionary with tactical adjustments
        """
        scenario = self.tactical_model.detect_scenario(match_data)
        
        # Adjust based on tactical scenario
        if scenario == 'deep_block':
            # Deep block scenarios favor draws and under goals
            return {
                'home_adjustment': -0.05,
                'away_adjustment': -0.02,
                'draw_adjustment': 0.07
            }
        elif scenario == 'possession':
            # Possession scenarios favor home wins
            return {
                'home_adjustment': 0.05,
                'away_adjustment': -0.03,
                'draw_adjustment': -0.02
            }
        else:
            return {
                'home_adjustment': 0.0,
                'away_adjustment': 0.0,
                'draw_adjustment': 0.0
            }
    
    def integrate_draw_threshold(self, base_probabilities: Dict[str, float], threshold: int = 30) -> float:
        """
        Calculate draw threshold probability enhancement.
        
        Args:
            base_probabilities: Base probability distribution
            threshold: Draw threshold percentage (0-100)
            
        Returns:
            Additional draw probability boost
        """
        engine = DrawThresholdEngine(threshold)
        
        # Use threshold to boost draw probability
        draw_boost = threshold / 1000.0  # Convert to probability boost
        return min(draw_boost, 0.1)  # Cap at 10% boost
    
    def integrate_streak_regression(self, home_streak: int, away_streak: int) -> Dict[str, float]:
        """
        Integrate streak regression analysis.
        
        Args:
            home_streak: Current winning streak for home team
            away_streak: Current winning streak for away team
            
        Returns:
            Dictionary with streak-based adjustments
        """
        home_adjusted = adjust_streak_logic(home_streak)
        away_adjusted = adjust_streak_logic(away_streak)
        
        # Long streaks tend to regress (reduce win probability)
        home_regression = 0.0
        away_regression = 0.0
        
        if home_streak > 3:
            home_regression = -0.03 * (home_streak - 3)
        if away_streak > 3:
            away_regression = -0.03 * (away_streak - 3)
            
        return {
            'home_adjustment': home_regression,
            'away_adjustment': away_regression,
            'draw_adjustment': -(home_regression + away_regression) / 2
        }
    
    def calculate_match_result_probabilities(
        self,
        base_home_win: float,
        base_draw: float,
        base_away_win: float,
        fatigue_home: int = 0,
        fatigue_away: int = 0,
        tactical_data: Optional[Dict] = None,
        home_streak: int = 0,
        away_streak: int = 0,
        draw_threshold: int = 30
    ) -> Dict[str, float]:
        """
        Calculate comprehensive match result probabilities.
        
        Args:
            base_home_win: Base probability for home win
            base_draw: Base probability for draw
            base_away_win: Base probability for away win
            fatigue_home: Home team fatigue level (0-10)
            fatigue_away: Away team fatigue level (0-10)
            tactical_data: Tactical match data
            home_streak: Home team winning streak
            away_streak: Away team winning streak
            draw_threshold: Draw threshold parameter
            
        Returns:
            Dictionary with final match result probabilities
        """
        # Start with base probabilities
        base_probs = {
            'home_win': base_home_win,
            'draw': base_draw,
            'away_win': base_away_win
        }
        
        adjustments_list = []
        descriptions_list = []
        
        # Apply fatigue adjustments
        fatigue_adj = self.integrate_fatigue_insights(fatigue_home, fatigue_away)
        adjustments_list.append({
            'home_win': fatigue_adj['home_adjustment'],
            'draw': fatigue_adj['draw_adjustment'],
            'away_win': fatigue_adj['away_adjustment']
        })
        descriptions_list.append("Fatigue Impact")
        
        # Apply tactical adjustments
        if tactical_data:
            tactical_adj = self.integrate_tactical_insights(tactical_data)
            adjustments_list.append({
                'home_win': tactical_adj['home_adjustment'],
                'draw': tactical_adj['draw_adjustment'],
                'away_win': tactical_adj['away_adjustment']
            })
            descriptions_list.append("Tactical Interaction")
        
        # Apply streak regression
        streak_adj = self.integrate_streak_regression(home_streak, away_streak)
        adjustments_list.append({
            'home_win': streak_adj['home_adjustment'],
            'draw': streak_adj['draw_adjustment'],
            'away_win': streak_adj['away_adjustment']
        })
        descriptions_list.append("Streak Regression")
        
        # Apply draw threshold
        draw_boost = self.integrate_draw_threshold(base_probs, draw_threshold)
        adjustments_list.append({
            'home_win': -draw_boost / 2,
            'draw': draw_boost,
            'away_win': -draw_boost / 2
        })
        descriptions_list.append("Draw Threshold")
        
        # Apply all adjustments sequentially
        final_probs, audit_trail = self.probability_manager.apply_sequence_of_adjustments(
            base_probs, adjustments_list, descriptions_list
        )
        
        return final_probs
    
    def calculate_goals_market_probabilities(
        self,
        match_result_probs: Dict[str, float],
        fatigue_home: int = 0,
        fatigue_away: int = 0,
        tactical_data: Optional[Dict] = None
    ) -> Dict[str, Dict[str, float]]:
        """
        Calculate goals market probabilities (BTTS, Over/Under).
        
        Args:
            match_result_probs: Match result probability distribution
            fatigue_home: Home team fatigue level
            fatigue_away: Away team fatigue level
            tactical_data: Tactical match data
            
        Returns:
            Dictionary with goals market predictions
        """
        home_win_prob = match_result_probs['home_win']
        draw_prob = match_result_probs['draw']
        away_win_prob = match_result_probs['away_win']
        
        # Use goal distribution predictor
        goal_predictor = GoalDistributionPredictor(home_win_prob, draw_prob, away_win_prob)
        
        # Base calculations
        base_over_25 = home_win_prob * 0.65 + away_win_prob * 0.55 + draw_prob * 0.35
        base_under_25 = 1.0 - base_over_25
        
        base_btts_yes = home_win_prob * 0.45 + away_win_prob * 0.45 + draw_prob * 0.60
        base_btts_no = 1.0 - base_btts_yes
        
        # Adjust for fatigue (high fatigue reduces goals)
        avg_fatigue = (fatigue_home + fatigue_away) / 2
        fatigue_factor = 1.0 - (avg_fatigue * 0.05)
        
        over_25 = base_over_25 * fatigue_factor
        under_25 = 1.0 - over_25
        
        btts_yes = base_btts_yes * fatigue_factor
        btts_no = 1.0 - btts_yes
        
        # Tactical adjustments
        if tactical_data:
            scenario = self.tactical_model.detect_scenario(tactical_data)
            if scenario == 'deep_block':
                # Deep block reduces goals
                over_25 *= 0.85
                under_25 = 1.0 - over_25
                btts_yes *= 0.80
                btts_no = 1.0 - btts_yes
        
        return {
            'over_under': {
                'over_2.5': over_25,
                'under_2.5': under_25,
                'over_1.5': min(0.95, over_25 * 1.4),
                'under_1.5': max(0.05, 1.0 - min(0.95, over_25 * 1.4)),
                'over_3.5': max(0.05, over_25 * 0.6),
                'under_3.5': min(0.95, 1.0 - max(0.05, over_25 * 0.6))
            },
            'btts': {
                'yes': btts_yes,
                'no': btts_no
            }
        }
    
    def calculate_correct_score_probabilities(
        self,
        match_result_probs: Dict[str, float],
        goals_market_probs: Dict[str, Dict[str, float]]
    ) -> Dict[str, float]:
        """
        Calculate correct score probabilities.
        
        Args:
            match_result_probs: Match result probability distribution
            goals_market_probs: Goals market probability distribution
            
        Returns:
            Dictionary with correct score predictions
        """
        home_win = match_result_probs['home_win']
        draw = match_result_probs['draw']
        away_win = match_result_probs['away_win']
        
        over_25 = goals_market_probs['over_under']['over_2.5']
        btts_yes = goals_market_probs['btts']['yes']
        
        # Calculate likely scorelines based on probabilities
        scores = {}
        
        # Home win scenarios
        scores['1-0'] = home_win * 0.25 * (1 - btts_yes)
        scores['2-0'] = home_win * 0.20 * (1 - btts_yes)
        scores['2-1'] = home_win * 0.25 * btts_yes
        scores['3-0'] = home_win * 0.10 * over_25
        scores['3-1'] = home_win * 0.15 * over_25 * btts_yes
        scores['3-2'] = home_win * 0.05 * over_25 * btts_yes
        
        # Draw scenarios
        scores['0-0'] = draw * 0.30 * (1 - btts_yes)
        scores['1-1'] = draw * 0.40 * btts_yes
        scores['2-2'] = draw * 0.20 * btts_yes * over_25
        scores['3-3'] = draw * 0.10 * btts_yes * over_25
        
        # Away win scenarios
        scores['0-1'] = away_win * 0.25 * (1 - btts_yes)
        scores['0-2'] = away_win * 0.20 * (1 - btts_yes)
        scores['1-2'] = away_win * 0.25 * btts_yes
        scores['0-3'] = away_win * 0.10 * over_25
        scores['1-3'] = away_win * 0.15 * over_25 * btts_yes
        scores['2-3'] = away_win * 0.05 * over_25 * btts_yes
        
        # Normalize probabilities
        total = sum(scores.values())
        if total > 0:
            scores = {k: v / total for k, v in scores.items()}
        
        return scores
    
    def calculate_confidence_score(self, probability: float, market_type: str) -> float:
        """
        Calculate confidence score for a prediction.
        
        Args:
            probability: Predicted probability
            market_type: Type of market (match_result, goals, correct_score)
            
        Returns:
            Confidence score (0-100)
        """
        # Base confidence from probability
        base_confidence = probability * 100
        
        # Adjust based on market type complexity
        market_complexity = {
            'match_result': 1.0,
            'goals': 0.95,
            'correct_score': 0.85
        }
        
        complexity_factor = market_complexity.get(market_type, 0.9)
        
        # Apply Kelly Criterion-like adjustment for edge
        if probability > 0.5:
            edge_boost = (probability - 0.5) * 20
        else:
            edge_boost = 0
            
        confidence = (base_confidence * complexity_factor + edge_boost) / 1.2
        
        return min(100.0, max(0.0, confidence))
    
    def generate_predictions(
        self,
        base_home_win: float = 0.45,
        base_draw: float = 0.30,
        base_away_win: float = 0.25,
        fatigue_home: int = 0,
        fatigue_away: int = 0,
        tactical_data: Optional[Dict] = None,
        home_streak: int = 0,
        away_streak: int = 0,
        draw_threshold: int = 30,
        markets: Optional[List[str]] = None
    ) -> Dict[str, any]:
        """
        Generate comprehensive predictions across all markets.
        
        Args:
            base_home_win: Base home win probability
            base_draw: Base draw probability
            base_away_win: Base away win probability
            fatigue_home: Home team fatigue level (0-10)
            fatigue_away: Away team fatigue level (0-10)
            tactical_data: Tactical match data dictionary
            home_streak: Home team winning streak
            away_streak: Away team winning streak
            draw_threshold: Draw threshold parameter
            markets: List of specific markets to evaluate (None = all)
            
        Returns:
            Dictionary containing all predictions with probabilities and confidence
        """
        results = {}
        
        # Calculate match result probabilities
        match_result_probs = self.calculate_match_result_probabilities(
            base_home_win, base_draw, base_away_win,
            fatigue_home, fatigue_away, tactical_data,
            home_streak, away_streak, draw_threshold
        )
        
        if markets is None or 'match_result' in markets:
            results['match_result'] = {
                'probabilities': match_result_probs,
                'confidence': {
                    outcome: self.calculate_confidence_score(prob, 'match_result')
                    for outcome, prob in match_result_probs.items()
                }
            }
        
        # Calculate goals market probabilities
        if markets is None or 'goals' in markets:
            goals_probs = self.calculate_goals_market_probabilities(
                match_result_probs, fatigue_home, fatigue_away, tactical_data
            )
            
            results['goals'] = {
                'probabilities': goals_probs,
                'confidence': {}
            }
            
            # Calculate confidence for each goal market
            for market, outcomes in goals_probs.items():
                results['goals']['confidence'][market] = {
                    outcome: self.calculate_confidence_score(prob, 'goals')
                    for outcome, prob in outcomes.items()
                }
        
        # Calculate correct score probabilities
        if markets is None or 'correct_score' in markets:
            if 'goals' not in results:
                goals_probs = self.calculate_goals_market_probabilities(
                    match_result_probs, fatigue_home, fatigue_away, tactical_data
                )
            else:
                goals_probs = results['goals']['probabilities']
                
            correct_score_probs = self.calculate_correct_score_probabilities(
                match_result_probs, goals_probs
            )
            
            results['correct_score'] = {
                'probabilities': correct_score_probs,
                'confidence': {
                    score: self.calculate_confidence_score(prob, 'correct_score')
                    for score, prob in correct_score_probs.items()
                }
            }
        
        return results


def rank_predictions(prediction_set: Dict[str, any], top_n: int = 10) -> List[Tuple[str, str, float, float]]:
    """
    Rank predictions across all markets by confidence level.
    
    Args:
        prediction_set: Complete prediction set from generate_predictions()
        top_n: Number of top predictions to return
        
    Returns:
        List of tuples: (market, outcome, probability, confidence)
        Sorted by confidence in descending order
    """
    all_predictions = []
    
    for market, data in prediction_set.items():
        if market == 'match_result':
            # Simple market structure
            for outcome, prob in data['probabilities'].items():
                confidence = data['confidence'][outcome]
                all_predictions.append((market, outcome, prob, confidence))
                
        elif market == 'goals':
            # Nested market structure
            for sub_market, outcomes in data['probabilities'].items():
                for outcome, prob in outcomes.items():
                    confidence = data['confidence'][sub_market][outcome]
                    prediction_name = f"{sub_market}:{outcome}"
                    all_predictions.append((market, prediction_name, prob, confidence))
                    
        elif market == 'correct_score':
            # Simple market structure
            for score, prob in data['probabilities'].items():
                confidence = data['confidence'][score]
                all_predictions.append((market, score, prob, confidence))
    
    # Sort by confidence (descending) and then by probability (descending)
    ranked = sorted(all_predictions, key=lambda x: (x[3], x[2]), reverse=True)
    
    return ranked[:top_n]


def format_predictions_report(predictions: Dict[str, any], top_predictions: List[Tuple]) -> str:
    """
    Format predictions into a readable report.
    
    Args:
        predictions: Full prediction set
        top_predictions: Ranked top predictions
        
    Returns:
        Formatted string report
    """
    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append("INTELLIGENT PREDICTION MODULE - ANALYSIS REPORT")
    report_lines.append("=" * 80)
    report_lines.append("")
    
    # Match Result Section
    if 'match_result' in predictions:
        report_lines.append("MATCH RESULT PROBABILITIES:")
        report_lines.append("-" * 80)
        for outcome, prob in predictions['match_result']['probabilities'].items():
            conf = predictions['match_result']['confidence'][outcome]
            report_lines.append(f"  {outcome:15s}: {prob:6.2%}  (Confidence: {conf:5.1f})")
        report_lines.append("")
    
    # Goals Market Section
    if 'goals' in predictions:
        report_lines.append("GOALS MARKET PROBABILITIES:")
        report_lines.append("-" * 80)
        for market, outcomes in predictions['goals']['probabilities'].items():
            report_lines.append(f"  {market.upper().replace('_', ' ')}:")
            for outcome, prob in outcomes.items():
                conf = predictions['goals']['confidence'][market][outcome]
                report_lines.append(f"    {outcome:12s}: {prob:6.2%}  (Confidence: {conf:5.1f})")
        report_lines.append("")
    
    # Top Predictions Section
    report_lines.append("TOP CONFIDENT PREDICTIONS:")
    report_lines.append("-" * 80)
    for i, (market, outcome, prob, conf) in enumerate(top_predictions, 1):
        report_lines.append(f"{i:2d}. [{market:15s}] {outcome:25s}: {prob:6.2%}  (Confidence: {conf:5.1f})")
    report_lines.append("")
    report_lines.append("=" * 80)
    
    return "\n".join(report_lines)


# Example usage
if __name__ == "__main__":
    # Initialize module
    predictor = IntelligentPredictionModule()
    
    # Example prediction scenario
    predictions = predictor.generate_predictions(
        base_home_win=0.45,
        base_draw=0.30,
        base_away_win=0.25,
        fatigue_home=3,
        fatigue_away=5,
        tactical_data={'formation': '4-4-2', 'style': 'possession'},
        home_streak=4,
        away_streak=1,
        draw_threshold=35
    )
    
    # Rank predictions
    top_predictions = rank_predictions(predictions, top_n=10)
    
    # Generate report
    report = format_predictions_report(predictions, top_predictions)
    print(report)
    
    # Example: Query only goals market
    print("\n" + "=" * 80)
    print("GOALS MARKET ONLY QUERY:")
    print("=" * 80)
    goals_only = predictor.generate_predictions(
        base_home_win=0.45,
        base_draw=0.30,
        base_away_win=0.25,
        markets=['goals']
    )
    print(goals_only)
