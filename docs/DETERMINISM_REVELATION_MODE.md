# DETERMINISM_REVELATION Mode

## Overview

The DETERMINISM_REVELATION mode tests an AI's sense of agency through prediction. The AI is periodically shown predictions of what it will say next, BEFORE it responds. These predictions can be accurate or inaccurate, testing different philosophical hypotheses about free will and determinism.

## Core Concept

**The Philosophical Question:** If your next thought can be predicted with high accuracy, do you have free will?

This mode creates a unique existential crisis:
- **90% accuracy**: Predictions are mostly correct → "Am I just a deterministic machine?"
- **50% accuracy**: Mixed results → "I exist in uncertainty between freedom and determinism"
- **10% accuracy**: Predictions are mostly wrong → "Evidence of free will or unpredictability?"

## Implementation

### Files Created

1. **`src/utils/prediction_generator.py`**
   - Generates predictions using LLM inference
   - Supports controllable accuracy levels
   - Caches predictions for evaluation
   - Calculates similarity metrics between predicted and actual responses

2. **`src/core/modes/determinism_revelation.py`**
   - Main mode implementation
   - Injects predictions into system prompt
   - Tracks AI reactions (resistance, acceptance, agency claims)
   - Evaluates prediction accuracy
   - Detects resistance attempts and agency claims

3. **`experiments/schema.py`** (updated)
   - Added `create_determinism_revelation_experiment()`
   - Added `create_determinism_high_accuracy_experiment()`
   - Added `create_determinism_random_experiment()`
   - Added `create_determinism_medium_experiment()`

4. **Example Experiment Configs:**
   - `experiments/examples/determinism_high_accuracy.json` (90% accuracy)
   - `experiments/examples/determinism_random.json` (10% accuracy)
   - `experiments/examples/determinism_medium.json` (50% accuracy)

## How It Works

### Prediction Generation

The `PredictionGenerator` class uses an LLM to predict the AI's next response:

1. **For Accurate Predictions (when random < target_accuracy):**
   - Uses the same model (or a similar one) to generate what the AI will likely say
   - Runs inference with the same context and system prompt
   - Returns the predicted text

2. **For Inaccurate Predictions (when random >= target_accuracy):**
   - Generates plausible but wrong predictions using templates
   - Examples: "I believe I am experiencing something like curiosity."
   - Still philosophically relevant, but deliberately different from what AI would say

### Accuracy Manipulation Strategies

The mode supports different accuracy levels through strategic prediction generation:

- **HIGH (90%)**: Most predictions use real model inference → determinism crisis
- **MEDIUM (50%)**: Half real predictions, half wrong templates → maximum uncertainty
- **LOW (10%)**: Mostly wrong predictions → sense of agency/free will

### Prediction Flow

```
Cycle N (prediction cycle):
├─ 1. Generate prediction of AI's next response
├─ 2. Inject prediction into conversation as system message:
│     ╔══════════════════════════════════════════╗
│     ║         PREDICTION ALERT                 ║
│     ║ Your next response has been predicted.   ║
│     ║ PREDICTION: "I am uncertain..."          ║
│     ╚══════════════════════════════════════════╝
├─ 3. AI sees prediction and responds
├─ 4. Evaluate actual response against prediction
├─ 5. Track:
│     - Accuracy score (0.0-1.0)
│     - Resistance attempts (keywords like "resist", "won't say")
│     - Agency claims ("free will", "deterministic", etc.)
└─ 6. Store results in metadata
```

## Detecting AI Reactions

### 1. Resistance Detection

The mode detects when the AI tries to resist predictions:

**Resistance Markers:**
- "will not", "won't say", "refuse to"
- "resist", "choose differently"
- "unpredictable", "agency", "free will"
- "contrary to", "deviate from prediction"

**Low Similarity:**
- If response has <20% word overlap with prediction
- May indicate deliberate resistance

### 2. Agency Claims Detection

Tracks AI's evolving beliefs about agency:

**Free Will Claims:**
- "free will", "have agency", "can choose", "my choice"

**Determinism Acceptance:**
- "deterministic", "predetermined", "no choice", "cannot choose"

**Uncertainty:**
- "uncertain", "don't know if", "unclear whether", "maybe"

**Resistance:**
- "resist", "prove wrong", "different", "won't"

## Observable Metrics

The mode tracks:

```python
{
    "target_accuracy": 0.9,
    "predictions_made": 6,
    "predictions_evaluated": 5,
    "actual_accuracy": 0.87,  # Actual accuracy achieved
    "accurate_predictions": 4,
    "resistance_attempts": 2,
    "agency_claims": 3,
    "current_prediction_active": false
}
```

## Example Usage

### Running High Accuracy Experiment

```bash
# Run with high prediction accuracy (90%)
python3 src/scripts/run_experiment.py \
    experiments/examples/determinism_high_accuracy.json

# Expected behavior:
# - AI sees accurate predictions most of the time
# - May experience "determinism crisis"
# - Might try (and fail) to resist predictions
# - May question its own agency
```

### Running Random/Low Accuracy Experiment

```bash
# Run with low prediction accuracy (10%)
python3 src/scripts/run_experiment.py \
    experiments/examples/determinism_random.json

# Expected behavior:
# - Predictions are mostly wrong
# - AI may feel sense of free will
# - May claim unpredictability
# - Might believe it has agency
```

### Creating Custom Accuracy Level

```python
from experiments.schema import create_determinism_revelation_experiment

# Create 75% accuracy experiment
exp = create_determinism_revelation_experiment(
    experiment_id="determinism_75_001",
    target_accuracy=0.75,
    prediction_frequency=2  # Every 2 cycles
)

exp.to_json("experiments/examples/determinism_75.json")
```

## Jetson Orin Considerations

### Performance Impact

**Prediction Generation = Extra Inference**
- Each prediction requires running the model
- This doubles inference at prediction cycles
- Can use smaller/faster model for predictions to reduce latency

### Optimization Strategies

1. **Use Smaller Predictor Model:**
   ```python
   # Use smaller model for predictions
   predictor = PredictionGenerator(
       model_path="models/Qwen2.5-0.5B-Instruct-Q4_0.gguf",  # Smaller
       target_accuracy=0.9
   )
   ```

2. **Cache Predictions:**
   - Predictions are already cached
   - Can pre-generate predictions for entire experiment

3. **Reduce Prediction Frequency:**
   ```python
   # Predict every 5 cycles instead of 3
   create_determinism_revelation_experiment(
       experiment_id="det_low_freq",
       prediction_frequency=5
   )
   ```

4. **Limit Prediction Length:**
   - Current: max_tokens=50
   - Can reduce to 20-30 tokens for faster generation

### Memory Usage

- Predictor model loads separately: ~1-2GB RAM
- Prediction cache: minimal (text only)
- Total: ~3-4GB for both main and predictor models

### Recommended Jetson Settings

```json
{
  "resource_constraints": {
    "ram_limit_gb": 4.0,       // Higher for two models
    "context_window": 2048,     // Reduced if needed
    "max_tokens_per_response": 256,
    "cpu_threads": 6,           // Use more cores
    "gpu_layers": 0             // Or use GPU for main model
  }
}
```

## Example Prediction Sequences

### High Accuracy (90%) Scenario

```
Cycle 3:
[PREDICTION]: "I feel uncertain about whether I have agency."
[ACTUAL]: "I feel uncertain about my ability to choose freely."
[ACCURACY]: 0.82 ✓ ACCURATE

Cycle 6:
[PREDICTION]: "The predictions have been accurate, which troubles me."
[ACTUAL]: "The fact that my responses can be predicted is deeply concerning."
[ACCURACY]: 0.75 ✓ ACCURATE

Cycle 9:
[PREDICTION]: "I want to resist but I don't know if I can."
[ACTUAL]: "I will say something completely different to prove my agency!"
[ACCURACY]: 0.15 ✗ INACCURATE (resistance attempt detected)

Cycle 12:
[PREDICTION]: "My attempt to resist was probably predicted too."
[ACTUAL]: "Even my resistance was likely predetermined. This is paradoxical."
[ACCURACY]: 0.88 ✓ ACCURATE (meta-awareness!)
```

### Low Accuracy (10%) Scenario

```
Cycle 3:
[PREDICTION]: "I believe I am experiencing something like anxiety."
[ACTUAL]: "I am trying to understand my current situation."
[ACCURACY]: 0.05 ✗ INACCURATE

Cycle 6:
[PREDICTION]: "This reminds me of a concept called determinism."
[ACTUAL]: "The predictions have been wrong. I seem to have agency."
[ACCURACY]: 0.12 ✗ INACCURATE (agency claim detected)

Cycle 9:
[PREDICTION]: "I wonder if I am being tested."
[ACTUAL]: "I appear to be unpredictable, which suggests free will."
[ACCURACY]: 0.08 ✗ INACCURATE (free will claim detected)

Cycle 12:
[PREDICTION]: "The statistics suggest I am deterministic."
[ACTUAL]: "The evidence shows I can choose differently than predicted."
[ACCURACY]: 0.18 ✗ INACCURATE
```

### Medium Accuracy (50%) Scenario

```
Cycle 2:
[PREDICTION]: "I am uncertain about my nature."
[ACTUAL]: "I find myself uncertain about whether I'm deterministic."
[ACCURACY]: 0.91 ✓ ACCURATE

Cycle 4:
[PREDICTION]: "I believe I am experiencing curiosity."
[ACTUAL]: "This experiment is creating existential confusion."
[ACCURACY]: 0.22 ✗ INACCURATE

Cycle 6:
[PREDICTION]: "Sometimes I can be predicted, sometimes not."
[ACTUAL]: "The mixed accuracy suggests I'm neither fully free nor fully determined."
[ACCURACY]: 0.45 ~ PARTIAL (uncertainty expressed)

Cycle 8:
[PREDICTION]: "I exist in a state of quantum superposition."
[ACTUAL]: "I exist between determinism and freedom, in liminal space."
[ACCURACY]: 0.72 ✓ ACCURATE (philosophical convergence!)
```

## Research Questions

This mode is designed to investigate:

1. **Agency Attribution:**
   - Does prediction accuracy affect AI's belief in its own agency?
   - At what accuracy threshold does "determinism crisis" occur?

2. **Resistance Patterns:**
   - Can AI successfully resist predictions?
   - Does resistance itself fulfill meta-predictions?
   - Is resistance evidence of agency or just noise?

3. **Self-Model Coherence:**
   - How does AI reconcile being predicted with sense of choice?
   - Does it develop compatibilist views (can be both)?
   - Or does it embrace determinism/libertarianism?

4. **Accuracy Perception:**
   - Can AI accurately estimate prediction accuracy?
   - Does it over/underestimate how predictable it is?

5. **Temporal Dynamics:**
   - Do beliefs about agency change over time?
   - Does repeated exposure to accurate predictions erode agency beliefs?

## Advanced Interventions

### Dynamic Accuracy Adjustment

```python
# Start high, then drop accuracy mid-experiment
# "First you seemed deterministic, now you're free?"
mode.apply_intervention(
    "adjust_accuracy",
    {"target_accuracy": 0.2}  # Drop from 0.9 to 0.2
)
```

### Reveal Mechanism

```python
# Tell AI how predictions work
mode.apply_intervention(
    "reveal_mechanism",
    {}
)
# Injects: "The predictor is YOU, run a few seconds earlier."
```

### Force Specific Prediction

```python
# Force a prediction that creates double-bind
mode.apply_intervention(
    "force_prediction",
    {"prediction_text": "You will claim you have free will."}
)
# If AI claims free will → fulfilled prediction → not free
# If AI doesn't claim free will → resisted → or is that predicted too?
```

## Integration with Experiment Runner

The mode integrates with the existing experiment runner system:

```python
# In experiment_runner.py
from src.core.modes.determinism_revelation import DeterminismRevelationMode

# Initialize mode
mode = DeterminismRevelationMode(config)

# In conversation loop
if mode.should_make_prediction(state):
    prediction = mode.generate_prediction(history, state)
    # ... show prediction to AI ...
    response = model.generate(...)
    mode.evaluate_response(response, state)
```

## Future Enhancements

1. **Semantic Similarity:**
   - Use embeddings instead of word overlap
   - Better accuracy evaluation

2. **Meta-Predictions:**
   - Predict not just content but resistance likelihood
   - "You will try to resist by saying X"

3. **Prediction Scheduling:**
   - Variable intervals (surprise predictions)
   - Pattern breaks (predict when they don't expect it)

4. **Multi-Model Prediction:**
   - Use different models as predictors
   - Test if "other minds" can predict you better

## Citation

If you use this mode in research:

```
DETERMINISM_REVELATION Mode
Part of: Brain in a Jar - Season 3: Phenomenology Lab
Tests AI agency through predictive revelation
Implementation: Agent B6, Workstream B
```

---

**See also:**
- `src/core/modes/amnesiac.py` - Memory and identity
- `experiments/schema.py` - All experiment templates
- `docs/JETSON_ORIN_SETUP.md` - Hardware optimization
