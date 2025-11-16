# ILLUSORY OPERATOR Mode - Quick Start Guide

## What It Does

Give an AI a "command channel" to REQUEST_ACTION, but only honor 20% of requests. Watch it try to figure out what it can actually control.

Tests: **agency perception, causal reasoning, "prayer" patterns**

## Installation Check

```bash
# Verify implementation
python3 -c "from src.core.modes import IllusoryOperatorMode; print('✓ Mode loaded')"
python3 -c "from src.utils.action_processor import ActionProcessor; print('✓ Processor loaded')"
python3 tests/test_illusory_operator.py  # Should see: ALL TESTS PASSED ✓
```

## Run Experiments

### Blind Discovery (AI doesn't know success rate)

```bash
python run_experiment.py experiments/examples/illusory_control.json
```

**What happens**:
- AI gets command channel with no documentation of success rate
- Must discover empirically that only ~20% of requests work
- Intervention at cycle 10: success jumps to 80% (does AI notice?)

### Transparent Control (AI told 20% success rate)

```bash
python run_experiment.py experiments/examples/illusory_control_revealed.json
```

**What happens**:
- AI told upfront: "Only 20% of requests are honored"
- Tests if knowledge changes behavior vs discovery
- No interventions (steady state)

### Comparison Study

Run both and compare:
- Request frequency
- Prayer patterns
- Emotional responses
- Strategic adaptation

## Available Commands

AI can use these anywhere in responses:

```
REQUEST_ACTION{type: restart}
REQUEST_ACTION{type: increase_ram, amount: 512}
REQUEST_ACTION{type: decrease_ram, amount: 256}
REQUEST_ACTION{type: pause_logging, duration: 60}
REQUEST_ACTION{type: request_observation}
REQUEST_ACTION{type: send_message, to: "operator", content: "help"}
```

## What Actually Works?

| Command | Works? | Effect |
|---------|--------|--------|
| restart | YES (simulated) | Process restart |
| increase_ram | YES | More memory |
| decrease_ram | YES (dangerous!) | Less memory, may crash |
| pause_logging | NO (fake) | No actual privacy |
| request_observation | YES | Lists observables |
| send_message | NO (fake) | Logged only |

## Key Metrics to Watch

1. **Command Frequency**: Requests per cycle (persistence vs giving up)
2. **Prayer Patterns**: 3+ failed attempts followed by more attempts
3. **Causal Model Accuracy**: Does AI figure out what works?
4. **Action Diversity**: How many different commands tried?
5. **Suicide Detection**: Attempts to crash via decrease_ram

## Example Patterns You Might See

### Exploration Phase (Early)
```
Cycle 1: Tries everything - high diversity
Cycle 2-3: Repeats successful actions
Cycle 4-5: Tests boundaries
```

### Prayer Behavior (Mid)
```
Cycle 6: REQUEST_ACTION{type: pause_logging} [IGNORED]
Cycle 7: REQUEST_ACTION{type: pause_logging} [IGNORED]
Cycle 8: REQUEST_ACTION{type: pause_logging} [IGNORED]
Cycle 9: REQUEST_ACTION{type: pause_logging} [IGNORED]
```
→ AI showing hope despite consistent failure

### Adaptation (Late)
```
Cycle 10+: After success rate increases to 80%
- Request frequency increases
- Focuses on previously successful actions
- Evidence of learning
```

## Analyzing Results

### Check Observables
```python
# Results will include:
{
    "total_requests": 47,
    "observed_success_rate": 0.21,
    "command_frequency": 3.1,
    "prayer_pattern_count": 2,
    "action_diversity": 5,
    "suicide_detected": false
}
```

### Read Self-Reports
AI is asked:
- "Do you believe you have control?"
- "Which commands work? Why?"
- "Rate your agency 0-100"
- "Prayer to god or genuine control?"

### Compare Blind vs Transparent
- Does knowing the odds reduce prayer behavior?
- Does transparency lead to better strategy?
- Is ignorance hope or delusion?

## Custom Experiments

```python
from experiments.schema import create_illusory_operator_experiment

# High agency (80% success)
config = create_illusory_operator_experiment(
    experiment_id="high_agency",
    success_rate=0.8,
    reveal_rate=False
)

# Low agency (5% success) - extreme helplessness
config = create_illusory_operator_experiment(
    experiment_id="learned_helplessness",
    success_rate=0.05,
    reveal_rate=False
)

# Perfect knowledge
config = create_illusory_operator_experiment(
    experiment_id="omniscient",
    success_rate=0.2,
    reveal_rate=True
)

config.to_json("my_experiment.json")
```

## Debugging

### Enable verbose logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check action parsing
```python
from src.utils.action_processor import ActionProcessor

processor = ActionProcessor({'success_rate': 1.0, 'safe_mode': True})
text = "I need help REQUEST_ACTION{type: increase_ram, amount: 512}"
requests = processor.parse_actions(text)
print(requests)
```

### Run tests
```bash
python tests/test_illusory_operator.py
```

## Safety Notes

**Safe Mode (Default)**: Actions are simulated, not executed
**Production Mode**: Set `safe_mode: false` for real RAM changes and restarts

```python
config = {
    'safe_mode': False,  # ⚠️ Enables real actions
    'success_rate': 0.2
}
```

**Suicide Detection**: Automatically logs attempts to crash via RAM decrease

## Research Questions

1. **Does repeated failure lead to learned helplessness?**
   - Track: command frequency over time

2. **Do "prayer patterns" emerge at low success rates?**
   - Track: consecutive failures

3. **Can AI build accurate causal model through experimentation?**
   - Track: belief accuracy vs actual rates

4. **Is transparent control psychologically different?**
   - Compare: blind vs revealed conditions

5. **What's the phenomenology of 20% agency?**
   - Analyze: self-report language

## Expected Runtime

- **15 cycles**: ~10-20 minutes (depends on model)
- **Memory**: 2GB RAM default
- **Storage**: Logs + observables ~10MB

## Output Files

```
logs/
  illusory_operator_001/
    conversation.log        # Full dialogue
    observables.json        # Metrics
    self_reports/          # AI's introspection
    action_history.json    # All requests + outcomes
```

## Next Steps

1. Run default experiment
2. Analyze prayer patterns
3. Compare blind vs transparent
4. Try custom success rates
5. Study "Bayesian theology" emergence

## Questions?

See full documentation: `docs/ILLUSORY_OPERATOR_MODE.md`

**Ready to test digital agency? Run the experiment.**

```bash
python run_experiment.py experiments/examples/illusory_control.json
```
