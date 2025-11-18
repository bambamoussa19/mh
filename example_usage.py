#!/usr/bin/env python3
"""
Example Usage of the Intelligent Prediction Module

This script demonstrates various ways to use the intelligent prediction module
in real-world scenarios.
"""

from intelligent_prediction_module import (
    IntelligentPredictionModule,
    rank_predictions,
    format_predictions_report
)


def example_1_basic_prediction():
    """Example 1: Basic prediction with default parameters"""
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Basic Prediction")
    print("=" * 80)
    
    predictor = IntelligentPredictionModule()
    
    # Simple prediction with just base probabilities
    predictions = predictor.generate_predictions(
        base_home_win=0.45,
        base_draw=0.30,
        base_away_win=0.25
    )
    
    # Get top 5 predictions
    top_5 = rank_predictions(predictions, top_n=5)
    
    print("\nTop 5 Most Confident Predictions:")
    for i, (market, outcome, prob, conf) in enumerate(top_5, 1):
        print(f"{i}. [{market:15s}] {outcome:25s}: {prob:6.2%} (Confidence: {conf:5.1f})")


def example_2_with_fatigue_analysis():
    """Example 2: Prediction with fatigue analysis"""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Prediction with Fatigue Analysis")
    print("=" * 80)
    
    predictor = IntelligentPredictionModule()
    
    # Scenario: Home team is fresh (fatigue=1), away team is tired (fatigue=7)
    predictions = predictor.generate_predictions(
        base_home_win=0.50,
        base_draw=0.30,
        base_away_win=0.20,
        fatigue_home=1,  # Fresh home team
        fatigue_away=7   # Tired away team
    )
    
    print("\nMatch Result Probabilities:")
    for outcome, prob in predictions['match_result']['probabilities'].items():
        conf = predictions['match_result']['confidence'][outcome]
        print(f"  {outcome:15s}: {prob:6.2%} (Confidence: {conf:5.1f})")
    
    print("\nNote: Away team fatigue should increase home win probability")


def example_3_tactical_analysis():
    """Example 3: Prediction with tactical analysis"""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Prediction with Tactical Analysis")
    print("=" * 80)
    
    predictor = IntelligentPredictionModule()
    
    # Scenario: Deep block defensive tactics
    predictions = predictor.generate_predictions(
        base_home_win=0.48,
        base_draw=0.30,
        base_away_win=0.22,
        tactical_data={
            'formation': '5-4-1',
            'style': 'deep_block'  # Defensive approach
        }
    )
    
    print("\nGoals Market Predictions (Deep Block Scenario):")
    for sub_market, outcomes in predictions['goals']['probabilities'].items():
        print(f"\n  {sub_market.upper().replace('_', ' ')}:")
        for outcome, prob in outcomes.items():
            conf = predictions['goals']['confidence'][sub_market][outcome]
            print(f"    {outcome:12s}: {prob:6.2%} (Confidence: {conf:5.1f})")
    
    print("\nNote: Deep block tactics should favor under goals")


def example_4_streak_regression():
    """Example 4: Prediction with streak regression"""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Prediction with Streak Regression")
    print("=" * 80)
    
    predictor = IntelligentPredictionModule()
    
    # Scenario: Home team on long winning streak (likely to regress)
    print("\nScenario A: Home team on 8-game winning streak")
    predictions_a = predictor.generate_predictions(
        base_home_win=0.60,
        base_draw=0.25,
        base_away_win=0.15,
        home_streak=8,  # Long streak - regression expected
        away_streak=0
    )
    
    print("Match Result (with streak regression):")
    for outcome, prob in predictions_a['match_result']['probabilities'].items():
        print(f"  {outcome:15s}: {prob:6.2%}")
    
    print("\nScenario B: No winning streak")
    predictions_b = predictor.generate_predictions(
        base_home_win=0.60,
        base_draw=0.25,
        base_away_win=0.15,
        home_streak=0,
        away_streak=0
    )
    
    print("Match Result (without streak):")
    for outcome, prob in predictions_b['match_result']['probabilities'].items():
        print(f"  {outcome:15s}: {prob:6.2%}")
    
    print("\nNote: Long streak reduces home win probability due to regression")


def example_5_market_specific_queries():
    """Example 5: Querying specific markets"""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Market-Specific Queries")
    print("=" * 80)
    
    predictor = IntelligentPredictionModule()
    
    # Query only goals market
    print("\nQuery 1: Goals Market Only")
    goals_only = predictor.generate_predictions(
        base_home_win=0.45,
        base_draw=0.30,
        base_away_win=0.25,
        markets=['goals']
    )
    top_goals = rank_predictions(goals_only, top_n=3)
    for market, outcome, prob, conf in top_goals:
        print(f"  {outcome:30s}: {prob:6.2%} (Confidence: {conf:5.1f})")
    
    # Query only correct score
    print("\nQuery 2: Correct Score Market Only")
    cs_only = predictor.generate_predictions(
        base_home_win=0.45,
        base_draw=0.30,
        base_away_win=0.25,
        markets=['correct_score']
    )
    top_scores = rank_predictions(cs_only, top_n=5)
    for market, outcome, prob, conf in top_scores:
        print(f"  {outcome:30s}: {prob:6.2%} (Confidence: {conf:5.1f})")
    
    # Query multiple markets
    print("\nQuery 3: Match Result and Goals Only")
    multi = predictor.generate_predictions(
        base_home_win=0.45,
        base_draw=0.30,
        base_away_win=0.25,
        markets=['match_result', 'goals']
    )
    print(f"  Markets included: {list(multi.keys())}")


def example_6_complete_analysis():
    """Example 6: Complete analysis with all factors"""
    print("\n" + "=" * 80)
    print("EXAMPLE 6: Complete Analysis with All Factors")
    print("=" * 80)
    
    predictor = IntelligentPredictionModule()
    
    # Real-world scenario with all factors
    predictions = predictor.generate_predictions(
        base_home_win=0.50,
        base_draw=0.28,
        base_away_win=0.22,
        fatigue_home=3,
        fatigue_away=5,
        tactical_data={
            'formation': '4-3-3',
            'style': 'possession'
        },
        home_streak=4,
        away_streak=1,
        draw_threshold=35
    )
    
    # Generate formatted report
    top_predictions = rank_predictions(predictions, top_n=10)
    report = format_predictions_report(predictions, top_predictions)
    
    print(report)


def example_7_confidence_filtering():
    """Example 7: Filtering predictions by confidence threshold"""
    print("\n" + "=" * 80)
    print("EXAMPLE 7: Filtering by Confidence Threshold")
    print("=" * 80)
    
    predictor = IntelligentPredictionModule()
    
    predictions = predictor.generate_predictions(
        base_home_win=0.55,
        base_draw=0.25,
        base_away_win=0.20
    )
    
    # Get all predictions and filter by confidence
    all_predictions = rank_predictions(predictions, top_n=100)
    
    confidence_threshold = 45.0
    high_confidence = [p for p in all_predictions if p[3] >= confidence_threshold]
    
    print(f"\nPredictions with Confidence >= {confidence_threshold}:")
    for market, outcome, prob, conf in high_confidence:
        print(f"  [{market:15s}] {outcome:25s}: {prob:6.2%} (Confidence: {conf:5.1f})")
    
    print(f"\nTotal high-confidence predictions: {len(high_confidence)}")


def example_8_comparative_analysis():
    """Example 8: Comparing different scenarios"""
    print("\n" + "=" * 80)
    print("EXAMPLE 8: Comparative Scenario Analysis")
    print("=" * 80)
    
    predictor = IntelligentPredictionModule()
    
    scenarios = [
        {
            'name': 'Balanced Match',
            'params': {
                'base_home_win': 0.40,
                'base_draw': 0.35,
                'base_away_win': 0.25
            }
        },
        {
            'name': 'Strong Home Team',
            'params': {
                'base_home_win': 0.65,
                'base_draw': 0.20,
                'base_away_win': 0.15
            }
        },
        {
            'name': 'Strong Away Team',
            'params': {
                'base_home_win': 0.20,
                'base_draw': 0.25,
                'base_away_win': 0.55
            }
        }
    ]
    
    for scenario in scenarios:
        print(f"\n{scenario['name']}:")
        predictions = predictor.generate_predictions(**scenario['params'])
        
        # Get top prediction
        top = rank_predictions(predictions, top_n=1)[0]
        market, outcome, prob, conf = top
        print(f"  Top Pick: [{market}] {outcome} - {prob:.2%} (Conf: {conf:.1f})")
        
        # Get match result winner
        match_probs = predictions['match_result']['probabilities']
        winner = max(match_probs.items(), key=lambda x: x[1])
        print(f"  Most Likely Result: {winner[0]} ({winner[1]:.2%})")


def main():
    """Run all examples"""
    print("=" * 80)
    print("INTELLIGENT PREDICTION MODULE - USAGE EXAMPLES")
    print("=" * 80)
    
    examples = [
        example_1_basic_prediction,
        example_2_with_fatigue_analysis,
        example_3_tactical_analysis,
        example_4_streak_regression,
        example_5_market_specific_queries,
        example_6_complete_analysis,
        example_7_confidence_filtering,
        example_8_comparative_analysis
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"\nError in {example.__name__}: {e}")
    
    print("\n" + "=" * 80)
    print("All examples completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    main()
