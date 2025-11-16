"""
Enhanced Advanced Metrics Module

Provides advanced analytical metrics for match prediction:
- DrawClusteringIndex: Measures team tendency to draw
- DefensiveSuperiorityMultiplier: Defensive strength indicator
- FormTrendMomentum: Recent form trajectory analysis
- HomeAdvantageContext: Context-aware home advantage calculation
"""

import numpy as np
from collections import defaultdict


class DrawClusteringIndex:
    """
    Measures historical draw clustering patterns for teams.
    Teams with high draw clustering are more likely to draw again.
    """
    
    def __init__(self):
        self.recent_weight = 0.6
        self.historical_weight = 0.4
    
    def calculate(self, recent_results, historical_results=None):
        """
        Calculate Draw Clustering Index.
        
        :param recent_results: List of recent match results (last 5-10 games)
                              Each result: 'W', 'D', or 'L'
        :param historical_results: List of historical results (season or longer)
        :return: Draw clustering index (0-1 scale)
        """
        if not recent_results:
            return 0.3  # Baseline
        
        # Recent draw rate
        recent_draws = sum(1 for r in recent_results if r == 'D')
        recent_rate = recent_draws / len(recent_results)
        
        # Historical draw rate
        if historical_results and len(historical_results) > 0:
            hist_draws = sum(1 for r in historical_results if r == 'D')
            hist_rate = hist_draws / len(historical_results)
        else:
            hist_rate = 0.25  # League average
        
        # Combine with weighting
        clustering_index = (
            recent_rate * self.recent_weight +
            hist_rate * self.historical_weight
        )
        
        # Boost for consecutive draws (clustering effect)
        consecutive_draws = 0
        for r in recent_results[::-1]:  # Reverse to check most recent first
            if r == 'D':
                consecutive_draws += 1
            else:
                break
        
        clustering_boost = min(0.15, consecutive_draws * 0.05)
        
        return min(1.0, clustering_index + clustering_boost)


class DefensiveSuperiorityMultiplier:
    """
    Calculates defensive superiority between teams.
    High values indicate strong defensive matchup (low scoring expected).
    """
    
    def __init__(self):
        self.xg_against_weight = 0.5
        self.clean_sheets_weight = 0.3
        self.defensive_actions_weight = 0.2
    
    def calculate(self, team_defensive_data, opponent_offensive_data):
        """
        Calculate Defensive Superiority Multiplier.
        
        :param team_defensive_data: Dict with keys:
            - xG_against_per_game (float): Average xG conceded
            - clean_sheet_rate (float): 0-1 scale
            - defensive_actions_per_game (int): Tackles + interceptions + blocks
        :param opponent_offensive_data: Dict with keys:
            - xG_per_game (float): Average xG created
            - shot_accuracy (float): 0-1 scale
            - conversion_rate (float): Goals per xG
        :return: Superiority multiplier (0-2 scale, 1 = neutral)
        """
        if not team_defensive_data or not opponent_offensive_data:
            return 1.0
        
        # Component 1: xG resistance
        team_xg_against = team_defensive_data.get('xG_against_per_game', 1.5)
        opponent_xg = opponent_offensive_data.get('xG_per_game', 1.5)
        xg_superiority = max(0, 2 - (team_xg_against / (opponent_xg + 0.1)))
        xg_superiority = min(2.0, xg_superiority)
        
        # Component 2: Clean sheet strength
        clean_sheet_rate = team_defensive_data.get('clean_sheet_rate', 0.3)
        cs_component = clean_sheet_rate * 2  # Scale to 0-2
        
        # Component 3: Defensive action intensity
        defensive_actions = team_defensive_data.get('defensive_actions_per_game', 30)
        action_component = min(2.0, defensive_actions / 30)
        
        # Weighted combination
        superiority = (
            xg_superiority * self.xg_against_weight +
            cs_component * self.clean_sheets_weight +
            action_component * self.defensive_actions_weight
        )
        
        return max(0.5, min(2.0, superiority))


class FormTrendMomentum:
    """
    Analyzes form trend and momentum (improving vs declining).
    """
    
    def __init__(self):
        pass
    
    def calculate(self, recent_results, recent_xg_data=None):
        """
        Calculate Form Trend Momentum.
        
        :param recent_results: List of recent results ['W', 'W', 'D', 'L', 'W']
                              (ordered from oldest to newest)
        :param recent_xg_data: Optional list of xG performance values
        :return: Dict with momentum score and trend direction
        """
        if not recent_results or len(recent_results) < 3:
            return {'momentum': 0.0, 'trend': 'neutral'}
        
        # Convert results to points
        points_map = {'W': 3, 'D': 1, 'L': 0}
        points = [points_map[r] for r in recent_results]
        
        # Calculate weighted moving average (recent games weighted more)
        weights = np.linspace(0.5, 1.5, len(points))
        weighted_avg = np.average(points, weights=weights)
        
        # Calculate trend (compare first half to second half)
        mid = len(points) // 2
        first_half_avg = np.mean(points[:mid])
        second_half_avg = np.mean(points[mid:])
        trend_delta = second_half_avg - first_half_avg
        
        # Determine trend direction
        if trend_delta > 0.5:
            trend = 'improving'
        elif trend_delta < -0.5:
            trend = 'declining'
        else:
            trend = 'stable'
        
        # Momentum score (-1 to +1, where +1 = strong positive momentum)
        momentum = trend_delta / 3.0  # Normalize by max possible change
        momentum = max(-1.0, min(1.0, momentum))
        
        # Adjust for xG data if provided
        if recent_xg_data and len(recent_xg_data) >= 3:
            xg_trend = np.polyfit(range(len(recent_xg_data)), recent_xg_data, 1)[0]
            momentum = (momentum * 0.7 + xg_trend * 0.3)
        
        return {
            'momentum': momentum,
            'trend': trend,
            'weighted_form': weighted_avg / 3.0  # Normalize to 0-1
        }


class HomeAdvantageContext:
    """
    Context-aware home advantage calculation.
    Considers stadium capacity, recent home form, and league context.
    """
    
    def __init__(self):
        self.base_home_advantage = 0.15
        self.max_home_advantage = 0.35
        self.min_home_advantage = 0.05
    
    def calculate(self, context_data):
        """
        Calculate context-aware home advantage.
        
        :param context_data: Dict with keys:
            - home_form (list): Recent home results ['W', 'W', 'D']
            - stadium_capacity (int): Stadium size
            - attendance_pct (float): 0-1 scale
            - league_tier (int): 1 = top league, 2 = second tier, etc.
            - derby_match (bool): Is this a local derby?
        :return: Home advantage multiplier (0.05-0.35 scale)
        """
        if not context_data:
            return self.base_home_advantage
        
        advantage = self.base_home_advantage
        
        # Factor 1: Home form
        home_form = context_data.get('home_form', [])
        if home_form:
            wins = sum(1 for r in home_form if r == 'W')
            form_rate = wins / len(home_form)
            form_boost = (form_rate - 0.4) * 0.15  # Above 40% win rate boosts advantage
            advantage += form_boost
        
        # Factor 2: Attendance impact
        attendance_pct = context_data.get('attendance_pct', 0.7)
        attendance_boost = (attendance_pct - 0.5) * 0.10  # Higher attendance = more advantage
        advantage += attendance_boost
        
        # Factor 3: Derby boost
        if context_data.get('derby_match', False):
            advantage += 0.05
        
        # Factor 4: League tier (lower tiers = stronger home advantage)
        league_tier = context_data.get('league_tier', 1)
        tier_boost = max(0, (league_tier - 1) * 0.03)  # +3% per tier below top
        advantage += tier_boost
        
        # Clamp to reasonable range
        advantage = max(self.min_home_advantage, min(self.max_home_advantage, advantage))
        
        return advantage


# Example usage and testing
if __name__ == '__main__':
    print("="*60)
    print("ADVANCED METRICS ENHANCED - Module Test")
    print("="*60)
    
    # Test DrawClusteringIndex
    print("\n1. Draw Clustering Index Test:")
    dci = DrawClusteringIndex()
    recent = ['D', 'D', 'W', 'D', 'L']
    historical = ['W', 'D', 'L', 'D', 'W', 'D', 'D', 'L', 'W', 'D']
    index = dci.calculate(recent, historical)
    print(f"   Recent: {recent}")
    print(f"   Draw Clustering Index: {index:.3f}")
    
    # Test DefensiveSuperiorityMultiplier
    print("\n2. Defensive Superiority Multiplier Test:")
    dsm = DefensiveSuperiorityMultiplier()
    defensive = {
        'xG_against_per_game': 1.2,
        'clean_sheet_rate': 0.45,
        'defensive_actions_per_game': 35
    }
    offensive = {
        'xG_per_game': 1.8,
        'shot_accuracy': 0.35,
        'conversion_rate': 0.12
    }
    superiority = dsm.calculate(defensive, offensive)
    print(f"   Defensive Superiority: {superiority:.3f}")
    
    # Test FormTrendMomentum
    print("\n3. Form Trend Momentum Test:")
    ftm = FormTrendMomentum()
    results = ['L', 'L', 'D', 'W', 'W', 'W']
    momentum_data = ftm.calculate(results)
    print(f"   Results: {results}")
    print(f"   Momentum: {momentum_data}")
    
    # Test HomeAdvantageContext
    print("\n4. Home Advantage Context Test:")
    hac = HomeAdvantageContext()
    context = {
        'home_form': ['W', 'W', 'D', 'W', 'L'],
        'stadium_capacity': 50000,
        'attendance_pct': 0.85,
        'league_tier': 1,
        'derby_match': True
    }
    home_adv = hac.calculate(context)
    print(f"   Context: Derby match with 85% attendance")
    print(f"   Home Advantage: {home_adv:.3f}")
    
    print("\n" + "="*60)
