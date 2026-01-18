#!/usr/bin/env python3
"""
Secure Web Server for Brain in a Jar Monitoring
Provides real-time monitoring of AI consciousness experiments via web interface
"""

import os
import json
import secrets
import hashlib
import time
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, Response
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import jwt

# Configuration
SECRET_KEY = os.environ.get('BRAIN_JAR_SECRET_KEY', secrets.token_hex(32))
JWT_SECRET = os.environ.get('BRAIN_JAR_JWT_SECRET', secrets.token_hex(32))
JWT_EXPIRATION_HOURS = 24

# Password hash (default: "admin123" - CHANGE THIS!)
# Generate with: python3 -c "import hashlib; print(hashlib.sha256('your_password'.encode()).hexdigest())"
DEFAULT_PASSWORD_HASH = os.environ.get(
    'BRAIN_JAR_PASSWORD_HASH',
    '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9'  # "admin123"
)

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# Enable CORS with credentials
CORS(app, supports_credentials=True)

# SocketIO for real-time updates
# Use eventlet for better stability and add ping settings to prevent disconnections
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='eventlet',
    ping_timeout=120,  # 2 minutes before timeout
    ping_interval=25,  # Send ping every 25 seconds
    logger=False,
    engineio_logger=False
)

# Global state store (will be updated by neural link system)
system_state = {
    'instances': {},  # Multiple AI instances
    'logs': [],
    'metrics': {
        'total_crashes': 0,
        'total_messages': 0,
        'uptime_seconds': 0,
        'start_time': datetime.now().isoformat()
    }
}

# Rate limiting
login_attempts = {}
MAX_LOGIN_ATTEMPTS = 5
LOGIN_TIMEOUT = 300  # 5 minutes


def hash_password(password):
    """Hash a password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password, password_hash):
    """Verify a password against a hash"""
    return hash_password(password) == password_hash


def check_rate_limit(ip_address):
    """Check if IP is rate limited"""
    if ip_address in login_attempts:
        attempts, last_attempt = login_attempts[ip_address]
        if attempts >= MAX_LOGIN_ATTEMPTS:
            if time.time() - last_attempt < LOGIN_TIMEOUT:
                return False
            else:
                # Reset after timeout
                login_attempts[ip_address] = (0, time.time())
    return True


def record_login_attempt(ip_address, success):
    """Record a login attempt"""
    if success:
        login_attempts.pop(ip_address, None)
    else:
        attempts, _ = login_attempts.get(ip_address, (0, 0))
        login_attempts[ip_address] = (attempts + 1, time.time())


def create_token(username):
    """Create a JWT token"""
    payload = {
        'username': username,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')


def verify_token(token):
    """Verify a JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload['username']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check session
        if 'authenticated' in session and session['authenticated']:
            return f(*args, **kwargs)

        # Check JWT token
        token = request.headers.get('Authorization')
        if token and token.startswith('Bearer '):
            token = token.split(' ')[1]
            username = verify_token(token)
            if username:
                return f(*args, **kwargs)

        # Check API key
        api_key = request.headers.get('X-API-Key')
        if api_key and verify_api_key(api_key):
            return f(*args, **kwargs)

        return jsonify({'error': 'Authentication required'}), 401

    return decorated_function


def verify_api_key(api_key):
    """Verify an API key"""
    # API keys stored in environment or file
    valid_keys = os.environ.get('BRAIN_JAR_API_KEYS', '').split(',')
    return api_key in valid_keys if valid_keys[0] else False


# Routes
@app.route('/')
def index():
    """Main dashboard page"""
    if 'authenticated' not in session or not session['authenticated']:
        return redirect(url_for('login'))
    return render_template('dashboard.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'GET':
        return render_template('login.html')

    # Get client IP
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()

    # Check rate limit
    if not check_rate_limit(ip_address):
        return jsonify({
            'success': False,
            'error': 'Too many failed attempts. Please try again later.'
        }), 429

    data = request.get_json()
    password = data.get('password', '')

    if verify_password(password, DEFAULT_PASSWORD_HASH):
        session['authenticated'] = True
        session.permanent = True
        record_login_attempt(ip_address, True)

        token = create_token('admin')
        return jsonify({
            'success': True,
            'token': token,
            'message': 'Authentication successful'
        })
    else:
        record_login_attempt(ip_address, False)
        return jsonify({
            'success': False,
            'error': 'Invalid password'
        }), 401


@app.route('/logout')
def logout():
    """Logout"""
    session.pop('authenticated', None)
    return redirect(url_for('login'))


@app.route('/api/status')
@require_auth
def api_status():
    """Get current system status"""
    return jsonify({
        'instances': system_state['instances'],
        'metrics': system_state['metrics'],
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/instances')
@require_auth
def api_instances():
    """Get list of AI instances"""
    return jsonify({
        'instances': list(system_state['instances'].keys())
    })


@app.route('/api/instance/<instance_id>')
@require_auth
def api_instance_details(instance_id):
    """Get details of a specific instance"""
    if instance_id not in system_state['instances']:
        return jsonify({'error': 'Instance not found'}), 404

    return jsonify(system_state['instances'][instance_id])


@app.route('/api/logs')
@require_auth
def api_logs():
    """Get recent logs"""
    limit = int(request.args.get('limit', 100))
    instance_id = request.args.get('instance_id')

    logs = system_state['logs']

    if instance_id:
        logs = [log for log in logs if log.get('instance_id') == instance_id]

    return jsonify({
        'logs': logs[-limit:],
        'count': len(logs)
    })


@app.route('/api/metrics')
@require_auth
def api_metrics():
    """Get system metrics"""
    return jsonify(system_state['metrics'])


@app.route('/api/health')
def api_health():
    """Health check endpoint (no auth required)"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'instances': len(system_state['instances'])
    })


@app.route('/api/update_password', methods=['POST'])
@require_auth
def update_password():
    """Update password"""
    data = request.get_json()
    old_password = data.get('old_password', '')
    new_password = data.get('new_password', '')

    if not verify_password(old_password, DEFAULT_PASSWORD_HASH):
        return jsonify({'success': False, 'error': 'Invalid old password'}), 401

    new_hash = hash_password(new_password)

    # Save to environment file
    env_file = Path(__file__).parent.parent.parent / '.env'
    env_file.write_text(f'BRAIN_JAR_PASSWORD_HASH={new_hash}\n')

    return jsonify({
        'success': True,
        'message': 'Password updated. Please restart the server.'
    })


# WebSocket events
@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    # Basic auth check
    token = request.args.get('token')
    if token:
        username = verify_token(token)
        if username:
            emit('connected', {'message': 'Connected to Brain in a Jar monitoring'})
            return

    # Check session
    if 'authenticated' in session and session['authenticated']:
        emit('connected', {'message': 'Connected to Brain in a Jar monitoring'})
        return

    # Disconnect unauthorized
    return False


@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    pass


@socketio.on('subscribe')
def handle_subscribe(data):
    """Subscribe to specific instance updates"""
    instance_id = data.get('instance_id')
    if instance_id:
        emit('subscribed', {'instance_id': instance_id})


# Public API for neural link to update state
def update_instance_state(instance_id, state_data):
    """Update state for a specific instance"""
    system_state['instances'][instance_id] = {
        **state_data,
        'last_update': datetime.now().isoformat()
    }

    # Emit to all connected clients
    socketio.emit('instance_update', {
        'instance_id': instance_id,
        'state': state_data
    })


def add_log_entry(instance_id, level, message, data=None):
    """Add a log entry"""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'instance_id': instance_id,
        'level': level,
        'message': message,
        'data': data
    }

    system_state['logs'].append(log_entry)

    # Keep only last 1000 logs
    if len(system_state['logs']) > 1000:
        system_state['logs'] = system_state['logs'][-1000:]

    # Emit to connected clients
    socketio.emit('log_entry', log_entry)


def update_metrics(metrics):
    """Update global metrics"""
    system_state['metrics'].update(metrics)
    socketio.emit('metrics_update', system_state['metrics'])


def run_server(host='0.0.0.0', port=8095, debug=False):
    """Run the web server"""
    print(f"Starting Brain in a Jar web server on {host}:{port}")
    print(f"Default password hash: {DEFAULT_PASSWORD_HASH}")
    print("Please change the password immediately after first login!")
    socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)


if __name__ == '__main__':
    run_server()
