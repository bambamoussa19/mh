class DecisionEngine:
    def __init__(self):
        self.adjustments = []  # Log of adjustments made

    def apply_adjustment(self, adjustment):
        # Example: apply psychological or tactical adjustment
        self.adjustments.append(adjustment)
        print(f"Applied adjustment: {adjustment}")

    def get_audit_trail(self):
        return self.adjustments  # Return the log of all adjustments made

    def clear_adjustments(self):
        self.adjustments.clear()  # Clear the audit trail if needed