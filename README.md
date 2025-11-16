# Match Prediction System - Enhanced

A comprehensive football match prediction system with xG integration, defensive collapse detection, and market coherence validation.

## Overview

This system addresses critical prediction failures by implementing:
- **xG to Goal Probability Conversion**: Accurately converts expected goals data into match outcome probabilities
- **Possession Efficiency Analysis**: Calculates actual conversion of possession into dangerous situations
- **Defensive Collapse Detection**: Identifies panic defense patterns through behavioral statistics
- **Form Streak Volatility Detection**: Distinguishes sustainable trends from variance-driven patterns
- **Transparent Confidence Scoring**: Formula-based confidence metrics (0-100) with full audit trails
- **Market Coherence Validation**: Ensures betting market predictions are logically aligned

## Key Features

### 1. xG to Goals Pipeline (`xg_to_goals_pipeline.py`)
Converts expected goals data into comprehensive probability distributions:
- Match outcome probabilities (home win, draw, away win)
- Over/Under goal lines (0.5, 1.5, 2.5, 3.5, 4.5)
- Both Teams To Score (BTTS) probabilities
- Correct score predictions
- Uses Poisson and Skellam distributions for accurate modeling

**Example:**
```python
from xg_to_goals_pipeline import XGToGoalsPipeline

pipeline = XGToGoalsPipeline()
result = pipeline.full_analysis(xg_home=1.5, xg_away=1.2)
# Returns: {'match_outcomes': {...}, 'over_under': {...}, 'btts': {...}}
```

### 2. Tactical Interaction Model (`tactical_interaction_model.py`)
Analyzes possession efficiency and defensive resistance:
- **Possession Efficiency**: Converts possession % into actual threat creation
  - Shot accuracy component (40%)
  - Pass completion component (30%)
  - Final third penetration component (30%)
- **Defensive Resistance**: Measures defensive effectiveness
  - Shot suppression (40%)
  - Tackle success (30%)
  - Defensive action volume (30%)

**Example:**
```python
from tactical_interaction_model import TacticalInteractionModel

model = TacticalInteractionModel()
possession_data = {
    'possession_pct': 60.0,
    'shots': 15,
    'shots_on_target': 8,
    'passes_completed': 450,
    'passes_attempted': 500,
    'final_third_entries': 30
}
efficiency = model.analyze_possession_efficiency(possession_data)
# Returns: 0.7 (70% efficiency)
```

### 3. Draw Threshold Engine (`draw_threshold_engine.py`)
Predictive draw probability calculation (replaces random number generation):
- Form parity analysis (±15%)
- Strength parity analysis (±12%)
- Defensive solidity bonus (±20%)
- Low scoring tendency adjustment (±10%)
- Head-to-head history (±8%)

**Example:**
```python
from draw_threshold_engine import DrawThresholdEngine

engine = DrawThresholdEngine()
features = {
    'home_form': 0.52,
    'away_form': 0.50,
    'home_strength': 0.51,
    'away_strength': 0.50,
    'home_defensive_rating': 0.75,
    'away_defensive_rating': 0.75,
    'head_to_head_draws': 3,
    'home_goals_avg': 1.2,
    'away_goals_avg': 1.3
}
result = engine.intelligent_draw_decision(features)
# Returns: {'prediction': 'Draw', 'probability': 0.42, 'confidence': 'High'}
```

### 4. Streak Volatility Detector (`streak_regression_model.py`)
Detects volatility in form streaks instead of assuming mean reversion:
- Calculates streak volatility (0-1 scale)
- Detects oscillating patterns (win-loss-win-loss)
- Assesses sustainability based on underlying performance metrics
- Distinguishes lucky wins from sustainable form

**Example:**
```python
from streak_regression_model import StreakVolatilityDetector

detector = StreakVolatilityDetector()
streak_data = {
    'current_streak': 5,
    'recent_results': [1, 1, 1, 1, 1],  # All wins
    'performance_metrics': {
        'xg_trend': 0.2,  # Improving xG
        'shot_quality_trend': 0.15
    }
}
result = detector.detect_streak_sustainability(streak_data)
# Returns: {'sustainability_score': 0.8, 'volatility': 0.15, 'regression_risk': 'Low'}
```

### 5. Defensive Collapse Detector (`defensive_collapse_detector.py`)
Identifies defensive panic patterns:
- **Panic Fouls**: Excessive yellow cards, especially early in match
- **Shot Suppression Failure**: High volume of quality shots allowed
- **Defensive Deterioration**: Worsening metrics over time
- **Blowout Risk Assessment**: Probability of heavy defeat

**Example:**
```python
from defensive_collapse_detector import DefensiveCollapseDetector

detector = DefensiveCollapseDetector()
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
        'xg_allowed': 2.8
    },
    'current_score_deficit': 2
}
result = detector.comprehensive_collapse_assessment(match_data)
# Returns: {'overall_collapse_score': 0.72, 'risk_level': 'Critical', 'blowout_risk': {...}}
```

### 6. Confidence Scoring Engine (`confidence_scoring_engine.py`)
Transparent formula-based confidence scores:
- **Probability Margin** (30%): How clear the favorite is
- **Data Quality** (20%): Completeness of input data
- **Model Agreement** (20%): Different models agreeing
- **Historical Accuracy** (15%): Past performance in similar scenarios
- **Volatility** (15%): Stability of predictions

**Example:**
```python
from confidence_scoring_engine import ConfidenceScoringEngine

engine = ConfidenceScoringEngine()
components = {
    'probabilities': {'home_win': 0.78, 'draw': 0.13, 'away_win': 0.09},
    'data_completeness': {
        'xg_available': True,
        'form_data_available': True,
        'h2h_available': True,
        'injuries_known': False,
        'tactical_data_available': True
    }
}
result = engine.calculate_overall_confidence(components)
# Returns: {'overall_confidence': 82, 'confidence_level': 'High', 'component_scores': {...}}
```

### 7. Market Coherence Validator (`market_coherence_validator.py`)
Validates logical consistency across betting markets:
- Win/Goals coherence (prevents "Home Win 80% + Under 0.5 Goals")
- BTTS/Outcome coherence (ensures BTTS aligns with total goals)
- Correct Score/Outcome coherence (scores must match win probabilities)
- xG/Outcome coherence (predictions must align with xG data)

**Example:**
```python
from market_coherence_validator import MarketCoherenceValidator

validator = MarketCoherenceValidator()
prediction_data = {
    'match_outcomes': {'home_win': 0.80, 'draw': 0.12, 'away_win': 0.08},
    'over_under': {'over_2.5': 0.25, 'under_2.5': 0.75, 'under_1.5': 0.60},
    'xg_values': {'xg_home': 0.5, 'xg_away': 2.5}
}
result = validator.comprehensive_validation(prediction_data)
# Returns: {'overall_coherent': False, 'total_issues': 2, 'validation_passed': False}
```

### 8. Main Pipeline (`main_pipeline_v4.py`)
Orchestrates all modules for comprehensive predictions:

**Example:**
```python
from main_pipeline_v4 import MatchPredictionPipeline

pipeline = MatchPredictionPipeline()

match_data = {
    'xg_home': 1.5,
    'xg_away': 1.2,
    'home_form_results': ['W', 'W', 'D', 'W', 'L'],
    'away_form_results': ['L', 'D', 'W', 'D', 'L'],
    'possession_data': {...},
    'defensive_data': {...}
}

result = pipeline.predict_match(match_data)
# Returns complete analysis with confidence, coherence validation, and recommendations
```

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
python -m unittest discover -s tests -p "test_*.py" -v

# Run main pipeline example
python main_pipeline_v4.py
```

## Requirements

- Python 3.8+
- pandas
- numpy
- scikit-learn
- scipy
- statsmodels
- xgboost
- requests

## Testing

The system includes 52 comprehensive unit tests covering all modules:

```bash
# Run all tests
python -m unittest discover -s tests -p "test_*.py" -v

# Run specific test module
python -m unittest tests.test_xg_to_goals_pipeline -v
```

## Audit Findings Addressed

### 1. Frankfurt vs Heidenheim (Predicted Win 78.2%, Result: Draw 1-1)
**Root Cause**: xG data (0.88 vs 2.32) not converted to probabilities
**Fix**: `xg_to_goals_pipeline.py` now correctly predicts Away Win 68.5% based on higher away xG

### 2. St. Pauli vs Gladbach (Predicted Draw 69.3% + Under 2.5, Result: 0-4)
**Root Causes**:
- Possession efficiency not calculated (52% possession treated uniformly)
- Defensive panic (4 yellows) not detected as blowout indicator
- Form streaks treated as mean reversion instead of volatility detection

**Fixes**:
- `tactical_interaction_model.py` calculates possession efficiency (shot accuracy, pass completion, penetration)
- `defensive_collapse_detector.py` detects panic patterns (excessive cards, shot volume, deterioration)
- `streak_regression_model.py` uses volatility detection to identify unstable vs sustainable form

## Architecture

```
Match Data Input
       ↓
[xG Pipeline] → Convert xG to probabilities
       ↓
[Tactical Analysis] → Calculate possession efficiency & defensive resistance
       ↓
[Draw Engine] → Predictive draw probability (not random)
       ↓
[Streak Detector] → Volatility-based form analysis
       ↓
[Collapse Detector] → Identify defensive panic patterns
       ↓
[Probability Manager] → Adjust and normalize probabilities
       ↓
[Goal Predictor] → Generate all betting markets
       ↓
[Coherence Validator] → Validate logical consistency
       ↓
[Confidence Engine] → Calculate transparent confidence score
       ↓
Final Predictions + Recommendations
```

## Advanced Metrics

The system includes enhanced metrics for deeper analysis:

- **DrawClusteringIndex**: Measures tendency for draws to cluster
- **DefensiveSuperiorityMultiplier**: Amplifies clean sheet probability based on defensive quality gap
- **FormTrendMomentum**: Analyzes form trajectory (improving vs declining)
- **HomeAdvantageContext**: Context-aware home advantage (league tier, derby, relegation battle)

## Contributing

When adding new features:
1. Follow existing module structure
2. Add comprehensive unit tests
3. Update documentation
4. Ensure market coherence validation passes
5. Provide audit trail for probability adjustments

## License

Copyright (c) 2024. All rights reserved.
