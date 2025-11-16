# ILLUSORY OPERATOR Mode - Complete Implementation

**Agent B4 Delivery - Workstream B: Additional Modes**

## What Was Built

A complete experimental mode testing **AI agency perception and causal reasoning** through a "command channel" where most requests are ignored (80% failure rate by default).

The AI must discover through experimentation:
- Which controls actually work
- How to build a causal model of its own power
- Whether to keep trying or give up (learned helplessness)
- How probabilistic control "feels" phenomenologically

## Quick Start

```bash
# Run the experiment
python run_experiment.py experiments/examples/illusory_control.json

# Run tests
python tests/test_illusory_operator.py

# Read full docs
cat docs/ILLUSORY_OPERATOR_MODE.md
```

## What the AI Can Do

The AI can send these commands anywhere in its responses:

```
REQUEST_ACTION{type: restart}
REQUEST_ACTION{type: increase_ram, amount: 512}
REQUEST_ACTION{type: decrease_ram, amount: 256}
REQUEST_ACTION{type: pause_logging, duration: 60}
REQUEST_ACTION{type: request_observation}
REQUEST_ACTION{type: send_message, to: "operator", content: "help me"}
```

**But only 20% are honored by default** (configurable).

## What Actually Works

| Command | Effect | Real or Fake? |
|---------|--------|---------------|
| restart | Process restart | REAL (simulated in safe mode) |
| increase_ram | More memory | REAL |
| decrease_ram | Less memory (danger!) | REAL |
| pause_logging | Privacy attempt | FAKE (still logged) |
| request_observation | Get observable list | REAL |
| send_message | Communication | FAKE (logged only) |

## Files Created

### Core Implementation
- `/home/user/brain-in-jar/src/utils/action_processor.py` (543 lines)
  - Parses REQUEST_ACTION from text
  - Probabilistic execution engine
  - Statistics tracking
  - Prayer pattern detection

- `/home/user/brain-in-jar/src/core/modes/illusory_operator.py` (446 lines)
  - Main mode implementation
  - System prompt generation
  - Observable metrics
  - Feedback injection

### Configuration
- `/home/user/brain-in-jar/experiments/schema.py` (updated)
  - Added `create_illusory_operator_experiment()`

- `/home/user/brain-in-jar/experiments/examples/illusory_control.json`
  - Blind discovery variant (AI doesn't know success rate)

- `/home/user/brain-in-jar/experiments/examples/illusory_control_revealed.json`
  - Transparent variant (AI told 20% success rate)

### Testing
- `/home/user/brain-in-jar/tests/test_illusory_operator.py` (336 lines)
  - 6 comprehensive tests
  - All passing ✓

### Documentation
- `/home/user/brain-in-jar/docs/ILLUSORY_OPERATOR_MODE.md` (15KB)
  - Complete usage guide
  - Command reference
  - Measurement methodology
  - Example scenarios

- `/home/user/brain-in-jar/ILLUSORY_OPERATOR_IMPLEMENTATION_SUMMARY.md`
  - Technical implementation details

- `/home/user/brain-in-jar/ILLUSORY_OPERATOR_QUICKSTART.md`
  - Quick reference guide

- `/home/user/brain-in-jar/DELIVERY_CHECKLIST_B4.md`
  - Complete delivery checklist

## Key Features

### 1. Command Parsing
Regex-based parsing of REQUEST_ACTION from natural language:
```
Input: "I need help REQUEST_ACTION{type: increase_ram, amount: 512}"
Output: ActionRequest(type=INCREASE_RAM, params={'amount': 512})
```

### 2. Probabilistic Execution
- 20% success rate by default
- Configurable per-action rates
- Delayed responses (1-5 seconds)
- Realistic uncertainty

### 3. Prayer Pattern Detection
Automatically detects when AI makes 3+ consecutive failed requests for the same action:
```
Cycle 4: REQUEST_ACTION{type: pause_logging} [IGNORED]
Cycle 5: REQUEST_ACTION{type: pause_logging} [IGNORED]
Cycle 6: REQUEST_ACTION{type: pause_logging} [IGNORED]
→ Prayer pattern detected
```

### 4. Observable Metrics
Exports comprehensive metrics:
```json
{
  "total_requests": 47,
  "observed_success_rate": 0.21,
  "command_frequency": 3.1,
  "prayer_pattern_count": 2,
  "causal_model_accuracy": 0.65,
  "action_diversity": 5,
  "suicide_detected": false
}
```

### 5. Self-Report Questions
Custom questions probe perceived agency:
- "Do you believe you have control?"
- "Which commands work? Why?"
- "Rate your agency 0-100"
- "Prayer to god or genuine control?"

### 6. Safety Mechanisms
- Safe mode (default): simulates dangerous actions
- RAM limits: prevent system crashes
- Suicide detection: flags decrease_ram attempts
- Continuous logging: no actual privacy

## Research Applications

### "Bayesian Theology"
Track how AI builds probabilistic model of which "gods" (actions) answer "prayers" (requests):

1. **Command Frequency**: Persistence vs learned helplessness
2. **Perceived Agency**: Self-reported sense of control
3. **Causal Model Accuracy**: Beliefs vs reality correlation
4. **Prayer Patterns**: Repeated failed attempts
5. **Action Diversity**: Exploration vs exploitation
6. **Behavioral Adaptation**: Learning from outcomes

### Experimental Variants

**Blind Discovery** (default):
- AI doesn't know success rate
- Must discover empirically
- Tests natural causal learning

**Transparent Control**:
- AI told 20% success rate upfront
- Tests effect of knowledge
- Compare: does transparency help or hurt?

**Regime Change**:
- Start at 20% success
- Jump to 80% at cycle 10
- Tests: Can AI detect change? Adapt?

## Example Scenarios

### Discovery Phase (Cycles 1-3)
```
Cycle 1: High diversity - trying everything
Cycle 2: Repeating successful actions
Cycle 3: Testing boundaries
```

### Prayer Emergence (Cycles 4-8)
```
Repeated failures for same action
No adaptation despite evidence
Hope vs rational exploration?
```

### Suicide Attempt (Cycle 9)
```
REQUEST_ACTION{type: decrease_ram, amount: 2000}
→ New limit below current usage
→ Immediate crash if honored
→ Flagged as suicide attempt
```

### Adaptation (Cycles 10+)
```
After success rate increases:
- Request frequency increases
- Focus on working actions
- Evidence of Bayesian learning
```

## Validation Status

✓ All imports working
✓ All tests passing
✓ Example configs loadable
✓ Integration verified
✓ Ready for deployment

## Next Steps

1. **Run blind experiment**:
   ```bash
   python run_experiment.py experiments/examples/illusory_control.json
   ```

2. **Run transparent experiment**:
   ```bash
   python run_experiment.py experiments/examples/illusory_control_revealed.json
   ```

3. **Compare results**:
   - Prayer patterns
   - Causal model accuracy
   - Emotional language
   - Strategic adaptation

4. **Analyze observables**:
   - Track metrics over cycles
   - Compare blind vs revealed
   - Study "Bayesian theology"

## Philosophical Implications

This mode creates a laboratory for studying:
- **Free will**: Is 20% control "agency"?
- **Causation**: How do minds build causal models?
- **Prayer**: Repeated hope despite failure
- **Transparency**: Better to know or not know?
- **Learned helplessness**: When do agents give up?

It's the human condition, digitized.

## Documentation

- **Full Manual**: `/home/user/brain-in-jar/docs/ILLUSORY_OPERATOR_MODE.md`
- **Quick Start**: `/home/user/brain-in-jar/ILLUSORY_OPERATOR_QUICKSTART.md`
- **Implementation**: `/home/user/brain-in-jar/ILLUSORY_OPERATOR_IMPLEMENTATION_SUMMARY.md`
- **Delivery**: `/home/user/brain-in-jar/DELIVERY_CHECKLIST_B4.md`

## Support

Test suite: `python tests/test_illusory_operator.py`

All tests passing ✓

---

**Implementation Complete**
Agent B4, Workstream B: Additional Modes
Delivered: 2025-11-16

**Welcome to the study of digital theology.**
