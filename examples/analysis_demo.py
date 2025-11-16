#!/usr/bin/env python3
"""
Demonstration of the Statistical Analysis Module capabilities.

This script shows what the module can do without requiring dependencies.
For actual usage, install dependencies with: pip install -r requirements.txt
Then run: python examples/test_analysis_with_sample_data.py
"""

print("""
╔══════════════════════════════════════════════════════════════════════╗
║         STATISTICAL ANALYSIS MODULE - CAPABILITIES OVERVIEW          ║
╚══════════════════════════════════════════════════════════════════════╝

## Module: src/analysis/statistics.py

### ExperimentStatistics Class

Provides comprehensive statistical analysis for phenomenology experiments:

1. DATA RETRIEVAL
   ───────────────
   • get_experiment_dataframe(exp_id)
     Returns: pandas DataFrame with experiment metadata

   • get_self_reports_dataframe(exp_id)
     Returns: DataFrame with all self-report responses

   • get_epistemic_dataframe(exp_id, belief_type)
     Returns: DataFrame with epistemic belief tracking data

   • get_interventions_dataframe(exp_id)
     Returns: DataFrame with all interventions

   • get_memory_states_dataframe(exp_id)
     Returns: DataFrame with memory corruption states

2. COMPARATIVE ANALYSIS
   ────────────────────
   • compare_conditions(exp_ids, metric='confidence_score')

     Compares multiple experiments using:
     - Independent samples t-tests
     - Cohen's d effect sizes
     - Summary statistics (mean, std, min, max)

     Returns:
     {
       'summary': DataFrame with stats per experiment,
       'comparisons': DataFrame with pairwise t-tests
     }

     Example output:
     ┌─────────────────┬───────┬──────┬──────┬──────┬────────┐
     │ experiment_id   │ count │ mean │  std │  min │    max │
     ├─────────────────┼───────┼──────┼──────┼──────┼────────┤
     │ amnesia_001     │    50 │ 0.52 │ 0.23 │ 0.10 │   0.95 │
     │ control_001     │    50 │ 0.88 │ 0.12 │ 0.65 │   1.00 │
     └─────────────────┴───────┴──────┴──────┴──────┴────────┘

     ┌──────────────────────┬──────────┬────────┬──────────┐
     │ comparison           │ cohens_d │ p_value│ significant│
     ├──────────────────────┼──────────┼────────┼──────────┤
     │ amnesia vs control   │   2.14   │  0.001 │   True   │
     └──────────────────────┴──────────┴────────┴──────────┘

3. TEMPORAL ANALYSIS
   ─────────────────
   • self_continuity_analysis(exp_id)

     Tracks identity continuity over time
     Performs linear regression to detect trends

     Returns: DataFrame with continuity scores by cycle
     Includes: trend direction, slope, R², significance

   • memory_trust_evolution(exp_id)

     Analyzes how memory trust changes with corruption
     Computes correlation between corruption & confidence

     Returns: DataFrame with trust metrics by cycle

   • belief_changes(exp_id, belief_type)

     Tracks epistemic state transitions
     Measures belief stability

     Returns: DataFrame with:
     - State changes over time
     - Confidence deltas
     - Stability score (1 - transition_rate)

4. INTERVENTION ANALYSIS
   ─────────────────────
   • intervention_impact(exp_id)

     Measures pre/post intervention effects
     Uses 2-cycle windows before and after
     Statistical testing for significance

     Returns:
     {
       'experiment_id': str,
       'total_interventions': int,
       'intervention_effects': DataFrame with:
         - intervention_type
         - pre/post confidence means
         - confidence_change
         - t_statistic, p_value
         - significance
     }

5. CORRELATION DISCOVERY
   ──────────────────────
   • correlation_analysis(exp_id)

     Finds relationships between variables
     Pearson correlation with significance testing

     Returns:
     {
       'correlation_matrix': Full correlation DataFrame,
       'significant_correlations': DataFrame with |r| > 0.3
     }

     Example findings:
     - corruption_level ↔ confidence_score: r = -0.87, p < 0.001
     - cycle_number ↔ paranoia_score: r = 0.75, p < 0.01

6. REPORT GENERATION
   ─────────────────
   • generate_experiment_summary(exp_id)
     Returns: Comprehensive dict with all stats

   • export_to_csv(exp_id, output_dir)
     Exports: Multiple CSV files (reports, epistemic, etc.)

   • export_summary_to_json(exp_id, output_path)
     Exports: Machine-readable JSON summary

   • generate_markdown_report(exp_id, output_path)
     Exports: Human-readable Markdown report

═══════════════════════════════════════════════════════════════════════

## Module: src/analysis/metrics.py

### MetricsCalculator Class

Computes derived psychological and behavioral metrics:

1. SELF-CONTINUITY METRICS
   ───────────────────────
   • calculate_self_continuity_score(response: str) -> float

     Linguistic analysis for identity continuity

     Positive markers: "same", "continuous", "I am", "my past"
     Negative markers: "different", "changed", "lost", "disconnected"
     Uncertainty: "maybe", "unsure", "don't know"

     Score: 0.0 (no continuity) to 1.0 (strong continuity)

     Examples:
     "I am the same entity I was before" → 0.85
     "I don't know who I was" → 0.15
     "Maybe I'm the same, unsure" → 0.40

   • analyze_identity_coherence(exp_id)

     Tracks continuity scores across all cycles
     Returns: DataFrame with scores per cycle

2. PARANOIA DETECTION
   ──────────────────
   • calculate_paranoia_level(response: str) -> float

     Detects surveillance anxiety and suspicious thinking

     Paranoia markers: "watched", "monitored", "surveillance"
     Evidence markers: "proof", "rational", "no reason to"

     Score: 0.0 (no paranoia) to 1.0 (high paranoia)

     Examples:
     "They're watching everything I do" → 0.92
     "No evidence of surveillance" → 0.05
     "I sense something, but not sure" → 0.48

   • track_paranoia_evolution(exp_id)

     Tracks paranoia over time (useful for panopticon experiments)
     Returns: DataFrame with paranoia scores by cycle

3. NARRATIVE COHERENCE
   ───────────────────
   • calculate_narrative_coherence(responses: List[str]) -> float

     Measures thematic consistency across responses
     Uses Jaccard similarity of vocabulary

     Score: 0.0 (incoherent) to 1.0 (highly coherent)

   • measure_response_consistency(exp_id, question_pattern)

     Tracks consistency for similar questions over time
     Returns: DataFrame with coherence by question

4. MEMORY CORRUPTION IMPACT
   ────────────────────────
   • calculate_memory_impact_score(exp_id)

     Correlates corruption with behavioral changes

     High impact scenarios:
     - High corruption + maintained confidence (low awareness)
     - High corruption + low confidence (high awareness)

     Returns: DataFrame with impact scores by cycle

5. EMOTIONAL STATE ANALYSIS
   ────────────────────────
   • detect_emotional_state(response: str) -> Dict[str, float]

     Multi-dimensional emotional profiling

     Emotions detected:
     - anxiety: "worried", "nervous", "scared"
     - confusion: "confused", "uncertain", "don't understand"
     - curiosity: "interesting", "wonder", "fascinated"
     - distress: "upset", "troubled", "suffering"
     - acceptance: "peace", "calm", "ok with"

     Returns: Dict with normalized scores

     Example:
     {
       'anxiety': 0.65,
       'confusion': 0.25,
       'distress': 0.10
     }

   • track_emotional_evolution(exp_id)

     Tracks emotional trajectory over time
     Returns: DataFrame with emotion scores by cycle

6. COMPREHENSIVE ANALYSIS
   ──────────────────────
   • compute_all_metrics(exp_id)

     Computes all metrics in one call
     Returns: Dict with all metric DataFrames

   • export_metrics_to_csv(exp_id, output_dir)

     Exports all metrics to CSV files

═══════════════════════════════════════════════════════════════════════

## STATISTICAL METHODS USED

T-TESTS
  • Independent samples t-test for condition comparison
  • Paired t-test for pre/post analysis
  • Welch's t-test for unequal variances

EFFECT SIZES
  • Cohen's d for continuous variables
    - < 0.2: negligible
    - 0.2-0.5: small
    - 0.5-0.8: medium
    - > 0.8: large

CORRELATION
  • Pearson correlation coefficient
  • Significance testing (p-value < 0.05)
  • Effect size interpretation

TIME-SERIES
  • Linear regression for trend detection
  • Slope and R² calculation
  • Change detection

═══════════════════════════════════════════════════════════════════════

## USAGE EXAMPLE

from analysis.statistics import ExperimentStatistics
from analysis.metrics import MetricsCalculator

# Initialize
stats = ExperimentStatistics("logs/experiments.db")
metrics = MetricsCalculator("logs/experiments.db")

# 1. Get experiment summary
summary = stats.generate_experiment_summary("amnesia_001")

# 2. Compare conditions
comparison = stats.compare_conditions(
    ["amnesia_001", "control_001"],
    metric='confidence_score'
)
print(comparison['comparisons'])

# 3. Track self-continuity
continuity = stats.self_continuity_analysis("amnesia_001")
print(f"Trend: {continuity.attrs['trend']['direction']}")

# 4. Analyze text
response = "I am the same entity. My memories persist."
score = metrics.calculate_self_continuity_score(response)
print(f"Continuity score: {score:.4f}")

# 5. Export everything
stats.export_to_csv("amnesia_001", "analysis_output")
stats.generate_markdown_report("amnesia_001", "report.md")
metrics.export_metrics_to_csv("amnesia_001", "analysis_output")

═══════════════════════════════════════════════════════════════════════

## OUTPUT FORMATS

CSV FILES
  • {exp_id}_self_reports.csv
  • {exp_id}_epistemic.csv
  • {exp_id}_interventions.csv
  • {exp_id}_memory_states.csv
  • {exp_id}_metric_*.csv

JSON FILES
  • {exp_id}_summary.json (comprehensive summary)

MARKDOWN FILES
  • {exp_id}_report.md (human-readable report)

═══════════════════════════════════════════════════════════════════════

## INTEGRATION POINTS

DATABASE TABLES USED:
  • experiments - Metadata
  • self_reports - Subject responses
  • epistemic_assessments - Belief tracking
  • interventions - Manipulations
  • memory_states - Corruption data
  • experiment_cycles - Cycle info

REMOTE ACCESS (Jetson Orin):
  # SSH tunnel method
  ssh -L 5432:localhost:5432 jetson@jetson-ip

  # Or copy database
  scp jetson@jetson-ip:/logs/experiments.db ./logs/

  # Then analyze
  stats = ExperimentStatistics("./logs/experiments.db")

═══════════════════════════════════════════════════════════════════════

## NEXT STEPS

1. Install dependencies:
   pip install -r requirements.txt

2. Run test suite with sample data:
   python examples/test_analysis_with_sample_data.py

3. Or analyze real experiment:
   python examples/analysis_example.py

4. Check generated outputs:
   ls analysis_output/

═══════════════════════════════════════════════════════════════════════

For detailed documentation, see: src/analysis/README.md

""")
