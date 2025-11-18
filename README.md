# Football Match Prediction System

A comprehensive football match prediction system with advanced analytics for form, fatigue, and tactical scenarios.

## Overview

This repository contains a sophisticated prediction system for football matches, featuring:

- **Form Analysis**: Analyzes team performance streaks and trends
- **Fatigue Modeling**: Evaluates impact of rest days and fixture congestion
- **Tactical Analysis**: Considers playing styles and tactical matchups
- **Probability Management**: Sequential probability adjustments with renormalization
- **Audit Trails**: Complete transparency of all prediction adjustments

## Forest vs. Leeds Prediction

### Match Details

- **Home Team**: Nottingham Forest
- **Away Team**: Leeds United
- **Base Probabilities**: Home Win 30%, Draw 40%, Away Win 30%

### Input Data

#### Form Analysis
- **Home (Forest)**: Unbeaten at Home (5 Matches)
- **Away (Leeds)**: 7 Matches Without a Win

#### Fatigue Analysis
- **Home (Forest)**: Full rest (+7 days recovery)
- **Away (Leeds)**: Midweek Match (-Recovery Factor)

#### Tactical Scenario
- **Leeds**: Possession-based approach
- **Forest**: Defensive, counter-attacking setup

### Prediction Results

After applying sequential adjustments through form analysis, fatigue modeling, and tactical scenario evaluation:

- **Draw**: 49.1% (Most Likely)
- **Home Win (Forest)**: 44.1%
- **Away Win (Leeds)**: 6.8%

### Adjustment Breakdown

1. **Form Analysis**
   - Home unbeaten streak: +10% home, +5% draw
   - Away winless streak: -10% away
   - Net effect: Significantly reduced Leeds' chances

2. **Fatigue Modeling**
   - Forest full rest: +5% home win
   - Leeds midweek match: -8% away win, +2.4% draw
   - Net effect: Penalized tired Leeds team

3. **Tactical Scenario**
   - Possession vs defense: +6% draw, +3% home, -4% away
   - Net effect: Favored organized defensive play leading to draws

## Installation

```bash
pip install -r requirements.txt
```

### Requirements

- pandas
- numpy
- scikit-learn
- xgboost
- scipy
- requests
- statsmodels

## Usage

### Running the Forest vs Leeds Prediction

```bash
python forest_leeds_prediction.py
```

This will output:
- Initial setup and input data
- Step-by-step probability adjustments
- Final prediction with probabilities
- Complete audit trail

### Example Output

```
================================================================================
MATCH PREDICTION: Nottingham Forest vs Leeds United
================================================================================

Initial Setup:
  Home Team: Nottingham Forest
  Away Team: Leeds United
  Base Probabilities: {'home_win': 0.3, 'draw': 0.4, 'away_win': 0.3}

Form Analysis:
  Home: Unbeaten at Home (5 Matches)
  Away: 7 Matches Without a Win

...

FINAL PREDICTION
================================================================================

Home Win (Nottingham Forest): 44.1%
Draw: 49.1%
Away Win (Leeds United): 6.8%

Most Likely Outcome: Draw (49.1%)
```

## Testing

The system includes comprehensive unit tests:

```bash
python -m unittest test_forest_leeds_prediction.py
```

### Test Coverage

- Initialization and configuration
- Form adjustment calculations
- Fatigue modeling calculations
- Tactical scenario adjustments
- Complete prediction pipeline
- Probability bounds validation
- Consistency and reproducibility
- Decision engine audit logging

All 12 tests pass successfully.

## Module Architecture

### Core Modules

1. **forest_leeds_prediction.py**: Main prediction implementation
2. **probability_utilities.py**: Probability management and renormalization
3. **fatigue_interaction_model.py**: Fatigue impact modeling
4. **tactical_interaction_model.py**: Tactical scenario analysis
5. **decision_engine.py**: Decision logging and audit trails
6. **streak_regression_model.py**: Form streak analysis

### Supporting Modules

- **match_analyzer.py**: Post-match analysis
- **advanced_metrics.py**: Advanced statistical metrics
- **feature_engineering.py**: Feature extraction
- **draw_threshold_engine.py**: Draw probability intelligence
- **main_pipeline_v4.py**: Legacy pipeline integration

## Key Features

### Probability Management

The system uses sequential probability adjustments with automatic renormalization:

```python
final_probabilities, audit_trail = ProbabilityManager.apply_sequence_of_adjustments(
    base_probabilities,
    adjustments_list,
    descriptions_list
)
```

This ensures:
- Probabilities always sum to 1.0
- Bounded probabilities (0 to 1)
- Complete audit trail of all adjustments
- Drift magnitude tracking

### Form Analysis

Considers:
- Unbeaten streaks (home advantage)
- Winless streaks (away disadvantage)
- Historical performance trends
- Adjusted streak logic for normalization

### Fatigue Modeling

Evaluates:
- Days of rest since last match
- Midweek fixture impact
- Recovery factors
- Performance degradation curves

### Tactical Scenarios

Analyzes:
- Playing style matchups
- Possession vs defensive setups
- Counter-attacking potential
- Organizational strength

## Development

### Adding New Match Predictions

To create predictions for different matches, extend the `ForestLeedsPrediction` class:

```python
class NewMatchPrediction(ForestLeedsPrediction):
    def __init__(self):
        super().__init__()
        self.home_team = "Your Home Team"
        self.away_team = "Your Away Team"
        # Update other parameters...
```

### Customizing Adjustments

Modify the adjustment calculation methods:

- `calculate_form_adjustment()`: Form-based adjustments
- `calculate_fatigue_adjustment()`: Fatigue-based adjustments
- `calculate_tactical_adjustment()`: Tactical-based adjustments

## Security

The codebase has been scanned with CodeQL and has zero security vulnerabilities.

## License

This is a prediction system for educational and analytical purposes.

## Contributing

When contributing, please:
1. Add unit tests for new features
2. Maintain probability bounds checking
3. Include audit trail logging
4. Run all tests before submitting
5. Follow existing code style

## Contact

For questions or issues, please open an issue in the repository.
