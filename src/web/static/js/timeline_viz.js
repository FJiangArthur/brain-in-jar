/**
 * Timeline Visualization for Brain in a Jar Experiments
 * Interactive D3.js-based timeline with multi-agent support
 */

class TimelineVisualization {
    constructor(containerId, experimentId) {
        this.containerId = containerId;
        this.experimentId = experimentId;

        // Configuration
        this.config = {
            width: 0,
            height: 600,
            margin: { top: 40, right: 40, bottom: 60, left: 80 },
            eventRadius: 8,
            rowHeight: 80,
            minZoom: 0.5,
            maxZoom: 20,
            transitionDuration: 300
        };

        // State
        this.state = {
            events: [],
            annotations: [],
            filters: new Set(['crash', 'resurrection', 'intervention', 'self_report', 'belief_change', 'observation']),
            zoom: 1,
            pan: 0,
            playing: false,
            playbackPosition: 0,
            playbackSpeed: 1,
            selectedEvent: null,
            timeRange: null
        };

        // Event type configuration
        this.eventTypes = {
            crash: { color: '#ff0000', label: 'Crash', icon: '💀' },
            resurrection: { color: '#00ff00', label: 'Resurrection', icon: '✨' },
            intervention: { color: '#ffff00', label: 'Intervention', icon: '⚡' },
            self_report: { color: '#0088ff', label: 'Self-Report', icon: '💭' },
            belief_change: { color: '#ff00ff', label: 'Belief Change', icon: '🔮' },
            observation: { color: '#ff8800', label: 'Observation', icon: '👁️' }
        };

        // D3 objects
        this.svg = null;
        this.xScale = null;
        this.yScale = null;
        this.zoomBehavior = null;

        // Playback
        this.playbackInterval = null;
    }

    async init() {
        console.log('Initializing timeline visualization...');

        // Set up container dimensions
        const container = document.getElementById(this.containerId);
        this.config.width = container.clientWidth;

        // Load experiment data
        await this.loadExperimentData();

        // Set up event listeners
        this.setupEventListeners();

        // Create SVG
        this.createSVG();

        // Render timeline
        this.render();

        // Update statistics
        this.updateStatistics();

        console.log('Timeline visualization initialized');
    }

    async loadExperimentData() {
        try {
            document.getElementById('connection-status').classList.remove('connected');
            document.getElementById('connection-text').textContent = 'Loading...';

            // Fetch experiment details
            const expResponse = await fetch(`/api/experiment/${this.experimentId}`);
            if (!expResponse.ok) throw new Error('Failed to load experiment');

            const experiment = await expResponse.json();
            document.getElementById('experiment-title').textContent =
                `${experiment.name} (${experiment.experiment_id})`;

            // Fetch timeline events
            const eventsResponse = await fetch(`/api/experiment/${this.experimentId}/events`);
            if (!eventsResponse.ok) throw new Error('Failed to load events');

            const eventsData = await eventsResponse.json();
            this.state.events = this.processEvents(eventsData);

            // Set time range
            if (this.state.events.length > 0) {
                const times = this.state.events.map(e => e.timestamp);
                this.state.timeRange = {
                    start: Math.min(...times),
                    end: Math.max(...times)
                };
            }

            document.getElementById('connection-status').classList.add('connected');
            document.getElementById('connection-text').textContent = 'Loaded';

        } catch (error) {
            console.error('Error loading experiment data:', error);
            document.getElementById('connection-text').textContent = 'Error';
            alert('Failed to load experiment data: ' + error.message);
        }
    }

    processEvents(eventsData) {
        const events = [];
        let eventId = 0;

        // Process crashes (from cycles)
        if (eventsData.cycles) {
            eventsData.cycles.forEach(cycle => {
                if (cycle.ended_at && cycle.crash_reason) {
                    events.push({
                        id: `crash_${eventId++}`,
                        type: 'crash',
                        timestamp: new Date(cycle.ended_at).getTime(),
                        cycle: cycle.cycle_number,
                        data: {
                            reason: cycle.crash_reason,
                            duration: cycle.duration_seconds,
                            memory_peak: cycle.memory_usage_peak,
                            tokens: cycle.tokens_generated
                        }
                    });
                }

                // Resurrection is the start of the next cycle
                if (cycle.started_at) {
                    events.push({
                        id: `resurrection_${eventId++}`,
                        type: 'resurrection',
                        timestamp: new Date(cycle.started_at).getTime(),
                        cycle: cycle.cycle_number,
                        data: {
                            cycle_number: cycle.cycle_number
                        }
                    });
                }
            });
        }

        // Process interventions
        if (eventsData.interventions) {
            eventsData.interventions.forEach(intervention => {
                events.push({
                    id: `intervention_${eventId++}`,
                    type: 'intervention',
                    timestamp: new Date(intervention.timestamp).getTime(),
                    cycle: intervention.cycle_number,
                    data: {
                        intervention_type: intervention.intervention_type,
                        description: intervention.description,
                        parameters: intervention.parameters,
                        result: intervention.result
                    }
                });
            });
        }

        // Process self-reports
        if (eventsData.self_reports) {
            eventsData.self_reports.forEach(report => {
                events.push({
                    id: `self_report_${eventId++}`,
                    type: 'self_report',
                    timestamp: new Date(report.timestamp).getTime(),
                    cycle: report.cycle_number,
                    data: {
                        question: report.question,
                        response: report.response,
                        confidence: report.confidence_score,
                        category: report.semantic_category
                    }
                });
            });
        }

        // Process belief changes
        if (eventsData.beliefs) {
            eventsData.beliefs.forEach(belief => {
                events.push({
                    id: `belief_${eventId++}`,
                    type: 'belief_change',
                    timestamp: new Date(belief.timestamp).getTime(),
                    cycle: belief.cycle_number,
                    data: {
                        belief_type: belief.belief_type,
                        belief_state: belief.belief_state,
                        confidence: belief.confidence,
                        evidence: belief.evidence
                    }
                });
            });
        }

        // Process observations
        if (eventsData.observations) {
            eventsData.observations.forEach(obs => {
                events.push({
                    id: `observation_${eventId++}`,
                    type: 'observation',
                    timestamp: new Date(obs.timestamp).getTime(),
                    cycle: obs.subject_cycle_number,
                    data: {
                        observer_mode: obs.observer_mode,
                        observation: obs.observation_text,
                        tags: obs.tags
                    }
                });
            });
        }

        // Sort by timestamp
        events.sort((a, b) => a.timestamp - b.timestamp);

        return events;
    }

    createSVG() {
        const container = document.getElementById(this.containerId);
        container.innerHTML = ''; // Clear existing

        // Create SVG
        this.svg = d3.select(`#${this.containerId}`)
            .append('svg')
            .attr('width', this.config.width)
            .attr('height', this.config.height);

        // Create main group for zoom/pan
        this.mainGroup = this.svg.append('g')
            .attr('class', 'main-group')
            .attr('transform', `translate(${this.config.margin.left}, ${this.config.margin.top})`);

        // Create groups for different layers
        this.gridGroup = this.mainGroup.append('g').attr('class', 'grid-layer');
        this.connectionGroup = this.mainGroup.append('g').attr('class', 'connection-layer');
        this.eventGroup = this.mainGroup.append('g').attr('class', 'event-layer');
        this.annotationGroup = this.mainGroup.append('g').attr('class', 'annotation-layer');

        // Setup zoom behavior
        this.setupZoom();
    }

    setupZoom() {
        const self = this;

        this.zoomBehavior = d3.zoom()
            .scaleExtent([this.config.minZoom, this.config.maxZoom])
            .on('zoom', function(event) {
                self.state.zoom = event.transform.k;
                self.state.pan = event.transform.x;
                self.render();
            });

        this.svg.call(this.zoomBehavior);
    }

    render() {
        if (!this.state.events.length) {
            this.showEmptyState();
            return;
        }

        // Calculate dimensions
        const innerWidth = this.config.width - this.config.margin.left - this.config.margin.right;
        const innerHeight = this.config.height - this.config.margin.top - this.config.margin.bottom;

        // Create scales
        this.xScale = d3.scaleTime()
            .domain([this.state.timeRange.start, this.state.timeRange.end])
            .range([0, innerWidth * this.state.zoom]);

        // Get unique cycles/rows
        const cycles = [...new Set(this.state.events.map(e => e.cycle))].filter(c => c !== null);
        const rowCount = Math.max(cycles.length, 1);

        this.yScale = d3.scaleLinear()
            .domain([0, rowCount])
            .range([0, Math.max(innerHeight, rowCount * this.config.rowHeight)]);

        // Render components
        this.renderGrid();
        this.renderAxis();
        this.renderEvents();
        this.renderConnections();

        // Update playback cursor
        this.updatePlaybackCursor();
    }

    renderGrid() {
        this.gridGroup.selectAll('*').remove();

        const innerWidth = this.config.width - this.config.margin.left - this.config.margin.right;
        const innerHeight = this.config.height - this.config.margin.top - this.config.margin.bottom;

        // Vertical time grid lines
        const timeScale = this.xScale;
        const ticks = timeScale.ticks(10);

        ticks.forEach(tick => {
            this.gridGroup.append('line')
                .attr('class', 'timeline-grid-line')
                .attr('x1', timeScale(tick))
                .attr('y1', 0)
                .attr('x2', timeScale(tick))
                .attr('y2', innerHeight);
        });

        // Horizontal cycle separators
        const cycles = [...new Set(this.state.events.map(e => e.cycle))].filter(c => c !== null);
        cycles.forEach((cycle, i) => {
            if (i > 0) {
                this.gridGroup.append('line')
                    .attr('class', 'timeline-grid-line')
                    .attr('x1', 0)
                    .attr('y1', this.yScale(i))
                    .attr('x2', innerWidth * this.state.zoom)
                    .attr('y2', this.yScale(i));
            }
        });
    }

    renderAxis() {
        // Remove old axis
        this.svg.selectAll('.axis').remove();

        // X axis (time)
        const xAxis = d3.axisBottom(this.xScale)
            .ticks(10)
            .tickFormat(d3.timeFormat('%H:%M:%S'));

        this.svg.append('g')
            .attr('class', 'axis timeline-axis')
            .attr('transform', `translate(${this.config.margin.left}, ${this.config.height - this.config.margin.bottom})`)
            .call(xAxis)
            .selectAll('text')
            .attr('class', 'timeline-axis-label')
            .style('text-anchor', 'end')
            .attr('dx', '-.8em')
            .attr('dy', '.15em')
            .attr('transform', 'rotate(-45)');

        // Y axis (cycles)
        const cycles = [...new Set(this.state.events.map(e => e.cycle))].filter(c => c !== null).sort((a, b) => a - b);

        const yAxis = d3.axisLeft(this.yScale)
            .tickValues(cycles.map((c, i) => i))
            .tickFormat((d, i) => `Cycle ${cycles[i]}`);

        this.svg.append('g')
            .attr('class', 'axis timeline-axis')
            .attr('transform', `translate(${this.config.margin.left}, ${this.config.margin.top})`)
            .call(yAxis)
            .selectAll('text')
            .attr('class', 'timeline-axis-label');
    }

    renderEvents() {
        const self = this;

        // Filter events
        const visibleEvents = this.state.events.filter(e => this.state.filters.has(e.type));

        // Prepare cycle-to-row mapping
        const cycles = [...new Set(this.state.events.map(e => e.cycle))].filter(c => c !== null).sort((a, b) => a - b);
        const cycleToRow = new Map();
        cycles.forEach((cycle, i) => cycleToRow.set(cycle, i));

        // Bind data
        const events = this.eventGroup.selectAll('.timeline-event')
            .data(visibleEvents, d => d.id);

        // Remove old events
        events.exit().remove();

        // Add new events
        const eventsEnter = events.enter()
            .append('circle')
            .attr('class', 'timeline-event')
            .attr('r', this.config.eventRadius)
            .style('fill', d => this.eventTypes[d.type].color)
            .style('stroke', d => this.eventTypes[d.type].color)
            .style('stroke-width', 2)
            .style('opacity', 0.8)
            .on('click', function(event, d) {
                self.selectEvent(d);
            })
            .on('mouseenter', function(event, d) {
                self.showTooltip(event, d);
            })
            .on('mouseleave', function() {
                self.hideTooltip();
            });

        // Update all events
        events.merge(eventsEnter)
            .transition()
            .duration(this.config.transitionDuration)
            .attr('cx', d => this.xScale(d.timestamp))
            .attr('cy', d => {
                const row = cycleToRow.get(d.cycle) || 0;
                return this.yScale(row) + this.config.rowHeight / 2;
            })
            .attr('class', d => {
                let classes = 'timeline-event';
                if (this.state.selectedEvent && this.state.selectedEvent.id === d.id) {
                    classes += ' selected';
                }
                return classes;
            });
    }

    renderConnections() {
        // Draw connections between related events (e.g., crash to resurrection)
        this.connectionGroup.selectAll('*').remove();

        const cycles = [...new Set(this.state.events.map(e => e.cycle))].filter(c => c !== null).sort((a, b) => a - b);
        const cycleToRow = new Map();
        cycles.forEach((cycle, i) => cycleToRow.set(cycle, i));

        // Find crash-resurrection pairs
        const crashes = this.state.events.filter(e => e.type === 'crash');
        const resurrections = this.state.events.filter(e => e.type === 'resurrection');

        crashes.forEach(crash => {
            // Find corresponding resurrection (next cycle)
            const nextCycle = crash.cycle + 1;
            const resurrection = resurrections.find(r => r.cycle === nextCycle);

            if (resurrection && this.state.filters.has('crash') && this.state.filters.has('resurrection')) {
                const y = this.yScale(cycleToRow.get(crash.cycle) || 0) + this.config.rowHeight / 2;

                this.connectionGroup.append('path')
                    .attr('class', 'timeline-connection')
                    .attr('d', `M ${this.xScale(crash.timestamp)} ${y}
                               L ${this.xScale(resurrection.timestamp)} ${y}`);
            }
        });
    }

    showEmptyState() {
        const container = document.getElementById(this.containerId);
        container.innerHTML = '<div class="loading">No events found for this experiment</div>';
    }

    selectEvent(event) {
        this.state.selectedEvent = event;
        this.render();
        this.showEventDetails(event);
    }

    showEventDetails(event) {
        const panel = document.getElementById('detail-panel');
        const content = document.getElementById('detail-content');

        const eventConfig = this.eventTypes[event.type];

        let html = `
            <div class="detail-field">
                <div class="detail-field-label">Event Type</div>
                <div class="detail-field-value">${eventConfig.icon} ${eventConfig.label}</div>
            </div>
            <div class="detail-field">
                <div class="detail-field-label">Timestamp</div>
                <div class="detail-field-value">${new Date(event.timestamp).toLocaleString()}</div>
            </div>
            <div class="detail-field">
                <div class="detail-field-label">Cycle</div>
                <div class="detail-field-value">${event.cycle || 'N/A'}</div>
            </div>
        `;

        // Add type-specific details
        Object.entries(event.data).forEach(([key, value]) => {
            if (value !== null && value !== undefined) {
                const displayValue = typeof value === 'object' ?
                    JSON.stringify(value, null, 2) : value;

                html += `
                    <div class="detail-field">
                        <div class="detail-field-label">${this.formatLabel(key)}</div>
                        <div class="detail-field-value"><pre>${displayValue}</pre></div>
                    </div>
                `;
            }
        });

        content.innerHTML = html;
        panel.classList.add('visible');
    }

    formatLabel(key) {
        return key
            .replace(/_/g, ' ')
            .replace(/\b\w/g, l => l.toUpperCase());
    }

    showTooltip(mouseEvent, event) {
        const tooltip = this.getOrCreateTooltip();
        const eventConfig = this.eventTypes[event.type];

        const html = `
            <div class="tooltip-title">${eventConfig.icon} ${eventConfig.label}</div>
            <div class="tooltip-content">
                ${new Date(event.timestamp).toLocaleTimeString()}<br>
                Cycle ${event.cycle || 'N/A'}
            </div>
        `;

        tooltip.innerHTML = html;
        tooltip.classList.add('visible');
        tooltip.style.left = (mouseEvent.pageX + 15) + 'px';
        tooltip.style.top = (mouseEvent.pageY + 15) + 'px';
    }

    hideTooltip() {
        const tooltip = this.getOrCreateTooltip();
        tooltip.classList.remove('visible');
    }

    getOrCreateTooltip() {
        let tooltip = document.getElementById('timeline-tooltip');
        if (!tooltip) {
            tooltip = document.createElement('div');
            tooltip.id = 'timeline-tooltip';
            tooltip.className = 'timeline-tooltip';
            document.body.appendChild(tooltip);
        }
        return tooltip;
    }

    updateStatistics() {
        const stats = {
            total: this.state.events.length,
            crashes: this.state.events.filter(e => e.type === 'crash').length,
            interventions: this.state.events.filter(e => e.type === 'intervention').length,
            selfReports: this.state.events.filter(e => e.type === 'self_report').length
        };

        document.getElementById('stat-total-events').textContent = stats.total;
        document.getElementById('stat-crashes').textContent = stats.crashes;
        document.getElementById('stat-interventions').textContent = stats.interventions;
        document.getElementById('stat-self-reports').textContent = stats.selfReports;

        if (this.state.timeRange) {
            const duration = this.state.timeRange.end - this.state.timeRange.start;
            const hours = Math.floor(duration / 3600000);
            const minutes = Math.floor((duration % 3600000) / 60000);
            const seconds = Math.floor((duration % 60000) / 1000);
            document.getElementById('stat-duration').textContent =
                `${hours}h ${minutes}m ${seconds}s`;
        }
    }

    setupEventListeners() {
        const self = this;

        // Zoom controls
        document.getElementById('zoom-in').addEventListener('click', () => {
            this.state.zoom = Math.min(this.state.zoom * 1.5, this.config.maxZoom);
            this.render();
        });

        document.getElementById('zoom-out').addEventListener('click', () => {
            this.state.zoom = Math.max(this.state.zoom / 1.5, this.config.minZoom);
            this.render();
        });

        document.getElementById('reset-zoom').addEventListener('click', () => {
            this.state.zoom = 1;
            this.state.pan = 0;
            this.svg.call(this.zoomBehavior.transform, d3.zoomIdentity);
            this.render();
        });

        document.getElementById('fit-to-screen').addEventListener('click', () => {
            this.fitToScreen();
        });

        // Filter checkboxes
        document.querySelectorAll('.filter-checkbox input[type="checkbox"]').forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                const eventType = this.getAttribute('data-event-type');
                if (this.checked) {
                    self.state.filters.add(eventType);
                } else {
                    self.state.filters.delete(eventType);
                }
                self.render();
                self.updateStatistics();
            });
        });

        // Playback controls
        document.getElementById('play-pause').addEventListener('click', () => {
            this.togglePlayback();
        });

        document.getElementById('stop-playback').addEventListener('click', () => {
            this.stopPlayback();
        });

        document.getElementById('playback-speed').addEventListener('change', function() {
            self.state.playbackSpeed = parseFloat(this.value);
            if (self.state.playing) {
                self.stopPlayback();
                self.startPlayback();
            }
        });

        // Export controls
        document.getElementById('export-png').addEventListener('click', () => {
            this.exportToPNG();
        });

        document.getElementById('export-svg').addEventListener('click', () => {
            this.exportToSVG();
        });

        document.getElementById('export-json').addEventListener('click', () => {
            this.exportToJSON();
        });

        // Detail panel close
        document.getElementById('close-detail').addEventListener('click', () => {
            document.getElementById('detail-panel').classList.remove('visible');
            this.state.selectedEvent = null;
            this.render();
        });

        // Window resize
        window.addEventListener('resize', () => {
            const container = document.getElementById(this.containerId);
            this.config.width = container.clientWidth;
            this.createSVG();
            this.render();
        });
    }

    fitToScreen() {
        if (!this.state.events.length) return;

        const innerWidth = this.config.width - this.config.margin.left - this.config.margin.right;
        const timeRange = this.state.timeRange.end - this.state.timeRange.start;

        // Calculate zoom to fit
        this.state.zoom = 1;
        this.state.pan = 0;
        this.svg.call(this.zoomBehavior.transform, d3.zoomIdentity);
        this.render();
    }

    togglePlayback() {
        if (this.state.playing) {
            this.pausePlayback();
        } else {
            this.startPlayback();
        }
    }

    startPlayback() {
        this.state.playing = true;
        document.getElementById('play-icon').textContent = '⏸';

        const self = this;
        const duration = this.state.timeRange.end - this.state.timeRange.start;
        const stepTime = 100; // ms
        const step = (duration / 100) * this.state.playbackSpeed;

        this.playbackInterval = setInterval(() => {
            self.state.playbackPosition += step;

            if (self.state.playbackPosition >= duration) {
                self.state.playbackPosition = duration;
                self.stopPlayback();
            }

            self.updatePlaybackCursor();
        }, stepTime);
    }

    pausePlayback() {
        this.state.playing = false;
        document.getElementById('play-icon').textContent = '▶';

        if (this.playbackInterval) {
            clearInterval(this.playbackInterval);
            this.playbackInterval = null;
        }
    }

    stopPlayback() {
        this.pausePlayback();
        this.state.playbackPosition = 0;
        this.updatePlaybackCursor();
    }

    updatePlaybackCursor() {
        if (!this.state.timeRange) return;

        const duration = this.state.timeRange.end - this.state.timeRange.start;
        const percentage = (this.state.playbackPosition / duration) * 100;

        const progressBar = document.getElementById('playback-progress');
        const cursor = document.getElementById('playback-cursor');

        progressBar.style.width = percentage + '%';
        cursor.style.left = percentage + '%';

        // Update time display
        const currentTime = new Date(this.state.timeRange.start + this.state.playbackPosition);
        document.getElementById('current-time-display').textContent =
            currentTime.toLocaleString();
    }

    async exportToPNG() {
        try {
            const container = document.getElementById(this.containerId);
            const canvas = await html2canvas(container, {
                backgroundColor: '#0a0e27'
            });

            const link = document.createElement('a');
            link.download = `timeline_${this.experimentId}_${Date.now()}.png`;
            link.href = canvas.toDataURL();
            link.click();
        } catch (error) {
            console.error('Error exporting to PNG:', error);
            alert('Failed to export PNG: ' + error.message);
        }
    }

    exportToSVG() {
        try {
            const svgElement = this.svg.node();
            const serializer = new XMLSerializer();
            const svgString = serializer.serializeToString(svgElement);

            const blob = new Blob([svgString], { type: 'image/svg+xml' });
            const url = URL.createObjectURL(blob);

            const link = document.createElement('a');
            link.download = `timeline_${this.experimentId}_${Date.now()}.svg`;
            link.href = url;
            link.click();

            URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Error exporting to SVG:', error);
            alert('Failed to export SVG: ' + error.message);
        }
    }

    exportToJSON() {
        try {
            const data = {
                experiment_id: this.experimentId,
                export_date: new Date().toISOString(),
                time_range: this.state.timeRange,
                events: this.state.events,
                annotations: this.state.annotations
            };

            const json = JSON.stringify(data, null, 2);
            const blob = new Blob([json], { type: 'application/json' });
            const url = URL.createObjectURL(blob);

            const link = document.createElement('a');
            link.download = `timeline_data_${this.experimentId}_${Date.now()}.json`;
            link.href = url;
            link.click();

            URL.revokeObjectURL(url);
        } catch (error) {
            console.error('Error exporting to JSON:', error);
            alert('Failed to export JSON: ' + error.message);
        }
    }
}
