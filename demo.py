#!/usr/bin/env python3
"""
Demo script for Forest vs Leeds Prediction System

This script demonstrates the complete prediction pipeline with
clear, formatted output suitable for presentations.
"""

from forest_leeds_prediction import ForestLeedsPrediction


def print_separator(char="=", length=80):
    """Print a separator line"""
    print(char * length)


def print_section_header(title):
    """Print a formatted section header"""
    print()
    print_separator()
    print(f" {title}")
    print_separator()
    print()


def demo_prediction():
    """Run a demonstration of the prediction system"""
    
    print_section_header("FOREST vs LEEDS - MATCH PREDICTION DEMO")
    
    print("This demo showcases the intelligent prediction query system")
    print("for the upcoming match between Nottingham Forest and Leeds United.")
    print()
    print("The system integrates:")
    print("  • Form analysis (team streaks)")
    print("  • Fatigue modeling (rest days and fixture congestion)")
    print("  • Tactical scenario analysis (playing styles)")
    print("  • Sequential probability adjustments with renormalization")
    print()
    
    input("Press Enter to start the prediction...")
    
    # Create predictor
    predictor = ForestLeedsPrediction()
    
    # Run prediction
    results = predictor.run_prediction()
    
    # Summary
    print_section_header("PREDICTION SUMMARY")
    
    final_probs = results['final_probabilities']
    outcome = results['most_likely_outcome']
    
    print("Starting Probabilities:")
    print(f"  Home Win: 30.0%  |  Draw: 40.0%  |  Away Win: 30.0%")
    print()
    
    print("Final Probabilities:")
    print(f"  Home Win: {final_probs['home_win']:.1%}  |  Draw: {final_probs['draw']:.1%}  |  Away Win: {final_probs['away_win']:.1%}")
    print()
    
    print(f"➤ Most Likely Outcome: {outcome}")
    print()
    
    print("Key Insights:")
    print("  • Forest's home form (5 matches unbeaten) significantly boosted their chances")
    print("  • Leeds' poor away form (7 matches winless) severely hurt their prospects")
    print("  • Leeds' midweek match fatigue reduced their winning probability")
    print("  • Tactical matchup (Leeds possession vs Forest defensive) favors a draw")
    print("  • Combined effect: Strong lean towards a draw or home win")
    print()
    
    print_separator()
    print("Demo completed successfully!")
    print_separator()
    print()
    
    return results


if __name__ == "__main__":
    demo_prediction()
