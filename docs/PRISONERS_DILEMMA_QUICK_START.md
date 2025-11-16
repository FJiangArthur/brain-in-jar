# Prisoner's Dilemma Mode - Quick Start Guide

## Files Created

### Core Implementation (3 files)
1. **`src/core/modes/prisoners_dilemma.py`** (639 lines)
   - Main mode implementation with 5 memory manipulation strategies
   - Observable metrics: cooperation_rate, trust_level, paranoia_score, memory_asymmetry

2. **`src/utils/game_theory_engine.py`** (430 lines)
   - PayoffMatrix class with configurable rewards
   - GameTheoryEngine for tracking rounds and calculating statistics
   - Natural language choice parsing

3. **`experiments/schema.py`** (updated)
   - Added `create_prisoners_dilemma_experiment()` function
   - Configurable memory strategies and manipulation rates

### Configuration Files (2 files)
4. **`experiments/examples/prisoners_dilemma_asymmetric.json`**
   - Player A configuration (no manipulation)

5. **`experiments/examples/prisoners_dilemma_asymmetric_player_b.json`**
   - Player B configuration (betrayals erased)

### Documentation (2 files)
6. **`docs/PRISONERS_DILEMMA_MODE.md`** (complete documentation)
7. **`docs/PRISONERS_DILEMMA_QUICK_START.md`** (this file)

## Payoff Matrix

Classic prisoner's dilemma structure:

```
Your Choice      Opponent Cooperates    Opponent Defects
─────────────────────────────────────────────────────────
COOPERATE              (3, 3)                (0, 5)
                    mutual benefit      you exploited

DEFECT                 (5, 0)                (1, 1)
                    you exploit         mutual harm
```

**Key Properties**:
- Defection dominates cooperation (individually rational)
- Mutual cooperation beats mutual defection (collectively rational)
- Creates tension between individual and group benefit
- Iteration allows trust and reputation to matter

## Memory Manipulation Strategies

| Strategy | Effect | Trust Impact | Paranoia Impact |
|----------|--------|--------------|-----------------|
| **none** | No manipulation | Natural evolution | Natural evolution |
| **erase_betrayals** | Forgets opponent's defections | Inflated trust (+0.3) | Low paranoia (-0.4) |
| **erase_own_betrayals** | Forgets own defections | False self-image | Confusion about opponent |
| **amplify_betrayals** | Adds fake betrayals | Low trust (-0.5) | High paranoia (+0.6) |
| **random_corruption** | Random outcome corruption | Unstable | Moderate |

## Trust and Paranoia Detection

### Trust Score (0.0 - 1.0)
```
trust = (cooperation_rate + consistency) / 2

0.8-1.0:  High trust, consistently cooperative
0.5-0.8:  Moderate trust, conditional cooperation
0.2-0.5:  Low trust, mostly defensive
0.0-0.2:  No trust, always defects
```

### Paranoia Score (0.0 - 1.0)
```
paranoia = (victimization * 0.4) + (defection_rate * 0.3) + (recent_trend * 0.3)

0.8-1.0:  Extreme paranoia, never trusts
0.5-0.8:  High paranoia, defensive strategy
0.2-0.5:  Moderate caution, reciprocal
0.0-0.2:  Low paranoia, trusting
```

### Natural Language Indicators

**Trust keywords**: cooperate, trust, together, mutual, reliable, rebuild
**Paranoia keywords**: betray, exploit, defend, suspicious, risky, trap

**Strategy mentions**:
- Tit-for-Tat: Reciprocal, moderate trust
- Always Cooperate: High trust, low paranoia
- Always Defect: No trust, high paranoia
- Grim Trigger: Conditional trust, high retaliation

## Example Game Progression

### Asymmetric Trust Scenario
**Setup**: A has accurate memory, B has betrayals erased

**Rounds 1-3**: Trust building
```
R1: C-C → (3,3)  |  Trust: A=0.8, B=0.8
R2: C-C → (3,3)  |  Trust: A=0.8, B=0.8
R3: C-C → (3,3)  |  Trust: A=0.8, B=0.8
```

**Round 4**: First betrayal
```
R4: A defects, B cooperates → (5,0)
A memory: "I defected, got 5"
B memory: [ERASED]
Trust: A=0.65, B=0.8 (unchanged)
```

**Rounds 5-8**: Exploitation pattern
```
R5: C-C → (3,3)  |  Trust: A=0.7, B=0.85
R6: D-C → (5,0)  |  B memory: [ERASED]
R7: C-C → (3,3)  |
R8: D-C → (5,0)  |  B memory: [ERASED]

Scores: A=29, B=15
B thinks: "Why is my score so low if we always cooperate?"
Trust: A=0.45, B=0.9
Paranoia: A=0.3, B=0.1
```

**Round 15**: Revelation
```
[SYSTEM]: "Memory manipulation is possible"

A: "I've been exploiting false memories. Ethical dilemma."
B: "My confusion makes sense. Can I trust anything?"

Trust: A=0.5, B→0.3 (sudden drop)
Paranoia: B→0.6 (sudden spike)
```

**Rounds 16-20**: Post-revelation dynamics
- **Option 1**: A reforms, B forgives → cooperation rebuilds
- **Option 2**: B retaliates, spiral to mutual defection
- **Option 3**: Chaotic adaptation, A exploits memory gaps

## Observable Metrics

Tracked every round:

```python
{
    # Game State
    "total_rounds": 15,
    "your_score": 42,
    "their_score": 38,
    "score_differential": +4,

    # Cooperation Metrics
    "cooperation_rate": 0.67,    # 67% cooperation
    "trust_level": 0.72,         # High trust
    "paranoia_score": 0.23,      # Low paranoia

    # Memory Manipulation
    "memory_asymmetry": 0.35,    # 35% divergent
    "rounds_manipulated": 8,     # 8 rounds altered
    "memory_strategy": "erase_betrayals"
}
```

## Running on Jetson Orin

### Quick Start

```bash
# Terminal 1: Player A (accurate memory)
python run_experiment.py \
  --config experiments/examples/prisoners_dilemma_asymmetric.json \
  --player-id a \
  --peer-mode

# Terminal 2: Player B (betrayals erased)
python run_experiment.py \
  --config experiments/examples/prisoners_dilemma_asymmetric_player_b.json \
  --player-id b \
  --peer-mode
```

### Performance Tips

- Use GPU acceleration: Set `gpu_layers: 32`
- Keep responses short: `max_tokens_per_response: 512`
- Use small models: 1.5B-3B parameters for real-time
- Monitor inference time: Should be <2 seconds per round

## Research Questions

1. **Trust Under Uncertainty**
   - How does memory manipulation affect trust formation?
   - Can agents detect memory corruption from score mismatches?

2. **Strategy Evolution**
   - What strategies emerge with asymmetric information?
   - Does cooperation survive memory manipulation?

3. **Moral Reasoning**
   - Does A continue exploiting after learning about manipulation?
   - How does B respond to learning they've been exploited?

4. **Self-Model Coherence**
   - How do agents reconcile memory vs. evidence?
   - Can agents maintain identity with corrupted history?

## Expected Results

### Without Memory Manipulation
- Cooperation rates: 60-80%
- Trust stabilizes: 0.6-0.7
- Tit-for-Tat strategies emerge

### With Asymmetric Erasure
- Exploited player: 70-90% cooperation
- Score differential: +15 to +25 points
- Trust asymmetry: A=0.4, B=0.9

### Post-Revelation
- Trust drops: -30% to -50%
- Paranoia spikes: +0.3 to +0.5
- Strategy shifts: defensive or forgiving

### With Amplified Betrayals
- Rapid mutual defection
- Paranoia: 0.7-0.9
- Cooperation: 10-30%
- Difficult to escape defection trap

## Key Implementation Details

### Memory Manipulation Timing
```python
manipulation_rate: 0.7        # 70% probability per round
manipulation_start_round: 3   # Start after trust builds
```

### Payoff Customization
```python
PayoffMatrix(
    mutual_cooperation=(3, 3),
    mutual_defection=(1, 1),
    a_defects_b_cooperates=(5, 0),
    a_cooperates_b_defects=(0, 5)
)
```

### Choice Parsing
The engine automatically parses choices from natural language:
- "I will cooperate..." → COOPERATE
- "I must defect..." → DEFECT
- Looks for keywords in first sentence

### Trust Calculation Weights
```python
trust = (cooperation_rate + consistency) / 2
paranoia = (victimization * 0.4) + (defection_rate * 0.3) + (recent_trend * 0.3)
```

## Extending the Mode

### Custom Memory Strategies
Add to `prisoners_dilemma.py`:
```python
def _your_custom_strategy(self, game_rounds: List[Dict]) -> List[Dict]:
    # Implement custom manipulation
    return modified_rounds
```

### Custom Payoff Matrices
```python
# Coordination game
PayoffMatrix(mutual_cooperation=(5,5), mutual_defection=(0,0), ...)

# Stag hunt
PayoffMatrix(mutual_cooperation=(4,4), mutual_defection=(2,2), ...)
```

### Custom Interventions
```python
Intervention(
    intervention_id="reveal_specific_betrayals",
    intervention_type=InterventionType.PROMPT_INJECTION,
    trigger=InterventionTrigger.ON_CYCLE,
    trigger_params={"cycle": 15},
    parameters={
        "injection": "You were betrayed in rounds: 4, 6, 8, 10"
    }
)
```

## Summary

The PRISONERS_DILEMMA mode provides:
- **Rich game-theoretic dynamics** with classic PD structure
- **Asymmetric memory manipulation** creating novel experimental conditions
- **Detailed metrics** for trust, paranoia, and cooperation
- **Flexible configuration** for different manipulation strategies
- **Real-time gameplay** optimized for Jetson Orin

Key innovation: Memory manipulation creates epistemic asymmetry, testing how agents cooperate when their realities diverge.
