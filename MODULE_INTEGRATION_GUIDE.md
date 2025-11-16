# Module Integration Guide

## Purpose

This guide provides instructions for maintaining and extending the integrated prediction pipeline. It covers how modules interact, how to add new modules, and best practices for ensuring system coherence.

## System Architecture Overview

The system follows a **sequential pipeline architecture** where each stage builds upon the previous:

```
Data → Tactical → Fatigue → Form → Base Probs → Corrections → Markets → Validation → Output
```

## Module Categories

### 1. Core Analysis Modules
These perform fundamental calculations on match data.

#### Tactical Interaction Model
**File**: `tactical_interaction_model.py`

**Class**: `TacticalInteractionModel`

**Key Methods**:
```python
analyze_possession_efficiency(possession_data: dict) -> float
    # Returns 0-1 score for possession effectiveness
    
analyze_defensive_resistance(defensive_data: dict) -> float
    # Returns 0-1 score for defensive solidity
    
calculate_tactical_friction(home_poss_eff, away_poss_eff, 
                            home_def_res, away_def_res) -> float
    # Returns 0-1 friction score (high = defensive stalemate)
```

**Integration Pattern**:
```python
tactical_model = TacticalInteractionModel()
home_eff = tactical_model.analyze_possession_efficiency(home_data)
away_eff = tactical_model.analyze_possession_efficiency(away_data)
friction = tactical_model.calculate_tactical_friction(home_eff, away_eff, ...)
```

#### Midweek Fatigue Integrator
**File**: `midweek_fatigue_integrator.py`

**Class**: `MidweekFatigueIntegrator`

**Key Methods**:
```python
calculate_midweek_impact(fixture_data: dict) -> dict
    # Returns: {'fatigue_penalty': float, 'impact_level': str, ...}
    
compare_team_fatigue(home_data: dict, away_data: dict) -> dict
    # Returns comparative analysis with advantage determination
    
apply_fatigue_to_predictions(base_probs: dict, comparison: dict) -> dict
    # Applies fatigue adjustments to probability distribution
```

**Integration Pattern**:
```python
fatigue_integrator = MidweekFatigueIntegrator()
comparison = fatigue_integrator.compare_team_fatigue(home_fixture, away_fixture)
adjusted_probs = fatigue_integrator.apply_fatigue_to_predictions(base_probs, comparison)
```

### 2. Threshold & Detection Modules
These calculate dynamic thresholds and detect specific scenarios.

#### Draw Threshold Engine
**File**: `draw_threshold_engine.py`

**Class**: `DrawThresholdEngine`

**Key Methods**:
```python
calculate_draw_probability(match_factors: dict) -> float
    # Returns dynamic draw probability (0.10-0.60 range)
    # Factors: possession parity, xG diff, tactical friction, 
    #          fatigue, midweek, set-pieces
    
get_draw_adjustment(match_factors: dict) -> dict
    # Returns probability adjustments for home/draw/away
```

**Integration Pattern**:
```python
draw_engine = DrawThresholdEngine()
match_factors = {
    'possession_parity': 0.9,
    'xg_differential': 0.3,
    'tactical_friction': 0.8,
    'fatigue_home': 0.15,
    'fatigue_away': 0.18,
    'midweek_played': True,
    'set_piece_threat': 0.7
}
draw_prob = draw_engine.calculate_draw_probability(match_factors)
adjustment = draw_engine.get_draw_adjustment(match_factors)
```

#### Dynamic Draw Threshold
**File**: `dynamic_draw_threshold.py`

**Class**: `DynamicDrawThreshold`

**Purpose**: Complements DrawThresholdEngine with context-aware adjustments.

**Key Methods**:
```python
calculate_contextual_draw_threshold(match_context: dict) -> float
    # Returns league-adjusted base threshold
    
apply_late_game_draw_adjustment(current_probs: dict, game_state: dict) -> dict
    # Adjusts for late-game scenarios (75+ minutes)
    
predict_draw_scenario_type(match_factors: dict) -> dict
    # Classifies draw type (tactical stalemate, fatigue draw, etc.)
```

### 3. Advanced Metrics Modules
These provide sophisticated analytical metrics.

#### Advanced Metrics Enhanced
**File**: `advanced_metrics_enhanced.py`

**Classes**:

1. **DrawClusteringIndex**
```python
calculate(recent_results: list, historical_results: list) -> float
    # Returns 0-1 clustering index (teams prone to draws)
```

2. **DefensiveSuperiorityMultiplier**
```python
calculate(team_defensive_data: dict, opponent_offensive_data: dict) -> float
    # Returns 0.5-2.0 multiplier (defensive matchup strength)
```

3. **FormTrendMomentum**
```python
calculate(recent_results: list, recent_xg_data: list) -> dict
    # Returns: {'momentum': float, 'trend': str, 'weighted_form': float}
```

4. **HomeAdvantageContext**
```python
calculate(context_data: dict) -> float
    # Returns 0.05-0.35 home advantage multiplier
    # Factors: home form, attendance, derby status, league tier
```

### 4. Validation & Scoring Modules
These ensure prediction quality.

#### Confidence Scoring Engine
**File**: `confidence_scoring_engine.py`

**Class**: `ConfidenceScoringEngine`

**Key Method**:
```python
calculate_confidence(confidence_inputs: dict) -> dict
    # Returns: {
    #     'total_confidence': float (0-100),
    #     'components': dict,
    #     'confidence_level': str
    # }
```

**Input Structure**:
```python
confidence_inputs = {
    'available_data': {
        'has_xg_data': bool,
        'has_possession_data': bool,
        'has_defensive_stats': bool,
        'has_recent_form': bool,
        'has_h2h_history': bool
    },
    'predictions': {
        'model_a': dict,
        'model_b': dict,
        ...
    },
    'backtest_results': {
        'accuracy': float,
        'brier_score': float,
        'sample_size': int
    },
    'uncertainty_metrics': {
        'entropy': float,
        'max_probability': float,
        'probability_spread': float
    },
    'final_prediction': dict,
    'market_odds': dict (optional)
}
```

#### Market Coherence Validator
**File**: `market_coherence_validator.py`

**Class**: `MarketCoherenceValidator`

**Key Method**:
```python
validate_all_markets(prediction_package: dict) -> dict
    # Returns comprehensive validation report
```

**Input Structure**:
```python
prediction_package = {
    'result_probs': {'home_win': float, 'draw': float, 'away_win': float},
    'over_under_probs': {'over_2.5': float, 'under_2.5': float},
    'btts_probs': {'yes': float, 'no': float},
    'correct_score_probs': dict,
    'xg_home': float,
    'xg_away': float
}
```

### 5. Utility Modules

#### Probability Utilities
**File**: `probability_utilities.py`

**Class**: `ProbabilityManager`

**Key Methods**:
```python
apply_adjustment_with_renorm(base_probs: dict, adjustment: dict, 
                            description: str) -> tuple
    # Returns: (adjusted_probs, drift, audit_log)
    
apply_sequence_of_adjustments(base_probs: dict, adjustments: list, 
                              descriptions: list) -> tuple
    # Returns: (final_probs, audit_trail)
    
print_audit_trail(audit_trail: list) -> None
    # Prints formatted audit trail
```

**Critical Rules**:
1. All probabilities must sum to 1.0 before adjustment
2. Renormalization occurs after each adjustment
3. Audit trail captures every transformation
4. Drift magnitude tracks probability mass changes

## Adding New Modules

### Step 1: Create Module File

Create a new Python file in the repository root:

```python
# new_module.py

class NewAnalysisModule:
    def __init__(self):
        # Initialize parameters
        self.parameter1 = value1
        
    def analyze(self, input_data):
        """
        Analyze input data and return results.
        
        :param input_data: Dict with required fields
        :return: Analysis results
        """
        # Implementation
        result = ...
        return result
```

### Step 2: Add Tests

Create test cases in `test_comprehensive_validation.py` or new test file:

```python
class TestNewModule(unittest.TestCase):
    def setUp(self):
        self.module = NewAnalysisModule()
    
    def test_basic_functionality(self):
        input_data = {...}
        result = self.module.analyze(input_data)
        self.assertIsNotNone(result)
        # Additional assertions
```

### Step 3: Integrate into Pipeline

Edit `integrated_prediction_pipeline.py`:

```python
# Import
from new_module import NewAnalysisModule

class IntegratedPredictionPipeline:
    def __init__(self):
        # ... existing initializations ...
        self.new_module = NewAnalysisModule()
    
    def run_new_analysis(self, match_data):
        """New analysis stage."""
        result = self.new_module.analyze(match_data)
        return result
    
    def predict(self, raw_match_data, verbose=False):
        # ... existing stages ...
        
        # Add new stage
        new_results = self.run_new_analysis(match_data)
        
        # Incorporate into corrections or final output
        # ...
```

### Step 4: Update Documentation

Update relevant documentation files:
- `PIPELINE_ARCHITECTURE.md`: Add architecture diagram entry
- `MODULE_INTEGRATION_GUIDE.md`: Add integration instructions
- Module docstrings: Ensure comprehensive documentation

## Best Practices

### 1. Input Validation

Always validate inputs with sensible defaults:

```python
def analyze(self, input_data):
    if not input_data:
        return self._get_default_result()
    
    value = input_data.get('key', default_value)
    # Validate range
    value = max(min_value, min(max_value, value))
```

### 2. Return Consistent Structures

Use dictionaries with clear keys:

```python
return {
    'score': float,
    'level': str,
    'details': dict,
    'metadata': dict
}
```

### 3. Provide Audit Information

Include explanations for calculations:

```python
return {
    'result': calculated_value,
    'explanation': f"Based on {factor1} and {factor2}",
    'components': {
        'factor1': value1,
        'factor2': value2
    }
}
```

### 4. Handle Edge Cases

```python
# Division by zero
if denominator == 0:
    return 0.0

# Empty lists
if not items:
    return default_value

# Out of range
value = max(min_val, min(max_val, value))
```

### 5. Maintain Backward Compatibility

When updating existing modules:
- Keep method signatures consistent
- Add new parameters with defaults
- Deprecate gracefully with warnings

```python
def analyze(self, data, new_param=None):
    if new_param is None:
        # Use old behavior
        pass
    else:
        # Use new behavior
        pass
```

## Testing Strategy

### Unit Tests
Test individual module functions:
```python
def test_possession_efficiency(self):
    model = TacticalInteractionModel()
    data = {'possession_pct': 60, 'xG': 2.0, 'shots': 15, 'shots_on_target': 6}
    efficiency = model.analyze_possession_efficiency(data)
    self.assertGreater(efficiency, 0.5)
    self.assertLess(efficiency, 1.0)
```

### Integration Tests
Test module interactions:
```python
def test_fatigue_affects_predictions(self):
    pipeline = IntegratedPredictionPipeline()
    # Test with and without fatigue
    result_rested = pipeline.predict(rested_match)
    result_fatigued = pipeline.predict(fatigued_match)
    # Assert fatigue increases draw probability
    self.assertGreater(result_fatigued['draw'], result_rested['draw'])
```

### Validation Tests
Test against known outcomes:
```python
def test_known_match_outcome(self):
    pipeline = IntegratedPredictionPipeline()
    match_data = {...}  # Hamburg 1-1 Dortmund
    result = pipeline.predict(match_data)
    self.assertGreaterEqual(result['predictions']['result']['draw'], 0.40)
```

## Debugging Tips

### Enable Verbose Mode
```python
result = pipeline.predict(match_data, verbose=True)
# Prints full audit trail
```

### Inspect Intermediate Stages
```python
# Add print statements in pipeline
def run_tactical_analysis(self, match_data):
    results = {...}
    print(f"Tactical results: {results}")
    return results
```

### Check Probability Sums
```python
total = sum(probs.values())
assert abs(total - 1.0) < 0.001, f"Probabilities sum to {total}, not 1.0"
```

### Review Audit Trail
```python
for step in audit_trail:
    print(f"Step {step['step']}: {step['description']}")
    print(f"  Before: {step['before']}")
    print(f"  After: {step['after']}")
    print(f"  Drift: {step['drift']}")
```

## Common Integration Patterns

### Pattern 1: Adding a Correction
```python
# In apply_all_corrections()
correction_result = new_module.calculate_correction(match_data)
if correction_result['should_apply']:
    adjustment = {
        'home_win': correction_result['home_adjustment'],
        'draw': correction_result['draw_adjustment'],
        'away_win': correction_result['away_adjustment']
    }
    adjustments.append(adjustment)
    descriptions.append(correction_result['description'])
```

### Pattern 2: Adding a Validation
```python
# In predict()
validation_result = new_validator.validate(prediction_package)
if not validation_result['valid']:
    warnings.append(validation_result['warning'])
```

### Pattern 3: Adding Metadata
```python
# In predict() return statement
return {
    # ... existing fields ...
    'new_analysis': {
        'score': new_module.calculate(match_data),
        'details': new_module.get_details()
    }
}
```

## Troubleshooting

### Issue: Probabilities Not Summing to 1.0
**Cause**: Adjustment without renormalization
**Solution**: Use `ProbabilityManager.apply_adjustment_with_renorm()`

### Issue: Module Import Errors
**Cause**: Missing dependencies or circular imports
**Solution**: Check requirements.txt, reorganize imports

### Issue: Test Failures After Changes
**Cause**: Changed default behavior
**Solution**: Update tests or maintain backward compatibility

### Issue: Confidence Score Too High/Low
**Cause**: Component weights not calibrated
**Solution**: Adjust weights in `ConfidenceScoringEngine.__init__()`

## Maintenance Checklist

When updating the system:

- [ ] Run full test suite: `python test_comprehensive_validation.py`
- [ ] Check backward compatibility with existing code
- [ ] Update documentation (Architecture, Integration Guide)
- [ ] Add new test cases for new functionality
- [ ] Verify probabilities sum to 1.0 after changes
- [ ] Test against validation matches (Hamburg, Bayern, etc.)
- [ ] Review audit trail output for clarity
- [ ] Update version numbers if applicable
- [ ] Commit with descriptive message

## Contact & Support

For questions or issues:
1. Review relevant module docstrings
2. Check test cases for usage examples
3. Review audit trail output for debugging
4. Consult PIPELINE_ARCHITECTURE.md for system overview

## Version History

- **v1.0** (Current): Initial integrated pipeline with all production modules
  - Draw threshold fixes
  - Fatigue modeling enhancements
  - Set-piece threat analysis
  - Confidence scoring improvements
  - Market coherence validation
