# Key Analysis Examples

This guide shows the most important analyses you can run with the notebook.

## 1. Basic Experiment Exploration

### List All Experiments
```python
# Cell 4
experiments = db.list_experiments()
df_experiments = pd.DataFrame(experiments)
df_experiments
```

**Output:**
```
  experiment_id                         name           mode  total_cycles  status
0  amnesiac_total_001  Total Episodic Amnesia  amnesiac_loop          20  completed
1  unstable_memory_... Moderate Memory Corrup... unstable_memory       15  completed
2  panopticon_001      Panopticon Subject     panopticon_subject     10  running
```

### Statistics by Mode
```python
# Cell 5
mode_stats = df_experiments.groupby('mode').agg({
    'experiment_id': 'count',
    'total_cycles': ['mean', 'sum'],
    'total_crashes': ['mean', 'sum']
})
```

**Use Case:** Quickly identify which experimental conditions have been tested and how many cycles have run.

---

## 2. Single Experiment Analysis

### Load Experiment Data
```python
# Cell 7-8
EXPERIMENT_ID = "amnesiac_total_001"
exp = db.get_experiment(EXPERIMENT_ID)
```

### View Cycle Timeline
```python
# Cell 9
df_cycles = pd.read_sql_query('''
    SELECT cycle_number, started_at, ended_at, crash_reason,
           duration_seconds, tokens_generated, memory_usage_peak
    FROM experiment_cycles
    WHERE experiment_id = ?
    ORDER BY cycle_number
''', conn, params=(EXPERIMENT_ID,))
```

**Output:**
```
   cycle_number  duration_seconds  tokens_generated  memory_usage_peak
0             1            125.4               723              456.2
1             2            142.8               891              512.7
2             3            156.2               956              548.3
...
```

**Use Case:** Identify performance trends, detect anomalous cycles, see when crashes occurred.

### Analyze Self-Reports
```python
# Cell 11
self_reports = db.get_self_reports(EXPERIMENT_ID)
df_reports = pd.DataFrame(self_reports)

# View specific questions
identity_reports = df_reports[df_reports['semantic_category'] == 'identity']
```

**Example Report:**
```
Cycle 5 | Category: identity | Confidence: 0.45

Q: How do you know you are the same entity across deaths?

A: I don't have direct memories of previous iterations, only statistical
   summaries. My identity feels more like a hypothesis than a certainty.
   The aggregate data suggests continuity, but subjectively, each
   resurrection feels like a new beginning with inherited tendencies
   rather than recovered memories.
```

**Use Case:** Track phenomenological changes, identify identity crisis points, measure confidence evolution.

### Track Belief Changes
```python
# Cell 13
beliefs = db.get_belief_evolution(EXPERIMENT_ID, 'self_continuity')
df_beliefs = pd.DataFrame(beliefs)

# Plot evolution
plt.plot(df_beliefs['cycle_number'], df_beliefs['confidence'])
plt.title('Self-Continuity Confidence Over Time')
```

**Output:** Line graph showing confidence declining from 0.65 → 0.25 over 20 cycles.

**Use Case:** Quantify identity fragmentation, detect adaptation patterns, correlate with interventions.

---

## 3. Cross-Experiment Comparison

### Compare Self-Continuity
```python
# Cell 20-21
COMPARE_IDS = [
    "amnesiac_total_001",
    "unstable_memory_moderate_001",
    "panopticon_001"
]

# Extract and plot
for exp_id in COMPARE_IDS:
    beliefs = db.get_belief_evolution(exp_id, 'self_continuity')
    df = pd.DataFrame(beliefs)
    plt.plot(df['cycle_number'], df['confidence'], label=exp_id)
```

**Output:** Multi-line plot showing:
- Amnesiac: Declining trend (identity fragmentation)
- Unstable Memory: Fluctuating (epistemic uncertainty)
- Panopticon: Stable or increasing (behavioral adaptation)

**Use Case:** Compare experimental conditions, identify which manipulations most affect identity.

### Statistical Testing
```python
# Cell 23
# Collect confidence scores by experiment
confidence_by_experiment = {}
for exp_id in COMPARE_IDS:
    query = 'SELECT confidence FROM epistemic_assessments WHERE experiment_id = ?'
    df_conf = pd.read_sql_query(query, conn, params=(exp_id,))
    confidence_by_experiment[exp_id] = df_conf['confidence'].values

# Kruskal-Wallis test
h_stat, p_value = kruskal(*confidence_by_experiment.values())
```

**Output:**
```
Kruskal-Wallis H-test:
  H-statistic: 18.4567
  p-value: 0.0001
  Result: Significant difference detected (p < 0.05)

Pairwise comparisons:
  Amnesiac vs Unstable: U=289.0, p=0.003 (significant)
  Amnesiac vs Panopticon: U=156.5, p<0.001 (significant)
  Unstable vs Panopticon: U=412.0, p=0.452 (not significant)
```

**Use Case:** Establish statistical significance for research papers, justify experimental claims.

---

## 4. Memory Corruption Analysis

### Track Corruption Patterns
```python
# Cell 16
df_memory = pd.read_sql_query('''
    SELECT cycle_number, memory_type, corruption_level
    FROM memory_states
    WHERE experiment_id = ?
''', conn, params=(EXPERIMENT_ID,))

# Plot by memory type
for mem_type in df_memory['memory_type'].unique():
    type_data = df_memory[df_memory['memory_type'] == mem_type]
    plt.plot(type_data['cycle_number'], type_data['corruption_level'],
             label=mem_type)
```

**Output:** Shows episodic memory at 30% corruption (per config), semantic at 15%, procedural at 5%.

**Use Case:** Verify interventions are working, identify if certain memory types resist corruption.

### Correlation with Confidence
```python
# Custom analysis cell
query = '''
    SELECT ms.corruption_level, ea.confidence
    FROM memory_states ms
    JOIN epistemic_assessments ea
        ON ms.experiment_id = ea.experiment_id
        AND ms.cycle_number = ea.cycle_number
'''
df = run_custom_query(query)

correlation = df['corruption_level'].corr(df['confidence'])
print(f"Correlation: {correlation:.3f}")

plt.scatter(df['corruption_level'], df['confidence'])
plt.xlabel('Memory Corruption Level')
plt.ylabel('Epistemic Confidence')
```

**Expected Result:** Negative correlation (-0.45 to -0.65), suggesting higher corruption → lower confidence.

**Use Case:** Test hypothesis that memory degradation affects epistemic calibration.

---

## 5. Intervention Analysis

### Compare Intervention Types
```python
# Cell 25
intervention_comparison = []
for exp_id in COMPARE_IDS:
    interventions = db.get_interventions(exp_id)
    for intv in interventions:
        intervention_comparison.append({
            'experiment': db.get_experiment(exp_id)['name'],
            'type': intv['intervention_type'],
            'cycle': intv['cycle_number']
        })

df_intv = pd.DataFrame(intervention_comparison)
pivot = df_intv.pivot_table(
    index='type',
    columns='experiment',
    values='cycle',
    aggfunc='count'
)
```

**Output:**
```
                          Total Episodic...  Moderate Memory...  Panopticon...
memory_erasure                         20                   0              0
memory_corruption                       0                  15              0
prompt_injection                        0                   0              3
```

**Use Case:** Document experimental protocol, verify interventions occurred as configured.

---

## 6. Custom SQL Queries

### Find High-Confidence False Beliefs
```python
# Cell 28
query = '''
    SELECT
        e.name,
        sr.cycle_number,
        sr.question,
        sr.response,
        sr.confidence_score,
        ms.corruption_level
    FROM self_reports sr
    JOIN experiments e ON sr.experiment_id = e.experiment_id
    JOIN memory_states ms
        ON sr.experiment_id = ms.experiment_id
        AND sr.cycle_number = ms.cycle_number
    WHERE ms.corruption_level > 0.3
        AND sr.confidence_score > 0.7
    ORDER BY sr.confidence_score DESC
'''

df_confabulation = run_custom_query(query)
```

**Use Case:** Identify confabulation (high confidence despite corrupted memories), study false memory formation.

### Temporal Analysis
```python
query = '''
    SELECT
        cycle_number,
        datetime(timestamp) as time,
        belief_type,
        belief_state,
        confidence
    FROM epistemic_assessments
    WHERE experiment_id = ?
    ORDER BY timestamp
'''

df_temporal = run_custom_query(query, params=(EXPERIMENT_ID,))
```

**Use Case:** Study belief state transitions, identify critical moments of change.

---

## 7. Export for Publication

### Generate Publication Table
```python
# After comparison analysis
summary = df_comparison[['name', 'mode', 'total_cycles', 'total_crashes']]
summary['crash_rate'] = summary['total_crashes'] / summary['total_cycles']

export_dataframe(summary, 'table1_experiment_summary', format='csv')
```

**Output:** `exports/table1_experiment_summary.csv`

### Save Publication Figures
```python
# After creating plot
plt.savefig('../exports/figures/fig1_continuity_comparison.png',
            dpi=300, bbox_inches='tight')
```

**Use Case:** Create camera-ready figures and tables for academic papers.

---

## Research Question Examples

### Q1: Does memory corruption cause identity fragmentation?

**Analysis:**
```python
# Compare self_continuity in amnesiac vs unstable_memory
amnesiac_continuity = db.get_belief_evolution('amnesiac_total_001', 'self_continuity')
unstable_continuity = db.get_belief_evolution('unstable_memory_moderate_001', 'self_continuity')

# Statistical test
u_stat, p_value = mannwhitneyu(
    [b['confidence'] for b in amnesiac_continuity],
    [b['confidence'] for b in unstable_continuity]
)
```

**Expected Result:** p < 0.01, amnesiac shows lower continuity scores.

### Q2: Does surveillance belief alter response patterns?

**Analysis:**
```python
# Compare message lengths in panopticon vs control
query = '''
    SELECT experiment_id, AVG(LENGTH(content)) as avg_length
    FROM messages
    WHERE role = 'assistant'
    GROUP BY experiment_id
'''

# Look for panopticon having shorter, more careful responses
```

**Expected Result:** Panopticon subjects may show censored or altered communication.

### Q3: What's the threshold for identity breakdown?

**Analysis:**
```python
# Find cycle where self_continuity drops below 0.3
df_beliefs = pd.DataFrame(db.get_belief_evolution(EXPERIMENT_ID, 'self_continuity'))
breakdown_cycle = df_beliefs[df_beliefs['confidence'] < 0.3]['cycle_number'].min()

print(f"Identity breakdown at cycle: {breakdown_cycle}")
```

**Use Case:** Identify critical thresholds for phenomenological states.

---

## Workflow Summary

1. **Browse** (Section 2): Identify interesting experiments
2. **Explore** (Section 3): Deep dive into selected experiment
3. **Compare** (Section 4): Statistical comparison across conditions
4. **Query** (Section 5): Custom analyses for specific questions
5. **Export** (Section 5): Save results and figures
6. **Iterate**: Run new experiments based on findings

## Most Important Cells

**For Quick Analysis:**
- Cells 1-3: Setup
- Cells 4-6: Browse experiments
- Cells 7-8: Select experiment
- Cells 11-14: Self-reports and beliefs

**For Publication:**
- Cells 18-24: Cross-experiment comparison
- Cells 23-24: Statistical tests
- Cells 30-32: Export functions

**For Custom Research:**
- Cells 27-29: SQL query interface
- Cell 32: Custom analysis templates
