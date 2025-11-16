/**
 * Season 3 Experiment Dashboard - Interactive Controls
 * Auto-refresh, filtering, sorting, and experiment management
 */

// Global state
let experiments = [];
let filteredExperiments = [];
let sortColumn = 'created_at';
let sortDirection = 'desc';
let autoRefreshInterval = null;
const REFRESH_INTERVAL = 5000; // 5 seconds

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
    setupEventListeners();
    startAutoRefresh();
});

/**
 * Initialize dashboard - load initial data
 */
async function initializeDashboard() {
    await fetchExperiments();
    updateSummaryCards();
}

/**
 * Setup event listeners for filters and actions
 */
function setupEventListeners() {
    // Filter change listeners
    const statusFilter = document.getElementById('filter-status');
    const modeFilter = document.getElementById('filter-mode');
    const dateFromFilter = document.getElementById('filter-date-from');
    const dateToFilter = document.getElementById('filter-date-to');

    if (statusFilter) statusFilter.addEventListener('change', applyFilters);
    if (modeFilter) modeFilter.addEventListener('change', applyFilters);
    if (dateFromFilter) dateFromFilter.addEventListener('change', applyFilters);
    if (dateToFilter) dateToFilter.addEventListener('change', applyFilters);

    // Clear filters button
    const clearFiltersBtn = document.getElementById('clear-filters');
    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', clearFilters);
    }

    // New experiment button
    const newExpBtn = document.getElementById('new-experiment');
    if (newExpBtn) {
        newExpBtn.addEventListener('click', showNewExperimentDialog);
    }
}

/**
 * Fetch experiments from API
 */
async function fetchExperiments() {
    try {
        showLoading();
        const token = localStorage.getItem('brain_jar_token');
        const response = await fetch('/api/experiments', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const data = await response.json();
            experiments = data.experiments || [];
            applyFilters();
        } else {
            showToast('Failed to fetch experiments', 'error');
        }
    } catch (error) {
        console.error('Error fetching experiments:', error);
        showToast('Connection error', 'error');
    } finally {
        hideLoading();
    }
}

/**
 * Apply filters to experiments
 */
function applyFilters() {
    const statusFilter = document.getElementById('filter-status')?.value || 'all';
    const modeFilter = document.getElementById('filter-mode')?.value || 'all';
    const dateFrom = document.getElementById('filter-date-from')?.value;
    const dateTo = document.getElementById('filter-date-to')?.value;

    filteredExperiments = experiments.filter(exp => {
        // Status filter
        if (statusFilter !== 'all' && exp.status !== statusFilter) {
            return false;
        }

        // Mode filter
        if (modeFilter !== 'all' && exp.mode !== modeFilter) {
            return false;
        }

        // Date range filter
        if (dateFrom) {
            const expDate = new Date(exp.created_at);
            const fromDate = new Date(dateFrom);
            if (expDate < fromDate) return false;
        }

        if (dateTo) {
            const expDate = new Date(exp.created_at);
            const toDate = new Date(dateTo);
            toDate.setHours(23, 59, 59, 999); // End of day
            if (expDate > toDate) return false;
        }

        return true;
    });

    // Apply sorting
    sortExperiments();
    renderExperimentsTable();
    updateSummaryCards();
}

/**
 * Clear all filters
 */
function clearFilters() {
    document.getElementById('filter-status').value = 'all';
    document.getElementById('filter-mode').value = 'all';
    document.getElementById('filter-date-from').value = '';
    document.getElementById('filter-date-to').value = '';
    applyFilters();
}

/**
 * Sort experiments by column
 */
function sortBy(column) {
    if (sortColumn === column) {
        sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
        sortColumn = column;
        sortDirection = 'asc';
    }
    sortExperiments();
    renderExperimentsTable();
}

/**
 * Sort experiments array
 */
function sortExperiments() {
    filteredExperiments.sort((a, b) => {
        let aVal = a[sortColumn];
        let bVal = b[sortColumn];

        // Handle null values
        if (aVal === null || aVal === undefined) return 1;
        if (bVal === null || bVal === undefined) return -1;

        // Compare
        if (typeof aVal === 'string') {
            aVal = aVal.toLowerCase();
            bVal = bVal.toLowerCase();
        }

        if (aVal < bVal) return sortDirection === 'asc' ? -1 : 1;
        if (aVal > bVal) return sortDirection === 'asc' ? 1 : -1;
        return 0;
    });
}

/**
 * Render experiments table
 */
function renderExperimentsTable() {
    const tbody = document.getElementById('experiments-tbody');

    if (!filteredExperiments.length) {
        tbody.innerHTML = `
            <tr>
                <td colspan="9" class="empty-state">
                    <div class="empty-state-icon">🧪</div>
                    <div class="empty-state-text">No experiments found</div>
                    <div class="empty-state-subtext">Try adjusting your filters or create a new experiment</div>
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = filteredExperiments.map(exp => `
        <tr>
            <td><span class="truncate" title="${exp.experiment_id}">${exp.experiment_id}</span></td>
            <td>${exp.name || 'Unnamed'}</td>
            <td><span class="mode-badge">${exp.mode}</span></td>
            <td><span class="status-badge status-${exp.status}">${exp.status}</span></td>
            <td class="metric-highlight">${exp.total_cycles || 0}</td>
            <td class="metric-highlight">${exp.total_crashes || 0}</td>
            <td>${formatDate(exp.created_at)}</td>
            <td class="duration">${calculateDuration(exp.started_at, exp.ended_at, exp.status)}</td>
            <td>
                <div class="action-buttons">
                    <button class="action-btn" onclick="viewExperiment('${exp.experiment_id}')">View</button>
                    <a href="/experiment/${exp.experiment_id}/network" class="action-btn">Network</a>
                    ${exp.status === 'running' ?
                        `<button class="action-btn stop" onclick="stopExperiment('${exp.experiment_id}')">Stop</button>` :
                        ''}
                    <button class="action-btn delete" onclick="deleteExperiment('${exp.experiment_id}')">Delete</button>
                </div>
            </td>
        </tr>
    `).join('');

    // Update sort indicators
    updateSortIndicators();
}

/**
 * Update sort indicators in table headers
 */
function updateSortIndicators() {
    document.querySelectorAll('.experiments-table th').forEach(th => {
        const column = th.dataset.column;
        const indicator = th.querySelector('.sort-indicator');

        if (indicator) {
            if (column === sortColumn) {
                indicator.textContent = sortDirection === 'asc' ? '▲' : '▼';
                indicator.style.opacity = '1';
            } else {
                indicator.textContent = '⬍';
                indicator.style.opacity = '0.3';
            }
        }
    });
}

/**
 * Update summary cards
 */
function updateSummaryCards() {
    // Total experiments
    document.getElementById('total-experiments').textContent = experiments.length;

    // Currently running
    const running = experiments.filter(e => e.status === 'running').length;
    document.getElementById('running-experiments').textContent = running;

    // Completed today
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const completedToday = experiments.filter(e => {
        if (e.status !== 'completed' || !e.ended_at) return false;
        const endDate = new Date(e.ended_at);
        return endDate >= today;
    }).length;
    document.getElementById('completed-today').textContent = completedToday;

    // Total cycles across all experiments
    const totalCycles = experiments.reduce((sum, e) => sum + (e.total_cycles || 0), 0);
    document.getElementById('total-cycles').textContent = totalCycles;
}

/**
 * Format date for display
 */
function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Calculate duration
 */
function calculateDuration(startedAt, endedAt, status) {
    if (!startedAt) return '-';

    const start = new Date(startedAt);
    const end = endedAt ? new Date(endedAt) : new Date();

    const diffMs = end - start;
    const hours = Math.floor(diffMs / (1000 * 60 * 60));
    const minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));

    if (status === 'running') {
        return `${hours}h ${minutes}m (running)`;
    }

    return `${hours}h ${minutes}m`;
}

/**
 * View experiment details
 */
function viewExperiment(experimentId) {
    window.location.href = `/experiment/${experimentId}`;
}

/**
 * Stop a running experiment
 */
async function stopExperiment(experimentId) {
    if (!confirm('Are you sure you want to stop this experiment?')) {
        return;
    }

    try {
        const token = localStorage.getItem('brain_jar_token');
        const response = await fetch(`/api/experiment/${experimentId}/stop`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            showToast('Experiment stopped successfully', 'success');
            await fetchExperiments();
        } else {
            const data = await response.json();
            showToast(data.error || 'Failed to stop experiment', 'error');
        }
    } catch (error) {
        console.error('Error stopping experiment:', error);
        showToast('Connection error', 'error');
    }
}

/**
 * Delete an experiment
 */
async function deleteExperiment(experimentId) {
    if (!confirm('Are you sure you want to delete this experiment? This action cannot be undone.')) {
        return;
    }

    try {
        const token = localStorage.getItem('brain_jar_token');
        const response = await fetch(`/api/experiment/${experimentId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            showToast('Experiment deleted successfully', 'success');
            await fetchExperiments();
        } else {
            const data = await response.json();
            showToast(data.error || 'Failed to delete experiment', 'error');
        }
    } catch (error) {
        console.error('Error deleting experiment:', error);
        showToast('Connection error', 'error');
    }
}

/**
 * Show new experiment dialog (placeholder - could be enhanced with modal)
 */
function showNewExperimentDialog() {
    // For now, redirect to a start script or show info
    showToast('Use run_isolated.py or other scripts to start new experiments', 'info');
}

/**
 * Start auto-refresh
 */
function startAutoRefresh() {
    autoRefreshInterval = setInterval(async () => {
        await fetchExperiments();
    }, REFRESH_INTERVAL);
}

/**
 * Stop auto-refresh
 */
function stopAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
    }
}

/**
 * Show loading state
 */
function showLoading() {
    const tbody = document.getElementById('experiments-tbody');
    if (tbody && experiments.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="9" class="loading">Loading experiments</td>
            </tr>
        `;
    }
}

/**
 * Hide loading state
 */
function hideLoading() {
    // Handled by renderExperimentsTable
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease-out reverse';
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 3000);
}

/**
 * Handle visibility change - pause refresh when tab not visible
 */
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        stopAutoRefresh();
    } else {
        startAutoRefresh();
        fetchExperiments(); // Immediate refresh when tab becomes visible
    }
});

/**
 * Cleanup on page unload
 */
window.addEventListener('beforeunload', function() {
    stopAutoRefresh();
});
