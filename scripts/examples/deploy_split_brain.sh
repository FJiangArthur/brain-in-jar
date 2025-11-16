#!/bin/bash
#
# Example: Deploy Split Brain Experiment Across Cluster
#
# This script demonstrates deploying a split brain experiment
# with Brain A on Jetson Orin (GPU) and Brain B on Raspberry Pi (CPU)
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

echo "=========================================="
echo "Split Brain Multi-Node Deployment"
echo "=========================================="
echo ""

# Step 1: Validate cluster configuration
echo "[1/5] Validating cluster configuration..."
python scripts/cluster_experiment.py --validate-config

# Step 2: Health check all nodes
echo ""
echo "[2/5] Running health check..."
python scripts/cluster_experiment.py --health-check

# Step 3: Deploy code to all nodes
echo ""
echo "[3/5] Deploying code to remote nodes..."
python scripts/cluster_experiment.py --deploy-all

# Step 4: Run split brain experiment
echo ""
echo "[4/5] Starting split brain experiment..."
echo "  Brain A (Original) → Jetson Orin AGX"
echo "  Brain B (Clone)    → Raspberry Pi 1"
echo ""

python scripts/cluster_experiment.py \
    --config experiments/examples/split_brain_001_brain_A.json \
    --config experiments/examples/split_brain_001_brain_B.json \
    --placement "split_brain_001_brain_A:jetson,split_brain_001_brain_B:rpi1" \
    --monitor-duration 300

# Step 5: Summary
echo ""
echo "[5/5] Deployment complete!"
echo ""
echo "To monitor experiments:"
echo "  - Jetson: ssh jetson@192.168.1.100"
echo "    tail -f ~/brain-in-jar/logs/split_brain_001_brain_A.log"
echo ""
echo "  - RPi: ssh pi@192.168.1.101"
echo "    tail -f ~/brain-in-jar/logs/split_brain_001_brain_B.log"
echo ""
echo "To fetch results:"
echo "  scp jetson@192.168.1.100:~/brain-in-jar/logs/experiments.db logs/jetson_experiments.db"
echo "  scp pi@192.168.1.101:~/brain-in-jar/logs/experiments.db logs/rpi1_experiments.db"
echo ""
