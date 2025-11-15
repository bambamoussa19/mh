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