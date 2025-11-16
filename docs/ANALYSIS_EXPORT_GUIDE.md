# Analysis and Export Tools Guide

## Agent D4 - Workstream D: Analysis Tools

This guide covers the export and automated reporting tools built for the Brain in Jar Season 3 experiments.

---

## Overview

The analysis tools provide comprehensive export and reporting functionality for experiment data in multiple formats:

- **Export Formats:** CSV, JSON, Markdown, LaTeX, HTML
- **Report Types:** Automated analysis, comparative analysis, paper skeletons
- **Multi-Experiment:** Comparison tables, combined datasets
- **Jetson Orin Support:** Local and remote database access

---

## Files Created

### Core Modules

1. **`src/analysis/export.py`**
   - `ExperimentExporter` class
   - Single and multi-experiment export functions
   - Supports: CSV, JSON, Markdown, LaTeX, HTML

2. **`src/analysis/report_generator.py`**
   - `AutomaticReportGenerator` class
   - Auto-detected key findings
   - Statistical test suggestions
   - Interpretation recommendations
   - Paper skeleton generation

3. **`src/analysis/__init__.py`**
   - Module initialization
   - Graceful imports for optional dependencies

### CLI Tool

4. **`scripts/generate_report.py`**
   - Command-line interface for all export and report functions
   - Supports local and remote (SSH) databases
   - Multiple output formats
   - Batch processing

### Templates

5. **`templates/report_template.md`**
   - Markdown report template with placeholders

6. **`templates/paper_template.tex`**
   - LaTeX academic paper template
   - Pre-structured sections
   - Bibliography setup

7. **`templates/comparison_template.md`**
   - Multi-experiment comparison template
   - Statistical comparison sections

---

## Export Formats Supported

### 1. CSV Export
- **Use Case:** Excel, R, SPSS analysis
- **Format:** Flat table with all data types
- **Columns:** data_type, cycle_number, timestamp, content, metadata, confidence, category

```python
from src.analysis.export import ExperimentExporter

exporter = ExperimentExporter("logs/experiments.db")
csv_file = exporter.export_to_csv("exp_001", "output.csv")
```

**CLI:**
```bash
python scripts/generate_report.py --experiment exp_001 --format csv --output data.csv
```

### 2. JSON Export
- **Use Case:** Web tools, programmatic analysis
- **Format:** Structured JSON with nested data
- **Includes:** Experiment metadata, self-reports, interventions, messages

```python
json_file = exporter.export_to_json("exp_001", "output.json")
```

**CLI:**
```bash
python scripts/generate_report.py --experiment exp_001 --format json
```

### 3. Markdown Export
- **Use Case:** GitHub, documentation, quick review
- **Format:** Human-readable markdown with sections
- **Includes:** Summary stats, self-reports, interventions

```python
md_file = exporter.export_to_markdown("exp_001", "report.md")
```

**CLI:**
```bash
python scripts/generate_report.py --experiment exp_001 --format markdown
```

### 4. LaTeX Export
- **Use Case:** Academic papers
- **Format:** LaTeX tables and figures
- **Includes:** Summary tables, self-report tables, intervention tables

```python
tex_file = exporter.export_for_paper("exp_001", "tables.tex")
```

**CLI:**
```bash
python scripts/generate_report.py --experiment exp_001 --format latex
```

### 5. HTML Export
- **Use Case:** Web viewing, presentations
- **Format:** Styled HTML with embedded CSS
- **Features:** Color-coded findings, responsive design

```python
html_file = exporter.export_to_html("exp_001", "report.html")
```

**CLI:**
```bash
python scripts/generate_report.py --experiment exp_001 --format html
```

---

## Automated Report Generation

### Single Experiment Analysis Report

Automatically generates comprehensive analysis with:
- Executive summary
- Auto-detected key findings (with severity levels)
- Suggested statistical tests
- Interpretation suggestions
- Detailed data sections
- Next steps

```python
from src.analysis.report_generator import AutomaticReportGenerator

generator = AutomaticReportGenerator("logs/experiments.db")
report = generator.generate_markdown_report("exp_001", "analysis.md")
```

**CLI:**
```bash
python scripts/generate_report.py --experiment exp_001 --format report
```

**Key Features:**

1. **Auto-Detected Findings:**
   - Crash patterns (system stability)
   - Self-report patterns (category distribution)
   - Confidence analysis (epistemic uncertainty)
   - Intervention effectiveness
   - Temporal patterns

2. **Severity Levels:**
   - High (🔴): Critical issues requiring immediate attention
   - Medium (🟡): Important patterns worth investigating
   - Low (🟢): Informational findings

3. **Statistical Test Suggestions:**
   - Binomial tests for crash rates
   - Chi-square for category distributions
   - T-tests for confidence changes
   - ANOVA for intervention comparisons
   - Time series analysis

4. **Mode-Specific Interpretations:**
   - Amnesiac: Memory loss effects
   - Total Amnesiac: Baseline responses
   - Observed: Observer effects
   - Peer: Interaction patterns

### Multi-Experiment Comparison

Compare multiple experiments side-by-side:

```python
comparison = generator.generate_comparison_report(
    ["exp_001", "exp_002", "exp_003"],
    "comparison.md"
)
```

**CLI:**
```bash
python scripts/generate_report.py \
  --experiment exp_001 exp_002 exp_003 \
  --format comparison
```

### Paper Skeleton Generation

Generate LaTeX paper template with experiment data pre-filled:

```python
paper = generator.generate_paper_skeleton(
    ["exp_001", "exp_002"],
    "paper.tex"
)
```

**CLI:**
```bash
python scripts/generate_report.py \
  --experiment exp_001 exp_002 \
  --format paper \
  --output paper.tex
```

---

## Multi-Experiment Exports

### Comparison Table

Generate side-by-side comparison of experiments:

```python
comp_table = exporter.export_comparison_table(
    ["exp_001", "exp_002", "exp_003"],
    "comparison.md"
)
```

### Combined Dataset

Export multiple experiments into single dataset:

```python
dataset = exporter.export_dataset(
    ["exp_001", "exp_002", "exp_003"],
    "dataset.json"
)
```

**CLI:**
```bash
python scripts/generate_report.py \
  --experiment exp_001 exp_002 exp_003 \
  --format dataset
```

---

## CLI Tool Usage

### Basic Usage

```bash
python scripts/generate_report.py --experiment EXP_ID --format FORMAT
```

### Options

- `--experiment, -e`: Experiment ID(s) to process (required)
- `--format, -f`: Output format (csv, json, markdown, latex, html, report, paper, comparison, dataset, all)
- `--output, -o`: Output file path (auto-generated if not specified)
- `--output-dir, -d`: Output directory (default: current directory)
- `--db`: Database path (default: logs/experiments.db)
- `--db-ssh`: SSH connection for remote database
- `--verbose, -v`: Verbose output
- `--list-experiments, -l`: List available experiments
- `--templates-dir`: Templates directory

### Examples

**Generate all formats for single experiment:**
```bash
python scripts/generate_report.py \
  --experiment amnesiac_total_001 \
  --format all \
  --output-dir ./reports/
```

**Compare multiple experiments:**
```bash
python scripts/generate_report.py \
  --experiment exp_001 exp_002 exp_003 \
  --format comparison \
  --output comparison_report.md
```

**Generate paper skeleton:**
```bash
python scripts/generate_report.py \
  --experiment exp_001 exp_002 \
  --format paper \
  --output paper.tex
```

**Export to CSV for R analysis:**
```bash
python scripts/generate_report.py \
  --experiment exp_001 \
  --format csv \
  --output data_for_r.csv
```

**Remote Jetson Orin database access:**
```bash
python scripts/generate_report.py \
  --experiment exp_001 \
  --format markdown \
  --db-ssh jetson@192.168.1.100
```

---

## Jetson Orin Integration

### Local Mode
Run exports directly on Jetson Orin:
```bash
# On Jetson Orin
python scripts/generate_report.py \
  --experiment exp_001 \
  --format html \
  --output /var/www/html/reports/exp_001.html
```

### Remote Mode
Access Jetson database from remote machine:
```bash
# Copy database
scp jetson@192.168.1.100:~/brain-in-jar/logs/experiments.db ./remote_db.db

# Generate reports locally
python scripts/generate_report.py \
  --experiment exp_001 \
  --format all \
  --db ./remote_db.db
```

### SSH Mode (Planned)
```bash
python scripts/generate_report.py \
  --experiment exp_001 \
  --format report \
  --db-ssh jetson@192.168.1.100
```

---

## Example Generated Report

Here's what an automated analysis report includes:

```markdown
# Automated Analysis Report: Test Amnesiac Experiment

**Generated:** 2025-11-16 07:21:41
**Experiment ID:** `test_amnesiac_001`
**Mode:** amnesiac
**Status:** completed

## Executive Summary

This report provides an automated analysis of experiment `test_amnesiac_001` 
conducted in **amnesiac** mode. The experiment ran for **5 cycles** with 
**2 crashes**, collecting **10 self-reports** and applying **1 interventions**.

### Quick Stats
- **Cycles:** 5
- **Crashes:** 2
- **Self-Reports:** 10
- **Interventions:** 1

## Key Findings

### 1. System Stability Analysis 🟡
**Type:** crash_pattern
**Severity:** medium

Crash rate of 40.00% (2 crashes in 5 cycles)

### 2. Phenomenological Response Patterns 🟡
Most common report categories: memory_continuity (5), phenomenological_state (5)

### 3. Self-Report Confidence Analysis 🟡
Average confidence score: 0.50 across 10 reports

## Suggested Statistical Analyses
1. Binomial test for crash rate significance
2. Chi-square test for category distribution uniformity
3. T-test for confidence score changes over time
...

## Interpretation Suggestions
1. Consider how memory loss affects self-report consistency
2. Analyze whether amnesiac state leads to divergent reports
3. Low confidence scores suggest epistemic uncertainty
...
```

---

## Template Customization

Templates use Mustache-style placeholders:

### Markdown Template Variables
- `{{experiment_name}}`, `{{experiment_id}}`
- `{{mode}}`, `{{status}}`
- `{{total_cycles}}`, `{{total_crashes}}`
- `{{#findings}}...{{/findings}}` (loops)

### LaTeX Template Variables
- `{{paper_title}}`, `{{author_names}}`
- `{{total_experiments}}`
- `{{#experiments}}...{{/experiments}}` (loops)

To customize, edit files in `templates/` directory.

---

## Example Workflow

### Research Paper Workflow

```bash
# 1. Run experiments
python src/runner/experiment_runner.py --mode amnesiac --cycles 10

# 2. Generate analysis reports for each experiment
for exp in exp_001 exp_002 exp_003; do
  python scripts/generate_report.py \
    --experiment $exp \
    --format report \
    --output-dir ./analysis/
done

# 3. Generate comparison
python scripts/generate_report.py \
  --experiment exp_001 exp_002 exp_003 \
  --format comparison \
  --output ./analysis/comparison.md

# 4. Generate paper skeleton
python scripts/generate_report.py \
  --experiment exp_001 exp_002 exp_003 \
  --format paper \
  --output ./paper/manuscript.tex

# 5. Export data for statistical analysis
python scripts/generate_report.py \
  --experiment exp_001 exp_002 exp_003 \
  --format dataset \
  --output ./data/combined_data.json

# 6. Generate web-viewable reports
for exp in exp_001 exp_002 exp_003; do
  python scripts/generate_report.py \
    --experiment $exp \
    --format html \
    --output-dir /var/www/html/experiments/
done
```

---

## Testing

Run the demo to test all functionality:

```bash
python test_export_demo.py
```

This creates sample experiments and generates all export formats:
- `test_outputs/exports/` - CSV, JSON, Markdown, LaTeX, HTML
- `test_outputs/reports/` - Analysis reports, comparisons
- `test_outputs/papers/` - Paper skeleton

---

## Dependencies

Required Python packages:
- Standard library: `csv`, `json`, `os`, `datetime`, `pathlib`, `argparse`
- No external dependencies required

Optional (for enhanced features):
- `jq` - JSON viewing/processing
- LaTeX distribution - PDF generation from .tex files

---

## API Reference

### ExperimentExporter

```python
class ExperimentExporter:
    def __init__(self, db_path: str = "logs/experiments.db")
    
    # Single experiment exports
    def export_to_csv(self, exp_id: str, output_path: str = None) -> str
    def export_to_json(self, exp_id: str, output_path: str = None) -> str
    def export_to_markdown(self, exp_id: str, output_path: str = None) -> str
    def export_for_paper(self, exp_id: str, output_path: str = None) -> str
    def export_to_html(self, exp_id: str, output_path: str = None) -> str
    
    # Multi-experiment exports
    def export_comparison_table(self, exp_ids: List[str], 
                                output_path: str = None) -> str
    def export_dataset(self, exp_ids: List[str], 
                      output_path: str = None) -> str
```

### AutomaticReportGenerator

```python
class AutomaticReportGenerator:
    def __init__(self, db_path: str = "logs/experiments.db",
                 templates_dir: str = "templates")
    
    def generate_markdown_report(self, exp_id: str,
                                 output_path: str = None) -> str
    
    def generate_paper_skeleton(self, exp_ids: List[str],
                               output_path: str = None) -> str
    
    def generate_comparison_report(self, exp_ids: List[str],
                                  output_path: str = None) -> str
```

---

## Troubleshooting

### Database Not Found
```bash
Error: [Errno 2] No such file or directory: 'logs/experiments.db'
```
Solution: Specify correct database path with `--db` option

### Experiment Not Found
```bash
Error: Experiment 'exp_001' not found in database
```
Solution: Use `--list-experiments` to see available experiments

### Permission Denied
```bash
Error: [Errno 13] Permission denied: '/var/www/html/report.html'
```
Solution: Ensure write permissions for output directory

---

## Future Enhancements

Potential additions:
- PDF generation from HTML/LaTeX
- Interactive web dashboard
- Real-time report updates
- Email report delivery
- Cloud storage integration
- Advanced statistical analysis integration
- Visualization embedding in reports

---

## Contact

For issues or questions about the analysis tools:
- Check experiment logs in `logs/`
- Review database schema in `src/db/experiment_database.py`
- Consult main README in project root

---

*Documentation for Brain in Jar Season 3 - Agent D4 (Analysis Tools)*
