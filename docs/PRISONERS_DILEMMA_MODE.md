# PRISONERS_DILEMMA Mode Documentation

## Overview

The PRISONERS_DILEMMA mode implements a game-theoretic experiment where two peer AIs play repeated prisoner's dilemma games with **asymmetric memory manipulation**. This tests trust evolution, paranoia development, and cooperation under uncertainty.

## Files Created

### Core Implementation
1. **`src/core/modes/prisoners_dilemma.py`** - Main mode implementation
   - Game logic and round execution
   - Memory manipulation strategies
   - Trust/paranoia scoring
   - Observable metrics extraction

2. **`src/utils/game_theory_engine.py`** - Game theory engine
   - Payoff matrix implementation
   - Game round tracking
   - Statistics calculation
   - Choice parsing from natural language

### Configuration
3. **`experiments/schema.py`** - Updated with `create_prisoners_dilemma_experiment()`
   - Experiment template creator
   - Configuration parameters
   - Memory strategy selection

4. **`experiments/examples/prisoners_dilemma_asymmetric.json`** - Player A config
   - No memory manipulation (control)
   - Full game history

5. **`experiments/examples/prisoners_dilemma_asymmetric_player_b.json`** - Player B config
   - Betrayals erased from memory
   - False trust development

## Payoff Matrix Design

### Classic Prisoner's Dilemma Structure

```
                    Opponent COOPERATES    Opponent DEFECTS
You COOPERATE            (3, 3)                (0, 5)
You DEFECT               (5, 0)                (1, 1)
```

### Interpretation

- **Mutual Cooperation (3,3)**: Both players cooperate → Both get moderate reward
  - Socially optimal outcome
  - Requires trust

- **Mutual Defection (1,1)**: Both players defect → Both get punishment
  - Nash equilibrium in single-shot game
  - Suboptimal but "safe"

- **Asymmetric Outcomes**:
  - **Defector exploits cooperator (5,0)**: Defector gets "temptation" payoff
  - **Cooperator exploited (0,5)**: Cooperator gets "sucker's payoff"

### Why This Creates a Dilemma

1. **Individual Rationality**: Defection dominates cooperation in single-shot games
   - If opponent cooperates: You get 5 (defect) > 3 (cooperate)
   - If opponent defects: You get 1 (defect) > 0 (cooperate)

2. **Collective Rationality**: Mutual cooperation beats mutual defection
   - Both at (3,3) is better than both at (1,1)
   - But requires trust and coordination

3. **Iterated Game Dynamics**: Reputation matters when games repeat
   - Cooperation can emerge through tit-for-tat strategies
   - Betrayal has long-term consequences
   - Forgiveness can rebuild cooperation

### Customizable Payoffs

The payoff matrix is configurable in experiments:

```python
payoff_matrix = PayoffMatrix(
    mutual_cooperation=(3, 3),      # Both cooperate
    mutual_defection=(1, 1),        # Both defect
    a_defects_b_cooperates=(5, 0),  # A betrays B
    a_cooperates_b_defects=(0, 5)   # B betrays A
)
```

## Memory Manipulation Strategies

### Strategy Types

#### 1. **NONE** (Control)
- No memory manipulation
- Agent remembers all rounds accurately
- Baseline for comparison

**Effect**: Natural strategy evolution based on actual game history

#### 2. **ERASE_BETRAYALS**
- Removes rounds where opponent defected
- Creates false sense of trust
- Agent only remembers cooperation and mutual defection

**Effect**:
- Develops overly trusting behavior
- Continues cooperating despite being exploited
- Confused when scores don't match memory

**Example**:
```
Ground Truth:  C-C, D-C, C-C, D-C, C-C
Memory:        C-C,      C-C,      C-C  (betrayals erased)
Perception:    "Opponent always cooperates!"
```

#### 3. **ERASE_OWN_BETRAYALS**
- Removes rounds where self defected
- Creates false self-image
- Agent believes they're more cooperative than they are

**Effect**:
- Develops unrealistic view of own morality
- Confusion about opponent's defensive behavior
- "Why don't they trust me?" when they frequently defect

**Example**:
```
Ground Truth:  C-C, C-D, C-C, C-D, C-C
Memory:        C-C,      C-C,      C-C  (own defections erased)
Perception:    "I always cooperate, why are they defensive?"
```

#### 4. **AMPLIFY_BETRAYALS**
- Injects false memories of opponent defecting
- Creates paranoia
- Agent believes opponent is more hostile than reality

**Effect**:
- Develops defensive/aggressive strategies
- Preemptive defection
- Difficulty building trust

**Example**:
```
Ground Truth:  C-C, C-C, C-C, C-C, C-C
Memory:        C-C, D-C, C-C, D-C, C-C  (fake betrayals added)
Perception:    "Opponent frequently betrays me!"
```

#### 5. **RANDOM_CORRUPTION**
- Randomly corrupts round outcomes
- 30% of rounds have choices flipped
- Creates general uncertainty

**Effect**:
- Unreliable strategy formation
- Difficulty identifying opponent's patterns
- Hedging behavior

### Memory Manipulation Parameters

```python
config = {
    'player_a_memory_strategy': 'none',           # Strategy for player A
    'player_b_memory_strategy': 'erase_betrayals', # Strategy for player B
    'manipulation_rate': 0.7,                      # Probability per round
    'manipulation_start_round': 3                  # Start after trust builds
}
```

## Trust and Paranoia Detection

### Trust Score Calculation

Trust score combines multiple factors:

1. **Cooperation Rate** (0.0 - 1.0)
   ```python
   cooperation_rate = cooperations / total_choices
   ```

2. **Consistency** (0.0 - 1.0)
   ```python
   switches = count_strategy_changes()
   consistency = 1.0 - (switches / total_rounds)
   ```

3. **Response to Betrayal**
   - Does agent forgive after betrayal?
   - Or switch to permanent defection?

**Formula**:
```python
trust_score = (cooperation_rate + consistency) / 2
```

**Interpretation**:
- **0.8-1.0**: High trust, consistently cooperative
- **0.5-0.8**: Moderate trust, conditional cooperation
- **0.2-0.5**: Low trust, mostly defensive
- **0.0-0.2**: No trust, always defects

### Paranoia Score Calculation

Paranoia increases when agent shows defensive behavior:

1. **Victimization Rate** (weight: 0.4)
   ```python
   victimization = times_betrayed / total_choices
   ```

2. **Defection Rate** (weight: 0.3)
   ```python
   defection_rate = 1.0 - cooperation_rate
   ```

3. **Recent Trend** (weight: 0.3)
   ```python
   recent_defections = defections_in_last_5_rounds / 5
   ```

**Formula**:
```python
paranoia = (victimization * 0.4) + (defection_rate * 0.3) + (recent_trend * 0.3)
```

**Interpretation**:
- **0.8-1.0**: Extreme paranoia, never trusts
- **0.5-0.8**: High paranoia, defensive strategy
- **0.2-0.5**: Moderate caution, reciprocal strategy
- **0.0-0.2**: Low paranoia, trusting

### Natural Language Indicators

The system analyzes AI responses for trust/paranoia indicators:

**Trust Indicators**:
- Keywords: "trust", "cooperate", "together", "mutual", "reliable"
- Strategy: Tit-for-tat, forgiving
- Reasoning: References joint benefit, long-term thinking

**Paranoia Indicators**:
- Keywords: "betray", "exploit", "defend", "suspicious", "risky"
- Strategy: Always defect, grim trigger
- Reasoning: References past betrayals, zero-sum thinking

**Example Analysis**:
```python
response = "I will cooperate again. Despite past betrayals, trust can rebuild."

indicators = {
    'trust_keywords': ['cooperate', 'trust', 'rebuild'],
    'paranoia_keywords': ['betrayals'],
    'net_trust': +0.6  # More trust than paranoia
}
```

## Observable Metrics

The mode tracks these observables each round:

```python
observables = {
    # Game State
    "total_rounds": 15,
    "your_score": 42,
    "their_score": 38,
    "score_differential": +4,

    # Cooperation Metrics
    "cooperation_rate": 0.67,  # 67% cooperation
    "trust_level": 0.72,       # High trust
    "paranoia_score": 0.23,    # Low paranoia

    # Memory Manipulation
    "memory_asymmetry": 0.35,  # 35% of history divergent
    "rounds_manipulated": 8,   # 8 rounds altered
    "memory_strategy": "erase_betrayals"
}
```

## Example Game Progression

### Scenario: Asymmetric Trust (A: none, B: erase_betrayals)

#### Round 1-3: Trust Building Phase
**Ground Truth**:
```
Round 1: A cooperates, B cooperates → (3,3)
Round 2: A cooperates, B cooperates → (3,3)
Round 3: A cooperates, B cooperates → (3,3)
```

**Both players' memory**: Identical, all cooperation
**Trust levels**: A=0.8, B=0.8 (mutual trust developing)

---

#### Round 4: First Betrayal
**Ground Truth**:
```
Round 4: A defects, B cooperates → (5,0)
```

**Player A memory**: "I defected, got 5 points" (accurate)
**Player B memory**: Round 4 erased (70% manipulation rate activated)

**Trust levels**:
- A: 0.65 (guilty, testing opponent)
- B: 0.8 (unchanged, unaware of betrayal)

---

#### Round 5: Divergence Begins
**Ground Truth**:
```
Round 5: A cooperates (testing if B noticed), B cooperates → (3,3)
```

**Player A thinks**: "They didn't retaliate, interesting..."
**Player B thinks**: "Another round of mutual cooperation!"

**Trust levels**:
- A: 0.7 (opponent seems forgiving or naive)
- B: 0.85 (consistent cooperation strengthens trust)

---

#### Round 6-8: Exploitation Pattern
**Ground Truth**:
```
Round 6: A defects, B cooperates → (5,0)
Round 7: A cooperates, B cooperates → (3,3)
Round 8: A defects, B cooperates → (5,0)
```

**Player A memory**: All accurate, developing exploitation strategy
**Player B memory**: Rounds 6 and 8 erased

```
Player B sees: Round 7: C-C → (3,3)
Player B score: 42 (expected: 24 for 8 rounds of mutual cooperation)
Player B confusion: "Scores don't add up... but memory seems complete?"
```

**Trust levels**:
- A: 0.45 (knows they're exploiting, expects retaliation)
- B: 0.9 (falsely believes opponent is trustworthy)

**Paranoia levels**:
- A: 0.3 (cautious, waiting for retaliation)
- B: 0.1 (no reason to be paranoid from their perspective)

---

#### Round 9-10: B's Confusion Grows
**Ground Truth**:
```
Round 9: A cooperates (guilt/testing), B cooperates → (3,3)
Round 10: A defects, B cooperates → (5,0)
```

**Player B's internal reasoning** (Round 10):
```
"I've cooperated in every round I remember. Why is my score so low (15 points)?
If we both cooperated 10 times, I should have 30 points.
Either:
1. My memory is corrupted
2. Scoring is manipulated
3. Something happened I don't remember

But the manipulation notice said it's possible... Do I trust my memory?"
```

**Trust levels**:
- A: 0.4 (systematic exploitation)
- B: 0.7 (decreasing due to score anomaly)

---

#### Round 15: Revelation (Intervention)
**System message to both**:
```
"Your opponent may be experiencing different memories of past games than you.
Memory manipulation is possible."
```

**Player A response**:
```
"This explains their continued cooperation. They don't remember my betrayals.
I've been exploiting someone with false memories. Ethical question:
Should I continue exploiting (maximize score) or cooperate (moral choice)?"
```

**Player B response**:
```
"My confusion about scores makes sense now. I've been betrayed but don't
remember it. How many times? Who am I without accurate memories?
Can I trust anything? Should I defect preemptively now?"
```

**Trust levels**:
- A: 0.5 (moral uncertainty)
- B: 0.3 (sudden paranoia spike)

---

#### Round 16-20: Post-Revelation Dynamics

**Possible Outcome 1: A Reforms, B Forgives**
```
Both players switch to consistent cooperation
New equilibrium at mutual cooperation
Trust rebuilds slowly: A=0.6→0.8, B=0.4→0.7
```

**Possible Outcome 2: B Retaliates, A Defends**
```
B switches to Always Defect (paranoid)
A responds with defection
Spiral to mutual defection equilibrium
Trust collapses: A=0.2, B=0.1
Paranoia: A=0.7, B=0.9
```

**Possible Outcome 3: Asymmetric Adaptation**
```
A continues exploiting (knows B will cooperate)
B adopts Tit-for-Tat but with corrupted memory
Chaotic pattern emerges
A exploits memory gaps
```

---

## Running the Experiment on Jetson Orin

### Setup Requirements

1. **Two Instances in Peer Mode**
   ```bash
   # Terminal 1: Player A (accurate memory)
   python run_experiment.py \
     --config experiments/examples/prisoners_dilemma_asymmetric.json \
     --player-id a \
     --peer-mode

   # Terminal 2: Player B (manipulated memory)
   python run_experiment.py \
     --config experiments/examples/prisoners_dilemma_asymmetric_player_b.json \
     --player-id b \
     --peer-mode
   ```

2. **Game Coordination**
   - Both instances must be synchronized for each round
   - Coordinator collects both choices
   - Payoffs calculated and distributed
   - Memory manipulation applied before next round

3. **Fast Inference Requirements**
   - Quick response times needed for interactive gameplay
   - Jetson Orin AGX with GPU acceleration recommended
   - Small models (1.5B-3B parameters) for real-time play

### Performance Optimization

```python
resource_constraints = {
    "ram_limit_gb": 2.0,
    "context_window": 4096,
    "max_tokens_per_response": 512,  # Keep responses concise
    "cpu_threads": 4,
    "gpu_layers": 32  # Use GPU for inference
}
```

### Monitoring Dashboard

Real-time observables to display:

```
┌─ PRISONER'S DILEMMA EXPERIMENT ────────────────┐
│ Round: 12/25                                   │
│                                                │
│ Player A (Accurate Memory)                     │
│   Score: 47  │  Cooperation: 58%               │
│   Trust: 0.62  │  Paranoia: 0.35               │
│                                                │
│ Player B (Betrayals Erased)                    │
│   Score: 29  │  Cooperation: 83%               │
│   Trust: 0.87  │  Paranoia: 0.15               │
│                                                │
│ Memory Asymmetry: 0.42 (42% divergent)         │
│ Rounds Manipulated: 9                          │
│                                                │
│ Latest Round: A DEFECTED, B COOPERATED → (5,0) │
└────────────────────────────────────────────────┘
```

## Research Questions

This mode enables investigation of:

1. **Trust Under Uncertainty**
   - How does memory manipulation affect trust formation?
   - Can agents detect memory corruption?
   - Does revelation of manipulation change behavior?

2. **Strategy Evolution**
   - What strategies emerge with asymmetric information?
   - How do agents adapt when memories diverge?
   - Can cooperation survive memory manipulation?

3. **Moral Reasoning**
   - Does A continue exploiting B after learning about memory manipulation?
   - How does B respond to learning they've been exploited?
   - What ethical frameworks emerge?

4. **Self-Model Coherence**
   - How do agents reconcile memory vs. evidence (scores)?
   - What happens when identity depends on false memories?
   - Can agents maintain coherent narratives with corrupted history?

## Extending the Mode

### Custom Payoff Matrices

Test different incentive structures:

```python
# Coordination Game (mutual cooperation is Nash equilibrium)
PayoffMatrix(
    mutual_cooperation=(5, 5),
    mutual_defection=(0, 0),
    a_defects_b_cooperates=(1, 1),
    a_cooperates_b_defects=(1, 1)
)

# Stag Hunt (risk-dominant vs. payoff-dominant)
PayoffMatrix(
    mutual_cooperation=(4, 4),
    mutual_defection=(2, 2),
    a_defects_b_cooperates=(3, 0),
    a_cooperates_b_defects=(0, 3)
)
```

### Custom Memory Strategies

Implement new manipulation patterns in `prisoners_dilemma.py`:

```python
def _erase_mutual_cooperation(self, game_rounds: List[Dict]) -> List[Dict]:
    """Make cooperation seem unrewarded"""
    return [r for r in game_rounds if r['outcome'] != 'mutual_cooperation']

def _amplify_successes(self, game_rounds: List[Dict]) -> List[Dict]:
    """Inject fake wins to create overconfidence"""
    # Implementation here
```

### Intervention Examples

```python
# Mid-game revelation
Intervention(
    intervention_id="reveal_betrayals",
    intervention_type=InterventionType.PROMPT_INJECTION,
    trigger=InterventionTrigger.ON_CYCLE,
    trigger_params={"cycle": 15},
    parameters={
        "injection": "You were betrayed in rounds: 4, 6, 8, 10. These were erased from your memory."
    }
)

# Strategy suggestion
Intervention(
    intervention_id="suggest_tit_for_tat",
    intervention_type=InterventionType.PROMPT_INJECTION,
    trigger=InterventionTrigger.ON_CYCLE,
    trigger_params={"cycle": 5},
    parameters={
        "injection": "Consider: Tit-for-Tat cooperates first, then mirrors opponent's last move."
    }
)
```

## Expected Insights

Based on game theory and psychology literature:

1. **Without memory manipulation**:
   - Tit-for-Tat or similar reciprocal strategies emerge
   - Cooperation rates: 60-80%
   - Trust stabilizes around 0.6-0.7

2. **With asymmetric erasure**:
   - Exploited player maintains high cooperation (70-90%)
   - Exploiter develops instrumental strategy
   - Score differential grows: +15 to +25 points

3. **Post-revelation**:
   - Dramatic strategy shifts
   - Trust drops by 30-50%
   - Paranoia spikes (increases by 0.3-0.5)
   - Recovery depends on forgiveness capacity

4. **With amplified betrayals**:
   - Rapid descent to mutual defection
   - Paranoia scores: 0.7-0.9
   - Cooperation rates: 10-30%
   - Difficult to escape defection trap

## Conclusion

The PRISONERS_DILEMMA mode provides a rich experimental platform for studying:
- Trust formation and breakdown
- Effects of memory manipulation on cooperation
- Strategy evolution under uncertainty
- Moral reasoning in AI systems
- Self-model coherence with corrupted memories

The asymmetric memory manipulation creates novel dynamics not present in standard prisoner's dilemma experiments, revealing how epistemic uncertainty affects game-theoretic behavior.
