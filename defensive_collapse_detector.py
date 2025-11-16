"""
Defensive Collapse Detector

Detects panic defense patterns through behavioral statistics that
indicate potential blowout scenarios.

Addresses audit finding: "Defensive panic (4 yellows) not detected 
as blowout risk indicator"
"""

import numpy as np


class DefensiveCollapseDetector:
    """
    Detects signs of defensive collapse through behavioral patterns:
    - Excessive yellow cards (panic fouls)
    - High shot volume allowed
    - Declining defensive metrics over time
    - Loss of tactical discipline
    """
    
    def __init__(self):
        # Thresholds for collapse indicators
        self.yellow_card_panic_threshold = 3
        self.shots_allowed_panic_threshold = 18
        self.defensive_deterioration_threshold = 0.3
        
    def detect_panic_fouls(self, card_data):
        """
        Detect panic fouling patterns.
        
        :param card_data: Dict with:
            - yellow_cards: Int
            - yellow_cards_first_half: Int
            - fouls_committed: Int
            - tactical_fouls: Int (intentional fouls)
        :return: Panic score (0-1) and details
        """
        yellow_cards = card_data.get('yellow_cards', 0)
        yellow_first_half = card_data.get('yellow_cards_first_half', 0)
        fouls = card_data.get('fouls_committed', 0)
        tactical_fouls = card_data.get('tactical_fouls', 0)
        
        panic_score = 0.0
        indicators = []
        
        # Excessive yellow cards
        if yellow_cards >= self.yellow_card_panic_threshold:
            panic_score += 0.4
            indicators.append(f"High yellow cards: {yellow_cards}")
            
            # Early yellows indicate loss of control
            if yellow_first_half >= 2:
                panic_score += 0.2
                indicators.append(f"Early discipline loss: {yellow_first_half} yellows in first half")
        
        # High foul rate
        if fouls > 0 and yellow_cards / fouls > 0.25:
            panic_score += 0.2
            indicators.append(f"High booking rate: {yellow_cards}/{fouls} fouls")
        
        # Non-tactical fouls (desperation)
        if fouls > 0:
            desperation_fouls = fouls - tactical_fouls
            if desperation_fouls / fouls > 0.7:
                panic_score += 0.2
                indicators.append("Majority desperation fouls")
        
        panic_score = min(1.0, panic_score)
        
        return {
            'panic_score': round(panic_score, 3),
            'risk_level': self._classify_risk(panic_score),
            'indicators': indicators
        }
    
    def detect_shot_suppression_failure(self, defensive_stats):
        """
        Detect failure to suppress opposition shots.
        
        :param defensive_stats: Dict with:
            - shots_allowed: Int
            - shots_on_target_allowed: Int
            - xg_allowed: Float
            - blocks: Int
            - clearances: Int
        :return: Failure assessment
        """
        shots_allowed = defensive_stats.get('shots_allowed', 0)
        shots_on_target = defensive_stats.get('shots_on_target_allowed', 0)
        xg_allowed = defensive_stats.get('xg_allowed', 0)
        blocks = defensive_stats.get('blocks', 0)
        clearances = defensive_stats.get('clearances', 0)
        
        failure_score = 0.0
        indicators = []
        
        # Excessive shots allowed
        if shots_allowed >= self.shots_allowed_panic_threshold:
            failure_score += 0.4
            indicators.append(f"High shot volume: {shots_allowed} shots")
        
        # High quality shots (on target percentage)
        if shots_allowed > 0:
            on_target_pct = shots_on_target / shots_allowed
            if on_target_pct > 0.5:
                failure_score += 0.3
                indicators.append(f"High shot quality: {on_target_pct:.1%} on target")
        
        # Expected goals allowed
        if xg_allowed > 2.5:
            failure_score += 0.3
            indicators.append(f"High xG allowed: {xg_allowed:.2f}")
        
        failure_score = min(1.0, failure_score)
        
        return {
            'failure_score': round(failure_score, 3),
            'risk_level': self._classify_risk(failure_score),
            'indicators': indicators
        }
    
    def detect_defensive_deterioration(self, time_series_data):
        """
        Detect deteriorating defensive performance over time.
        
        :param time_series_data: List of dicts with metrics at different time points:
            - time_period: String (e.g., "0-15", "15-30", etc.)
            - shots_allowed: Int
            - possession_lost: Int
            - defensive_actions: Int
        :return: Deterioration assessment
        """
        if len(time_series_data) < 3:
            return {
                'deterioration_score': 0.5,
                'risk_level': 'Insufficient Data',
                'trend': 'Unknown'
            }
        
        # Extract metrics over time
        shots_trend = [period.get('shots_allowed', 0) for period in time_series_data]
        actions_trend = [period.get('defensive_actions', 0) for period in time_series_data]
        
        # Calculate trends (positive = worsening)
        shots_slope = self._calculate_trend(shots_trend)
        actions_slope = self._calculate_trend(actions_trend)
        
        deterioration_score = 0.0
        indicators = []
        
        # Increasing shots allowed
        if shots_slope > self.defensive_deterioration_threshold:
            deterioration_score += 0.5
            indicators.append(f"Shots allowed increasing (slope: {shots_slope:.2f})")
        
        # Decreasing defensive activity
        if actions_slope < -self.defensive_deterioration_threshold:
            deterioration_score += 0.3
            indicators.append(f"Defensive activity declining")
        
        # Check for acceleration (getting worse faster)
        if len(shots_trend) >= 4:
            recent_slope = self._calculate_trend(shots_trend[-3:])
            if recent_slope > shots_slope * 1.5:
                deterioration_score += 0.2
                indicators.append("Accelerating deterioration")
        
        deterioration_score = min(1.0, deterioration_score)
        
        return {
            'deterioration_score': round(deterioration_score, 3),
            'risk_level': self._classify_risk(deterioration_score),
            'trend': 'Worsening' if deterioration_score > 0.5 else 'Stable',
            'indicators': indicators
        }
    
    def comprehensive_collapse_assessment(self, match_data):
        """
        Comprehensive defensive collapse assessment.
        
        :param match_data: Dict containing:
            - card_data: Dict for panic fouls
            - defensive_stats: Dict for shot suppression
            - time_series_data: List for deterioration tracking
            - current_score_deficit: Int (0 if level/ahead, positive if behind)
        :return: Overall collapse risk assessment
        """
        panic_result = self.detect_panic_fouls(match_data.get('card_data', {}))
        suppression_result = self.detect_shot_suppression_failure(
            match_data.get('defensive_stats', {}))
        deterioration_result = self.detect_defensive_deterioration(
            match_data.get('time_series_data', []))
        
        score_deficit = match_data.get('current_score_deficit', 0)
        
        # Weighted combination of factors
        panic_weight = 0.35
        suppression_weight = 0.35
        deterioration_weight = 0.30
        
        overall_score = (panic_result['panic_score'] * panic_weight +
                        suppression_result['failure_score'] * suppression_weight +
                        deterioration_result['deterioration_score'] * deterioration_weight)
        
        # Amplify if already behind (desperation)
        if score_deficit >= 2:
            overall_score = min(1.0, overall_score * 1.3)
        elif score_deficit >= 1:
            overall_score = min(1.0, overall_score * 1.15)
        
        # Determine blowout risk
        blowout_risk = self._assess_blowout_risk(overall_score, score_deficit)
        
        return {
            'overall_collapse_score': round(overall_score, 3),
            'risk_level': self._classify_risk(overall_score),
            'blowout_risk': blowout_risk,
            'components': {
                'panic_fouls': panic_result,
                'shot_suppression': suppression_result,
                'deterioration': deterioration_result
            },
            'recommendation': self._get_betting_recommendation(overall_score, blowout_risk)
        }
    
    def _calculate_trend(self, values):
        """Calculate linear trend (slope) of values."""
        if len(values) < 2:
            return 0.0
        x = np.arange(len(values))
        y = np.array(values)
        if np.std(y) == 0:
            return 0.0
        slope = np.polyfit(x, y, 1)[0]
        return slope
    
    def _classify_risk(self, score):
        """Classify risk level from score."""
        if score >= 0.7:
            return 'Critical'
        elif score >= 0.5:
            return 'High'
        elif score >= 0.3:
            return 'Moderate'
        else:
            return 'Low'
    
    def _assess_blowout_risk(self, collapse_score, deficit):
        """Assess probability of blowout scenario."""
        if collapse_score >= 0.7 and deficit >= 1:
            return {'probability': 0.65, 'scenario': 'Blowout likely (3+ goal margin)'}
        elif collapse_score >= 0.6:
            return {'probability': 0.45, 'scenario': 'Heavy defeat possible (2+ goal margin)'}
        elif collapse_score >= 0.4:
            return {'probability': 0.25, 'scenario': 'Increased scoring expected'}
        else:
            return {'probability': 0.10, 'scenario': 'Normal match flow'}
    
    def _get_betting_recommendation(self, score, blowout_risk):
        """Generate betting recommendations."""
        if score >= 0.7:
            return {
                'primary': 'Back opposition win with handicap',
                'secondary': 'Over total goals',
                'avoid': 'Backing team under pressure'
            }
        elif score >= 0.5:
            return {
                'primary': 'Over total goals',
                'secondary': 'Opposition win',
                'caution': 'Team showing defensive fragility'
            }
        else:
            return {
                'primary': 'Standard analysis applies',
                'note': 'No severe defensive concerns detected'
            }


# Example usage
if __name__ == "__main__":
    detector = DefensiveCollapseDetector()
    
    # Example: St. Pauli with 4 yellows
    match_data = {
        'card_data': {
            'yellow_cards': 4,
            'yellow_cards_first_half': 2,
            'fouls_committed': 18,
            'tactical_fouls': 3
        },
        'defensive_stats': {
            'shots_allowed': 22,
            'shots_on_target_allowed': 12,
            'xg_allowed': 2.8,
            'blocks': 4,
            'clearances': 18
        },
        'time_series_data': [
            {'time_period': '0-15', 'shots_allowed': 3, 'defensive_actions': 12},
            {'time_period': '15-30', 'shots_allowed': 5, 'defensive_actions': 10},
            {'time_period': '30-45', 'shots_allowed': 7, 'defensive_actions': 8},
            {'time_period': '45-60', 'shots_allowed': 4, 'defensive_actions': 7},
            {'time_period': '60-75', 'shots_allowed': 3, 'defensive_actions': 6}
        ],
        'current_score_deficit': 2
    }
    
    result = detector.comprehensive_collapse_assessment(match_data)
    print(f"Overall Collapse Score: {result['overall_collapse_score']}")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Blowout Risk: {result['blowout_risk']}")
