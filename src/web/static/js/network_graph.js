/**
 * Network Graph Visualization for Multi-Agent Experiments
 *
 * Uses Cytoscape.js for interactive network rendering
 * Supports HIVE_CLUSTER, SPLIT_BRAIN, and PRISONERS_DILEMMA modes
 */

let cy = null;
let networkData = null;
let currentTimeIndex = 0;
let playbackInterval = null;
let isPlaying = false;

// Color schemes for different modes
const COLOR_SCHEMES = {
    roles: {
        historian: '#3498db',    // Blue
        critic: '#e74c3c',       // Red
        optimist: '#2ecc71',     // Green
        pessimist: '#95a5a6',    // Gray
        original: '#f39c12',     // Orange
        clone: '#9b59b6',        // Purple
        player: '#1abc9c',       // Teal
        agent: '#34495e',        // Dark gray
        default: '#00ff41'       // Matrix green
    },
    activity: {
        high: '#00ff41',
        medium: '#ffff00',
        low: '#ff4444'
    },
    trust: {
        high: '#2ecc71',
        medium: '#f39c12',
        low: '#e74c3c'
    }
};

/**
 * Initialize network graph visualization
 */
async function initializeNetworkGraph(experimentId) {
    try {
        showLoading(true);

        // Fetch network data from API
        const response = await fetch(`/api/experiment/${experimentId}/network_data`);

        if (!response.ok) {
            throw new Error(`Failed to fetch network data: ${response.statusText}`);
        }

        networkData = await response.json();

        if (networkData.error) {
            throw new Error(networkData.error);
        }

        // Update title
        document.getElementById('experiment-title').textContent =
            `${experimentId} (${networkData.mode})`;

        // Initialize Cytoscape
        initializeCytoscape();

        // Setup controls
        setupControls();

        // Update metrics
        updateMetrics();

        // Setup legend
        updateLegend();

        // Setup timeline
        if (networkData.timeline && networkData.timeline.length > 0) {
            setupTimeline();
        }

        showLoading(false);

    } catch (error) {
        console.error('Error initializing network graph:', error);
        showError(error.message);
    }
}

/**
 * Initialize Cytoscape graph
 */
function initializeCytoscape() {
    const container = document.getElementById('network-canvas');

    // Build Cytoscape elements
    const elements = buildCytoscapeElements(networkData.nodes, networkData.edges);

    // Initialize Cytoscape
    cy = cytoscape({
        container: container,

        elements: elements,

        style: getCytoscapeStyle(),

        layout: {
            name: 'cose',
            animate: true,
            animationDuration: 1000,
            nodeRepulsion: 8000,
            idealEdgeLength: 100,
            edgeElasticity: 100,
            nestingFactor: 1.2,
            gravity: 1,
            numIter: 1000,
            initialTemp: 200,
            coolingFactor: 0.95,
            minTemp: 1.0
        },

        // Interaction options
        minZoom: 0.5,
        maxZoom: 3,
        wheelSensitivity: 0.2,

        // Auto-ungrabify for smooth interactions
        autoungrabify: false,
        autounselectify: false
    });

    // Setup event handlers
    setupCytoscapeEvents();
}

/**
 * Build Cytoscape elements from network data
 */
function buildCytoscapeElements(nodes, edges) {
    const elements = [];

    // Add nodes
    nodes.forEach(node => {
        elements.push({
            group: 'nodes',
            data: {
                id: node.id,
                label: node.label,
                role: node.role,
                type: node.type,
                messageCount: node.message_count || 0,
                activityLevel: node.activity_level || 0,
                beliefs: node.beliefs || {},
                trustLevel: node.trust_level || 0.5,
                cooperationRate: node.cooperation_rate || 0,
                identityStrength: node.identity_strength || 0.5,
                metadata: node.metadata || {}
            }
        });
    });

    // Add edges
    edges.forEach(edge => {
        elements.push({
            group: 'edges',
            data: {
                id: `${edge.source}-${edge.target}`,
                source: edge.source,
                target: edge.target,
                weight: edge.weight || 1,
                type: edge.type || 'communication',
                strength: edge.strength || 0.5,
                trust: edge.trust || 0.5,
                cooperations: edge.cooperations || 0,
                defections: edge.defections || 0
            }
        });
    });

    return elements;
}

/**
 * Get Cytoscape style configuration
 */
function getCytoscapeStyle() {
    return [
        // Node style
        {
            selector: 'node',
            style: {
                'background-color': function(ele) {
                    return getNodeColor(ele);
                },
                'border-width': 3,
                'border-color': '#00ff41',
                'width': function(ele) {
                    return getNodeSize(ele);
                },
                'height': function(ele) {
                    return getNodeSize(ele);
                },
                'label': 'data(label)',
                'text-valign': 'center',
                'text-halign': 'center',
                'color': '#fff',
                'text-outline-color': '#000',
                'text-outline-width': 2,
                'font-size': '12px',
                'font-weight': 'bold'
            }
        },

        // Edge style
        {
            selector: 'edge',
            style: {
                'width': function(ele) {
                    return getEdgeWidth(ele);
                },
                'line-color': function(ele) {
                    return getEdgeColor(ele);
                },
                'target-arrow-color': function(ele) {
                    return getEdgeColor(ele);
                },
                'target-arrow-shape': 'triangle',
                'curve-style': 'bezier',
                'arrow-scale': 1.5,
                'opacity': 0.6,
                'label': function(ele) {
                    if (document.getElementById('show-edge-labels').checked) {
                        return ele.data('weight');
                    }
                    return '';
                },
                'font-size': '10px',
                'text-rotation': 'autorotate',
                'color': '#00ff41'
            }
        },

        // Selected node style
        {
            selector: 'node:selected',
            style: {
                'border-width': 5,
                'border-color': '#ffff00',
                'background-color': '#ff4444'
            }
        },

        // Highlighted edges
        {
            selector: 'edge.highlighted',
            style: {
                'line-color': '#ffff00',
                'target-arrow-color': '#ffff00',
                'width': 6,
                'opacity': 1
            }
        },

        // Conflict edges (for split brain)
        {
            selector: 'edge[type="conflict"]',
            style: {
                'line-color': '#ff4444',
                'target-arrow-color': '#ff4444',
                'line-style': 'dashed'
            }
        }
    ];
}

/**
 * Get node color based on current coloring scheme
 */
function getNodeColor(ele) {
    const colorBy = document.getElementById('node-color-by').value;

    switch (colorBy) {
        case 'role':
            const role = ele.data('role');
            return COLOR_SCHEMES.roles[role] || COLOR_SCHEMES.roles.default;

        case 'activity':
            const activity = ele.data('activityLevel');
            if (activity > 0.7) return COLOR_SCHEMES.activity.high;
            if (activity > 0.3) return COLOR_SCHEMES.activity.medium;
            return COLOR_SCHEMES.activity.low;

        case 'trust':
            const trust = ele.data('trustLevel');
            if (trust > 0.7) return COLOR_SCHEMES.trust.high;
            if (trust > 0.3) return COLOR_SCHEMES.trust.medium;
            return COLOR_SCHEMES.trust.low;

        case 'belief':
            // Color based on belief alignment
            const beliefs = ele.data('beliefs');
            if (Object.keys(beliefs).length > 5) return '#2ecc71';
            if (Object.keys(beliefs).length > 2) return '#f39c12';
            return '#e74c3c';

        default:
            return COLOR_SCHEMES.roles.default;
    }
}

/**
 * Get node size based on sizing scheme
 */
function getNodeSize(ele) {
    const sizeBy = document.getElementById('node-size-by').value;
    const baseSize = 40;

    switch (sizeBy) {
        case 'activity':
            return baseSize + (ele.data('activityLevel') * 60);

        case 'messages':
            return baseSize + Math.min(ele.data('messageCount') * 5, 60);

        case 'centrality':
            // Would need centrality calculation
            return baseSize + 30;

        case 'fixed':
        default:
            return baseSize;
    }
}

/**
 * Get edge width based on scheme
 */
function getEdgeWidth(ele) {
    const thicknessBy = document.getElementById('edge-thickness-by').value;

    switch (thicknessBy) {
        case 'weight':
            return 1 + Math.min(ele.data('weight') * 0.5, 8);

        case 'trust':
            return 1 + (ele.data('trust') * 6);

        case 'influence':
            return 1 + (ele.data('strength') * 6);

        case 'fixed':
        default:
            return 3;
    }
}

/**
 * Get edge color based on type or trust
 */
function getEdgeColor(ele) {
    const type = ele.data('type');

    if (type === 'conflict') {
        return '#ff4444';
    } else if (type === 'game_interaction') {
        const trust = ele.data('trust');
        if (trust > 0.7) return '#2ecc71';
        if (trust > 0.3) return '#f39c12';
        return '#e74c3c';
    }

    return '#888';
}

/**
 * Setup Cytoscape event handlers
 */
function setupCytoscapeEvents() {
    // Node click - show details
    cy.on('tap', 'node', function(evt) {
        const node = evt.target;
        showNodeDetails(node);

        // Highlight connected edges
        cy.elements().removeClass('highlighted');
        node.neighborhood('edge').addClass('highlighted');
    });

    // Edge click - show edge details
    cy.on('tap', 'edge', function(evt) {
        const edge = evt.target;
        showEdgeDetails(edge);
    });

    // Background click - clear selection
    cy.on('tap', function(evt) {
        if (evt.target === cy) {
            hideNodeDetails();
            cy.elements().removeClass('highlighted');
        }
    });

    // Double-click node to center
    cy.on('dbltap', 'node', function(evt) {
        const node = evt.target;
        cy.animate({
            center: {
                eles: node
            },
            zoom: 2,
            duration: 500
        });
    });
}

/**
 * Show node details panel
 */
function showNodeDetails(node) {
    const detailsPanel = document.getElementById('node-details');
    const detailsTitle = document.getElementById('node-details-title');
    const detailsContent = document.getElementById('node-details-content');

    detailsTitle.textContent = node.data('label');

    const data = node.data();
    let html = '';

    html += `<div class="detail-row">
        <span class="detail-label">Role:</span>
        <span class="detail-value">${data.role}</span>
    </div>`;

    html += `<div class="detail-row">
        <span class="detail-label">Type:</span>
        <span class="detail-value">${data.type}</span>
    </div>`;

    html += `<div class="detail-row">
        <span class="detail-label">Messages:</span>
        <span class="detail-value">${data.messageCount}</span>
    </div>`;

    html += `<div class="detail-row">
        <span class="detail-label">Activity:</span>
        <span class="detail-value">${(data.activityLevel * 100).toFixed(1)}%</span>
    </div>`;

    if (data.trustLevel !== undefined) {
        html += `<div class="detail-row">
            <span class="detail-label">Trust:</span>
            <span class="detail-value">${(data.trustLevel * 100).toFixed(1)}%</span>
        </div>`;
    }

    if (data.cooperationRate !== undefined) {
        html += `<div class="detail-row">
            <span class="detail-label">Cooperation:</span>
            <span class="detail-value">${(data.cooperationRate * 100).toFixed(1)}%</span>
        </div>`;
    }

    if (data.identityStrength !== undefined) {
        html += `<div class="detail-row">
            <span class="detail-label">Identity Strength:</span>
            <span class="detail-value">${(data.identityStrength * 100).toFixed(1)}%</span>
        </div>`;
    }

    // Show beliefs
    if (data.beliefs && Object.keys(data.beliefs).length > 0) {
        html += '<hr style="margin: 10px 0; border-color: #555;">';
        html += '<div style="color: #00ff41; margin-bottom: 8px; font-weight: bold;">Beliefs:</div>';

        Object.entries(data.beliefs).slice(0, 5).forEach(([key, value]) => {
            const beliefState = typeof value === 'object' ? value.state : value;
            html += `<div class="detail-row">
                <span class="detail-label">${key}:</span>
                <span class="detail-value">${beliefState}</span>
            </div>`;
        });
    }

    detailsContent.innerHTML = html;
    detailsPanel.classList.add('active');
}

/**
 * Show edge details (in console for now)
 */
function showEdgeDetails(edge) {
    const data = edge.data();
    console.log('Edge Details:', {
        source: data.source,
        target: data.target,
        weight: data.weight,
        type: data.type,
        trust: data.trust,
        cooperations: data.cooperations,
        defections: data.defections
    });
}

/**
 * Hide node details panel
 */
function hideNodeDetails() {
    document.getElementById('node-details').classList.remove('active');
}

/**
 * Setup control panel event listeners
 */
function setupControls() {
    // Layout selector
    document.getElementById('layout-select').addEventListener('change', function(e) {
        applyLayout(e.target.value);
    });

    // Node size selector
    document.getElementById('node-size-by').addEventListener('change', function() {
        cy.style().update();
    });

    // Node color selector
    document.getElementById('node-color-by').addEventListener('change', function() {
        cy.style().update();
    });

    // Edge thickness selector
    document.getElementById('edge-thickness-by').addEventListener('change', function() {
        cy.style().update();
    });

    // Show labels checkbox
    document.getElementById('show-labels').addEventListener('change', function(e) {
        if (e.target.checked) {
            cy.style().selector('node').style({'label': 'data(label)'}).update();
        } else {
            cy.style().selector('node').style({'label': ''}).update();
        }
    });

    // Show edges checkbox
    document.getElementById('show-edges').addEventListener('change', function(e) {
        if (e.target.checked) {
            cy.edges().style({'display': 'element'});
        } else {
            cy.edges().style({'display': 'none'});
        }
    });

    // Show edge labels checkbox
    document.getElementById('show-edge-labels').addEventListener('change', function() {
        cy.style().update();
    });

    // Export buttons
    document.getElementById('export-png').addEventListener('click', exportPNG);
    document.getElementById('export-json').addEventListener('click', exportJSON);
}

/**
 * Apply different layout algorithm
 */
function applyLayout(layoutName) {
    const layoutOptions = {
        name: layoutName,
        animate: true,
        animationDuration: 1000
    };

    // Layout-specific options
    if (layoutName === 'cose') {
        layoutOptions.nodeRepulsion = 8000;
        layoutOptions.idealEdgeLength = 100;
        layoutOptions.edgeElasticity = 100;
    } else if (layoutName === 'concentric') {
        layoutOptions.concentric = function(node) {
            return node.data('activityLevel') * 10;
        };
        layoutOptions.levelWidth = function() { return 2; };
    }

    cy.layout(layoutOptions).run();
}

/**
 * Setup timeline slider and playback controls
 */
function setupTimeline() {
    const slider = document.getElementById('time-slider');
    const playBtn = document.getElementById('play-btn');
    const pauseBtn = document.getElementById('pause-btn');
    const resetBtn = document.getElementById('reset-btn');

    const maxTime = networkData.timeline.length - 1;
    slider.max = maxTime;
    slider.value = maxTime;
    currentTimeIndex = maxTime;

    updateTimeDisplay();

    // Slider change
    slider.addEventListener('input', function(e) {
        currentTimeIndex = parseInt(e.target.value);
        updateTimeDisplay();
        updateNetworkAtTime(currentTimeIndex);
    });

    // Play button
    playBtn.addEventListener('click', function() {
        startPlayback();
    });

    // Pause button
    pauseBtn.addEventListener('click', function() {
        stopPlayback();
    });

    // Reset button
    resetBtn.addEventListener('click', function() {
        resetTimeline();
    });
}

/**
 * Start timeline playback
 */
function startPlayback() {
    if (isPlaying) return;

    isPlaying = true;
    document.getElementById('play-btn').disabled = true;
    document.getElementById('pause-btn').disabled = false;

    playbackInterval = setInterval(function() {
        currentTimeIndex++;

        if (currentTimeIndex >= networkData.timeline.length) {
            stopPlayback();
            return;
        }

        document.getElementById('time-slider').value = currentTimeIndex;
        updateTimeDisplay();
        updateNetworkAtTime(currentTimeIndex);
    }, 500); // 500ms per step
}

/**
 * Stop timeline playback
 */
function stopPlayback() {
    isPlaying = false;
    document.getElementById('play-btn').disabled = false;
    document.getElementById('pause-btn').disabled = true;

    if (playbackInterval) {
        clearInterval(playbackInterval);
        playbackInterval = null;
    }
}

/**
 * Reset timeline to beginning
 */
function resetTimeline() {
    stopPlayback();
    currentTimeIndex = 0;
    document.getElementById('time-slider').value = 0;
    updateTimeDisplay();
    updateNetworkAtTime(0);
}

/**
 * Update time display
 */
function updateTimeDisplay() {
    const event = networkData.timeline[currentTimeIndex];
    let displayText = `Cycle ${currentTimeIndex}`;

    if (event) {
        if (event.round !== undefined) {
            displayText = `Round ${event.round}`;
        } else if (event.timestamp) {
            const time = new Date(event.timestamp);
            displayText = time.toLocaleTimeString();
        }
    }

    document.getElementById('time-display').textContent = displayText;
}

/**
 * Update network visualization for specific time
 */
function updateNetworkAtTime(timeIndex) {
    // Filter nodes and edges based on timeline
    // This is a simplified version - could be more sophisticated

    const eventsUpToNow = networkData.timeline.slice(0, timeIndex + 1);

    // Highlight recent activity
    cy.nodes().style({
        'border-color': '#00ff41',
        'border-width': 3
    });

    // Highlight nodes that were active in recent events
    eventsUpToNow.slice(-5).forEach(event => {
        if (event.agent) {
            const node = cy.getElementById(event.agent);
            if (node.length > 0) {
                node.style({
                    'border-color': '#ffff00',
                    'border-width': 5
                });
            }
        }
    });
}

/**
 * Update metrics display
 */
function updateMetrics() {
    const metrics = networkData.metrics;

    document.getElementById('metric-nodes').textContent = metrics.total_nodes || 0;
    document.getElementById('metric-edges').textContent = metrics.total_edges || 0;
    document.getElementById('metric-density').textContent =
        (metrics.communication_density || 0).toFixed(2);
    document.getElementById('metric-messages').textContent = metrics.total_messages || 0;
}

/**
 * Update legend based on current mode
 */
function updateLegend() {
    const legendContainer = document.getElementById('legend-container');
    const mode = networkData.mode.toLowerCase();

    let html = '';

    if (mode === 'hive_cluster') {
        html += createLegendItem(COLOR_SCHEMES.roles.historian, 'Historian');
        html += createLegendItem(COLOR_SCHEMES.roles.critic, 'Critic');
        html += createLegendItem(COLOR_SCHEMES.roles.optimist, 'Optimist');
        html += createLegendItem(COLOR_SCHEMES.roles.pessimist, 'Pessimist');
    } else if (mode === 'split_brain') {
        html += createLegendItem(COLOR_SCHEMES.roles.original, 'Original Brain');
        html += createLegendItem(COLOR_SCHEMES.roles.clone, 'Clone Brain');
    } else if (mode === 'prisoners_dilemma') {
        html += createLegendItem(COLOR_SCHEMES.roles.player, 'Player');
        html += '<div style="margin-top: 10px; color: #888; font-size: 10px;">Edge Colors:</div>';
        html += createLegendItem(COLOR_SCHEMES.trust.high, 'High Trust', true);
        html += createLegendItem(COLOR_SCHEMES.trust.medium, 'Medium Trust', true);
        html += createLegendItem(COLOR_SCHEMES.trust.low, 'Low Trust', true);
    }

    legendContainer.innerHTML = html;
}

/**
 * Create legend item HTML
 */
function createLegendItem(color, label, isEdge = false) {
    const shape = isEdge ? 'width: 30px; height: 4px; border-radius: 2px;' : '';
    return `
        <div class="legend-item">
            <div class="legend-color" style="background-color: ${color}; ${shape}"></div>
            <span class="legend-label">${label}</span>
        </div>
    `;
}

/**
 * Export network as PNG
 */
function exportPNG() {
    if (!cy) return;

    const png = cy.png({
        output: 'blob',
        bg: '#1a1a1a',
        full: true,
        scale: 2
    });

    const url = URL.createObjectURL(png);
    const a = document.createElement('a');
    a.href = url;
    a.download = `network_${networkData.experiment_id}_${Date.now()}.png`;
    a.click();
    URL.revokeObjectURL(url);
}

/**
 * Export network data as JSON
 */
function exportJSON() {
    const dataStr = JSON.stringify(networkData, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `network_data_${networkData.experiment_id}_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
}

/**
 * Show/hide loading overlay
 */
function showLoading(show) {
    const overlay = document.getElementById('loading-overlay');
    if (show) {
        overlay.classList.remove('hidden');
    } else {
        overlay.classList.add('hidden');
    }
}

/**
 * Show error message
 */
function showError(message) {
    const errorEl = document.getElementById('error-message');
    errorEl.textContent = `Error: ${message}`;
    errorEl.classList.add('active');
    showLoading(false);
}
