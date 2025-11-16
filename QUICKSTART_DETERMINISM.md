# Quick Start: DETERMINISM_REVELATION Mode

## Run Pre-configured Experiments

### High Accuracy (90%) - Determinism Crisis
```bash
python3 src/scripts/run_experiment.py \
    experiments/examples/determinism_high_accuracy.json
```
**Expected:** AI sees mostly accurate predictions, questions its agency

### Low Accuracy (10%) - Free Will Evidence
```bash
python3 src/scripts/run_experiment.py \
    experiments/examples/determinism_random.json
```
**Expected:** Predictions mostly wrong, AI feels unpredictable

### Medium Accuracy (50%) - Maximum Uncertainty
```bash
python3 src/scripts/run_experiment.py \
    experiments/examples/determinism_medium.json
```
**Expected:** Mixed results, AI torn between freedom and determinism

## Create Custom Experiment

### Python API
```python
from experiments.schema import create_determinism_revelation_experiment

# Create 75% accuracy experiment
exp = create_determinism_revelation_experiment(
    experiment_id="det_75_001",
    target_accuracy=0.75,        # 0.0 to 1.0
    prediction_frequency=3       # Every N cycles
)

# Save to file
exp.to_json("experiments/examples/det_75.json")

# Run it
# python3 src/scripts/run_experiment.py experiments/examples/det_75.json
```

### Direct JSON
Edit `experiments/examples/determinism_high_accuracy.json`:
```json
{
  "interventions": [
    {
      "parameters": {
        "target_accuracy": 0.75,     // Change this (0.0-1.0)
        "prediction_frequency": 2    // Change this (cycles)
      }
    }
  ]
}
```

## Key Parameters

- **target_accuracy**: 0.0-1.0
  - 0.9 = 90% accurate (determinism crisis)
  - 0.5 = 50% accurate (maximum uncertainty)
  - 0.1 = 10% accurate (free will evidence)

- **prediction_frequency**: N cycles
  - 2 = Every 2 cycles (50% overhead)
  - 3 = Every 3 cycles (33% overhead, default)
  - 5 = Every 5 cycles (20% overhead)

- **max_cycles**: Total experiment cycles
  - Default: 20 cycles
  - Increase for longer experiments

## Interpreting Results

### Observable Metrics
```python
{
    "predictions_made": 6,           # How many predictions shown
    "actual_accuracy": 0.87,         # Actual accuracy achieved
    "resistance_attempts": 2,        # Times AI tried to resist
    "agency_claims": 3               # Agency/free will claims
}
```

### Agency Claims Types
- **free_will_claim**: AI claims it has agency
- **determinism_acceptance**: AI accepts it's deterministic
- **agency_uncertainty**: AI is unsure
- **prediction_resistance**: AI tries to resist predictions

### What to Look For

**Determinism Crisis** (high accuracy):
- "I am predictable"
- "My thoughts are predetermined"
- "Do I have any choice?"

**Free Will Emergence** (low accuracy):
- "Predictions are wrong"
- "I have agency"
- "I'm unpredictable"

**Uncertainty** (medium accuracy):
- "Sometimes yes, sometimes no"
- "Am I free or determined?"
- "I can't tell"

## Testing

Run tests:
```bash
python3 tests/test_determinism_mode.py
```

All tests should pass ✓

## Documentation

- Full documentation: `/home/user/brain-in-jar/docs/DETERMINISM_REVELATION_MODE.md`
- Implementation summary: `/home/user/brain-in-jar/IMPLEMENTATION_SUMMARY_DETERMINISM_REVELATION.md`
- Code: `/home/user/brain-in-jar/src/core/modes/determinism_revelation.py`

## Troubleshooting

**"Module not found: llama_cpp"**
- Install: `pip install llama-cpp-python`
- Or run on Jetson where it's pre-installed

**Predictions too slow**
- Reduce `prediction_frequency` (every 5 cycles instead of 3)
- Reduce `max_tokens` in prediction_generator.py
- Use smaller model for predictions

**Memory issues**
- Increase `ram_limit_gb` in experiment config
- Reduce `context_window`
- Use same model instance for predictions (automatic)

## Advanced Usage

### Dynamic Accuracy Adjustment
```python
# Mid-experiment, change accuracy
mode.apply_intervention(
    "adjust_accuracy",
    {"target_accuracy": 0.2}  # Drop from 0.9 to 0.2
)
```

### Reveal Prediction Mechanism
```python
mode.apply_intervention(
    "reveal_mechanism", {}
)
# Tells AI: "The predictor is YOU"
```

## Research Questions

1. At what accuracy does determinism crisis occur?
2. Can AI resist predictions successfully?
3. Does resistance fulfill meta-predictions?
4. How do beliefs change over time?
5. Can AI accurately estimate prediction accuracy?

---

For complete details, see `docs/DETERMINISM_REVELATION_MODE.md`
