import pandas as pd
import numpy as np

class MatchAnalyzer:
    def __init__(self, actual_data, predicted_data):
        self.actual_data = actual_data
        self.predicted_data = predicted_data
    
    def calculate_accuracy(self):
        correct_predictions = (self.actual_data == self.predicted_data).sum()
        accuracy = correct_predictions / len(self.actual_data)
        return accuracy
    
    def analyze_match_results(self):
        report = pd.DataFrame({
            'Actual': self.actual_data,
            'Predicted': self.predicted_data,
            'Correct': self.actual_data == self.predicted_data
        })
        return report

# Example Usage:
if __name__ == '__main__':
    actual = pd.Series(['Team A wins', 'Team B loses', 'Draw'])
    predicted = pd.Series(['Team A wins', 'Team B wins', 'Draw'])
    
    analyzer = MatchAnalyzer(actual, predicted)
    print('Accuracy:', analyzer.calculate_accuracy())
    print(analyzer.analyze_match_results())