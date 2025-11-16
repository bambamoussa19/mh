# Intelligent Prediction Module

## Overview

The Intelligent Prediction Module is a comprehensive multi-market prediction system that evaluates all available markets and generates the best predictions across multiple markets based on key probabilities and confidence ratings.

## Features

### Core Capabilities

1. **Multi-Market Analysis**
   - Match Result predictions (Home Win, Draw, Away Win)
   - Goals Market predictions (BTTS, Over/Under 1.5, 2.5, 3.5)
   - Correct Score predictions (multiple scorelines)

2. **Integrated Insights**
   - Fatigue Impact Analysis
   - Tactical Interaction Analysis
   - Draw Threshold Calculation
   - Streak Regression Analysis

3. **Confidence Ranking**
   - Systematic ranking of predictions across all markets
   - Confidence scores (0-100) for each prediction
   - Market-specific confidence adjustments

4. **Modular Queries**
   - Query all markets at once
   - Query specific markets (e.g., only goals)
   - Flexible top-N prediction selection

5. **Real-Time Optimization**
   - Efficient computation for live predictions
   - Sequential probability adjustments with audit trails
   - Normalized probability distributions

## Installation

Ensure you have the required dependencies:

```bash
pip install -r requirements.txt
```

Required packages:
- pandas
- numpy
- scikit-learn
- scipy
- statsmodels

## Quick Start

### Basic Usage

```python
from intelligent_prediction_module import IntelligentPredictionModule, rank_predictions

# Initialize the predictor
predictor = IntelligentPredictionModule()

# Generate predictions
predictions = predictor.generate_predictions(
    base_home_win=0.45,
    base_draw=0.30,
    base_away_win=0.25,
    fatigue_home=3,
    fatigue_away=5,
    tactical_data={'formation': '4-4-2', 'style': 'possession'},
    home_streak=4,
    away_streak=1,
    draw_threshold=35
)

# Rank predictions by confidence
top_predictions = rank_predictions(predictions, top_n=10)

# Display results
for market, outcome, prob, conf in top_predictions:
    print(f"{market}: {outcome} - {prob:.2%} (Confidence: {conf:.1f})")
```

### Query Specific Markets

```python
# Only goals market
goals_predictions = predictor.generate_predictions(
    base_home_win=0.45,
    base_draw=0.30,
    base_away_win=0.25,
    markets=['goals']
)

# Multiple specific markets
match_and_goals = predictor.generate_predictions(
    base_home_win=0.45,
    base_draw=0.30,
    base_away_win=0.25,
    markets=['match_result', 'goals']
)
```

### Generate Formatted Report

```python
from intelligent_prediction_module import format_predictions_report

predictions = predictor.generate_predictions(
    base_home_win=0.45,
    base_draw=0.30,
    base_away_win=0.25
)

top_predictions = rank_predictions(predictions)
report = format_predictions_report(predictions, top_predictions)
print(report)
```

## API Reference

### IntelligentPredictionModule

#### `__init__()`
Initialize the prediction module with all sub-modules.

#### `generate_predictions(...)`
Generate comprehensive predictions across all markets.

**Parameters:**
- `base_home_win` (float): Base home win probability (0-1)
- `base_draw` (float): Base draw probability (0-1)
- `base_away_win` (float): Base away win probability (0-1)
- `fatigue_home` (int): Home team fatigue level (0-10)
- `fatigue_away` (int): Away team fatigue level (0-10)
- `tactical_data` (dict, optional): Tactical match data
- `home_streak` (int): Home team winning streak
- `away_streak` (int): Away team winning streak
- `draw_threshold` (int): Draw threshold parameter (0-100)
- `markets` (list, optional): Specific markets to evaluate (None = all)

**Returns:**
- Dictionary containing predictions with probabilities and confidence scores

### Helper Functions

#### `rank_predictions(prediction_set, top_n=10)`
Rank predictions across all markets by confidence level.

**Parameters:**
- `prediction_set` (dict): Complete prediction set from generate_predictions()
- `top_n` (int): Number of top predictions to return

**Returns:**
- List of tuples: (market, outcome, probability, confidence)

#### `format_predictions_report(predictions, top_predictions)`
Format predictions into a readable report.

**Parameters:**
- `predictions` (dict): Full prediction set
- `top_predictions` (list): Ranked top predictions

**Returns:**
- Formatted string report

## Integration with Main Pipeline

The module is integrated with the main pipeline in `main_pipeline_v4.py`:

```python
from intelligent_prediction_module import (
    IntelligentPredictionModule,
    rank_predictions,
    format_predictions_report
)

# Use the integrated function
predictions, ranked, report = intelligent_multi_market_prediction(
    base_home_win=0.50,
    base_draw=0.28,
    base_away_win=0.22,
    fatigue_home=2,
    fatigue_away=4,
    tactical_data={'formation': '4-3-3', 'style': 'possession'},
    home_streak=3,
    away_streak=1,
    draw_threshold=32,
    top_n=10
)

print(report)
```

## Understanding the Outputs

### Match Result Probabilities
Shows the probability and confidence for:
- Home Win
- Draw
- Away Win

Example:
```
home_win: 45.90% (Confidence: 38.2)
draw: 34.84% (Confidence: 29.0)
away_win: 19.26% (Confidence: 16.0)
```

### Goals Market Probabilities

**Over/Under Markets:**
- Over/Under 1.5 goals
- Over/Under 2.5 goals
- Over/Under 3.5 goals

**BTTS (Both Teams To Score):**
- Yes
- No

Example:
```
over_2.5: 42.10% (Confidence: 33.3)
under_2.5: 57.90% (Confidence: 47.2)
btts:yes: 40.18% (Confidence: 31.8)
btts:no: 59.82% (Confidence: 49.0)
```

### Correct Score Probabilities
Shows probabilities for likely scorelines:
- Home win scores: 1-0, 2-0, 2-1, 3-0, 3-1, 3-2
- Draw scores: 0-0, 1-1, 2-2, 3-3
- Away win scores: 0-1, 0-2, 1-2, 0-3, 1-3, 2-3

### Confidence Scores

Confidence scores range from 0 to 100 and represent:
- **60-100**: Very high confidence
- **40-60**: High confidence
- **30-40**: Moderate confidence
- **20-30**: Low confidence
- **0-20**: Very low confidence

The confidence calculation considers:
- Base probability
- Market complexity
- Edge over fair odds

## How It Works

### 1. Integration of Insights

The module integrates insights from multiple analysis modules:

**Fatigue Impact:**
- Higher fatigue reduces team performance
- Fatigue difference affects draw probability
- Applied as probability adjustments

**Tactical Interaction:**
- Deep block scenarios favor draws and under goals
- Possession scenarios favor home wins
- Scenario-based probability adjustments

**Draw Threshold:**
- Enhances draw probability based on threshold parameter
- Useful for balanced matches

**Streak Regression:**
- Long winning streaks tend to regress
- Reduces win probability for teams on long streaks
- Increases draw probability proportionally

### 2. Probability Calculation

Base probabilities are adjusted sequentially:
1. Base probabilities normalized to sum to 1.0
2. Apply fatigue adjustments
3. Apply tactical adjustments
4. Apply streak regression
5. Apply draw threshold
6. Renormalize after each adjustment

### 3. Market Evaluation

**Match Result:**
- Direct use of adjusted probabilities

**Goals Market:**
- Derived from match result probabilities
- Adjusted for fatigue (high fatigue = fewer goals)
- Tactical scenarios affect goal likelihood

**Correct Score:**
- Calculated from match result and goals market probabilities
- Considers BTTS and Over/Under outcomes
- Normalized to sum to 1.0

### 4. Confidence Ranking

Confidence scores are calculated based on:
- Probability magnitude (higher probability = higher confidence)
- Market complexity factor
- Edge calculation (boost for probabilities > 0.5)

## Testing

The module includes comprehensive tests in `test_intelligent_prediction_module.py`:

```bash
python -m unittest test_intelligent_prediction_module.py -v
```

Test coverage includes:
- Module initialization
- Individual insight integration functions
- Probability calculations for all markets
- Confidence score calculations
- Prediction ranking
- Report formatting
- Integration scenarios
- Edge cases

All 23 tests pass successfully.

## Examples

### Example 1: High Home Favorite

```python
predictions = predictor.generate_predictions(
    base_home_win=0.65,
    base_draw=0.20,
    base_away_win=0.15,
    fatigue_home=1,
    fatigue_away=6
)
```

Expected: High home win probability, likely under goals due to away fatigue.

### Example 2: Balanced Match

```python
predictions = predictor.generate_predictions(
    base_home_win=0.35,
    base_draw=0.35,
    base_away_win=0.30,
    fatigue_home=3,
    fatigue_away=3
)
```

Expected: Relatively balanced probabilities across outcomes.

### Example 3: Tired Teams

```python
predictions = predictor.generate_predictions(
    base_home_win=0.45,
    base_draw=0.30,
    base_away_win=0.25,
    fatigue_home=8,
    fatigue_away=8
)
```

Expected: Higher under goals probability due to high fatigue.

### Example 4: Long Winning Streak

```python
predictions = predictor.generate_predictions(
    base_home_win=0.55,
    base_draw=0.25,
    base_away_win=0.20,
    home_streak=8
)
```

Expected: Reduced home win probability due to streak regression.

## Performance Considerations

- **Real-Time Ready**: Efficient computation suitable for live predictions
- **Modular Design**: Query only needed markets to reduce computation
- **Cached Results**: Intermediate calculations can be reused
- **Scalability**: Can process multiple matches in parallel

## Troubleshooting

### Common Issues

1. **Probabilities don't sum to 1.0**
   - The module automatically renormalizes after each adjustment
   - Check that base probabilities sum to 1.0

2. **Unexpected confidence scores**
   - Confidence depends on probability and market complexity
   - Lower probabilities naturally have lower confidence

3. **Tactical data not working**
   - Ensure tactical_data is a dictionary
   - Check that scenario detection logic matches your data

## Future Enhancements

Potential areas for enhancement:
- Add more markets (Asian Handicaps, Half Time/Full Time, etc.)
- Include historical performance data
- Machine learning model integration
- Real-time odds comparison
- Backtesting framework
- Performance metrics tracking

## Contributing

When contributing to this module:
1. Maintain the modular design
2. Add tests for new features
3. Update documentation
4. Ensure probability distributions always sum to 1.0
5. Run security checks before committing

## License

This module is part of the mh prediction system.

## Contact

For questions or issues, please refer to the main repository documentation.
