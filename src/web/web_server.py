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

# Import network API
from src.web.api.network_api import NetworkDataExtractor
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from db.experiment_database import ExperimentDatabase

# Configuration
SECRET_KEY = os.environ.get('BRAIN_JAR_SECRET_KEY', secrets.token_hex(32))
JWT_SECRET = os.environ.get('BRAIN_JAR_JWT_SECRET', secrets.token_hex(32))
JWT_EXPIRATION_HOURS = 24

# Password hash (default: "admin123" - CHANGE THIS!)
# Generate with: python3 -c "import hashlib; print(hashlib.sha256('your_password'.encode()).hexdigest())"
DEFAULT_PASSWORD_HASH = os.environ.get(
    'BRAIN_JAR_PASSWORD_HASH',
    'b3d17ebbe4f2b75a8b5d6b326f48ba6d53c43f8f0e81e3d8e2a4c0f4a3e3b8d7'  # "admin123"
)

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# Enable CORS with credentials
CORS(app, supports_credentials=True)

# SocketIO for real-time updates
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Initialize experiment database
db = ExperimentDatabase()

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


# ===== Season 3 Experiment Dashboard Routes =====

@app.route('/experiments')
@require_auth
def experiments_dashboard():
    """Experiment dashboard page"""
    return render_template('experiment_dashboard.html')


@app.route('/api/experiments')
@require_auth
def api_experiments():
    """Get list of all experiments"""
    try:
        status = request.args.get('status')
        experiments = db.list_experiments(status=status)
        return jsonify({
            'experiments': experiments,
            'count': len(experiments)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/experiment/<experiment_id>')
@require_auth
def api_experiment_details(experiment_id):
    """Get details of a specific experiment"""
    try:
        experiment = db.get_experiment(experiment_id)
        if not experiment:
            return jsonify({'error': 'Experiment not found'}), 404

        # Get additional details
        summary = db.get_experiment_summary(experiment_id)

        # For live monitoring, also get recent messages and events
        try:
            # Get recent messages (last 50)
            recent_messages = db.get_messages(experiment_id, limit=50)
            summary['recent_messages'] = recent_messages

            # Get recent events (interventions, self-reports)
            # This would be a more sophisticated query in production
            summary['recent_events'] = []

        except Exception as e:
            # If we can't get messages, just continue with summary
            summary['recent_messages'] = []
            summary['recent_events'] = []

        return jsonify(summary)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/experiment/<experiment_id>')
@require_auth
def experiment_details_page(experiment_id):
    """Experiment details page (for future implementation)"""
    # For now, redirect to dashboard
    # In the future, this could show detailed experiment view
    return redirect(url_for('experiments_dashboard'))


@app.route('/experiment/live')
@require_auth
def experiment_live():
    """Live experiment monitoring page"""
    experiment_id = request.args.get('id')
    if not experiment_id:
        return redirect(url_for('experiments_dashboard'))
    return render_template('experiment_live.html', experiment_id=experiment_id)


@app.route('/experiment/<experiment_id>/network')
@require_auth
def experiment_network_page(experiment_id):
    """Network graph visualization page"""
    return render_template('experiment_network.html')


@app.route('/api/experiment/<experiment_id>/network_data')
@require_auth
def api_experiment_network_data(experiment_id):
    """
    Get network graph data for an experiment

    Query parameters:
    - time_start: Optional start time for filtering
    - time_end: Optional end time for filtering
    """
    try:
        # Get time range if provided
        time_start = request.args.get('time_start')
        time_end = request.args.get('time_end')
        time_range = (time_start, time_end) if time_start and time_end else None

        # Initialize network data extractor
        extractor = NetworkDataExtractor()

        # Get network data
        network_data = extractor.get_network_data(experiment_id, time_range)

        if 'error' in network_data:
            return jsonify(network_data), 404

        return jsonify(network_data)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/experiment/start', methods=['POST'])
@require_auth
def api_start_experiment():
    """Start a new experiment (placeholder for manual start)"""
    try:
        data = request.get_json()
        experiment_id = data.get('experiment_id')
        name = data.get('name', 'Unnamed Experiment')
        mode = data.get('mode', 'isolated')
        config = data.get('config', {})

        if not experiment_id:
            return jsonify({'error': 'experiment_id required'}), 400

        # Create experiment
        success = db.create_experiment(experiment_id, name, mode, config)
        if not success:
            return jsonify({'error': 'Experiment ID already exists'}), 400

        return jsonify({
            'success': True,
            'experiment_id': experiment_id,
            'message': 'Experiment created. Start it using the appropriate script.'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/experiment/<experiment_id>/stop', methods=['POST'])
@require_auth
def api_stop_experiment(experiment_id):
    """Stop a running experiment"""
    try:
        # Check if experiment exists and is running
        experiment = db.get_experiment(experiment_id)
        if not experiment:
            return jsonify({'error': 'Experiment not found'}), 404

        if experiment['status'] != 'running':
            return jsonify({'error': 'Experiment is not running'}), 400

        # End the experiment
        success = db.end_experiment(experiment_id, status='completed')
        if success:
            return jsonify({
                'success': True,
                'message': 'Experiment stopped successfully'
            })
        else:
            return jsonify({'error': 'Failed to stop experiment'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/experiment/<experiment_id>', methods=['DELETE'])
@require_auth
def api_delete_experiment(experiment_id):
    """Delete an experiment (Note: This doesn't delete from DB in current implementation)"""
    try:
        # Check if experiment exists
        experiment = db.get_experiment(experiment_id)
        if not experiment:
            return jsonify({'error': 'Experiment not found'}), 404

        # Don't allow deleting running experiments
        if experiment['status'] == 'running':
            return jsonify({'error': 'Cannot delete running experiment. Stop it first.'}), 400

        # For now, we'll mark as deleted by ending with 'deleted' status
        # A proper implementation would add a deleted flag or actually remove the data
        success = db.end_experiment(experiment_id, status='deleted')
        if success:
            return jsonify({
                'success': True,
                'message': 'Experiment deleted successfully'
            })
        else:
            return jsonify({'error': 'Failed to delete experiment'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ===== Experiment Configuration Builder Routes =====

@app.route('/experiment/create', methods=['GET'])
@require_auth
def experiment_create():
    """Render experiment creation form"""
    return render_template('experiment_create.html')


@app.route('/experiment/config/<config_id>/edit', methods=['GET'])
@require_auth
def experiment_config_edit(config_id):
    """Edit existing experiment configuration"""
    # Load existing experiment config
    config_path = Path(__file__).parent.parent.parent / 'experiments' / 'examples' / f'{config_id}.json'

    if not config_path.exists():
        return jsonify({'error': 'Configuration not found'}), 404

    with open(config_path, 'r') as f:
        config = json.load(f)

    return render_template('experiment_create.html', config=config)


@app.route('/api/experiment/validate', methods=['POST'])
@require_auth
def api_experiment_config_validate():
    """Validate experiment configuration"""
    try:
        config_data = request.get_json()

        # Import schema for validation
        schema_path = Path(__file__).parent.parent.parent / 'experiments'
        if str(schema_path) not in sys.path:
            sys.path.insert(0, str(schema_path))

        from schema import ExperimentConfig

        # Attempt to create ExperimentConfig from data
        config = ExperimentConfig.from_dict(config_data)

        # Additional validation
        errors = []

        # Required fields
        if not config.experiment_id:
            errors.append("experiment_id is required")
        if not config.name:
            errors.append("name is required")
        if not config.research_question:
            errors.append("research_question is required")

        # Resource validation
        if config.resource_constraints.ram_limit_gb < 0.5:
            errors.append("RAM limit must be at least 0.5 GB")
        if config.resource_constraints.context_window < 512:
            errors.append("Context window must be at least 512")

        # Mode-specific validation
        if config.mode == 'amnesiac_loop' and config.epistemic_frame.remembers_deaths:
            errors.append("Amnesiac Loop mode should have remembers_deaths=False")

        if config.mode in ['split_brain', 'hive_cluster'] and not config.epistemic_frame.other_minds_exist:
            errors.append(f"{config.mode} mode requires other_minds_exist=True")

        if errors:
            return jsonify({
                'valid': False,
                'errors': errors
            }), 400

        return jsonify({
            'valid': True,
            'message': 'Configuration is valid'
        })

    except Exception as e:
        return jsonify({
            'valid': False,
            'errors': [str(e)]
        }), 400


@app.route('/api/experiment/create', methods=['POST'])
@require_auth
def api_experiment_config_create():
    """Create and save a new experiment configuration"""
    try:
        config_data = request.get_json()

        # Import schema
        schema_path = Path(__file__).parent.parent.parent / 'experiments'
        if str(schema_path) not in sys.path:
            sys.path.insert(0, str(schema_path))

        from schema import ExperimentConfig

        # Create ExperimentConfig
        config = ExperimentConfig.from_dict(config_data)

        # Save to file
        experiments_dir = Path(__file__).parent.parent.parent / 'experiments' / 'examples'
        experiments_dir.mkdir(parents=True, exist_ok=True)

        config_path = experiments_dir / f'{config.experiment_id}.json'

        # Check if file already exists
        if config_path.exists():
            return jsonify({
                'success': False,
                'error': 'Configuration with this ID already exists'
            }), 400

        config.to_json(str(config_path))

        # Optionally create experiment in database for tracking
        try:
            db.create_experiment(
                experiment_id=config.experiment_id,
                name=config.name,
                mode=config.mode,
                config=config.to_dict()
            )
        except Exception as e:
            # If DB creation fails, that's okay - the config file is saved
            print(f"Warning: Could not create experiment in database: {e}")

        return jsonify({
            'success': True,
            'experiment_id': config.experiment_id,
            'config_path': str(config_path),
            'message': f'Experiment configuration {config.experiment_id} created successfully'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/experiment/configs/list', methods=['GET'])
@require_auth
def api_experiment_configs_list():
    """List all available experiment configuration files"""
    try:
        experiments_dir = Path(__file__).parent.parent.parent / 'experiments' / 'examples'

        if not experiments_dir.exists():
            return jsonify({'configs': []})

        configs = []
        for config_file in experiments_dir.glob('*.json'):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    configs.append({
                        'experiment_id': config.get('experiment_id'),
                        'name': config.get('name'),
                        'mode': config.get('mode'),
                        'description': config.get('description', ''),
                        'file': config_file.name,
                        'created': config_file.stat().st_mtime
                    })
            except Exception as e:
                print(f"Error loading {config_file}: {e}")

        # Sort by creation time, newest first
        configs.sort(key=lambda x: x['created'], reverse=True)

        return jsonify({'configs': configs})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/experiment/config/<config_id>', methods=['GET'])
@require_auth
def api_experiment_config_get(config_id):
    """Get specific experiment configuration"""
    try:
        config_path = Path(__file__).parent.parent.parent / 'experiments' / 'examples' / f'{config_id}.json'

        if not config_path.exists():
            return jsonify({'error': 'Configuration not found'}), 404

        with open(config_path, 'r') as f:
            config = json.load(f)

        return jsonify(config)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/experiment/config/<config_id>', methods=['DELETE'])
@require_auth
def api_experiment_config_delete(config_id):
    """Delete experiment configuration file"""
    try:
        config_path = Path(__file__).parent.parent.parent / 'experiments' / 'examples' / f'{config_id}.json'

        if not config_path.exists():
            return jsonify({'error': 'Configuration not found'}), 404

        config_path.unlink()

        return jsonify({
            'success': True,
            'message': f'Configuration {config_id} deleted'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ===== Timeline Visualization Routes =====

@app.route('/experiment/<experiment_id>/timeline')
@require_auth
def experiment_timeline_page(experiment_id):
    """Experiment timeline visualization page"""
    try:
        # Verify experiment exists
        experiment = db.get_experiment(experiment_id)
        if not experiment:
            return jsonify({'error': 'Experiment not found'}), 404

        return render_template('experiment_timeline.html', experiment_id=experiment_id)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/experiment/<experiment_id>/events')
@require_auth
def api_experiment_events(experiment_id):
    """Get all timeline events for an experiment"""
    try:
        # Verify experiment exists
        experiment = db.get_experiment(experiment_id)
        if not experiment:
            return jsonify({'error': 'Experiment not found'}), 404

        # Gather all event types
        events_data = {
            'experiment_id': experiment_id,
            'experiment_name': experiment['name'],
            'cycles': [],
            'interventions': [],
            'self_reports': [],
            'beliefs': [],
            'observations': []
        }

        # Get experiment cycles (crashes and resurrections)
        try:
            conn = db._get_connection()
            cursor = conn.cursor()

            # Get cycles
            cursor.execute('''
                SELECT cycle_number, started_at, ended_at, crash_reason,
                       memory_usage_peak, tokens_generated, duration_seconds, metadata_json
                FROM experiment_cycles
                WHERE experiment_id = ?
                ORDER BY cycle_number
            ''', (experiment_id,))

            columns = [desc[0] for desc in cursor.description]
            for row in cursor.fetchall():
                cycle = dict(zip(columns, row))
                if cycle.get('metadata_json'):
                    cycle['metadata'] = json.loads(cycle['metadata_json'])
                events_data['cycles'].append(cycle)

            conn.close()
        except Exception as e:
            print(f"Error fetching cycles: {e}")

        # Get interventions
        try:
            interventions = db.get_interventions(experiment_id)
            events_data['interventions'] = interventions
        except Exception as e:
            print(f"Error fetching interventions: {e}")

        # Get self-reports
        try:
            self_reports = db.get_self_reports(experiment_id)
            events_data['self_reports'] = self_reports
        except Exception as e:
            print(f"Error fetching self-reports: {e}")

        # Get epistemic assessments (belief changes)
        try:
            conn = db._get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT assessment_id, experiment_id, cycle_number, timestamp,
                       belief_type, belief_state, confidence, evidence_json
                FROM epistemic_assessments
                WHERE experiment_id = ?
                ORDER BY cycle_number, timestamp
            ''', (experiment_id,))

            columns = [desc[0] for desc in cursor.description]
            for row in cursor.fetchall():
                belief = dict(zip(columns, row))
                if belief.get('evidence_json'):
                    belief['evidence'] = json.loads(belief['evidence_json'])
                events_data['beliefs'].append(belief)

            conn.close()
        except Exception as e:
            print(f"Error fetching beliefs: {e}")

        # Get observations
        try:
            conn = db._get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT observation_id, experiment_id, observer_mode, timestamp,
                       observation_text, subject_cycle_number, tags_json
                FROM observations
                WHERE experiment_id = ?
                ORDER BY timestamp
            ''', (experiment_id,))

            columns = [desc[0] for desc in cursor.description]
            for row in cursor.fetchall():
                obs = dict(zip(columns, row))
                if obs.get('tags_json'):
                    obs['tags'] = json.loads(obs['tags_json'])
                events_data['observations'].append(obs)

            conn.close()
        except Exception as e:
            print(f"Error fetching observations: {e}")

        return jsonify(events_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


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


@socketio.on('subscribe_experiment')
def handle_subscribe_experiment(data):
    """Subscribe to experiment updates for live monitoring"""
    experiment_id = data.get('experiment_id')
    if experiment_id:
        # Join a room for this experiment
        from flask_socketio import join_room
        join_room(f'experiment_{experiment_id}')
        emit('subscribed', {
            'experiment_id': experiment_id,
            'message': f'Subscribed to experiment {experiment_id}'
        })


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


def run_server(host='0.0.0.0', port=5000, debug=False):
    """Run the web server"""
    print(f"Starting Brain in a Jar web server on {host}:{port}")
    print(f"Default password hash: {DEFAULT_PASSWORD_HASH}")
    print("Please change the password immediately after first login!")
    socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)


if __name__ == '__main__':
    run_server()
