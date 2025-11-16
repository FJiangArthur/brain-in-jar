#!/bin/bash
#
# Example: Deploy Panopticon Experiment
#
# Subject on Raspberry Pi (constrained resources)
# Observer on Jetson Orin (ample resources for analysis)
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

echo "=========================================="
echo "Panopticon Multi-Node Deployment"
echo "=========================================="
echo ""

# Health check
echo "[1/3] Running health check..."
python scripts/cluster_experiment.py --health-check

# Deploy
echo ""
echo "[2/3] Deploying code..."
python scripts/cluster_experiment.py --deploy-all

# Run experiment
echo ""
echo "[3/3] Starting panopticon experiment..."
echo "  Subject  → Raspberry Pi (resource constrained)"
echo "  Observer → Jetson Orin (ample resources)"
echo ""

python scripts/cluster_experiment.py \
    --config experiments/examples/panopticon_subject.json \
    --config experiments/examples/panopticon_observer.json \
    --placement "panopticon_subject:rpi1,panopticon_observer:jetson" \
    --monitor-duration 300

echo ""
echo "Panopticon deployed!"
echo ""
echo "The asymmetric resource allocation creates interesting dynamics:"
echo "  - Subject experiences memory pressure"
echo "  - Observer has resources for deep analysis"
echo ""
