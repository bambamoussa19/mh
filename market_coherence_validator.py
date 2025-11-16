"""
Market Coherence Validator

Validates that market predictions are logically aligned.
Prevents contradictory predictions like "Home Win 80%" + "Under 0.5 Goals 70%".
"""

import numpy as np


class MarketCoherenceValidator:
    """
    Validates coherence across different betting markets to ensure
    predictions don't contradict each other.
    """
    
    def __init__(self):
        self.tolerance = 0.15  # 15% tolerance for minor inconsistencies
        
    def validate_win_goals_coherence(self, match_outcome_probs, over_under_probs):
        """
        Validate coherence between win probabilities and over/under goals.
        
        Example contradiction: High home win + very low total goals
        
        :param match_outcome_probs: Dict with home_win, draw, away_win
        :param over_under_probs: Dict with over_X and under_X probabilities
        :return: Validation result with issues
        """
        home_win = match_outcome_probs.get('home_win', 0)
        away_win = match_outcome_probs.get('away_win', 0)
        draw = match_outcome_probs.get('draw', 0)
        
        over_25 = over_under_probs.get('over_2.5', 0)
        under_15 = over_under_probs.get('under_1.5', 0)
        
        issues = []
        
        # Check 1: High win probability with very low goals
        decisive_win_prob = max(home_win, away_win)
        if decisive_win_prob > 0.65 and under_15 > 0.50:
            issues.append({
                'type': 'win_low_goals_contradiction',
                'severity': 'high',
                'description': f'High win probability ({decisive_win_prob:.1%}) contradicts low goals ({under_15:.1%} under 1.5)',
                'recommendation': 'Reduce under 1.5 probability or lower win confidence'
            })
        
        # Check 2: High draw probability with high goals
        if draw > 0.50 and over_25 > 0.65:
            issues.append({
                'type': 'draw_high_goals_contradiction',
                'severity': 'medium',
                'description': f'High draw probability ({draw:.1%}) less consistent with high goals ({over_25:.1%} over 2.5)',
                'recommendation': 'Draws typically lower scoring - review goal expectations'
            })
        
        # Check 3: Both wins high probability (impossible)
        if home_win > 0.45 and away_win > 0.45:
            issues.append({
                'type': 'both_wins_high',
                'severity': 'critical',
                'description': f'Both home win ({home_win:.1%}) and away win ({away_win:.1%}) too high',
                'recommendation': 'Probabilities must be properly normalized'
            })
        
        is_coherent = len(issues) == 0
        
        return {
            'coherent': is_coherent,
            'issues': issues,
            'validation_passed': is_coherent or all(i['severity'] != 'critical' for i in issues)
        }
    
    def validate_btts_outcome_coherence(self, btts_probs, match_outcome_probs, over_under_probs):
        """
        Validate BTTS coherence with match outcome and goals.
        
        :param btts_probs: Dict with btts_yes, btts_no
        :param match_outcome_probs: Dict with home_win, draw, away_win
        :param over_under_probs: Dict with over/under probabilities
        :return: Validation result
        """
        btts_yes = btts_probs.get('btts_yes', 0)
        btts_no = btts_probs.get('btts_no', 0)
        
        under_15 = over_under_probs.get('under_1.5', 0)
        over_25 = over_under_probs.get('over_2.5', 0)
        
        issues = []
        
        # Check 1: High BTTS with very low total goals
        if btts_yes > 0.60 and under_15 > 0.50:
            issues.append({
                'type': 'btts_low_goals_contradiction',
                'severity': 'high',
                'description': f'High BTTS probability ({btts_yes:.1%}) contradicts low total goals ({under_15:.1%} under 1.5)',
                'recommendation': 'If both teams score, total must be at least 2'
            })
        
        # Check 2: High BTTS_No with high goals
        if btts_no > 0.65 and over_25 > 0.60:
            # This suggests one team dominates scoring
            # Not necessarily contradictory, but worth noting
            issues.append({
                'type': 'btts_no_high_goals_pattern',
                'severity': 'low',
                'description': f'BTTS No ({btts_no:.1%}) with high goals ({over_25:.1%}) suggests one-sided scoring',
                'recommendation': 'Verify one team is expected to dominate'
            })
        
        # Check 3: BTTS probabilities don't sum to ~1.0
        btts_sum = btts_yes + btts_no
        if abs(btts_sum - 1.0) > 0.05:
            issues.append({
                'type': 'btts_probability_sum',
                'severity': 'medium',
                'description': f'BTTS probabilities sum to {btts_sum:.3f}, expected ~1.0',
                'recommendation': 'Normalize BTTS probabilities'
            })
        
        is_coherent = len([i for i in issues if i['severity'] in ['critical', 'high']]) == 0
        
        return {
            'coherent': is_coherent,
            'issues': issues,
            'validation_passed': is_coherent
        }
    
    def validate_correct_score_coherence(self, correct_scores, match_outcome_probs):
        """
        Validate correct score probabilities align with match outcomes.
        
        :param correct_scores: Dict with score probabilities (e.g., '2-1': 0.12)
        :param match_outcome_probs: Dict with home_win, draw, away_win
        :return: Validation result
        """
        # Aggregate correct scores by outcome
        home_win_scores = 0
        draw_scores = 0
        away_win_scores = 0
        
        for score, prob in correct_scores.items():
            if '-' in score:
                home, away = map(int, score.split('-'))
                if home > away:
                    home_win_scores += prob
                elif home < away:
                    away_win_scores += prob
                else:
                    draw_scores += prob
        
        issues = []
        
        # Compare aggregated scores with match outcomes
        home_win_expected = match_outcome_probs.get('home_win', 0)
        draw_expected = match_outcome_probs.get('draw', 0)
        away_win_expected = match_outcome_probs.get('away_win', 0)
        
        if abs(home_win_scores - home_win_expected) > self.tolerance:
            issues.append({
                'type': 'home_win_mismatch',
                'severity': 'medium',
                'description': f'Home win scores ({home_win_scores:.1%}) differ from outcome probability ({home_win_expected:.1%})',
                'recommendation': 'Align correct score distribution with outcome probabilities'
            })
        
        if abs(draw_scores - draw_expected) > self.tolerance:
            issues.append({
                'type': 'draw_mismatch',
                'severity': 'medium',
                'description': f'Draw scores ({draw_scores:.1%}) differ from outcome probability ({draw_expected:.1%})',
                'recommendation': 'Adjust draw score probabilities'
            })
        
        if abs(away_win_scores - away_win_expected) > self.tolerance:
            issues.append({
                'type': 'away_win_mismatch',
                'severity': 'medium',
                'description': f'Away win scores ({away_win_scores:.1%}) differ from outcome probability ({away_win_expected:.1%})',
                'recommendation': 'Align away win scores with outcome probabilities'
            })
        
        is_coherent = len(issues) == 0
        
        return {
            'coherent': is_coherent,
            'issues': issues,
            'validation_passed': is_coherent,
            'aggregated_scores': {
                'home_win': home_win_scores,
                'draw': draw_scores,
                'away_win': away_win_scores
            }
        }
    
    def validate_xg_outcome_coherence(self, xg_values, match_outcome_probs):
        """
        Validate xG values align with predicted match outcomes.
        
        :param xg_values: Dict with xg_home, xg_away
        :param match_outcome_probs: Dict with home_win, draw, away_win
        :return: Validation result
        """
        xg_home = xg_values.get('xg_home', 0)
        xg_away = xg_values.get('xg_away', 0)
        
        home_win = match_outcome_probs.get('home_win', 0)
        draw = match_outcome_probs.get('draw', 0)
        away_win = match_outcome_probs.get('away_win', 0)
        
        issues = []
        
        # Calculate xG-based expectation
        xg_diff = xg_home - xg_away
        
        # Rough heuristics for xG difference
        if xg_diff > 1.0:  # Home significantly better
            expected_home_win = max(home_win, 0.55)
            if home_win < 0.45:
                issues.append({
                    'type': 'xg_suggests_home_win',
                    'severity': 'medium',
                    'description': f'xG difference ({xg_diff:.2f}) suggests home win, but probability only {home_win:.1%}',
                    'recommendation': 'Review home win probability given xG advantage'
                })
        elif xg_diff < -1.0:  # Away significantly better
            expected_away_win = max(away_win, 0.55)
            if away_win < 0.45:
                issues.append({
                    'type': 'xg_suggests_away_win',
                    'severity': 'medium',
                    'description': f'xG difference ({xg_diff:.2f}) suggests away win, but probability only {away_win:.1%}',
                    'recommendation': 'Review away win probability given xG advantage'
                })
        elif abs(xg_diff) < 0.3:  # Very close xG
            if draw < 0.20:
                issues.append({
                    'type': 'close_xg_suggests_draw',
                    'severity': 'low',
                    'description': f'Similar xG ({xg_home:.2f} vs {xg_away:.2f}) but low draw probability {draw:.1%}',
                    'recommendation': 'Consider increasing draw probability for closely matched teams'
                })
        
        is_coherent = len([i for i in issues if i['severity'] in ['critical', 'high']]) == 0
        
        return {
            'coherent': is_coherent,
            'issues': issues,
            'validation_passed': is_coherent,
            'xg_difference': xg_diff
        }
    
    def comprehensive_validation(self, prediction_data):
        """
        Perform comprehensive coherence validation across all markets.
        
        :param prediction_data: Dict with all prediction markets
        :return: Full validation report
        """
        validations = {}
        all_issues = []
        
        # Extract data
        match_outcomes = prediction_data.get('match_outcomes', {})
        over_under = prediction_data.get('over_under', {})
        btts = prediction_data.get('btts', {})
        correct_scores = prediction_data.get('correct_scores', {})
        xg_values = prediction_data.get('xg_values', {})
        
        # Run validations
        if match_outcomes and over_under:
            win_goals = self.validate_win_goals_coherence(match_outcomes, over_under)
            validations['win_goals'] = win_goals
            all_issues.extend(win_goals['issues'])
        
        if btts and match_outcomes and over_under:
            btts_validation = self.validate_btts_outcome_coherence(btts, match_outcomes, over_under)
            validations['btts'] = btts_validation
            all_issues.extend(btts_validation['issues'])
        
        if correct_scores and match_outcomes:
            score_validation = self.validate_correct_score_coherence(correct_scores, match_outcomes)
            validations['correct_scores'] = score_validation
            all_issues.extend(score_validation['issues'])
        
        if xg_values and match_outcomes:
            xg_validation = self.validate_xg_outcome_coherence(xg_values, match_outcomes)
            validations['xg'] = xg_validation
            all_issues.extend(xg_validation['issues'])
        
        # Overall assessment
        critical_issues = [i for i in all_issues if i['severity'] == 'critical']
        high_issues = [i for i in all_issues if i['severity'] == 'high']
        
        overall_coherent = len(critical_issues) == 0 and len(high_issues) == 0
        
        return {
            'overall_coherent': overall_coherent,
            'validation_passed': len(critical_issues) == 0,
            'total_issues': len(all_issues),
            'critical_issues': len(critical_issues),
            'high_issues': len(high_issues),
            'validations': validations,
            'all_issues': all_issues,
            'summary': self._generate_summary(all_issues, overall_coherent)
        }
    
    def _generate_summary(self, issues, coherent):
        """Generate human-readable validation summary."""
        if coherent:
            return "All predictions are logically coherent. No contradictions detected."
        
        summary_parts = []
        
        critical = [i for i in issues if i['severity'] == 'critical']
        if critical:
            summary_parts.append(f"{len(critical)} CRITICAL issues requiring immediate attention")
        
        high = [i for i in issues if i['severity'] == 'high']
        if high:
            summary_parts.append(f"{len(high)} HIGH severity issues that should be addressed")
        
        medium = [i for i in issues if i['severity'] == 'medium']
        if medium:
            summary_parts.append(f"{len(medium)} MEDIUM severity issues to review")
        
        return "; ".join(summary_parts) if summary_parts else "Minor inconsistencies detected"


# Example usage
if __name__ == "__main__":
    validator = MarketCoherenceValidator()
    
    # Example: Test with Frankfurt prediction
    prediction_data = {
        'match_outcomes': {
            'home_win': 0.782,
            'draw': 0.128,
            'away_win': 0.090
        },
        'over_under': {
            'over_2.5': 0.55,
            'under_2.5': 0.45,
            'under_1.5': 0.15
        },
        'btts': {
            'btts_yes': 0.45,
            'btts_no': 0.55
        },
        'xg_values': {
            'xg_home': 0.88,
            'xg_away': 2.32
        },
        'correct_scores': {
            '2-1': 0.15,
            '2-0': 0.12,
            '1-0': 0.10,
            '1-1': 0.08
        }
    }
    
    result = validator.comprehensive_validation(prediction_data)
    
    print(f"Overall Coherent: {result['overall_coherent']}")
    print(f"Summary: {result['summary']}")
    print(f"\nTotal Issues: {result['total_issues']}")
    
    if result['all_issues']:
        print("\nIssues Found:")
        for issue in result['all_issues']:
            print(f"  [{issue['severity'].upper()}] {issue['description']}")
