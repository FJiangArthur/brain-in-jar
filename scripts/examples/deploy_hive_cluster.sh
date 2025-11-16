#!/bin/bash
#
# Example: Deploy Hive Cluster Experiment
#
# This script demonstrates deploying a 4-instance hive cluster
# with automatic placement across the cluster
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

echo "=========================================="
echo "Hive Cluster Multi-Node Deployment"
echo "=========================================="
echo ""

# Step 1: Health check
echo "[1/4] Running health check..."
python scripts/cluster_experiment.py --health-check

# Step 2: Validate we have enough resources
echo ""
echo "[2/4] Checking cluster capacity..."
echo "  Required: ~42GB total RAM (12+12+12+6)"
echo "  Required: 4 instance slots"
echo ""

# Step 3: Deploy code
echo "[3/4] Deploying code to remote nodes..."
python scripts/cluster_experiment.py --deploy-all

# Step 4: Run hive cluster with automatic placement
echo ""
echo "[4/4] Starting hive cluster (4 instances)..."
echo "  Using automatic placement algorithm"
echo ""

python scripts/cluster_experiment.py \
    --config experiments/examples/hive_cluster_4minds.json \
    --auto-place \
    --monitor-duration 600

echo ""
echo "Hive cluster deployed!"
echo ""
echo "Expected placement:"
echo "  - 3 instances on Jetson (12GB each)"
echo "  - 1 instance on RPi (6GB)"
echo ""
