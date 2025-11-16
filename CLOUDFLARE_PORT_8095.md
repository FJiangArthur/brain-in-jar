# Cloudflare Tunnel Configuration for Port 8095

This Brain in a Jar instance is configured to run on **port 8095** (instead of the default 5000) for Cloudflare Tunnel integration.

## Update Your Cloudflare Tunnel Config

If you've already set up a Cloudflare tunnel following `docs/CLOUDFLARE_SETUP.md`, update your config:

### Edit `/etc/cloudflared/config.yml`

```yaml
tunnel: YOUR_TUNNEL_ID
credentials-file: /root/.cloudflared/YOUR_TUNNEL_ID.json

ingress:
  # Brain in a Jar web interface
  - hostname: brain.yourdomain.com
    service: http://localhost:8095  # ← Changed from 5000 to 8095
    originRequest:
      noTLSVerify: true
      connectTimeout: 30s
      keepAliveConnections: 10

  # Catch-all rule (required)
  - service: http_status:404
```

### Restart Cloudflared

```bash
sudo systemctl restart cloudflared
sudo systemctl status cloudflared
```

## New Tunnel Setup

If you haven't set up Cloudflare tunnel yet, follow these steps:

### 1. Install Cloudflared (if not already installed)

```bash
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64
sudo mv cloudflared-linux-arm64 /usr/local/bin/cloudflared
sudo chmod +x /usr/local/bin/cloudflared
cloudflared --version
```

### 2. Login and Create Tunnel

```bash
# Login to Cloudflare
cloudflared tunnel login

# Create tunnel
cloudflared tunnel create brain-in-jar

# Get tunnel ID
TUNNEL_ID=$(cloudflared tunnel list | grep brain-in-jar | awk '{print $1}')
echo "Your Tunnel ID: $TUNNEL_ID"
```

### 3. Create Configuration

```bash
sudo mkdir -p /etc/cloudflared

# Replace YOUR_TUNNEL_ID with actual ID from previous step
sudo tee /etc/cloudflared/config.yml > /dev/null << 'EOF'
tunnel: YOUR_TUNNEL_ID
credentials-file: /root/.cloudflared/YOUR_TUNNEL_ID.json

ingress:
  - hostname: brain.yourdomain.com
    service: http://localhost:8095
    originRequest:
      noTLSVerify: true
      connectTimeout: 30s
      keepAliveConnections: 10
  - service: http_status:404
EOF

# Copy credentials
sudo cp ~/.cloudflared/$TUNNEL_ID.json /etc/cloudflared/
```

### 4. Create DNS Record

```bash
# Point your domain to the tunnel
cloudflared tunnel route dns brain-in-jar brain.yourdomain.com
```

### 5. Install and Start Service

```bash
# Install as system service
sudo cloudflared service install

# Start and enable
sudo systemctl start cloudflared
sudo systemctl enable cloudflared

# Check status
sudo systemctl status cloudflared
```

## Verify Setup

After both services are running:

```bash
# Check Brain in a Jar is running on 8095
curl -I http://localhost:8095

# Check Cloudflare tunnel status
sudo journalctl -u cloudflared -n 20

# Access via your domain
curl -I https://brain.yourdomain.com
```

## Quick Status Check

```bash
# Brain in a Jar service
sudo systemctl status brain-in-jar

# Cloudflare tunnel
sudo systemctl status cloudflared

# Check what's listening on port 8095
sudo netstat -tlnp | grep 8095
```

## Troubleshooting

### Service not accessible via Cloudflare

1. Check Brain in a Jar is running:
   ```bash
   sudo systemctl status brain-in-jar
   sudo journalctl -u brain-in-jar -n 50
   ```

2. Verify it's listening on port 8095:
   ```bash
   curl http://localhost:8095
   ```

3. Check Cloudflare tunnel logs:
   ```bash
   sudo journalctl -u cloudflared -f
   ```

4. Test tunnel connectivity:
   ```bash
   cloudflared tunnel info brain-in-jar
   ```

### Port already in use

```bash
# See what's using port 8095
sudo lsof -i :8095
sudo netstat -tlnp | grep 8095

# Kill the process if needed
sudo kill <PID>
```

## Security Note

The service is configured to listen on `127.0.0.1:8095` (localhost only), which means:
- ✅ Not directly accessible from external network
- ✅ Only accessible via Cloudflare tunnel
- ✅ No need to open firewall ports
- ✅ All traffic goes through Cloudflare's security

This is the recommended secure configuration!
