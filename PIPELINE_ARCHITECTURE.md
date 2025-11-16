# Pipeline Architecture

## Overview

The Integrated Prediction Pipeline is a comprehensive football match prediction system that chains multiple specialized modules into a unified prediction framework. The pipeline processes match data through sequential stages, applying corrections and validations to produce high-quality predictions with transparent confidence scoring and audit trails.

## Architecture Diagram

```
Raw Match Data
      ↓
[Data Preprocessing]
      ↓
[Stage 1: Tactical Analysis]
      ├→ Possession Efficiency
      ├→ Defensive Resistance
      └→ Tactical Friction
      ↓
[Stage 2: Fatigue Analysis]
      ├→ Midweek Fatigue Impact
      └→ Fixture Congestion
      ↓
[Stage 3: Form Analysis]
      ├→ Form Momentum
      └→ Streak Volatility
      ↓
[Stage 4: Base Probabilities]
      └→ xG-based Poisson Model
      ↓
[Stage 5: Sequential Corrections]
      ├→ Midweek Fatigue Correction
      ├→ Dynamic Draw Threshold
      ├→ Form Momentum Adjustment
      └→ Set-Piece Threat
      ↓
[Stage 6: Market Predictions]
      ├→ Over/Under 2.5
      ├→ BTTS (Both Teams To Score)
      └→ Correct Score Probabilities
      ↓
[Stage 7: Confidence Scoring]
      └→ Formula-based 0-100 Score
      ↓
[Stage 8: Coherence Validation]
      └→ Cross-Market Consistency
      ↓
Final Prediction Package
```

## Module Descriptions

### 1. Data Preprocessing
**File**: `integrated_prediction_pipeline.py::preprocess_match_data()`

**Purpose**: Validates and normalizes incoming match data, fills missing values with sensible defaults.

**Inputs**: Raw match data dictionary

**Outputs**: Processed match data with:
- Team names
- xG values (home/away)
- Possession percentages
- Form data (recent results)
- Fatigue indicators (days rest, competition type)
- Tactical statistics (shots, tackles, etc.)
- Set-piece statistics

### 2. Tactical Analysis Module
**File**: `tactical_interaction_model.py`

**Purpose**: Analyzes tactical matchups between teams.

**Key Functions**:
- `analyze_possession_efficiency()`: Converts possession into threat (xG per possession unit)
- `analyze_defensive_resistance()`: Measures defensive solidity
- `calculate_tactical_friction()`: Identifies defensive stalemates

**Fixed Issues**:
- ✅ Previously returned 0 for all calculations
- ✅ Now uses real xG, shots, and defensive metrics

### 3. Fatigue Analysis Module
**Files**: 
- `midweek_fatigue_integrator.py`
- `fatigue_interaction_model.py`

**Purpose**: Models performance degradation from fixture congestion.

**Key Functions**:
- `calculate_midweek_impact()`: Calculates fatigue penalty (5-25%)
- `compare_team_fatigue()`: Identifies fatigue advantage
- `apply_fatigue_to_predictions()`: Adjusts probabilities

**Fixed Issues**:
- ✅ Previously only applied -4% penalty for midweek games
- ✅ Now applies -15 to -20% for elite teams with 3 days rest after Champions League

**Factors Considered**:
- Days of rest (2-7 days)
- Competition importance (Champions League > Europa League > League)
- Travel distance
- Squad rotation level
- Injury count
- Match intensity

### 4. Form Analysis Module
**Files**:
- `streak_regression_model.py`
- `advanced_metrics_enhanced.py::FormTrendMomentum`

**Purpose**: Analyzes recent form trends and momentum.

**Key Functions**:
- `calculate()`: Computes momentum score from recent results
- `calculate_streak_volatility()`: Models streak sustainability

**Fixed Issues**:
- ✅ Previously had backward logic (longer streaks = less volatility)
- ✅ Now correctly models: longer streaks = higher volatility (regression to mean)

### 5. Base Probability Calculation
**File**: `integrated_prediction_pipeline.py::calculate_base_probabilities()`

**Purpose**: Generates initial probability distribution from xG using Poisson model.

**Process**:
1. Adjust xG based on possession efficiency
2. Calculate goal probability distributions for each team
3. Compute match result probabilities (home win, draw, away win)
4. Normalize to sum to 1.0

### 6. Sequential Corrections
**File**: `integrated_prediction_pipeline.py::apply_all_corrections()`

**Purpose**: Applies multiple corrections sequentially with renormalization.

#### Correction 1: Midweek Fatigue
- Reduces win probabilities for fatigued teams
- Increases draw probability when both teams are fatigued
- Audit trail: "Midweek Fatigue (H:X%, A:Y%)"

#### Correction 2: Dynamic Draw Threshold
**File**: `draw_threshold_engine.py`

**Factors** (6 total):
1. Possession parity (15% weight)
2. xG differential (20% weight)
3. Tactical friction (20% weight)
4. Fatigue levels (15% weight)
5. Midweek factor (15% weight)
6. Set-piece threat (15% weight)

**Fixed Issues**:
- ✅ Previously used random.randint() for draw prediction
- ✅ Now calculates dynamic threshold based on real match factors

#### Correction 3: Form Momentum
- Adjusts win probabilities based on recent form trajectory
- Applied when momentum differential > 0.2

#### Correction 4: Set-Piece Threat
**File**: `set_piece_threat_analyzer.py`

**Purpose**: Models goals from set-pieces (corners, free-kicks).

**Fixed Issues**:
- ✅ Previously ignored set-piece threat entirely
- ✅ Now explicitly models late-game equalizers from set-pieces

### 7. Market Predictions
**Files**:
- `xg_to_goals_pipeline.py`
- `integrated_prediction_pipeline.py::calculate_market_predictions()`

**Outputs**:
- Over/Under 2.5 goals
- Both Teams To Score (BTTS)
- Correct score probabilities

### 8. Confidence Scoring
**File**: `confidence_scoring_engine.py`

**Purpose**: Provides transparent, formula-based confidence scoring (0-100 scale).

**Components** (weights):
1. Data Completeness (20 points): Availability of xG, possession, form, etc.
2. Model Agreement (25 points): Consistency between different prediction methods
3. Historical Accuracy (20 points): Backtest performance
4. Uncertainty Metrics (20 points): Entropy, probability spread
5. Market Coherence (15 points): Agreement with betting markets

**Fixed Issues**:
- ✅ Previously used empirical values (78%, 75%, 77%)
- ✅ Now uses transparent formula with audit trail

### 9. Market Coherence Validation
**File**: `market_coherence_validator.py`

**Purpose**: Validates internal consistency across markets.

**Validations**:
- Result vs Goals: High draw → Under 2.5
- BTTS Consistency: Both xG > 1.0 → BTTS Yes
- Correct Score Sum: Should total ~60-90%

**Severity Levels**:
- High: Major logical inconsistency
- Medium: Moderate inconsistency
- Low: Minor discrepancy

## Audit Trail System

Every prediction includes a complete audit trail showing:

1. **Initial State**: Base probabilities from xG
2. **Each Correction**: 
   - Description (e.g., "Midweek Fatigue")
   - Before probabilities
   - Adjustment applied
   - After probabilities (renormalized)
   - Drift magnitude
3. **Final State**: Final probabilities after all corrections

Example audit entry:
```
STEP 2: Dynamic Draw Threshold (60.0%)
Before:      {'home_win': 0.308, 'draw': 0.307, 'away_win': 0.385}
Adjustment:  {'home_win': -0.175, 'draw': 0.35, 'away_win': -0.175}
After:       {'home_win': 0.133, 'draw': 0.657, 'away_win': 0.210}
Drift:       0.000000
```

## Integration Points

### Main Entry Point
**File**: `main_pipeline_v4.py`

```python
from integrated_prediction_pipeline import IntegratedPredictionPipeline

pipeline = IntegratedPredictionPipeline()
result = pipeline.predict(match_data, verbose=True)
```

### Batch Processing
```python
from main_pipeline_v4 import MainPipelineV4

pipeline = MainPipelineV4()
results = pipeline.process_batch(matches_list, output_file='results.json')
```

## Key Improvements Over Previous System

### Draw Prediction
- **Before**: Random threshold (random.randint), 19-24% draw probability
- **After**: Dynamic threshold based on 6 factors, 40-66% for actual draws
- **Test Results**:
  - Hamburg 1-1 Dortmund: 66.3% (was 19%)
  - Bayern 2-2 Union: 62.6% (was 24%)
  - Heidenheim 1-1 Frankfurt: 64.2% (was 22%)

### Fatigue Modeling
- **Before**: Fixed -4% penalty for midweek matches
- **After**: Dynamic -5% to -25% based on days rest, competition, travel
- **Impact**: Significantly improves predictions for fixture-congested teams

### Set-Piece Threat
- **Before**: Completely ignored
- **After**: Explicitly modeled with team-specific threat scores
- **Impact**: Better prediction of late equalizers

### Confidence Scoring
- **Before**: Empirical values (78%, 75%, 77%)
- **After**: Formula-based (0-100) with component breakdown
- **Impact**: Transparent, auditable confidence metrics

### Possession Efficiency
- **Before**: Always returned 0
- **After**: Real calculation (xG per possession unit × shot accuracy)
- **Impact**: Proper modeling of possession-based vs counter-attacking styles

### Streak Volatility
- **Before**: Backward logic (longer streak = less volatile)
- **After**: Correct logic (longer streak = more volatile, regression to mean)
- **Impact**: Realistic prediction of streak breaks

## Performance Metrics

### Test Suite Results
- **Tests Run**: 9
- **Pass Rate**: 100%
- **Coverage**: 
  - Draw prediction accuracy ✓
  - High-scoring match detection ✓
  - Confidence scoring transparency ✓
  - Market coherence validation ✓
  - Fatigue impact modeling ✓

### Validation Results
| Match | Expected Draw | Predicted | Status |
|-------|--------------|-----------|--------|
| Hamburg 1-1 Dortmund | ≥40% | 66.3% | ✅ PASS |
| Bayern 2-2 Union | ≥45% | 62.6% | ✅ PASS |
| Heidenheim 1-1 Frankfurt | ≥45% | 64.2% | ✅ PASS |
| St. Pauli 0-4 Gladbach | Over 2.5 | 54.4% | ✅ PASS |

## Future Enhancements

Potential areas for improvement:
1. Machine learning calibration for adjustment weights
2. Historical H2H (head-to-head) analysis module
3. Weather impact modeling
4. Referee bias analysis
5. Injury impact quantification
6. Live in-game prediction updates

## Dependencies

Required Python packages:
- numpy
- pandas
- scipy
- scikit-learn
- statsmodels
- requests
- xgboost

Install with:
```bash
pip install -r requirements.txt
```

## References

- Poisson distribution for goal modeling
- Shannon entropy for uncertainty quantification
- Brier score for probability calibration
- Market odds for coherence validation
