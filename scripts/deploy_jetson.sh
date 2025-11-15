#!/bin/bash
# Deployment script for Brain in a Jar on Jetson Orin AGX
# This script automates the installation and setup process

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="$HOME/projects/brain-in-jar"
VENV_DIR="$PROJECT_DIR/venv"
MODELS_DIR="$PROJECT_DIR/models"

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

check_jetson() {
    print_status "Checking if running on Jetson..."
    if [ -f /etc/nv_tegra_release ]; then
        print_status "Jetson detected!"
        cat /etc/nv_tegra_release
    else
        print_warning "Not running on Jetson hardware, continuing anyway..."
    fi
}

install_system_packages() {
    print_status "Installing system packages..."
    sudo apt update
    sudo apt install -y \
        build-essential \
        git \
        cmake \
        python3-pip \
        python3-dev \
        python3-venv \
        curl \
        wget \
        htop \
        tmux \
        nginx \
        certbot \
        python3-certbot-nginx \
        sqlite3 \
        || { print_error "Failed to install system packages"; exit 1; }
}

setup_project_directory() {
    print_status "Setting up project directory..."

    if [ ! -d "$PROJECT_DIR" ]; then
        mkdir -p "$(dirname $PROJECT_DIR)"
        print_status "Created project directory: $PROJECT_DIR"
    else
        print_status "Project directory exists: $PROJECT_DIR"
    fi

    cd "$PROJECT_DIR"
}

create_virtual_environment() {
    print_status "Creating Python virtual environment..."

    if [ -d "$VENV_DIR" ]; then
        print_warning "Virtual environment already exists, skipping..."
    else
        python3 -m venv "$VENV_DIR"
        print_status "Virtual environment created at $VENV_DIR"
    fi

    source "$VENV_DIR/bin/activate"
    pip install --upgrade pip setuptools wheel
}

install_llama_cpp() {
    print_status "Installing llama-cpp-python with CUDA support..."

    # Check if CUDA is available
    if command -v nvidia-smi &> /dev/null; then
        print_status "CUDA detected, installing with GPU support..."
        CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python --force-reinstall --no-cache-dir
    else
        print_warning "CUDA not detected, installing CPU-only version..."
        pip install llama-cpp-python
    fi
}

install_python_dependencies() {
    print_status "Installing Python dependencies..."

    source "$VENV_DIR/bin/activate"

    if [ -f "$PROJECT_DIR/requirements.txt" ]; then
        pip install -r "$PROJECT_DIR/requirements.txt"
        pip install -e "$PROJECT_DIR"
    else
        print_error "requirements.txt not found!"
        exit 1
    fi
}

download_models() {
    print_status "Setting up models directory..."
    mkdir -p "$MODELS_DIR"

    print_warning "Would you like to download a model? (y/n)"
    read -r response

    if [[ "$response" =~ ^[Yy]$ ]]; then
        print_status "Downloading Mistral 7B Q5_K_M model..."
        cd "$MODELS_DIR"

        MODEL_URL="https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q5_K_M.gguf"
        MODEL_FILE="mistral-7b-instruct-v0.2.Q5_K_M.gguf"

        if [ -f "$MODEL_FILE" ]; then
            print_warning "Model already exists, skipping download..."
        else
            wget "$MODEL_URL" -O "$MODEL_FILE" || print_error "Failed to download model"
        fi

        cd "$PROJECT_DIR"
    else
        print_warning "Skipping model download. You'll need to download a model manually."
        print_warning "Place GGUF models in: $MODELS_DIR"
    fi
}

generate_secrets() {
    print_status "Generating security secrets..."

    cd "$PROJECT_DIR"

    python3 << 'PYTHON'
import secrets
import hashlib
import os

# Generate secrets
secret_key = secrets.token_hex(32)
jwt_secret = secrets.token_hex(32)

# Generate default password
default_password = secrets.token_urlsafe(16)
password_hash = hashlib.sha256(default_password.encode()).hexdigest()

# Write to .env file
with open('.env', 'w') as f:
    f.write(f'# Security settings\n')
    f.write(f'BRAIN_JAR_SECRET_KEY={secret_key}\n')
    f.write(f'BRAIN_JAR_JWT_SECRET={jwt_secret}\n')
    f.write(f'BRAIN_JAR_PASSWORD_HASH={password_hash}\n')
    f.write(f'\n')
    f.write(f'# Web server settings\n')
    f.write(f'WEB_HOST=0.0.0.0\n')
    f.write(f'WEB_PORT=5000\n')

# Save password to separate file
with open('.initial_password.txt', 'w') as f:
    f.write(f'INITIAL PASSWORD: {default_password}\n')
    f.write(f'\nPLEASE CHANGE THIS PASSWORD IMMEDIATELY AFTER FIRST LOGIN!\n')
    f.write(f'Access the web interface and change the password in settings.\n')

os.chmod('.initial_password.txt', 0o600)

print(f'\n{"="*60}')
print(f'IMPORTANT: Your initial password is: {default_password}')
print(f'{"="*60}')
print(f'This password has been saved to: .initial_password.txt')
print(f'CHANGE IT IMMEDIATELY AFTER FIRST LOGIN!')
print(f'{"="*60}\n')
PYTHON

    print_status "Secrets generated and saved to .env"
}

create_directories() {
    print_status "Creating necessary directories..."
    mkdir -p "$PROJECT_DIR/logs"
    mkdir -p "$PROJECT_DIR/logs/model_io"
    mkdir -p "$PROJECT_DIR/backups"
}

setup_systemd_service() {
    print_status "Setting up systemd service..."

    SERVICE_FILE="/etc/systemd/system/brain-in-jar.service"

    sudo tee "$SERVICE_FILE" > /dev/null << EOF
[Unit]
Description=Brain in a Jar - Neural Link Experiment
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$VENV_DIR/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
EnvironmentFile=$PROJECT_DIR/.env
ExecStart=$VENV_DIR/bin/python3 -m src.web.web_server
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    print_status "Systemd service created: brain-in-jar.service"
}

enable_performance_mode() {
    print_status "Enabling performance mode..."

    if command -v nvpmodel &> /dev/null; then
        sudo nvpmodel -m 0
        sudo jetson_clocks
        print_status "Performance mode enabled"
    else
        print_warning "nvpmodel not found, skipping performance mode setup"
    fi
}

setup_swap() {
    print_status "Checking swap configuration..."

    SWAP_SIZE="32G"
    SWAP_FILE="/swapfile"

    if [ -f "$SWAP_FILE" ]; then
        print_warning "Swap file already exists, skipping..."
    else
        print_warning "Creating 32GB swap file (this may take a while)..."
        sudo fallocate -l "$SWAP_SIZE" "$SWAP_FILE"
        sudo chmod 600 "$SWAP_FILE"
        sudo mkswap "$SWAP_FILE"
        sudo swapon "$SWAP_FILE"

        # Make permanent
        if ! grep -q "$SWAP_FILE" /etc/fstab; then
            echo "$SWAP_FILE none swap sw 0 0" | sudo tee -a /etc/fstab
        fi

        # Set swappiness
        if ! grep -q "vm.swappiness" /etc/sysctl.conf; then
            echo "vm.swappiness=10" | sudo tee -a /etc/sysctl.conf
            sudo sysctl -p
        fi

        print_status "Swap configured: 32GB"
    fi
}

create_run_script() {
    print_status "Creating run script..."

    cat > "$PROJECT_DIR/run.sh" << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python3 -m src.web.web_server
EOF

    chmod +x "$PROJECT_DIR/run.sh"
    print_status "Run script created: $PROJECT_DIR/run.sh"
}

print_summary() {
    print_status "Installation complete!"
    echo ""
    echo -e "${GREEN}================================${NC}"
    echo -e "${GREEN}  Brain in a Jar - Jetson Setup${NC}"
    echo -e "${GREEN}================================${NC}"
    echo ""
    echo "Project directory: $PROJECT_DIR"
    echo "Virtual environment: $VENV_DIR"
    echo "Models directory: $MODELS_DIR"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo ""
    echo "1. View your initial password:"
    echo "   cat $PROJECT_DIR/.initial_password.txt"
    echo ""
    echo "2. Start the web server:"
    echo "   sudo systemctl start brain-in-jar"
    echo "   sudo systemctl enable brain-in-jar"
    echo ""
    echo "3. Check status:"
    echo "   sudo systemctl status brain-in-jar"
    echo ""
    echo "4. View logs:"
    echo "   sudo journalctl -u brain-in-jar -f"
    echo ""
    echo "5. Access web interface:"
    echo "   http://$(hostname -I | awk '{print $1}'):5000"
    echo ""
    echo -e "${YELLOW}For Cloudflare setup, see:${NC}"
    echo "   $PROJECT_DIR/docs/CLOUDFLARE_SETUP.md"
    echo ""
    echo -e "${RED}IMPORTANT: Change your password after first login!${NC}"
    echo ""
}

# Main execution
main() {
    echo -e "${GREEN}================================${NC}"
    echo -e "${GREEN}  Brain in a Jar - Deployment  ${NC}"
    echo -e "${GREEN}================================${NC}"
    echo ""

    check_jetson
    install_system_packages
    setup_project_directory
    create_virtual_environment
    install_llama_cpp
    install_python_dependencies
    download_models
    generate_secrets
    create_directories
    setup_systemd_service
    enable_performance_mode
    setup_swap
    create_run_script
    print_summary
}

# Run main function
main
