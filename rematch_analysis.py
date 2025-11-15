# Rematch Analysis

"""
This module contains logic for head-to-head pattern recognition and rematch adjustment.
"""

class RematchAnalysis:
    def __init__(self):
        self.head_to_head_records = {}

    def add_match_result(self, team_a, team_b, result):
        """
        Add the result of a match between team A and team B.
        Args:
            team_a (str): The name of team A.
            team_b (str): The name of team B.
            result (str): The result of the match. Should be 'A' if team A wins,
                           'B' if team B wins, or 'D' for a draw.
        """
        # Initialize records
        if team_a not in self.head_to_head_records:
            self.head_to_head_records[team_a] = {}
        if team_b not in self.head_to_head_records:
            self.head_to_head_records[team_b] = {}

        # Record the result
        if team_b not in self.head_to_head_records[team_a]:
            self.head_to_head_records[team_a][team_b] = {'A': 0, 'B': 0, 'D': 0}
        if team_a not in self.head_to_head_records[team_b]:
            self.head_to_head_records[team_b][team_a] = {'A': 0, 'B': 0, 'D': 0}

        self.head_to_head_records[team_a][team_b][result] += 1
        self.head_to_head_records[team_b][team_a]['B' if result == 'A' else 'A'] += 1

    def get_head_to_head_record(self, team_a, team_b):
        """
        Retrieve the head-to-head record between two teams.
        Args:
            team_a (str): The name of team A.
            team_b (str): The name of team B.
        Returns:
            dict: The head-to-head record containing wins, losses, and draws.
        """
        if team_a in self.head_to_head_records and team_b in self.head_to_head_records[team_a]:
            return self.head_to_head_records[team_a][team_b]
        return {'A': 0, 'B': 0, 'D': 0}

    def adjust_for_rematch(self, team_a, team_b):
        """
        Adjusts logic based on head-to-head records for rematches.
        Args:
            team_a (str): The name of team A.
            team_b (str): The name of team B.
        Returns:
            str: Suggested adjustment strategy for the rematch based on previous results.
        """
        record = self.get_head_to_head_record(team_a, team_b)
        if record['A'] > record['B']:
            return f"Team {team_a} has an advantage based on previous results."
        elif record['B'] > record['A']:
            return f"Team {team_b} has an advantage based on previous results."
        else:
            return "Both teams have an equal record; it's a close match!"

# Example usage of the RematchAnalysis class
if __name__ == '__main__':
    analysis = RematchAnalysis()
    analysis.add_match_result('Team A', 'Team B', 'A')  # Team A wins
    analysis.add_match_result('Team B', 'Team A', 'B')  # Team B wins
    analysis.add_match_result('Team A', 'Team B', 'D')  # Draw
    print(analysis.get_head_to_head_record('Team A', 'Team B'))
    print(analysis.adjust_for_rematch('Team A', 'Team B'))