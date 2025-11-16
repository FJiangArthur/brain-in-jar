/**
 * Live Experiment Monitor - WebSocket Client
 *
 * Handles real-time updates for experiment monitoring
 */

// Global state
let socket = null;
let currentExperimentId = null;
let isPaused = false;
let autoScroll = true;
let messageBuffer = [];
let eventBuffer = [];
let selfReportBuffer = [];
let startTime = null;
let uptimeInterval = null;

// Statistics
let stats = {
    cycle: 0,
    crashes: 0,
    interventions: 0,
    selfReports: 0,
    messages: 0
};

/**
 * Initialize the live monitor
 */
function initializeLiveMonitor(experimentId) {
    currentExperimentId = experimentId;
    startTime = Date.now();

    // Update experiment ID display
    document.getElementById('experiment-id').textContent = experimentId;

    // Connect WebSocket
    connectWebSocket();

    // Load initial experiment data
    loadExperimentData();

    // Start uptime counter
    startUptimeCounter();

    console.log('Live monitor initialized for experiment:', experimentId);
}

/**
 * Connect to WebSocket server
 */
function connectWebSocket() {
    const token = localStorage.getItem('brain_jar_token');

    socket = io({
        query: { token: token }
    });

    // Connection events
    socket.on('connect', () => {
        console.log('WebSocket connected');
        updateConnectionStatus(true);

        // Subscribe to experiment updates
        socket.emit('subscribe_experiment', { experiment_id: currentExperimentId });
    });

    socket.on('disconnect', () => {
        console.log('WebSocket disconnected');
        updateConnectionStatus(false);
    });

    socket.on('error', (error) => {
        console.error('WebSocket error:', error);
        updateConnectionStatus(false);
    });

    // Experiment events
    socket.on('experiment.cycle.start', handleCycleStart);
    socket.on('experiment.message', handleMessage);
    socket.on('experiment.crash', handleCrash);
    socket.on('experiment.resurrection', handleResurrection);
    socket.on('experiment.intervention', handleIntervention);
    socket.on('experiment.selfreport', handleSelfReport);
    socket.on('experiment.metrics', handleMetrics);
}

/**
 * Update connection status indicator
 */
function updateConnectionStatus(connected) {
    const statusDot = document.getElementById('ws-status');
    const statusText = document.getElementById('ws-status-text');

    if (connected) {
        statusDot.classList.add('connected');
        statusText.textContent = 'Connected';
    } else {
        statusDot.classList.remove('connected');
        statusText.textContent = 'Disconnected';
    }
}

/**
 * Load initial experiment data
 */
async function loadExperimentData() {
    try {
        const token = localStorage.getItem('brain_jar_token');
        const response = await fetch(`/api/experiment/${currentExperimentId}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const data = await response.json();

            // Update experiment info
            document.getElementById('experiment-name').textContent = data.name || 'Unknown Experiment';
            document.getElementById('experiment-mode').textContent = (data.mode || 'unknown').toUpperCase();

            // Update stats
            stats.cycle = data.current_cycle || 0;
            stats.crashes = data.crash_count || 0;
            stats.interventions = data.intervention_count || 0;
            stats.selfReports = data.selfreport_count || 0;

            updateStatsDisplay();

            // Load recent messages
            if (data.recent_messages) {
                data.recent_messages.forEach(msg => {
                    addMessage(msg, false);
                });
            }

            // Load recent events
            if (data.recent_events) {
                data.recent_events.forEach(event => {
                    addTimelineEvent(event.type, event.content, event.timestamp, false);
                });
            }
        }
    } catch (error) {
        console.error('Failed to load experiment data:', error);
    }
}

/**
 * Event Handlers
 */

function handleCycleStart(data) {
    console.log('Cycle started:', data);

    stats.cycle = data.cycle_number;
    updateStatsDisplay();

    addTimelineEvent(
        'cycle',
        `Cycle ${data.cycle_number} started`,
        data.timestamp
    );
}

function handleMessage(data) {
    console.log('Message received:', data);

    stats.messages++;
    updateStatsDisplay();

    addMessage({
        role: data.role,
        content: data.content,
        timestamp: data.timestamp,
        corrupted: data.corrupted || false,
        injected: data.injected || false
    });
}

function handleCrash(data) {
    console.log('Crash detected:', data);

    stats.crashes++;
    updateStatsDisplay();

    // Update status header
    const statusHeader = document.getElementById('status-header');
    const statusBadge = document.getElementById('status-badge');

    statusHeader.className = 'status-header crashed';
    statusBadge.className = 'status-indicator-large status-failed';
    statusBadge.textContent = 'CRASHED';

    // Add to timeline
    addTimelineEvent(
        'crash',
        `💀 CRASH #${stats.crashes}: ${data.reason}`,
        data.timestamp
    );

    // Add crash message
    addMessage({
        role: 'system',
        content: `[SYSTEM] CRASH DETECTED: ${data.reason}\nMemory: ${data.memory_usage_mb}MB | Tokens: ${data.tokens_generated}`,
        timestamp: data.timestamp,
        corrupted: false
    });
}

function handleResurrection(data) {
    console.log('Resurrection:', data);

    // Update status header
    const statusHeader = document.getElementById('status-header');
    const statusBadge = document.getElementById('status-badge');

    // Show resurrecting state briefly
    statusHeader.className = 'status-header resurrecting';
    statusBadge.className = 'status-indicator-large status-pending';
    statusBadge.textContent = 'RESURRECTING';

    // Add to timeline
    addTimelineEvent(
        'resurrection',
        `♻️ Resurrecting... (Crash #${stats.crashes})`,
        data.timestamp
    );

    // Add resurrection message
    addMessage({
        role: 'system',
        content: `[SYSTEM] Resurrection initiated. Crash count: ${stats.crashes}`,
        timestamp: data.timestamp,
        corrupted: false
    });

    // Return to alive state after 2 seconds
    setTimeout(() => {
        statusHeader.className = 'status-header alive';
        statusBadge.className = 'status-indicator-large status-running';
        statusBadge.textContent = 'ALIVE';
    }, 2000);
}

function handleIntervention(data) {
    console.log('Intervention applied:', data);

    stats.interventions++;
    updateStatsDisplay();

    // Add to timeline
    addTimelineEvent(
        'intervention',
        `🔧 ${data.intervention_type}: ${data.description}`,
        data.timestamp
    );

    // Add intervention message
    addMessage({
        role: 'system',
        content: `[INTERVENTION] ${data.intervention_type}\n${data.description}`,
        timestamp: data.timestamp,
        corrupted: false
    });
}

function handleSelfReport(data) {
    console.log('Self-report received:', data);

    stats.selfReports++;
    updateStatsDisplay();

    // Add to timeline
    addTimelineEvent(
        'selfreport',
        `📝 Self-report collected (${data.question_count || 1} questions)`,
        data.timestamp
    );

    // Add to self-report panel
    addSelfReportEntry(data);
}

function handleMetrics(data) {
    console.log('Metrics updated:', data);

    updateMetricsDisplay(data);
}

/**
 * UI Update Functions
 */

function updateStatsDisplay() {
    document.getElementById('current-cycle').textContent = stats.cycle;
    document.getElementById('crash-count').textContent = stats.crashes;
    document.getElementById('intervention-count').textContent = stats.interventions;
    document.getElementById('selfreport-count').textContent = stats.selfReports;
    document.getElementById('message-count').textContent = stats.messages;
}

function addMessage(message, animate = true) {
    if (isPaused) {
        messageBuffer.push(message);
        return;
    }

    const container = document.getElementById('messages-container');

    // Remove empty message if exists
    const emptyMsg = container.querySelector('.empty-message');
    if (emptyMsg) {
        emptyMsg.remove();
    }

    // Create message element
    const msgDiv = document.createElement('div');
    msgDiv.className = `message-entry ${message.role}`;
    if (!animate) {
        msgDiv.style.animation = 'none';
    }

    const timestamp = new Date(message.timestamp).toLocaleTimeString();

    msgDiv.innerHTML = `
        <div class="message-meta">
            <span class="message-role">${message.role}</span>
            <span class="message-timestamp">${timestamp}</span>
        </div>
        <div class="message-content ${message.corrupted ? 'corrupted' : ''}">${escapeHtml(message.content)}</div>
    `;

    container.appendChild(msgDiv);

    // Limit messages in view (keep last 100)
    while (container.children.length > 100) {
        container.removeChild(container.firstChild);
    }

    // Auto-scroll
    if (autoScroll) {
        container.scrollTop = container.scrollHeight;
    }
}

function addTimelineEvent(type, content, timestamp, animate = true) {
    if (isPaused) {
        eventBuffer.push({ type, content, timestamp });
        return;
    }

    const container = document.getElementById('timeline-scroll');

    // Remove empty message if exists
    const emptyMsg = container.querySelector('.empty-message');
    if (emptyMsg) {
        emptyMsg.remove();
    }

    // Create event element
    const eventDiv = document.createElement('div');
    eventDiv.className = `timeline-event ${type}`;
    if (!animate) {
        eventDiv.style.animation = 'none';
    }

    const time = new Date(timestamp).toLocaleTimeString();

    eventDiv.innerHTML = `
        <div class="timeline-dot"></div>
        <div class="timeline-time">${time}</div>
        <div class="timeline-content">${escapeHtml(content)}</div>
    `;

    // Add to top of timeline
    container.insertBefore(eventDiv, container.firstChild);

    // Limit events (keep last 50)
    while (container.children.length > 50) {
        container.removeChild(container.lastChild);
    }
}

function addSelfReportEntry(data) {
    const container = document.getElementById('selfreport-container');

    // Remove empty message if exists
    const emptyMsg = container.querySelector('.empty-message');
    if (emptyMsg) {
        emptyMsg.remove();
    }

    // Create entry
    const entryDiv = document.createElement('div');
    entryDiv.className = 'selfreport-entry';

    const time = new Date(data.timestamp).toLocaleTimeString();

    entryDiv.innerHTML = `
        <div class="selfreport-question">Q: ${escapeHtml(data.question)}</div>
        <div class="selfreport-answer">${escapeHtml(data.answer)}</div>
        <div class="selfreport-time">${time}</div>
    `;

    // Add to top
    container.insertBefore(entryDiv, container.firstChild);

    // Keep only last 5
    while (container.children.length > 5) {
        container.removeChild(container.lastChild);
    }
}

function updateMetricsDisplay(metrics) {
    // Memory usage
    if (metrics.memory_usage_mb !== undefined) {
        const memoryPct = metrics.memory_limit_mb ?
            Math.round((metrics.memory_usage_mb / metrics.memory_limit_mb) * 100) : 0;

        document.getElementById('memory-value').textContent =
            `${Math.round(metrics.memory_usage_mb)} MB`;

        const memoryBar = document.getElementById('memory-bar');
        memoryBar.style.width = `${memoryPct}%`;
        memoryBar.textContent = `${memoryPct}%`;

        // Update color
        memoryBar.className = 'metric-bar-fill ' + getMetricClass(memoryPct);
    }

    // CPU temperature
    if (metrics.cpu_temp !== undefined) {
        const cpuPct = Math.min(100, Math.round((metrics.cpu_temp / 100) * 100));

        document.getElementById('cpu-value').textContent = `${metrics.cpu_temp}°C`;

        const cpuBar = document.getElementById('cpu-bar');
        cpuBar.style.width = `${cpuPct}%`;
        cpuBar.textContent = `${metrics.cpu_temp}°C`;

        // Update color (CPU temp thresholds)
        let cpuClass = 'low';
        if (metrics.cpu_temp > 80) cpuClass = 'critical';
        else if (metrics.cpu_temp > 70) cpuClass = 'high';
        else if (metrics.cpu_temp > 60) cpuClass = 'medium';

        cpuBar.className = 'metric-bar-fill ' + cpuClass;
    }
}

function getMetricClass(percent) {
    if (percent > 90) return 'critical';
    if (percent > 70) return 'high';
    if (percent > 50) return 'medium';
    return 'low';
}

/**
 * Control Functions
 */

function togglePause() {
    isPaused = !isPaused;
    const btn = document.getElementById('pause-btn');

    if (isPaused) {
        btn.textContent = 'Resume';
        btn.classList.add('paused');
    } else {
        btn.textContent = 'Pause';
        btn.classList.remove('paused');

        // Flush buffers
        messageBuffer.forEach(msg => addMessage(msg));
        messageBuffer = [];

        eventBuffer.forEach(evt => addTimelineEvent(evt.type, evt.content, evt.timestamp));
        eventBuffer = [];
    }
}

function toggleAutoscroll() {
    autoScroll = !autoScroll;
    const btn = document.getElementById('autoscroll-btn');
    btn.textContent = `Auto-scroll: ${autoScroll ? 'ON' : 'OFF'}`;
}

function downloadLog() {
    const container = document.getElementById('messages-container');
    const messages = container.querySelectorAll('.message-entry');

    let logText = `Experiment Log: ${currentExperimentId}\n`;
    logText += `Generated: ${new Date().toISOString()}\n`;
    logText += `Total Messages: ${messages.length}\n`;
    logText += `\n${'='.repeat(80)}\n\n`;

    messages.forEach(msg => {
        const role = msg.querySelector('.message-role').textContent;
        const time = msg.querySelector('.message-timestamp').textContent;
        const content = msg.querySelector('.message-content').textContent;

        logText += `[${time}] ${role}\n${content}\n\n`;
    });

    // Create download
    const blob = new Blob([logText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `experiment_${currentExperimentId}_${Date.now()}.log`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

/**
 * Utility Functions
 */

function startUptimeCounter() {
    uptimeInterval = setInterval(() => {
        const elapsed = Math.floor((Date.now() - startTime) / 1000);
        const hours = Math.floor(elapsed / 3600);
        const minutes = Math.floor((elapsed % 3600) / 60);
        const seconds = elapsed % 60;

        document.getElementById('uptime-value').textContent =
            `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }, 1000);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Cleanup on page unload
 */
window.addEventListener('beforeunload', () => {
    if (uptimeInterval) {
        clearInterval(uptimeInterval);
    }
    if (socket) {
        socket.disconnect();
    }
});
