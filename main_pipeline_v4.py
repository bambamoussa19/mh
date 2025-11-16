# main_pipeline_v4.py
"""
Main Pipeline v4 - Integrated Prediction System

This module serves as the entry point for the comprehensive prediction pipeline,
integrating all production-ready modules into a unified system.
"""

import numpy as np
import pandas as pd
import json
import logging
from datetime import datetime

from integrated_prediction_pipeline import IntegratedPredictionPipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MainPipelineV4:
    """
    Main pipeline orchestrator with comprehensive logging and audit trails.
    """
    
    def __init__(self):
        self.pipeline = IntegratedPredictionPipeline()
        logger.info("Initialized Main Pipeline v4")
    
    def process_single_match(self, match_data, verbose=False):
        """
        Process a single match through the pipeline.
        
        :param match_data: Dict with match information
        :param verbose: Enable detailed logging
        :return: Prediction results
        """
        logger.info(f"Processing match: {match_data.get('home_team', 'Unknown')} vs {match_data.get('away_team', 'Unknown')}")
        
        try:
            result = self.pipeline.predict(match_data, verbose=verbose)
            logger.info("Match prediction completed successfully")
            return result
        except Exception as e:
            logger.error(f"Error processing match: {str(e)}", exc_info=True)
            raise
    
    def process_batch(self, matches_data, output_file=None):
        """
        Process multiple matches in batch.
        
        :param matches_data: List of match data dicts
        :param output_file: Optional file to save results
        :return: List of results
        """
        logger.info(f"Processing batch of {len(matches_data)} matches")
        
        results = []
        for i, match_data in enumerate(matches_data, 1):
            logger.info(f"Processing match {i}/{len(matches_data)}")
            try:
                result = self.process_single_match(match_data, verbose=False)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to process match {i}: {str(e)}")
                results.append({'error': str(e), 'match_data': match_data})
        
        if output_file:
            self._save_results(results, output_file)
            logger.info(f"Results saved to {output_file}")
        
        return results
    
    def _save_results(self, results, output_file):
        """Save results to JSON file."""
        try:
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving results: {str(e)}")
    
    def generate_prediction_report(self, result):
        """
        Generate a formatted prediction report.
        
        :param result: Prediction result from pipeline
        :return: Formatted report string
        """
        report = []
        report.append("="*80)
        report.append(f"MATCH PREDICTION REPORT - {result['match']['home']} vs {result['match']['away']}")
        report.append("="*80)
        report.append("")
        
        # Match result predictions
        report.append("MATCH RESULT:")
        report.append(f"  Home Win: {result['predictions']['result']['home_win']:.1%}")
        report.append(f"  Draw:     {result['predictions']['result']['draw']:.1%}")
        report.append(f"  Away Win: {result['predictions']['result']['away_win']:.1%}")
        report.append("")
        
        # Over/Under predictions
        report.append("GOALS MARKET:")
        report.append(f"  Over 2.5:  {result['predictions']['over_under_2_5']['Over 2.5 Goals']:.1%}")
        report.append(f"  Under 2.5: {result['predictions']['over_under_2_5']['Under 2.5 Goals']:.1%}")
        report.append("")
        
        # BTTS predictions
        report.append("BOTH TEAMS TO SCORE:")
        report.append(f"  Yes: {result['predictions']['btts']['yes']:.1%}")
        report.append(f"  No:  {result['predictions']['btts']['no']:.1%}")
        report.append("")
        
        # xG information
        report.append("EXPECTED GOALS (Adjusted):")
        report.append(f"  Home: {result['xg_adjusted']['home']}")
        report.append(f"  Away: {result['xg_adjusted']['away']}")
        report.append(f"  Total: {result['xg_adjusted']['total']}")
        report.append("")
        
        # Confidence and coherence
        report.append("PREDICTION QUALITY:")
        report.append(f"  Confidence: {result['confidence']['total_confidence']:.1f}/100 ({result['confidence']['confidence_level']})")
        report.append(f"  Coherence:  {result['coherence']['coherence_score']:.2f}/1.00")
        report.append("")
        
        # Key factors
        report.append("KEY FACTORS:")
        tactical = result['tactical_analysis']
        report.append(f"  Tactical Friction: {tactical['tactical_friction']:.2f}")
        fatigue = result['fatigue_analysis']
        report.append(f"  Home Fatigue: {fatigue['home_fatigue']['effective_penalty_pct']}")
        report.append(f"  Away Fatigue: {fatigue['away_fatigue']['effective_penalty_pct']}")
        
        report.append("="*80)
        
        return "\n".join(report)


# Example usage and testing functions
def run_test_scenarios():
    """Run test scenarios with known match outcomes."""
    pipeline = MainPipelineV4()
    
    test_matches = [
        {
            'name': 'Hamburg 1-1 Dortmund',
            'data': {
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
            },
            'expected_draw': 0.40  # Should be 40%+
        },
        {
            'name': 'Bayern 2-2 Union',
            'data': {
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
            },
            'expected_draw': 0.45  # Should be 45%+
        }
    ]
    
    print("\n" + "="*80)
    print("TEST SCENARIOS - Validation Against Known Outcomes")
    print("="*80)
    
    for test in test_matches:
        print(f"\n{test['name']}:")
        print("-"*80)
        result = pipeline.process_single_match(test['data'], verbose=False)
        draw_prob = result['predictions']['result']['draw']
        
        print(f"Expected Draw Prob: ≥{test['expected_draw']:.0%}")
        print(f"Actual Draw Prob:   {draw_prob:.1%}")
        
        if draw_prob >= test['expected_draw']:
            print("✓ PASS - Draw probability meets expectations")
        else:
            print("✗ FAIL - Draw probability below expectations")
        
        print(f"\nFull prediction:")
        print(f"  Home Win: {result['predictions']['result']['home_win']:.1%}")
        print(f"  Draw:     {draw_prob:.1%}")
        print(f"  Away Win: {result['predictions']['result']['away_win']:.1%}")


def main():
    """Main function for pipeline execution."""
    logger.info("Starting Main Pipeline v4")
    
    # Example: Process a single match
    example_match = {
        'home_team': 'Team A',
        'away_team': 'Team B',
        'league': 'premier_league',
        'home_xg': 1.8,
        'away_xg': 1.2,
        'home_possession': 55,
        'away_possession': 45,
        'home_form': ['W', 'W', 'D', 'L', 'W'],
        'away_form': ['L', 'D', 'W', 'L', 'D'],
        'home_days_rest': 4,
        'away_days_rest': 3,
        'home_midweek_competition': 'league',
        'away_midweek_competition': 'europa_league'
    }
    
    pipeline = MainPipelineV4()
    result = pipeline.process_single_match(example_match, verbose=True)
    
    # Generate and print report
    report = pipeline.generate_prediction_report(result)
    print("\n" + report)
    
    logger.info("Pipeline execution completed")


if __name__ == "__main__":
    # Run test scenarios to validate against known outcomes
    run_test_scenarios()
    
    print("\n" + "="*80)
    print("\nRunning main pipeline example...")
    print("="*80)
    
    # Run main example
    main()