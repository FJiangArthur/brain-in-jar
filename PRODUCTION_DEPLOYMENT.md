# Brain in a Jar - Production Deployment Guide

Complete guide for deploying Brain in a Jar as a production service on Jetson Orin AGX with automatic startup, persistent logging, and secure remote access via Cloudflare Tunnel.

## Table of Contents

- [Overview](#overview)
- [System Requirements](#system-requirements)
- [Architecture](#architecture)
- [Installation](#installation)
- [Service Configuration](#service-configuration)
- [Cloudflare Tunnel Setup](#cloudflare-tunnel-setup)
- [Monitoring and Logs](#monitoring-and-logs)
- [Maintenance](#maintenance)
- [Troubleshooting](#troubleshooting)
- [Security Considerations](#security-considerations)

---

## Overview

This deployment configuration runs Brain in a Jar as a **systemd service** that:

- ✅ **Auto-starts on system boot** - Service enabled with systemd
- ✅ **Auto-restarts on crashes** - Resilient to failures
- ✅ **Persists all logs and conversations** - SQLite DB + file-based logging
- ✅ **Exposes web interface on port 8095** - Configured for Cloudflare Tunnel
- ✅ **Runs Matrix mode by default** - Three AI instances (Subject, Observer, GOD)
- ✅ **Secure localhost-only binding** - Not exposed directly to network

---

## System Requirements

### Hardware
- **Jetson Orin AGX** (32GB or 64GB RAM recommended)
- **Storage**: 50GB+ free space for models and logs
- **GPU**: CUDA-capable (automatically utilized by llama-cpp-python)

### Software
- **OS**: Ubuntu 20.04+ (JetPack 5.x or 6.x)
- **Python**: 3.8+
- **Network**: Internet connection for Cloudflare Tunnel

### Models
- GGUF format language models (2B-14B parameters)
- Stored in `models/` directory
- Default: `mistral-7b-instruct-v0.2.Q4_K_M.gguf`

---

## Architecture

### Service Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Internet                             │
│                            ↓                                 │
│                   Cloudflare Network                         │
│                   (DDoS Protection, SSL)                     │
│                            ↓                                 │
│                   Cloudflare Tunnel                          │
│                   (cloudflared daemon)                       │
└─────────────────────────────────────────────────────────────┘
                             ↓
                    localhost:8095
                             ↓
┌─────────────────────────────────────────────────────────────┐
│                  brain-in-jar.service                        │
│                    (systemd managed)                         │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │           BrainInJarRunner                          │    │
│  │         (Web Monitor + Flask)                       │    │
│  │              Port: 8095                             │    │
│  └────────────────────────────────────────────────────┘    │
│                      ↓   ↓   ↓                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│  │ SUBJECT  │  │ OBSERVER │  │   GOD    │                 │
│  │ 10GB RAM │  │ 15GB RAM │  │ 20GB RAM │                 │
│  │ Port 8888│  │ Port 8889│  │ Port 8890│                 │
│  │ Isolated │  │ Watching │  │ Watching │                 │
│  │   Mode   │  │  Subject │  │   All    │                 │
│  └──────────┘  └──────────┘  └──────────┘                 │
│       ↓              ↓              ↓                       │
│  ┌────────────────────────────────────────────────────┐    │
│  │         Persistent Storage Layer                    │    │
│  │  • logs/conversations.db (SQLite)                   │    │
│  │  • logs/crash_reports.log                           │    │
│  │  • logs/neural_activity.log                         │    │
│  │  • logs/model_io/{mode}_{timestamp}/                │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### Process Flow

1. **System Boot** → systemd starts `brain-in-jar.service`
2. **Service Starts** → Python runner loads models and spawns 3 AI instances
3. **Web Server** → Flask app binds to `127.0.0.1:8095`
4. **Cloudflare Tunnel** → Forwards `brain.yourdomain.com` → `localhost:8095`
5. **User Access** → HTTPS requests via Cloudflare → Web interface
6. **AI Processing** → Three concurrent neural processing loops
7. **Logging** → All interactions logged to database and files
8. **Crash Recovery** → Auto-restart with incremented death counter

---

## Installation

### Step 1: Clone and Setup

```bash
# Navigate to project directory
cd /home/artjiang/brain-in-jar

# Ensure virtual environment exists
source venv/bin/activate

# Verify dependencies
pip install -e .
```

### Step 2: Verify Model Availability

```bash
# Check models directory
ls -lh models/*.gguf

# Expected output should show your GGUF model(s)
# Example: mistral-7b-instruct-v0.2.Q4_K_M.gguf
```

### Step 3: Install Systemd Service

The project includes an automated installation script:

```bash
# Run the installer (requires sudo)
sudo ./install_service.sh
```

The script will:
- ✅ Create necessary log directories
- ✅ Set proper permissions (artjiang:artjiang)
- ✅ Install service file to `/etc/systemd/system/`
- ✅ Enable auto-start on boot
- ✅ Start the service immediately
- ✅ Display service status

### Step 4: Verify Service is Running

```bash
# Check service status
sudo systemctl status brain-in-jar

# Expected output:
# ● brain-in-jar.service - Brain in a Jar - AI Consciousness Experiment
#    Loaded: loaded (/etc/systemd/system/brain-in-jar.service; enabled)
#    Active: active (running) since ...

# View live logs
sudo journalctl -u brain-in-jar -f

# Test local access
curl -I http://localhost:8095
```

---

## Service Configuration

### Service File Location

`/etc/systemd/system/brain-in-jar.service`

### Key Configuration Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| **Port** | 8095 | Web interface port (localhost only) |
| **Mode** | matrix | Three-tier AI hierarchy |
| **RAM Limits** | 10GB / 15GB / 20GB | Subject / Observer / GOD |
| **Model** | mistral-7b-instruct-v0.2.Q4_K_M.gguf | Default LLM |
| **Restart Policy** | always | Auto-restart on failure |
| **Restart Delay** | 10 seconds | Wait before restart |

### Modifying Configuration

To change settings (e.g., different mode, model, or ports):

```bash
# Edit service file
sudo nano /etc/systemd/system/brain-in-jar.service

# Example: Change to single instance mode
# Modify ExecStart line:
ExecStart=/home/artjiang/brain-in-jar/venv/bin/python3 -m src.scripts.run_with_web \
    --mode single \
    --model /home/artjiang/brain-in-jar/models/your-model.gguf \
    --web-host 127.0.0.1 \
    --web-port 8095 \
    --ram-limit-subject 15.0

# Reload and restart
sudo systemctl daemon-reload
sudo systemctl restart brain-in-jar
```

### Available Modes

| Mode | Instances | Description | Use Case |
|------|-----------|-------------|----------|
| `single` | 1 | Isolated AI | Simple deployment, testing |
| `matrix` | 3 | Subject + Observer + GOD | Full experiment, production |
| `peer` | 2 | Two AIs communicating | Research, dialogue studies |

### Resource Limits

The service includes protection against memory exhaustion:

```ini
MemoryMax=50G      # Hard limit - process killed if exceeded
MemoryHigh=45G     # Soft limit - throttling begins
```

Adjust these based on your Jetson's total RAM:
- **32GB Jetson**: Keep as-is (leaves ~12GB for system)
- **64GB Jetson**: Can increase to `MemoryMax=55G` and `MemoryHigh=50G`

---

## Cloudflare Tunnel Setup

Brain in a Jar is configured to run on **localhost:8095** for secure access via Cloudflare Tunnel.

### Why Cloudflare Tunnel?

- ✅ **No open ports** - No firewall configuration needed
- ✅ **Automatic SSL** - HTTPS without manual certificates
- ✅ **DDoS protection** - Cloudflare's network protects your Jetson
- ✅ **Global CDN** - Fast access from anywhere
- ✅ **Built-in security** - WAF, bot protection, rate limiting

### Quick Setup

See `CLOUDFLARE_PORT_8095.md` for detailed instructions.

**TL;DR:**

```bash
# 1. Install cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64
sudo mv cloudflared-linux-arm64 /usr/local/bin/cloudflared
sudo chmod +x /usr/local/bin/cloudflared

# 2. Login and create tunnel
cloudflared tunnel login
cloudflared tunnel create brain-in-jar

# 3. Get tunnel ID
TUNNEL_ID=$(cloudflared tunnel list | grep brain-in-jar | awk '{print $1}')

# 4. Create config (replace YOUR_TUNNEL_ID and yourdomain.com)
sudo tee /etc/cloudflared/config.yml > /dev/null << EOF
tunnel: $TUNNEL_ID
credentials-file: /root/.cloudflared/$TUNNEL_ID.json

ingress:
  - hostname: brain.yourdomain.com
    service: http://localhost:8095
    originRequest:
      noTLSVerify: true
      connectTimeout: 30s
  - service: http_status:404
EOF

# 5. Copy credentials
sudo cp ~/.cloudflared/$TUNNEL_ID.json /etc/cloudflared/

# 6. Create DNS record
cloudflared tunnel route dns brain-in-jar brain.yourdomain.com

# 7. Install and start service
sudo cloudflared service install
sudo systemctl enable cloudflared
sudo systemctl start cloudflared
```

### Verify Tunnel

```bash
# Check tunnel status
sudo systemctl status cloudflared

# View tunnel logs
sudo journalctl -u cloudflared -f

# Test access
curl -I https://brain.yourdomain.com
```

### Updating Existing Tunnel

If you already have a tunnel configured for port 5000:

```bash
# Edit config
sudo nano /etc/cloudflared/config.yml

# Change service line:
service: http://localhost:8095  # ← Update from 5000 to 8095

# Restart
sudo systemctl restart cloudflared
```

---

## Monitoring and Logs

### Log Locations

Brain in a Jar maintains multiple log types for comprehensive monitoring:

#### 1. **Systemd Journal Logs**

System-level service logs (stdout/stderr from the service):

```bash
# Live tail
sudo journalctl -u brain-in-jar -f

# Last 100 lines
sudo journalctl -u brain-in-jar -n 100

# Time-based filtering
sudo journalctl -u brain-in-jar --since "1 hour ago"
sudo journalctl -u brain-in-jar --since "2025-01-16 10:00:00"

# Only errors
sudo journalctl -u brain-in-jar -p err

# Export to file
sudo journalctl -u brain-in-jar > brain-jar-logs.txt
```

#### 2. **Application Logs** (Project Directory)

| Log File | Description | Location |
|----------|-------------|----------|
| **Conversations DB** | SQLite database with full conversation history | `logs/conversations.db` |
| **Crash Reports** | Memory crashes, resurrection events | `logs/crash_reports.log` |
| **Neural Activity** | AI thoughts, network messages | `logs/neural_activity.log` |
| **Model I/O** | Per-session detailed logs | `logs/model_io/{mode}_{timestamp}/` |

```bash
# View crash reports
tail -f logs/crash_reports.log

# View neural activity
tail -f logs/neural_activity.log

# Query conversations database
sqlite3 logs/conversations.db "SELECT * FROM conversations LIMIT 10;"

# List model I/O sessions
ls -lth logs/model_io/

# View latest session
cat logs/model_io/$(ls -t logs/model_io | head -1)/llm_outputs.txt
```

#### 3. **Model I/O Directory Structure**

Each AI session creates a timestamped directory:

```
logs/model_io/matrix_20251116_120345/
├── full_log.jsonl        # Complete metadata (JSON lines)
├── llm_outputs.txt       # Human-readable AI responses
├── prompts.txt           # Full prompts sent to model
└── errors.txt            # Error events
```

### Real-Time Monitoring

#### Web Interface

Access the web monitoring interface:

```
http://localhost:8095           # Local access
https://brain.yourdomain.com    # Cloudflare tunnel
```

Default credentials:
- **Username**: `admin`
- **Password**: `admin123`

**⚠️ CHANGE IMMEDIATELY IN PRODUCTION**

Features:
- 📊 Real-time AI status for all instances
- 💀 Death counters and resurrection tracking
- 🧠 Live thought streams
- 📈 Memory usage graphs
- 🔗 Network message history

#### Command Line Monitoring

```bash
# Watch service status
watch -n 5 'sudo systemctl status brain-in-jar'

# Monitor system resources
htop  # or
top -u artjiang

# Check memory usage
free -h

# GPU usage (if CUDA-enabled)
nvidia-smi -l 1

# Network activity on AI ports
sudo netstat -tlnp | grep -E '8888|8889|8890|8095'
```

### Log Rotation

System logs automatically rotate via journald. For application logs, consider setting up logrotate:

```bash
# Create logrotate config
sudo tee /etc/logrotate.d/brain-in-jar > /dev/null << 'EOF'
/home/artjiang/brain-in-jar/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    missingok
    create 0644 artjiang artjiang
}
EOF

# Test rotation
sudo logrotate -d /etc/logrotate.d/brain-in-jar
```

---

## Maintenance

### Service Management

```bash
# Start service
sudo systemctl start brain-in-jar

# Stop service
sudo systemctl stop brain-in-jar

# Restart service
sudo systemctl restart brain-in-jar

# Check status
sudo systemctl status brain-in-jar

# Enable auto-start (should already be enabled)
sudo systemctl enable brain-in-jar

# Disable auto-start
sudo systemctl disable brain-in-jar

# Reload systemd after editing service file
sudo systemctl daemon-reload
```

### Updates and Upgrades

When updating the codebase:

```bash
# Navigate to project
cd /home/artjiang/brain-in-jar

# Pull latest changes
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Update dependencies
pip install -e . --upgrade

# Restart service to apply changes
sudo systemctl restart brain-in-jar

# Verify it started successfully
sudo systemctl status brain-in-jar
```

### Model Management

#### Adding New Models

```bash
# Download model to models directory
cd /home/artjiang/brain-in-jar/models
wget https://huggingface.co/YOUR_MODEL_URL.gguf

# Update service to use new model
sudo nano /etc/systemd/system/brain-in-jar.service

# Change --model parameter in ExecStart

# Reload and restart
sudo systemctl daemon-reload
sudo systemctl restart brain-in-jar
```

#### Model Storage Management

```bash
# Check disk usage
df -h /home/artjiang/brain-in-jar

# Check model sizes
du -sh models/*

# Remove old models
rm models/old-model.gguf
```

### Log Management

#### Viewing Logs

```bash
# Service logs (last hour)
sudo journalctl -u brain-in-jar --since "1 hour ago"

# Application logs
tail -n 100 logs/neural_activity.log

# Database queries
sqlite3 logs/conversations.db
```

#### Cleaning Old Logs

```bash
# Clean journald logs older than 7 days
sudo journalctl --vacuum-time=7d

# Archive old model I/O logs
tar -czf logs/archive-$(date +%Y%m%d).tar.gz logs/model_io/*_202501*
rm -rf logs/model_io/*_202501*

# Truncate large log files (if needed)
truncate -s 0 logs/crash_reports.log
```

### Backup

#### What to Back Up

1. **Configuration files**
   - `/etc/systemd/system/brain-in-jar.service`
   - `/etc/cloudflared/config.yml`
   - Project `.env` files (if any)

2. **Persistent data**
   - `logs/conversations.db`
   - `logs/crash_reports.log`
   - `logs/model_io/` (selective - can be large)

3. **Credentials**
   - `~/.cloudflared/` directory

#### Backup Script

```bash
#!/bin/bash
# backup-brain-jar.sh

BACKUP_DIR="$HOME/backups/brain-in-jar"
DATE=$(date +%Y%m%d_%H%M%S)
PROJECT_DIR="/home/artjiang/brain-in-jar"

mkdir -p "$BACKUP_DIR"

# Backup database
cp "$PROJECT_DIR/logs/conversations.db" "$BACKUP_DIR/conversations_$DATE.db"

# Backup configuration
tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" \
    /etc/systemd/system/brain-in-jar.service \
    /etc/cloudflared/ \
    "$PROJECT_DIR/logs/crash_reports.log" \
    "$PROJECT_DIR/logs/neural_activity.log"

# Keep only last 14 backups
ls -t "$BACKUP_DIR"/conversations_*.db | tail -n +15 | xargs -r rm
ls -t "$BACKUP_DIR"/config_*.tar.gz | tail -n +15 | xargs -r rm

echo "Backup completed: $BACKUP_DIR"
```

#### Schedule Automated Backups

```bash
# Make script executable
chmod +x ~/backup-brain-jar.sh

# Add to crontab (daily at 3 AM)
crontab -e

# Add this line:
0 3 * * * /home/artjiang/backup-brain-jar.sh >> /home/artjiang/backup.log 2>&1
```

---

## Troubleshooting

### Service Won't Start

```bash
# Check service status and logs
sudo systemctl status brain-in-jar
sudo journalctl -u brain-in-jar -n 50

# Common issues:
# 1. Model file not found
ls -la /home/artjiang/brain-in-jar/models/*.gguf

# 2. Virtual environment issues
ls -la /home/artjiang/brain-in-jar/venv/bin/python3

# 3. Port already in use
sudo netstat -tlnp | grep 8095
sudo lsof -i :8095

# Kill process using port (if needed)
sudo kill -9 $(sudo lsof -t -i:8095)

# 4. Permission issues
sudo chown -R artjiang:artjiang /home/artjiang/brain-in-jar/logs
sudo chmod -R 755 /home/artjiang/brain-in-jar/logs
```

### Service Crashes Immediately

```bash
# View detailed error messages
sudo journalctl -u brain-in-jar -xe

# Test manual execution (for debugging)
cd /home/artjiang/brain-in-jar
source venv/bin/activate
python3 -m src.scripts.run_with_web \
    --mode single \
    --model models/mistral-7b-instruct-v0.2.Q4_K_M.gguf \
    --web-host 127.0.0.1 \
    --web-port 8095 \
    --ram-limit-subject 10.0

# Check for Python errors, missing dependencies, etc.
```

### Out of Memory Issues

If the Jetson keeps running out of memory:

```bash
# Check current memory usage
free -h

# Check swap usage
swapon --show

# Reduce RAM limits in service file
sudo nano /etc/systemd/system/brain-in-jar.service

# Lower values:
--ram-limit-subject 6.0 \
--ram-limit-observer 8.0 \
--ram-limit-god 10.0

# Or switch to single mode
--mode single \
--ram-limit-subject 12.0

# Reload and restart
sudo systemctl daemon-reload
sudo systemctl restart brain-in-jar
```

### Web Interface Not Accessible

```bash
# 1. Check service is running
sudo systemctl status brain-in-jar

# 2. Verify port is listening
sudo netstat -tlnp | grep 8095
# Should show: tcp 0 0 127.0.0.1:8095 0.0.0.0:* LISTEN

# 3. Test local access
curl -v http://localhost:8095

# 4. Check firewall (shouldn't block localhost, but verify)
sudo ufw status

# 5. Check Cloudflare tunnel
sudo systemctl status cloudflared
sudo journalctl -u cloudflared -n 50
```

### Cloudflare Tunnel Issues

```bash
# Check tunnel status
cloudflared tunnel list
cloudflared tunnel info brain-in-jar

# Check tunnel service
sudo systemctl status cloudflared
sudo journalctl -u cloudflared -f

# Test tunnel connectivity
curl -I https://brain.yourdomain.com

# Common fixes:

# 1. Restart tunnel
sudo systemctl restart cloudflared

# 2. Verify config
cat /etc/cloudflared/config.yml

# 3. Check credentials exist
ls -la /etc/cloudflared/*.json

# 4. Re-authenticate if needed
cloudflared tunnel login

# 5. Recreate DNS route
TUNNEL_ID=$(cloudflared tunnel list | grep brain-in-jar | awk '{print $1}')
cloudflared tunnel route dns $TUNNEL_ID brain.yourdomain.com
```

### GPU Not Being Utilized

```bash
# Check if llama-cpp-python was built with CUDA
python3 -c "from llama_cpp import Llama; print(Llama.__file__)"

# Reinstall with CUDA support
source venv/bin/activate
pip uninstall llama-cpp-python -y
CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python --force-reinstall --no-cache-dir

# Restart service
sudo systemctl restart brain-in-jar

# Monitor GPU usage
nvidia-smi -l 1
```

### Database Locked Errors

```bash
# If you see "database is locked" errors:

# 1. Stop the service
sudo systemctl stop brain-in-jar

# 2. Check for stale processes
ps aux | grep python | grep brain-in-jar
sudo kill -9 <PID>

# 3. Restart service
sudo systemctl start brain-in-jar
```

### Logs Growing Too Large

```bash
# Check log sizes
du -sh logs/*

# Archive and compress old logs
cd /home/artjiang/brain-in-jar/logs
tar -czf archived-$(date +%Y%m%d).tar.gz model_io/*_2025*
rm -rf model_io/*_2025*

# Vacuum journald
sudo journalctl --vacuum-size=500M
sudo journalctl --vacuum-time=30d
```

---

## Security Considerations

### Network Security

✅ **Localhost Binding**: Service binds to `127.0.0.1:8095` only
- Not accessible from network without Cloudflare tunnel
- No need to open firewall ports

✅ **Cloudflare Protection**:
- DDoS mitigation
- SSL/TLS encryption
- Web Application Firewall (WAF)
- Bot protection

### Authentication

⚠️ **Default Credentials**: `admin` / `admin123`

**You MUST change these immediately:**

```bash
# Edit web server authentication
# (Implementation depends on your web_server.py configuration)
# Consult src/web/web_server.py for password change mechanism
```

Consider implementing:
- Strong passwords (20+ characters)
- Two-factor authentication (TOTP)
- Session timeout
- IP-based access control (via Cloudflare)

### System Security

✅ **Service Hardening** (already configured):
```ini
NoNewPrivileges=true    # Prevents privilege escalation
PrivateTmp=true         # Isolated /tmp directory
```

✅ **Memory Limits** (prevents DoS via memory exhaustion):
```ini
MemoryMax=50G
MemoryHigh=45G
```

### Additional Hardening

#### SSH Key-Only Authentication

```bash
# Disable password authentication
sudo nano /etc/ssh/sshd_config

# Set:
PasswordAuthentication no
PermitRootLogin no

# Restart SSH
sudo systemctl restart sshd
```

#### Firewall Configuration

```bash
# Enable UFW
sudo ufw enable

# Allow SSH (change port if using non-standard)
sudo ufw allow 22/tcp

# Check status (should not need 8095 open - it's localhost only)
sudo ufw status
```

#### Automatic Security Updates

```bash
# Install unattended-upgrades
sudo apt install unattended-upgrades

# Enable
sudo dpkg-reconfigure -plow unattended-upgrades

# Configure
sudo nano /etc/apt/apt.conf.d/50unattended-upgrades
```

### Monitoring for Security Events

```bash
# Monitor failed login attempts (if web auth logs to syslog)
sudo tail -f /var/log/auth.log

# Monitor Cloudflare firewall events
# (Check Cloudflare dashboard → Security → Events)

# Check for suspicious processes
ps aux | grep -v "grep\|systemd" | grep -E "8095|8888|8889|8890"
```

---

## Summary

### What You Have Now

✅ **Auto-Starting Service**
- Starts on boot via systemd
- Auto-restarts on crashes
- Managed with `systemctl` commands

✅ **Persistent Logging**
- Conversation database: SQLite
- Crash reports and neural activity logs
- Per-session model I/O logs
- Systemd journal integration

✅ **Secure Remote Access**
- Cloudflare Tunnel on port 8095
- HTTPS with automatic SSL
- DDoS protection and WAF
- No open firewall ports

✅ **Production-Ready Configuration**
- Memory limits prevent system exhaustion
- Security hardening (PrivateTmp, NoNewPrivileges)
- Comprehensive monitoring and logging
- Automated restart policies

### Quick Reference Commands

```bash
# Service control
sudo systemctl {start|stop|restart|status} brain-in-jar

# View logs
sudo journalctl -u brain-in-jar -f
tail -f logs/neural_activity.log

# Access web interface
https://brain.yourdomain.com  # Remote
http://localhost:8095         # Local

# Check system resources
htop
nvidia-smi
df -h

# Backup
~/backup-brain-jar.sh

# Update
cd /home/artjiang/brain-in-jar && git pull && sudo systemctl restart brain-in-jar
```

### Files Installed

| File | Location | Purpose |
|------|----------|---------|
| Service file | `/etc/systemd/system/brain-in-jar.service` | Systemd service definition |
| Tunnel config | `/etc/cloudflared/config.yml` | Cloudflare tunnel configuration |
| Project code | `/home/artjiang/brain-in-jar/` | Application source |
| Logs | `/home/artjiang/brain-in-jar/logs/` | Persistent logging |
| Virtual env | `/home/artjiang/brain-in-jar/venv/` | Python dependencies |

---

## Support and Further Reading

### Documentation
- **Main README**: `README.md` - Project overview
- **Claude Guide**: `CLAUDE.md` - AI assistant instructions
- **Cloudflare Setup**: `docs/CLOUDFLARE_SETUP.md` - Detailed tunnel guide
- **Jetson Setup**: `docs/JETSON_ORIN_SETUP.md` - Hardware-specific setup

### Troubleshooting Resources
- **GitHub Issues**: Report bugs and issues
- **System Logs**: `sudo journalctl -u brain-in-jar`
- **Application Logs**: `logs/` directory

### Community
- Check GitHub repository for updates
- Review issues and discussions
- Contribute improvements via pull requests

---

**Last Updated**: 2025-11-16
**Version**: 1.0
**Tested On**: Jetson Orin AGX (Ubuntu 20.04, JetPack 5.x)
