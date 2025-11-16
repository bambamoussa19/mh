"""
Market Coherence Validator

Validates internal consistency of predictions across different markets.
Ensures logical coherence between:
- Match result (1X2)
- Over/Under goals
- Both Teams To Score (BTTS)
- Correct Score
- Asian Handicaps
"""

import numpy as np


class MarketCoherenceValidator:
    """
    Validates prediction consistency across multiple betting markets.
    """
    
    def __init__(self):
        self.tolerance = 0.10  # 10% tolerance for inconsistencies
        
    def validate_result_vs_goals(self, result_probs, over_under_probs, total_xg):
        """
        Validate coherence between match result and over/under goals.
        
        :param result_probs: Dict {'home_win': p1, 'draw': p2, 'away_win': p3}
        :param over_under_probs: Dict {'over_2.5': p1, 'under_2.5': p2}
        :param total_xg: Total expected goals (home_xg + away_xg)
        :return: Dict with validation results
        """
        issues = []
        
        # Rule 1: High draw probability should correlate with under 2.5
        if result_probs.get('draw', 0) > 0.35:
            if over_under_probs.get('under_2.5', 0) < 0.45:
                issues.append({
                    'type': 'draw_vs_goals',
                    'severity': 'medium',
                    'description': f"High draw prob ({result_probs['draw']:.1%}) but low under 2.5 ({over_under_probs.get('under_2.5', 0):.1%})"
                })
        
        # Rule 2: Over 2.5 probability should align with total xG
        expected_over_prob = self._xg_to_over_probability(total_xg)
        actual_over_prob = over_under_probs.get('over_2.5', 0.5)
        
        if abs(expected_over_prob - actual_over_prob) > self.tolerance:
            issues.append({
                'type': 'xg_vs_over',
                'severity': 'high',
                'description': f"xG suggests {expected_over_prob:.1%} Over 2.5, but prediction is {actual_over_prob:.1%}"
            })
        
        # Rule 3: Dominant win probability (>60%) should suggest over 2.5
        max_win_prob = max(result_probs.get('home_win', 0), result_probs.get('away_win', 0))
        if max_win_prob > 0.60 and over_under_probs.get('over_2.5', 0) < 0.40:
            issues.append({
                'type': 'dominant_win_vs_goals',
                'severity': 'low',
                'description': f"Dominant win prob ({max_win_prob:.1%}) but low Over 2.5 ({over_under_probs.get('over_2.5', 0):.1%})"
            })
        
        is_coherent = len(issues) == 0
        
        return {
            'coherent': is_coherent,
            'issues': issues,
            'coherence_score': max(0, 1.0 - len(issues) * 0.2)
        }
    
    def validate_btts_consistency(self, result_probs, btts_probs, xg_home, xg_away):
        """
        Validate BTTS consistency with results and xG.
        
        :param result_probs: Dict with result probabilities
        :param btts_probs: Dict {'yes': p1, 'no': p2}
        :param xg_home: Home team expected goals
        :param xg_away: Away team expected goals
        :return: Dict with validation results
        """
        issues = []
        
        # Rule 1: Both xG > 1.0 should suggest BTTS Yes
        if xg_home > 1.0 and xg_away > 1.0:
            if btts_probs.get('yes', 0) < 0.50:
                issues.append({
                    'type': 'xg_vs_btts',
                    'severity': 'medium',
                    'description': f"Both teams with xG > 1.0 but BTTS Yes only {btts_probs.get('yes', 0):.1%}"
                })
        
        # Rule 2: High draw probability + moderate xG suggests BTTS Yes
        if result_probs.get('draw', 0) > 0.35 and min(xg_home, xg_away) > 0.8:
            if btts_probs.get('yes', 0) < 0.55:
                issues.append({
                    'type': 'draw_vs_btts',
                    'severity': 'low',
                    'description': f"High draw probability but BTTS Yes only {btts_probs.get('yes', 0):.1%}"
                })
        
        # Rule 3: Dominant win + low xG from loser suggests BTTS No
        home_win_prob = result_probs.get('home_win', 0)
        away_win_prob = result_probs.get('away_win', 0)
        
        if home_win_prob > 0.60 and xg_away < 0.8:
            if btts_probs.get('no', 0) < 0.50:
                issues.append({
                    'type': 'dominant_win_vs_btts',
                    'severity': 'low',
                    'description': "Dominant home win + low away xG should favor BTTS No"
                })
        elif away_win_prob > 0.60 and xg_home < 0.8:
            if btts_probs.get('no', 0) < 0.50:
                issues.append({
                    'type': 'dominant_win_vs_btts',
                    'severity': 'low',
                    'description': "Dominant away win + low home xG should favor BTTS No"
                })
        
        is_coherent = len(issues) == 0
        
        return {
            'coherent': is_coherent,
            'issues': issues,
            'coherence_score': max(0, 1.0 - len(issues) * 0.2)
        }
    
    def validate_correct_score_sum(self, correct_score_probs):
        """
        Validate that correct score probabilities sum to reasonable value.
        
        :param correct_score_probs: Dict with score predictions
        :return: Dict with validation results
        """
        issues = []
        
        total_prob = sum(correct_score_probs.values())
        
        # Should sum to ~1.0, but we only predict top scores so 0.60-0.90 is reasonable
        if total_prob < 0.50:
            issues.append({
                'type': 'correct_score_sum',
                'severity': 'high',
                'description': f"Correct score probabilities sum to only {total_prob:.1%}"
            })
        elif total_prob > 1.05:
            issues.append({
                'type': 'correct_score_sum',
                'severity': 'high',
                'description': f"Correct score probabilities sum to {total_prob:.1%} (>100%)"
            })
        
        is_coherent = len(issues) == 0
        
        return {
            'coherent': is_coherent,
            'issues': issues,
            'coherence_score': 1.0 if is_coherent else 0.5
        }
    
    def validate_all_markets(self, prediction_package):
        """
        Comprehensive validation of all market predictions.
        
        :param prediction_package: Dict containing all predictions:
            - result_probs (dict)
            - over_under_probs (dict)
            - btts_probs (dict)
            - correct_score_probs (dict)
            - xg_home (float)
            - xg_away (float)
        :return: Comprehensive validation report
        """
        validations = {}
        all_issues = []
        
        # Validate result vs goals
        if 'result_probs' in prediction_package and 'over_under_probs' in prediction_package:
            total_xg = prediction_package.get('xg_home', 1.5) + prediction_package.get('xg_away', 1.5)
            result_goals_validation = self.validate_result_vs_goals(
                prediction_package['result_probs'],
                prediction_package['over_under_probs'],
                total_xg
            )
            validations['result_vs_goals'] = result_goals_validation
            all_issues.extend(result_goals_validation['issues'])
        
        # Validate BTTS consistency
        if 'btts_probs' in prediction_package:
            btts_validation = self.validate_btts_consistency(
                prediction_package.get('result_probs', {}),
                prediction_package['btts_probs'],
                prediction_package.get('xg_home', 1.5),
                prediction_package.get('xg_away', 1.5)
            )
            validations['btts_consistency'] = btts_validation
            all_issues.extend(btts_validation['issues'])
        
        # Validate correct score sum
        if 'correct_score_probs' in prediction_package:
            cs_validation = self.validate_correct_score_sum(
                prediction_package['correct_score_probs']
            )
            validations['correct_score_sum'] = cs_validation
            all_issues.extend(cs_validation['issues'])
        
        # Calculate overall coherence score
        coherence_scores = [v['coherence_score'] for v in validations.values()]
        overall_coherence = np.mean(coherence_scores) if coherence_scores else 1.0
        
        # Categorize issues by severity
        high_severity = [i for i in all_issues if i.get('severity') == 'high']
        medium_severity = [i for i in all_issues if i.get('severity') == 'medium']
        low_severity = [i for i in all_issues if i.get('severity') == 'low']
        
        return {
            'overall_coherent': len(high_severity) == 0,
            'coherence_score': overall_coherence,
            'total_issues': len(all_issues),
            'high_severity_issues': len(high_severity),
            'medium_severity_issues': len(medium_severity),
            'low_severity_issues': len(low_severity),
            'detailed_validations': validations,
            'all_issues': all_issues
        }
    
    def _xg_to_over_probability(self, total_xg):
        """Convert total xG to Over 2.5 probability using Poisson."""
        from scipy.stats import poisson
        
        # P(Over 2.5) = 1 - P(0) - P(1) - P(2)
        under_prob = sum(poisson.pmf(k, total_xg) for k in range(3))
        over_prob = 1 - under_prob
        
        return over_prob
    
    def print_coherence_report(self, validation_report):
        """Print formatted coherence validation report."""
        print("\n" + "="*70)
        print("MARKET COHERENCE VALIDATION REPORT")
        print("="*70)
        
        print(f"\nOverall Coherence Score: {validation_report['coherence_score']:.2f}/1.00")
        print(f"Status: {'✓ COHERENT' if validation_report['overall_coherent'] else '✗ ISSUES FOUND'}")
        
        print(f"\nIssue Summary:")
        print(f"  High Severity:   {validation_report['high_severity_issues']}")
        print(f"  Medium Severity: {validation_report['medium_severity_issues']}")
        print(f"  Low Severity:    {validation_report['low_severity_issues']}")
        
        if validation_report['all_issues']:
            print("\nDetailed Issues:")
            print("-"*70)
            for i, issue in enumerate(validation_report['all_issues'], 1):
                severity_symbol = "🔴" if issue['severity'] == 'high' else "🟡" if issue['severity'] == 'medium' else "🟢"
                print(f"{i}. {severity_symbol} [{issue['type']}]")
                print(f"   {issue['description']}")
        
        print("="*70 + "\n")


# Example usage and testing
if __name__ == '__main__':
    validator = MarketCoherenceValidator()
    
    # Example 1: Coherent predictions
    print("Example 1: Coherent Prediction Package")
    coherent_package = {
        'result_probs': {'home_win': 0.50, 'draw': 0.30, 'away_win': 0.20},
        'over_under_probs': {'over_2.5': 0.55, 'under_2.5': 0.45},
        'btts_probs': {'yes': 0.60, 'no': 0.40},
        'correct_score_probs': {'1-0': 0.15, '2-1': 0.20, '2-0': 0.15, '1-1': 0.12},
        'xg_home': 1.8,
        'xg_away': 1.2
    }
    
    report1 = validator.validate_all_markets(coherent_package)
    validator.print_coherence_report(report1)
    
    # Example 2: Incoherent predictions
    print("\nExample 2: Incoherent Prediction Package")
    incoherent_package = {
        'result_probs': {'home_win': 0.35, 'draw': 0.45, 'away_win': 0.20},
        'over_under_probs': {'over_2.5': 0.65, 'under_2.5': 0.35},  # Inconsistent with high draw
        'btts_probs': {'yes': 0.30, 'no': 0.70},  # Inconsistent with over 2.5
        'correct_score_probs': {'1-0': 0.15, '2-1': 0.20},
        'xg_home': 1.6,
        'xg_away': 1.4
    }
    
    report2 = validator.validate_all_markets(incoherent_package)
    validator.print_coherence_report(report2)
