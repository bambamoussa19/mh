# weak_attacking_detector_fixed.py

class WeakAttackingDetector:
    def __init__(self):
        self.false_classifications = 0
        self.smart_btts_adjustment = 0

    def detect(self, data):
        # Implement the detection logic here
        if self.is_attack(data):
            # Prevent false classifications
            self.false_classifications = 0
            return True  # Attack detected
        else:
            self.false_classifications += 1
            self.adjust_btts()  # Adjust BTTS based on misclassification
            return False  # No attack detected

    def is_attack(self, data):
        """
        Determine if the data represents an attacking pattern.
        :param data: dict with keys 'shots' (int), 'shots_on_target' (int),
                     and 'xg' (float, expected goals).
        :return: True if an attacking pattern is detected, False otherwise.
        """
        shots = data.get('shots', 0) if isinstance(data, dict) else 0
        shots_on_target = data.get('shots_on_target', 0) if isinstance(data, dict) else 0
        xg = data.get('xg', 0.0) if isinstance(data, dict) else 0.0
        return shots >= 3 or shots_on_target >= 1 or xg >= 0.3

    def adjust_btts(self):
        # Smart logic for BTTS adjustment
        if self.false_classifications > 5:
            self.smart_btts_adjustment += 1
        elif self.false_classifications < 2:
            self.smart_btts_adjustment -= 1

        # Ensure adjustment is within acceptable bounds
        self.smart_btts_adjustment = max(0, min(self.smart_btts_adjustment, 10))

        print(f"BTTS adjusted to {self.smart_btts_adjustment}")

