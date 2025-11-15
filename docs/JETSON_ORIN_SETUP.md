# Jetson Orin AGX Setup Guide for Brain in a Jar

This guide provides step-by-step instructions for setting up Brain in a Jar on an NVIDIA Jetson Orin AGX with 64GB RAM.

## Hardware Requirements

- **NVIDIA Jetson Orin AGX** with 64GB RAM
- **Storage**: 128GB+ NVMe SSD (recommended)
- **Network**: Ethernet or WiFi connection
- **Power**: Official Jetson power supply

## System Specifications

The Jetson Orin AGX provides excellent performance for running larger language models:
- **RAM**: 64GB LPDDR5
- **CPU**: 12-core ARM Cortex-A78AE
- **GPU**: NVIDIA Ampere with 2048 CUDA cores
- **AI Performance**: Up to 275 TOPS

## Initial Setup

### 1. Flash JetPack

1. Download the latest JetPack from NVIDIA:
   ```bash
   # JetPack 5.1.2 or later recommended
   ```

2. Flash the Jetson using NVIDIA SDK Manager or SD card image

3. Complete initial setup and create user account

### 2. System Updates

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install essential build tools
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
    python3-certbot-nginx

# Install CUDA toolkit (if not already installed)
sudo apt install -y nvidia-jetpack
```

### 3. Install Python Dependencies

```bash
# Create project directory
mkdir -p ~/projects
cd ~/projects

# Clone repository
git clone https://github.com/yourusername/brain-in-jar.git
cd brain-in-jar

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel
```

### 4. Install llama-cpp-python with CUDA Support

The Jetson Orin AGX has a powerful GPU. We'll compile llama-cpp-python with CUDA support:

```bash
# Install CUDA-enabled version
CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python --force-reinstall --no-cache-dir

# Verify CUDA support
python3 -c "from llama_cpp import Llama; print('CUDA available')"
```

### 5. Install Other Dependencies

```bash
# Install all requirements
pip install -r requirements.txt

# Install package
pip install -e .
```

### 6. Download Models

Download GGUF models optimized for the Jetson:

```bash
# Create models directory
mkdir -p models

# Download a 7B model (recommended for Jetson Orin AGX)
cd models

# Option 1: Mistral 7B (Recommended)
wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q5_K_M.gguf

# Option 2: Llama 3.1 8B
wget https://huggingface.co/TheBloke/Meta-Llama-3.1-8B-Instruct-GGUF/resolve/main/meta-llama-3.1-8b-instruct.Q5_K_M.gguf

# Option 3: Qwen 14B (uses more RAM but excellent performance)
wget https://huggingface.co/TheBloke/Qwen-14B-Chat-GGUF/resolve/main/qwen-14b-chat.Q4_K_M.gguf

cd ..
```

## Configuration

### 1. Environment Configuration

Create environment file for security:

```bash
# Create .env file
cat > .env << 'EOF'
# Security settings
BRAIN_JAR_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
BRAIN_JAR_JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")

# Generate password hash (change "your_secure_password" to your actual password)
BRAIN_JAR_PASSWORD_HASH=$(python3 -c "import hashlib; print(hashlib.sha256('your_secure_password'.encode()).hexdigest())")

# Optional: API keys (comma-separated)
BRAIN_JAR_API_KEYS=

# Web server settings
WEB_HOST=0.0.0.0
WEB_PORT=5000
EOF

# Generate actual secrets
python3 << 'PYTHON'
import secrets
import hashlib

# Generate new secrets
secret_key = secrets.token_hex(32)
jwt_secret = secrets.token_hex(32)

# Default password (CHANGE THIS!)
password = "change_me_immediately"
password_hash = hashlib.sha256(password.encode()).hexdigest()

print(f"\nAdd these to your .env file:")
print(f"BRAIN_JAR_SECRET_KEY={secret_key}")
print(f"BRAIN_JAR_JWT_SECRET={jwt_secret}")
print(f"BRAIN_JAR_PASSWORD_HASH={password_hash}")
print(f"\nDefault password: {password}")
print("CHANGE THE PASSWORD IMMEDIATELY AFTER FIRST LOGIN!")
PYTHON
```

### 2. RAM Limits Configuration

For Jetson Orin AGX with 64GB RAM, you can run multiple instances or larger models:

```bash
# Example configuration for multiple instances:
# - Observer (GOD mode): 20GB RAM
# - Subject: 15GB RAM
# - Observer AI: 15GB RAM
# This leaves ~14GB for system and other processes
```

## Running the System

### 1. Test Basic Functionality

```bash
# Activate virtual environment
source venv/bin/activate

# Test single instance
python3 -m src.core.neural_link \
    --model models/mistral-7b-instruct-v0.2.Q5_K_M.gguf \
    --mode isolated \
    --ram-limit 10.0
```

### 2. Run Web Monitoring Interface

```bash
# Start web server (in separate terminal)
cd ~/projects/brain-in-jar
source venv/bin/activate
python3 -m src.web.web_server

# Web interface will be available at http://jetson-ip:5000
```

### 3. Run Full Experiment with Web Monitoring

Create a launcher script:

```bash
cat > run_with_web.sh << 'EOF'
#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Start web server in background
python3 -m src.web.web_server &
WEB_PID=$!

# Wait for web server to start
sleep 3

# Start neural link experiment
python3 -m src.scripts.run_experiment_with_web

# Cleanup on exit
trap "kill $WEB_PID" EXIT
EOF

chmod +x run_with_web.sh
./run_with_web.sh
```

## Systemd Service Setup

Create a systemd service for automatic startup:

```bash
sudo tee /etc/systemd/system/brain-in-jar.service > /dev/null << EOF
[Unit]
Description=Brain in a Jar - Neural Link Experiment
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$HOME/projects/brain-in-jar
Environment="PATH=$HOME/projects/brain-in-jar/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
EnvironmentFile=$HOME/projects/brain-in-jar/.env
ExecStart=$HOME/projects/brain-in-jar/venv/bin/python3 -m src.web.web_server
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable brain-in-jar
sudo systemctl start brain-in-jar

# Check status
sudo systemctl status brain-in-jar

# View logs
sudo journalctl -u brain-in-jar -f
```

## Nginx Reverse Proxy Setup

Setup Nginx as a reverse proxy for better performance and security:

```bash
sudo tee /etc/nginx/sites-available/brain-in-jar > /dev/null << 'EOF'
server {
    listen 80;
    server_name your-domain.com;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
    limit_req_zone $binary_remote_addr zone=api:10m rate=30r/m;

    location /login {
        limit_req zone=login burst=3 nodelay;
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/ {
        limit_req zone=api burst=10 nodelay;
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket support
    location /socket.io/ {
        proxy_pass http://127.0.0.1:5000/socket.io/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Enable site
sudo ln -sf /etc/nginx/sites-available/brain-in-jar /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Performance Optimization

### 1. CPU Governor

```bash
# Set performance mode
sudo nvpmodel -m 0
sudo jetson_clocks

# Make it persistent
echo "sudo nvpmodel -m 0" | sudo tee -a /etc/rc.local
echo "sudo jetson_clocks" | sudo tee -a /etc/rc.local
```

### 2. Swap Configuration

```bash
# Disable zram and create swap file
sudo systemctl disable nvzramconfig

# Create 32GB swap file
sudo fallocate -l 32G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# Configure swappiness
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

### 3. Model Optimization

For best performance on Jetson Orin AGX:
- Use **Q5_K_M** or **Q4_K_M** quantized models
- Models up to 13B parameters work well
- Enable GPU acceleration (CUDA)
- Use `n_gpu_layers=-1` to offload all layers to GPU

## Monitoring

### System Monitoring

```bash
# Watch GPU/CPU usage
sudo tegrastats

# Or install jtop
sudo pip3 install -U jetson-stats
sudo jtop

# Monitor memory
watch -n 1 free -h

# Monitor temperatures
watch -n 1 'cat /sys/class/thermal/thermal_zone*/temp'
```

### Application Monitoring

- Access web interface: `http://your-jetson-ip:5000`
- View logs: `sudo journalctl -u brain-in-jar -f`
- Check processes: `htop`

## Troubleshooting

### Out of Memory Issues

```bash
# Check memory usage
free -h

# Check swap
swapon --show

# Reduce RAM limits in configuration
# Edit the neural_link.py arguments
```

### CUDA Not Available

```bash
# Check CUDA installation
nvidia-smi

# Reinstall llama-cpp-python with CUDA
pip uninstall llama-cpp-python
CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python --force-reinstall --no-cache-dir
```

### Web Interface Not Accessible

```bash
# Check if service is running
sudo systemctl status brain-in-jar

# Check if port is listening
sudo netstat -tlnp | grep 5000

# Check nginx
sudo nginx -t
sudo systemctl status nginx

# Check firewall
sudo ufw status
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

## Security Recommendations

1. **Change default password** immediately after setup
2. **Use strong passwords** (20+ characters)
3. **Enable UFW firewall**
4. **Setup SSL/TLS** with Let's Encrypt
5. **Use Cloudflare** for additional protection
6. **Regular updates**: `sudo apt update && sudo apt upgrade`
7. **Monitor logs** regularly
8. **Disable SSH password auth**, use keys only

## Next Steps

See `CLOUDFLARE_SETUP.md` for instructions on:
- Setting up Cloudflare tunnel
- Enabling HTTPS
- Advanced security features
- CDN configuration
