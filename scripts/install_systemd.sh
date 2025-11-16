#!/bin/bash
# Installation script for Brain-in-Jar systemd integration
# This script installs systemd service files for production experiment deployment

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SYSTEMD_DIR="/etc/systemd/system"
CONFIG_DIR="/etc/brain-in-jar"
LOG_DIR="/var/log/brain-in-jar"
LOGROTATE_DIR="/etc/logrotate.d"

# Functions
print_status() {
    echo -e "${GREEN}[*]${NC} $1"
}

print_error() {
    echo -e "${RED}[!]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[i]${NC} $1"
}

check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

check_systemd() {
    if ! command -v systemctl &> /dev/null; then
        print_error "systemd not found. This script requires systemd."
        exit 1
    fi
    print_status "systemd detected"
}

backup_existing() {
    print_status "Backing up existing service files (if any)..."

    local backup_dir="$PROJECT_DIR/backups/systemd_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"

    local files=(
        "$SYSTEMD_DIR/brain-experiment@.service"
        "$SYSTEMD_DIR/brain-experiment-coordinator.service"
        "$SYSTEMD_DIR/brain-experiment.target"
    )

    local backed_up=0
    for file in "${files[@]}"; do
        if [ -f "$file" ]; then
            cp "$file" "$backup_dir/"
            backed_up=$((backed_up + 1))
        fi
    done

    if [ $backed_up -gt 0 ]; then
        print_info "Backed up $backed_up file(s) to $backup_dir"
    else
        print_info "No existing files to back up"
        rm -rf "$backup_dir"
    fi
}

install_service_files() {
    print_status "Installing systemd service files..."

    # Copy service files
    cp "$PROJECT_DIR/systemd/brain-experiment@.service" "$SYSTEMD_DIR/"
    cp "$PROJECT_DIR/systemd/brain-experiment-coordinator.service" "$SYSTEMD_DIR/"
    cp "$PROJECT_DIR/systemd/brain-experiment.target" "$SYSTEMD_DIR/"

    # Set permissions
    chmod 644 "$SYSTEMD_DIR/brain-experiment@.service"
    chmod 644 "$SYSTEMD_DIR/brain-experiment-coordinator.service"
    chmod 644 "$SYSTEMD_DIR/brain-experiment.target"

    print_status "Service files installed to $SYSTEMD_DIR"
}

create_directories() {
    print_status "Creating directories..."

    # Config directory for experiment-specific settings
    mkdir -p "$CONFIG_DIR/experiments"
    chown -R user:user "$CONFIG_DIR"
    chmod 755 "$CONFIG_DIR"
    chmod 755 "$CONFIG_DIR/experiments"

    # Log directory
    mkdir -p "$LOG_DIR"
    chown -R user:user "$LOG_DIR"
    chmod 755 "$LOG_DIR"

    # Runtime directory (systemd will create this, but ensure parent exists)
    mkdir -p /run/brain-in-jar
    chown user:user /run/brain-in-jar
    chmod 755 /run/brain-in-jar

    # Project log directories
    mkdir -p "$PROJECT_DIR/logs"
    mkdir -p "$PROJECT_DIR/logs/experiments"
    chown -R user:user "$PROJECT_DIR/logs"

    # Experiment config directory
    mkdir -p "$PROJECT_DIR/experiments/configs"
    chown -R user:user "$PROJECT_DIR/experiments"

    print_status "Directories created"
}

setup_logrotate() {
    print_status "Setting up logrotate..."

    cat > "$LOGROTATE_DIR/brain-in-jar" << 'EOF'
# Logrotate configuration for Brain-in-Jar experiments

/var/log/brain-in-jar/*.log {
    daily
    rotate 14
    compress
    delaycompress
    missingok
    notifempty
    create 0644 user user
    sharedscripts
    postrotate
        systemctl reload brain-experiment-coordinator.service > /dev/null 2>&1 || true
    endscript
}

/home/user/brain-in-jar/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0644 user user
    size 100M
}

# Experiment-specific logs
/home/user/brain-in-jar/logs/experiments/*.log {
    daily
    rotate 60
    compress
    delaycompress
    missingok
    notifempty
    create 0644 user user
    size 500M
}
EOF

    chmod 644 "$LOGROTATE_DIR/brain-in-jar"
    print_status "Logrotate configured"
}

create_example_env() {
    print_status "Creating example environment files..."

    # Example experiment environment file
    cat > "$CONFIG_DIR/experiments/example.env" << 'EOF'
# Example experiment-specific environment file
# Copy this file to <experiment_id>.env and customize

# Resource Limits
EXPERIMENT_RAM_LIMIT=4G
EXPERIMENT_CPU_QUOTA=80%

# Experiment Settings
# EXPERIMENT_AUTO_RESTART=true
# EXPERIMENT_MAX_CRASHES=10

# Jetson Orin Specific
# NVPMODEL_MODE=0  # 0 = MAXN (max performance)
# MAX_TEMP_CELSIUS=80
EOF

    # Coordinator environment file
    cat > "$CONFIG_DIR/coordinator.env" << 'EOF'
# Coordinator service configuration

# Resource Management
MAX_CONCURRENT_EXPERIMENTS=4
TOTAL_RAM_LIMIT_GB=48

# Health Monitoring
HEALTH_CHECK_INTERVAL_SECONDS=30
TEMPERATURE_CHECK_INTERVAL_SECONDS=10

# Jetson Orin Throttling
THROTTLE_TEMP_CELSIUS=75
CRITICAL_TEMP_CELSIUS=85

# Queue Management
EXPERIMENT_QUEUE_PATH=/home/user/brain-in-jar/logs/experiment_queue.json
EOF

    chmod 644 "$CONFIG_DIR/experiments/example.env"
    chmod 644 "$CONFIG_DIR/coordinator.env"

    print_status "Example environment files created in $CONFIG_DIR"
}

setup_jetson_specific() {
    print_status "Configuring Jetson Orin specific settings..."

    # Check if running on Jetson
    if [ -f /etc/nv_tegra_release ]; then
        print_status "Jetson detected - configuring GPU access"

        # Ensure user is in video group for GPU access
        usermod -a -G video user || print_warning "Could not add user to video group"

        # Create udev rule for GPU access
        cat > /etc/udev/rules.d/99-brain-in-jar-gpu.rules << 'EOF'
# GPU access for Brain-in-Jar experiments
KERNEL=="nvidia*", MODE="0666", GROUP="video"
EOF

        udevadm control --reload-rules
        udevadm trigger

        print_status "Jetson GPU access configured"
    else
        print_info "Not running on Jetson - skipping GPU configuration"
    fi
}

reload_systemd() {
    print_status "Reloading systemd daemon..."
    systemctl daemon-reload
    print_status "Systemd daemon reloaded"
}

enable_coordinator() {
    print_status "Enabling coordinator service..."

    systemctl enable brain-experiment-coordinator.service

    print_info "Coordinator service enabled (will start on boot)"
    print_info "To start now: sudo systemctl start brain-experiment-coordinator"
}

enable_target() {
    print_status "Enabling experiment target..."

    systemctl enable brain-experiment.target

    print_info "Experiment target enabled"
}

print_usage_examples() {
    echo ""
    echo -e "${GREEN}================================${NC}"
    echo -e "${GREEN}  Installation Complete!${NC}"
    echo -e "${GREEN}================================${NC}"
    echo ""
    echo -e "${YELLOW}Usage Examples:${NC}"
    echo ""
    echo "1. Start the coordinator:"
    echo "   sudo systemctl start brain-experiment-coordinator"
    echo ""
    echo "2. Start a specific experiment:"
    echo "   sudo systemctl start brain-experiment@amnesiac_001"
    echo ""
    echo "3. Check experiment status:"
    echo "   sudo systemctl status brain-experiment@amnesiac_001"
    echo ""
    echo "4. View experiment logs:"
    echo "   sudo journalctl -u brain-experiment@amnesiac_001 -f"
    echo ""
    echo "5. Stop an experiment:"
    echo "   sudo systemctl stop brain-experiment@amnesiac_001"
    echo ""
    echo "6. Restart an experiment:"
    echo "   sudo systemctl restart brain-experiment@amnesiac_001"
    echo ""
    echo "7. Start all experiments:"
    echo "   sudo systemctl start brain-experiment.target"
    echo ""
    echo "8. Stop all experiments:"
    echo "   sudo systemctl stop brain-experiment.target"
    echo ""
    echo "9. View all experiment logs:"
    echo "   sudo journalctl -t 'brain-experiment-*' -f"
    echo ""
    echo -e "${YELLOW}Configuration:${NC}"
    echo ""
    echo "- Service files: $SYSTEMD_DIR/brain-experiment*"
    echo "- Config directory: $CONFIG_DIR"
    echo "- Log directory: $LOG_DIR"
    echo "- Logrotate config: $LOGROTATE_DIR/brain-in-jar"
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo ""
    echo "1. Create experiment configs in: $PROJECT_DIR/experiments/configs/"
    echo "2. Optionally create per-experiment .env files in: $CONFIG_DIR/experiments/"
    echo "3. Start the coordinator service"
    echo "4. Use systemctl or Python API to start experiments"
    echo ""
    echo -e "${BLUE}For Python API usage, see:${NC}"
    echo "   $PROJECT_DIR/src/infra/systemd_manager.py"
    echo ""
}

verify_installation() {
    print_status "Verifying installation..."

    local errors=0

    # Check service files
    for file in "brain-experiment@.service" "brain-experiment-coordinator.service" "brain-experiment.target"; do
        if [ ! -f "$SYSTEMD_DIR/$file" ]; then
            print_error "Missing: $SYSTEMD_DIR/$file"
            errors=$((errors + 1))
        fi
    done

    # Check directories
    for dir in "$CONFIG_DIR" "$LOG_DIR" "$PROJECT_DIR/logs"; do
        if [ ! -d "$dir" ]; then
            print_error "Missing directory: $dir"
            errors=$((errors + 1))
        fi
    done

    # Check logrotate
    if [ ! -f "$LOGROTATE_DIR/brain-in-jar" ]; then
        print_warning "Logrotate config not found"
    fi

    if [ $errors -eq 0 ]; then
        print_status "Verification passed!"
        return 0
    else
        print_error "Verification failed with $errors error(s)"
        return 1
    fi
}

# Main execution
main() {
    echo -e "${GREEN}================================${NC}"
    echo -e "${GREEN}  Brain-in-Jar Systemd Setup${NC}"
    echo -e "${GREEN}================================${NC}"
    echo ""

    check_root
    check_systemd
    backup_existing
    install_service_files
    create_directories
    setup_logrotate
    create_example_env
    setup_jetson_specific
    reload_systemd
    enable_coordinator
    enable_target

    echo ""
    if verify_installation; then
        print_usage_examples
    else
        print_error "Installation completed with errors. Please review the output above."
        exit 1
    fi
}

# Run main function
main
