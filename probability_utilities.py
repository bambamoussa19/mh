"""
Probability Utilities - Enhanced with xG Integration

Utilities for managing and adjusting probabilities with full audit trails.
Enhanced to support xG-based probability calculations.
"""


class ProbabilityManager:
    
    @staticmethod
    def apply_adjustment_with_renorm(base_prob_dict, adjustment_dict, description=""):
        """Apply adjustment and renormalize probabilities to sum to 1.0"""
        pre_total = sum(base_prob_dict.values())
        if abs(pre_total - 1.0) > 0.001:
            raise ValueError(f"Input probabilities don't sum to 1.0: {pre_total}")
        
        adjusted = {}
        for outcome, base_prob in base_prob_dict.items():
            delta = adjustment_dict.get(outcome, 0)
            adjusted[outcome] = base_prob + delta
        
        out_of_bounds = []
        for outcome, prob in adjusted.items():
            if prob < 0 or prob > 1:
                out_of_bounds.append((outcome, prob))
        
        if out_of_bounds:
            print(f"WARNING: Out of bounds after {description}")
        
        total = sum(adjusted.values())
        if total == 0:
            raise ValueError("Total probability is 0 after adjustment")
        
        renormalized = {k: v / total for k, v in adjusted.items()}
        drift_magnitude = abs(total - 1.0)
        
        audit_log = {
            'description': description,
            'before': base_prob_dict.copy(),
            'adjustment': adjustment_dict.copy(),
            'after_raw': adjusted.copy(),
            'after_renorm': renormalized.copy(),
            'total_before_renorm': total,
            'drift_magnitude': drift_magnitude
        }
        
        return renormalized, drift_magnitude, audit_log
    
    @staticmethod
    def xg_to_outcome_probabilities(xg_home, xg_away):
        """
        Convert xG values to match outcome probabilities using Skellam distribution.
        
        :param xg_home: Home team expected goals
        :param xg_away: Away team expected goals
        :return: Dict with home_win, draw, away_win probabilities
        """
        from scipy.stats import skellam
        
        lambda_home = xg_home * 0.95  # Slight calibration adjustment
        lambda_away = xg_away * 0.95
        
        # Calculate outcome probabilities
        home_win = sum(skellam.pmf(i, lambda_home, lambda_away) for i in range(1, 8))
        draw = skellam.pmf(0, lambda_home, lambda_away)
        away_win = sum(skellam.pmf(i, lambda_home, lambda_away) for i in range(-7, 0))
        
        # Normalize
        total = home_win + draw + away_win
        if total > 0:
            home_win /= total
            draw /= total
            away_win /= total
        
        return {
            'home_win': round(home_win, 4),
            'draw': round(draw, 4),
            'away_win': round(away_win, 4)
        }
    
    @staticmethod
    def blend_xg_with_model(model_probs, xg_probs, xg_weight=0.4):
        """
        Blend model-based probabilities with xG-based probabilities.
        
        :param model_probs: Probabilities from prediction model
        :param xg_probs: Probabilities from xG data
        :param xg_weight: Weight for xG (0-1), default 0.4
        :return: Blended probabilities
        """
        if not (0 <= xg_weight <= 1):
            raise ValueError("xg_weight must be between 0 and 1")
        
        model_weight = 1 - xg_weight
        
        blended = {}
        for outcome in model_probs.keys():
            if outcome in xg_probs:
                blended[outcome] = (model_probs[outcome] * model_weight + 
                                   xg_probs[outcome] * xg_weight)
            else:
                blended[outcome] = model_probs[outcome] * model_weight
        
        # Normalize
        total = sum(blended.values())
        if total > 0:
            blended = {k: v / total for k, v in blended.items()}
        
        return {k: round(v, 4) for k, v in blended.items()}
    
    @staticmethod
    def apply_sequence_of_adjustments(base_probs, adjustments_list, descriptions_list):
        """Apply multiple adjustments sequentially, renormalizing after each"""
        current = base_probs.copy()
        audit_trail = []
        
        for i, (adjustment, description) in enumerate(zip(adjustments_list, descriptions_list)):
            current, drift, log = ProbabilityManager.apply_adjustment_with_renorm(
                current, adjustment, description
            )
            
            audit_trail.append({
                'step': i + 1,
                'description': description,
                'before': log['before'],
                'adjustment': log['adjustment'],
                'after': current,
                'drift': drift
            })
        
        return current, audit_trail
    
    @staticmethod
    def print_audit_trail(audit_trail):
        """Pretty print the full adjustment audit trail"""
        print("\n" + "="*80)
        print("PROBABILITY ADJUSTMENT AUDIT TRAIL")
        print("="*80 + "\n")
        
        for step in audit_trail:
            print(f"STEP {step['step']}: {step['description']}")
            print("-" * 80)
            print(f"Before:      {step['before']}")
            print(f"Adjustment:  {step['adjustment']}")
            print(f"After:       {step['after']}")
            print(f"Drift:       {step['drift']:.6f}")
            print()