# Cloudflare Setup Guide for Brain in a Jar

This guide explains how to securely expose your Brain in a Jar web interface to the internet using Cloudflare.

## Prerequisites

- Cloudflare account (free tier works)
- Domain name added to Cloudflare
- Jetson Orin AGX with Brain in a Jar installed
- SSH access to your Jetson

## Option 1: Cloudflare Tunnel (Recommended)

Cloudflare Tunnel creates a secure outbound connection without opening firewall ports. This is the most secure option.

### Why Cloudflare Tunnel?

- ✅ No open ports on your firewall
- ✅ No port forwarding needed
- ✅ Automatic HTTPS/SSL
- ✅ DDoS protection
- ✅ Built-in access controls
- ✅ Works behind NAT/CGNAT

### Step 1: Install Cloudflared

```bash
# Download and install cloudflared for ARM64
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64
sudo mv cloudflared-linux-arm64 /usr/local/bin/cloudflared
sudo chmod +x /usr/local/bin/cloudflared

# Verify installation
cloudflared --version
```

### Step 2: Authenticate with Cloudflare

```bash
# Login to Cloudflare
cloudflared tunnel login

# This will open a browser. Login and select your domain
# The cert will be saved to ~/.cloudflared/cert.pem
```

### Step 3: Create a Tunnel

```bash
# Create tunnel
cloudflared tunnel create brain-in-jar

# This creates:
# - Tunnel ID
# - Tunnel credentials file: ~/.cloudflared/<TUNNEL-ID>.json

# Save your tunnel ID
TUNNEL_ID=$(cloudflared tunnel list | grep brain-in-jar | awk '{print $1}')
echo "Tunnel ID: $TUNNEL_ID"
```

### Step 4: Create Tunnel Configuration

```bash
# Create config directory
sudo mkdir -p /etc/cloudflared

# Create configuration file
sudo tee /etc/cloudflared/config.yml > /dev/null << EOF
tunnel: $TUNNEL_ID
credentials-file: $HOME/.cloudflared/$TUNNEL_ID.json

ingress:
  # Brain in a Jar web interface
  - hostname: brain.yourdomain.com
    service: http://localhost:5000
    originRequest:
      noTLSVerify: true
      connectTimeout: 30s
      keepAliveConnections: 10

  # Catch-all rule (required)
  - service: http_status:404
EOF

# Copy credentials to /etc/cloudflared
sudo cp ~/.cloudflared/$TUNNEL_ID.json /etc/cloudflared/
```

### Step 5: Create DNS Record

```bash
# Create DNS record pointing to your tunnel
cloudflared tunnel route dns brain-in-jar brain.yourdomain.com

# Or manually in Cloudflare dashboard:
# Type: CNAME
# Name: brain
# Target: <TUNNEL-ID>.cfargotunnel.com
# Proxy: Yes (orange cloud)
```

### Step 6: Test the Tunnel

```bash
# Test tunnel configuration
cloudflared tunnel --config /etc/cloudflared/config.yml run brain-in-jar

# Visit https://brain.yourdomain.com to test
# Press Ctrl+C to stop
```

### Step 7: Install as System Service

```bash
# Install cloudflared as a service
sudo cloudflared service install

# Start the service
sudo systemctl start cloudflared
sudo systemctl enable cloudflared

# Check status
sudo systemctl status cloudflared

# View logs
sudo journalctl -u cloudflared -f
```

### Step 8: Configure Cloudflare Security Settings

Go to Cloudflare Dashboard → Your Domain → Security

#### A. Enable Bot Protection

1. Navigate to **Security → Bots**
2. Enable **Bot Fight Mode** (free) or **Super Bot Fight Mode** (paid)

#### B. Configure WAF Rules

1. Navigate to **Security → WAF**
2. Create custom rules:

```
Rule 1: Rate Limiting
- Field: IP Address
- When: Requests exceed 100 per minute
- Then: Challenge

Rule 2: Geographic Restrictions (optional)
- Field: Country
- When: Country is in [blocked countries]
- Then: Block

Rule 3: Protect Login
- Field: URI Path
- When: equals "/login"
- And: Requests exceed 5 per minute
- Then: Block
```

#### C. Enable Browser Integrity Check

1. Navigate to **Security → Settings**
2. Enable **Browser Integrity Check**

#### D. Configure Access Policies (Optional - Paid Feature)

1. Navigate to **Zero Trust → Access → Applications**
2. Add application:
   - Name: Brain in a Jar
   - Domain: brain.yourdomain.com
   - Policy: Allow only your IP or email

### Step 9: SSL/TLS Settings

1. Navigate to **SSL/TLS → Overview**
2. Set encryption mode to **Full (strict)**
3. Navigate to **SSL/TLS → Edge Certificates**
4. Enable:
   - Always Use HTTPS
   - Automatic HTTPS Rewrites
   - Minimum TLS Version: 1.2
   - TLS 1.3: On

## Option 2: Direct DNS + Nginx + Let's Encrypt

If you prefer traditional setup without tunnels:

### Step 1: Point DNS to Your IP

In Cloudflare DNS:
```
Type: A
Name: brain
Content: <your-jetson-public-ip>
Proxy: Yes (orange cloud)
TTL: Auto
```

### Step 2: Install Certbot

```bash
# Install certbot
sudo apt install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d brain.yourdomain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

### Step 3: Configure Nginx with SSL

```bash
sudo tee /etc/nginx/sites-available/brain-in-jar > /dev/null << 'EOF'
# HTTP - redirect to HTTPS
server {
    listen 80;
    server_name brain.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS
server {
    listen 443 ssl http2;
    server_name brain.yourdomain.com;

    # SSL certificates (managed by Certbot)
    ssl_certificate /etc/letsencrypt/live/brain.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/brain.yourdomain.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # Rate limiting zones
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
    limit_req_zone $binary_remote_addr zone=api:10m rate=30r/m;
    limit_req_zone $binary_remote_addr zone=general:10m rate=60r/m;

    # Max body size
    client_max_body_size 10M;

    # Login endpoint - strict rate limit
    location /login {
        limit_req zone=login burst=3 nodelay;
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API endpoints
    location /api/ {
        limit_req zone=api burst=10 nodelay;
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket for real-time updates
    location /socket.io/ {
        proxy_pass http://127.0.0.1:5000/socket.io/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }

    # Static files (if any)
    location /static/ {
        alias /home/ubuntu/projects/brain-in-jar/src/web/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Main application
    location / {
        limit_req zone=general burst=20 nodelay;
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Test and reload
sudo nginx -t
sudo systemctl reload nginx
```

### Step 4: Configure Firewall

```bash
# Enable UFW
sudo ufw enable

# Allow SSH (change port if you use non-standard)
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Check status
sudo ufw status
```

## Additional Security Measures

### 1. Fail2Ban

Install Fail2Ban to block repeated failed login attempts:

```bash
# Install fail2ban
sudo apt install -y fail2ban

# Create jail for Brain in a Jar
sudo tee /etc/fail2ban/jail.d/brain-in-jar.conf > /dev/null << 'EOF'
[brain-in-jar]
enabled = true
port = http,https
filter = brain-in-jar
logpath = /var/log/nginx/access.log
maxretry = 3
bantime = 3600
findtime = 600
EOF

# Create filter
sudo tee /etc/fail2ban/filter.d/brain-in-jar.conf > /dev/null << 'EOF'
[Definition]
failregex = ^<HOST> .* "POST /login HTTP.*" 401
ignoreregex =
EOF

# Restart fail2ban
sudo systemctl restart fail2ban
sudo systemctl status fail2ban

# Check bans
sudo fail2ban-client status brain-in-jar
```

### 2. Two-Factor Authentication (Future Enhancement)

Consider adding 2FA to the web interface:
- Use PyOTP library
- Generate QR codes for authenticator apps
- Require TOTP codes on login

### 3. IP Whitelist (Optional)

If you only access from specific IPs:

```nginx
# In nginx config, add:
location / {
    allow 1.2.3.4;      # Your IP
    allow 5.6.7.8/24;   # Your network
    deny all;
    # ... rest of config
}
```

### 4. Cloudflare Access Control Lists

Create IP Access Rules in Cloudflare:
1. Navigate to **Security → WAF → Tools**
2. Add IP Access Rule:
   - IP: Your trusted IPs
   - Action: Allow

3. Add blocking rule:
   - IP: Known malicious IPs
   - Action: Block

## Monitoring and Alerts

### 1. Cloudflare Analytics

Monitor traffic in Cloudflare Dashboard:
- **Analytics → Web Traffic**: View requests, bandwidth, threats
- **Security → Events**: See security events and blocks
- **Speed → Performance**: Monitor load times

### 2. Email Alerts

Configure email alerts in Cloudflare:
1. Navigate to **Notifications**
2. Create alerts for:
   - DDoS attacks
   - Traffic anomalies
   - Certificate expiration

### 3. Application Monitoring

Monitor Brain in a Jar logs:

```bash
# View web server logs
sudo journalctl -u brain-in-jar -f

# View nginx access logs
sudo tail -f /var/log/nginx/access.log

# View nginx error logs
sudo tail -f /var/log/nginx/error.log

# View fail2ban logs
sudo tail -f /var/log/fail2ban.log
```

## Backup and Recovery

### Backup Configuration

```bash
# Create backup script
cat > ~/backup-brain-jar.sh << 'EOF'
#!/bin/bash
BACKUP_DIR=~/backups/brain-in-jar
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup configuration
tar -czf $BACKUP_DIR/config_$DATE.tar.gz \
    ~/projects/brain-in-jar/.env \
    ~/projects/brain-in-jar/logs \
    ~/.cloudflared

# Backup database (if you add one)
# sqlite3 ~/projects/brain-in-jar/brain.db ".backup $BACKUP_DIR/db_$DATE.sqlite"

# Keep only last 7 backups
ls -t $BACKUP_DIR/config_*.tar.gz | tail -n +8 | xargs -r rm

echo "Backup completed: $BACKUP_DIR/config_$DATE.tar.gz"
EOF

chmod +x ~/backup-brain-jar.sh

# Add to crontab (daily backup at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * $HOME/backup-brain-jar.sh") | crontab -
```

## Testing Your Setup

### 1. Security Headers Test

```bash
curl -I https://brain.yourdomain.com
```

Should include:
- `Strict-Transport-Security`
- `X-Frame-Options`
- `X-Content-Type-Options`
- `X-XSS-Protection`

### 2. SSL Test

Visit: https://www.ssllabs.com/ssltest/analyze.html?d=brain.yourdomain.com

Target grade: A or A+

### 3. Load Test

```bash
# Install Apache Bench
sudo apt install -y apache2-utils

# Test (after login)
ab -n 100 -c 10 https://brain.yourdomain.com/api/status
```

### 4. Penetration Testing

Run basic security scan:

```bash
# Install nikto
sudo apt install -y nikto

# Scan
nikto -h https://brain.yourdomain.com
```

## Troubleshooting

### Cloudflare Tunnel Not Connecting

```bash
# Check tunnel status
cloudflared tunnel list

# Check logs
sudo journalctl -u cloudflared -n 50

# Test connectivity
curl -I https://brain.yourdomain.com
```

### 502 Bad Gateway

```bash
# Check if Brain in a Jar is running
sudo systemctl status brain-in-jar

# Check if service is listening
sudo netstat -tlnp | grep 5000

# Check nginx
sudo nginx -t
sudo systemctl status nginx
```

### SSL Certificate Issues

```bash
# Renew certificate manually
sudo certbot renew

# Check certificate expiration
sudo certbot certificates
```

## Security Best Practices Checklist

- [ ] Changed default password
- [ ] Using strong password (20+ characters)
- [ ] Enabled HTTPS/SSL
- [ ] Configured Cloudflare proxy
- [ ] Enabled rate limiting
- [ ] Configured fail2ban
- [ ] Regular backups scheduled
- [ ] Monitoring setup
- [ ] UFW firewall enabled
- [ ] SSH key-only authentication
- [ ] Regular system updates
- [ ] Security headers configured
- [ ] Bot protection enabled
- [ ] WAF rules configured

## Performance Optimization

### Cloudflare Caching

1. Navigate to **Caching → Configuration**
2. Caching Level: **Standard**
3. Browser Cache TTL: **4 hours**

### Page Rules

Create page rules for static content:
```
URL: brain.yourdomain.com/static/*
Settings:
- Cache Level: Cache Everything
- Edge Cache TTL: 1 month
- Browser Cache TTL: 1 month
```

## Cost Considerations

### Free Tier (Cloudflare)

Includes:
- Unlimited DDoS protection
- Global CDN
- Shared SSL certificate
- Basic analytics
- Cloudflare Tunnel (up to 50 connections)

### Paid Features (Optional)

- **Cloudflare Access**: $3-7/user/month for Zero Trust access
- **Argo Smart Routing**: $5/month + $0.10/GB for faster routing
- **Load Balancing**: $5/month + $0.50/endpoint/month
- **Rate Limiting**: $5/month + usage

## Support and Resources

- Cloudflare Docs: https://developers.cloudflare.com/
- Cloudflare Tunnel: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/
- Nginx Docs: https://nginx.org/en/docs/
- Let's Encrypt: https://letsencrypt.org/docs/

## Summary

You now have:
- ✅ Secure HTTPS connection
- ✅ DDoS protection via Cloudflare
- ✅ Rate limiting
- ✅ Authentication
- ✅ Real-time monitoring
- ✅ Automatic backups
- ✅ Intrusion prevention

Your Brain in a Jar installation is now securely accessible from anywhere in the world!
