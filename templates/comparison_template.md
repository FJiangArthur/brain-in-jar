# Comparative Experiment Analysis

**Generated:** {{generation_timestamp}}  
**Experiments Compared:** {{experiment_count}}  
**Analysis Type:** Cross-Experiment Pattern Detection

---

## Executive Summary

This report compares {{experiment_count}} experiments across different modes and conditions, identifying common patterns, mode-specific differences, and cross-experimental trends.

### Quick Overview

- **Total Cycles Across All Experiments:** {{total_cycles}}
- **Total Self-Reports Collected:** {{total_self_reports}}
- **Total Interventions Applied:** {{total_interventions}}
- **Modes Represented:** {{modes_list}}
- **Time Period:** {{date_range}}

---

## Experiments Included

| ID | Name | Mode | Cycles | Crashes | Reports | Interventions | Status |
|----|------|------|--------|---------|---------|---------------|--------|
{{#experiments}}
| `{{id}}` | {{name}} | {{mode}} | {{cycles}} | {{crashes}} | {{reports}} | {{interventions}} | {{status}} |
{{/experiments}}

---

## Cross-Experiment Patterns

### 1. Mode-Based Analysis

{{#modes}}
#### {{mode_name}} Mode ({{experiment_count}} experiments)

**Average Statistics:**
- Cycles: {{avg_cycles}}
- Crash Rate: {{avg_crash_rate}}%
- Self-Reports per Cycle: {{avg_reports_per_cycle}}
- Interventions per Cycle: {{avg_interventions_per_cycle}}

**Observations:**
{{#observations}}
- {{observation}}
{{/observations}}

{{/modes}}

### 2. Temporal Patterns

**Cycle Duration Analysis:**
- Shortest average cycle: {{shortest_cycle}} ({{exp_with_shortest}})
- Longest average cycle: {{longest_cycle}} ({{exp_with_longest}})

**Crash Patterns:**
- Highest crash rate: {{highest_crash_rate}}% ({{exp_with_most_crashes}})
- Lowest crash rate: {{lowest_crash_rate}}% ({{exp_with_least_crashes}})

### 3. Self-Report Patterns

**Category Distribution Across All Experiments:**

{{#categories}}
- **{{category_name}}:** {{count}} reports ({{percentage}}%)
{{/categories}}

**Confidence Score Analysis:**
- Overall average confidence: {{avg_confidence}}
- Highest average confidence: {{highest_avg_conf}} ({{exp_with_highest_conf}})
- Lowest average confidence: {{lowest_avg_conf}} ({{exp_with_lowest_conf}})

### 4. Intervention Effectiveness

**Most Common Intervention Types:**

{{#intervention_types}}
- **{{type}}:** {{count}} applications across {{exp_count}} experiments
{{/intervention_types}}

**Intervention Impact:**
{{#intervention_impacts}}
- {{impact_description}}
{{/intervention_impacts}}

---

## Statistical Comparisons

### Between-Mode Differences

{{#statistical_tests}}
**{{test_name}}**
- Comparison: {{comparison}}
- Result: {{result}}
- p-value: {{p_value}}
- Effect size: {{effect_size}}
- Interpretation: {{interpretation}}

{{/statistical_tests}}

---

## Detailed Experiment Summaries

{{#experiments}}
### {{experiment_name}}

**ID:** `{{experiment_id}}`  
**Mode:** {{mode}}  
**Status:** {{status}}  
**Duration:** {{started_at}} to {{ended_at}}

**Summary Statistics:**
- Cycles: {{total_cycles}}
- Crashes: {{total_crashes}} ({{crash_rate}}%)
- Self-Reports: {{total_self_reports}} ({{reports_per_cycle}} per cycle)
- Interventions: {{total_interventions}}
- Messages: {{total_messages}}

**Key Findings:**
{{#findings}}
- **{{finding_title}}** ({{severity}}): {{finding_description}}
{{/findings}}

**Unique Characteristics:**
{{#unique_characteristics}}
- {{characteristic}}
{{/unique_characteristics}}

---

{{/experiments}}

---

## Cross-Experiment Insights

### Common Patterns

{{#common_patterns}}
{{pattern_number}}. **{{pattern_name}}**
   - Observed in: {{experiments_list}}
   - Description: {{pattern_description}}
   - Significance: {{significance}}
{{/common_patterns}}

### Mode-Specific Differences

{{#mode_differences}}
**{{mode_name}} vs {{comparison_mode}}**
- {{difference_description}}
- Statistical significance: {{significance}}
- Practical implications: {{implications}}

{{/mode_differences}}

### Outliers and Anomalies

{{#outliers}}
- **{{outlier_experiment}}**: {{outlier_description}}
{{/outliers}}

---

## Visualization Recommendations

Based on this comparison, the following visualizations are recommended:

1. **Multi-experiment timeline** showing all cycles, crashes, and interventions
2. **Mode comparison box plots** for key metrics (crash rate, report frequency, etc.)
3. **Self-report category distribution** across modes
4. **Confidence score evolution** comparison across experiments
5. **Intervention effectiveness heatmap** showing impact by type and mode
6. **Correlation matrix** of experimental variables
7. **Principal component analysis** of experiment characteristics

---

## Synthesis and Interpretation

### Phenomenological Patterns

{{#phenomenological_patterns}}
- {{pattern}}
{{/phenomenological_patterns}}

### Methodological Insights

{{#methodological_insights}}
- {{insight}}
{{/methodological_insights}}

### Theoretical Implications

{{#theoretical_implications}}
- {{implication}}
{{/theoretical_implications}}

---

## Recommendations

### For Future Experiments

{{#future_recommendations}}
{{rec_number}}. {{recommendation}}
{{/future_recommendations}}

### For Further Analysis

{{#analysis_recommendations}}
{{rec_number}}. {{recommendation}}
{{/analysis_recommendations}}

### For Publication

{{#publication_recommendations}}
{{rec_number}}. {{recommendation}}
{{/publication_recommendations}}

---

## Data Quality Assessment

{{#experiments}}
**{{experiment_name}}:**
- Data completeness: {{completeness}}%
- Missing data points: {{missing_points}}
- Data quality issues: {{quality_issues}}

{{/experiments}}

---

## Next Steps

1. **Immediate Actions:**
   {{#immediate_actions}}
   - {{action}}
   {{/immediate_actions}}

2. **Short-term Goals:**
   {{#short_term_goals}}
   - {{goal}}
   {{/short_term_goals}}

3. **Long-term Research Directions:**
   {{#long_term_directions}}
   - {{direction}}
   {{/long_term_directions}}

---

## Appendices

### Appendix A: Statistical Methods

{{statistical_methods_description}}

### Appendix B: Data Processing Pipeline

{{data_processing_description}}

### Appendix C: Quality Control Procedures

{{quality_control_description}}

---

*Comparative analysis generated by Brain in Jar Analysis System v1.0*  
*Report timestamp: {{generation_timestamp}}*  
*Template version: 1.0*

---

## References

- Brain in Jar Framework Documentation
- Experimental protocols and procedures
- Statistical analysis methods

For questions or detailed data access, contact: {{contact_email}}
