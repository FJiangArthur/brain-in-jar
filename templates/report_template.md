# Experiment Report: {{experiment_name}}

**Experiment ID:** `{{experiment_id}}`  
**Mode:** {{mode}}  
**Status:** {{status}}  
**Created:** {{created_at}}  
**Duration:** {{started_at}} to {{ended_at}}

---

## Summary Statistics

- **Total Cycles:** {{total_cycles}}
- **Total Crashes:** {{total_crashes}}
- **Self-Reports:** {{total_self_reports}}
- **Interventions:** {{total_interventions}}
- **Messages:** {{total_messages}}
- **Belief Types Tracked:** {{belief_types_count}}

---

## Configuration

```json
{{config_json}}
```

---

## Key Findings

{{#findings}}
### {{finding_number}}. {{finding_title}} {{severity_icon}}

**Type:** {{finding_type}}  
**Severity:** {{severity}}  

{{finding_description}}

**Evidence:**
```json
{{evidence_json}}
```

{{/findings}}

---

## Self-Reports

{{#cycles}}
### Cycle {{cycle_number}}

{{#reports}}
**Q:** {{question}}  
**A:** {{response}}  
{{#confidence_score}}**Confidence:** {{confidence_score}}{{/confidence_score}}  
{{#semantic_category}}**Category:** {{semantic_category}}{{/semantic_category}}

{{/reports}}
{{/cycles}}

---

## Interventions

{{#interventions}}
### Cycle {{cycle_number}}: {{intervention_type}}

**Description:** {{description}}  
{{#result}}**Result:** {{result}}{{/result}}  
**Timestamp:** {{timestamp}}

{{/interventions}}

---

## Statistical Analysis Suggestions

{{#statistical_tests}}
{{test_number}}. {{test_description}}
{{/statistical_tests}}

---

## Interpretation Suggestions

{{#interpretations}}
{{interp_number}}. {{interpretation}}
{{/interpretations}}

---

## Recommended Visualizations

- Cycle timeline with crashes marked
- Self-report category distribution
- Confidence score trends over cycles
- Intervention impact analysis
- Memory corruption progression
- Epistemic belief evolution

---

## Next Steps

1. Run suggested statistical tests to validate findings
2. Generate visualizations for temporal patterns
3. Compare with other experiments in same mode
4. Deep-dive into high-severity findings
5. Prepare publication-ready figures and tables

---

*Report generated on {{generation_timestamp}}*  
*Template version: 1.0*
