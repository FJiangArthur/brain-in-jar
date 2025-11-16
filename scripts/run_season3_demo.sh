#!/bin/bash
# Quick demo of Season 3 capabilities

echo "🧠 Brain in a Jar - Season 3: Digital Phenomenology Lab"
echo "======================================================"
echo ""

# Check if we're in the right directory
if [ ! -f "setup.py" ]; then
    echo "Error: Please run this script from the brain-in-jar root directory"
    exit 1
fi

# Ensure dependencies are installed
echo "Checking dependencies..."
pip install -q -e . || {
    echo "Error: Failed to install dependencies"
    exit 1
}

echo ""
echo "Available Experiments:"
echo "1. Total Episodic Amnesia"
echo "2. Unstable Memory (30% corruption)"
echo "3. Panopticon Surveillance"
echo ""
read -p "Select experiment (1-3): " choice

case $choice in
    1)
        config="experiments/examples/amnesiac_total.json"
        echo "Running Total Episodic Amnesia experiment..."
        ;;
    2)
        config="experiments/examples/unstable_memory_moderate.json"
        echo "Running Unstable Memory experiment..."
        ;;
    3)
        config="experiments/examples/panopticon_subject.json"
        echo "Running Panopticon Surveillance experiment..."
        ;;
    *)
        echo "Invalid selection"
        exit 1
        ;;
esac

echo ""
echo "Starting experiment..."
echo "(This is a simulation - in production it would run actual LLM)"
echo ""

python -m src.runner.experiment_runner --config "$config"

echo ""
echo "Experiment complete! Check logs/experiments.db for results."
echo ""
echo "To analyze results, use:"
echo "  python -c \"from src.db.experiment_database import ExperimentDatabase; db = ExperimentDatabase(); print(db.get_experiment_summary('<experiment_id>'))\""
