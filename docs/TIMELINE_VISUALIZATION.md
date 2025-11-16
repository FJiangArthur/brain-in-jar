# Timeline Visualization - Technical Documentation

## Overview

The Timeline Visualization system provides an interactive, D3.js-based interface for exploring the temporal dynamics of Brain in a Jar experiments. It visualizes all experiment events including crashes, resurrections, interventions, self-reports, belief changes, and observations on a unified timeline.

## Architecture

### Components

1. **Frontend (D3.js + HTML/CSS)**
   - `src/web/templates/experiment_timeline.html` - Timeline page template
   - `src/web/static/js/timeline_viz.js` - D3.js visualization logic
   - `src/web/static/css/timeline.css` - Timeline-specific styles

2. **Backend (Flask)**
   - `src/web/web_server.py` - Timeline routes and event API

3. **Database**
   - `src/db/experiment_database.py` - Event data access

## Event Types

The timeline visualizes six types of events:

| Event Type | Color | Icon | Description |
|------------|-------|------|-------------|
| **Crash** | Red (#ff0000) | 💀 | AI instance termination (memory limit, token limit, etc.) |
| **Resurrection** | Green (#00ff00) | ✨ | AI instance restart (beginning of new cycle) |
| **Intervention** | Yellow (#ffff00) | ⚡ | External manipulation (memory injection, parameter change) |
| **Self-Report** | Blue (#0088ff) | 💭 | AI's phenomenological self-report response |
| **Belief Change** | Purple (#ff00ff) | 🔮 | Epistemic assessment update |
| **Observation** | Orange (#ff8800) | 👁️ | Observer/God mode annotation |

## Features

### Interactive Controls

#### Zoom & Pan
- **Zoom In/Out**: Scale the timeline for detail
- **Pan**: Drag to navigate horizontally
- **Reset View**: Return to default zoom level
- **Fit to Screen**: Auto-scale to fit all events

#### Event Filtering
- Toggle event types on/off
- Filter checkboxes in control panel
- Real-time rendering updates

#### Playback Mode
- Animate through timeline chronologically
- Adjustable playback speed (0.5x - 10x)
- Play/Pause/Stop controls
- Visual progress indicator

#### Event Details
- Click any event to view full details
- Detail panel shows:
  - Event type and timestamp
  - Cycle number
  - Type-specific data (e.g., crash reason, intervention parameters)
  - Formatted JSON for complex data

### Export Capabilities

#### Export to PNG
- Renders timeline as raster image
- Uses html2canvas for client-side rendering
- Maintains visual fidelity

#### Export to SVG
- Vector format for scalability
- Preserves D3.js SVG structure
- Ideal for publications

#### Export to JSON
- Raw event data export
- Includes all events and metadata
- Supports data portability

## API Endpoints

### GET /experiment/<experiment_id>/timeline

Renders the timeline visualization page.

**Authentication**: Required
**Parameters**:
- `experiment_id` (path) - Experiment identifier

**Response**: HTML page

---

### GET /api/experiment/<experiment_id>/events

Fetches all timeline events for an experiment.

**Authentication**: Required
**Parameters**:
- `experiment_id` (path) - Experiment identifier

**Response**: JSON object
```json
{
  "experiment_id": "exp_001",
  "experiment_name": "Test Experiment",
  "cycles": [
    {
      "cycle_number": 1,
      "started_at": "2025-11-16T10:00:00",
      "ended_at": "2025-11-16T10:05:00",
      "crash_reason": "Memory limit exceeded",
      "memory_usage_peak": 450.2,
      "tokens_generated": 3500,
      "duration_seconds": 300
    }
  ],
  "interventions": [...],
  "self_reports": [...],
  "beliefs": [...],
  "observations": [...]
}
```

## Data Flow

```
┌─────────────────┐
│  Web Browser    │
│  (Timeline UI)  │
└────────┬────────┘
         │
         ↓ HTTP GET /experiment/<id>/timeline
┌─────────────────┐
│  Flask Server   │
│  (web_server.py)│
└────────┬────────┘
         │
         ↓ Fetch events
┌─────────────────┐
│  SQLite DB      │
│  (experiments.db)│
└────────┬────────┘
         │
         ↓ JSON response
┌─────────────────┐
│  D3.js Render   │
│  (timeline_viz.js)│
└─────────────────┘
```

## Timeline Rendering Logic

### Scale Creation

The timeline uses D3.js scales to map data to visual coordinates:

```javascript
// Time scale (X-axis)
xScale = d3.scaleTime()
    .domain([startTime, endTime])
    .range([0, width * zoom]);

// Cycle scale (Y-axis)
yScale = d3.scaleLinear()
    .domain([0, numCycles])
    .range([0, height]);
```

### Event Positioning

Events are positioned based on:
- **X-coordinate**: Timestamp (scaled to pixels)
- **Y-coordinate**: Cycle number (row in timeline)
- **Radius**: Fixed (8px, configurable)

### Event Connections

The system draws visual connections between related events:
- Crash → Resurrection (dashed line showing cycle transition)
- Can be extended for other relationships

## Multi-Agent Support

The timeline is designed to handle multi-agent experiments:

### Vertical Stacking
- Each cycle gets its own row
- Multiple agents in same cycle share the row
- Events differentiated by horizontal position

### Synchronized Interactions
- Zoom/pan applies to all timelines
- Filter changes affect all event types
- Playback cursor moves across all timelines

### Future Enhancements
- Color-code events by agent
- Agent-specific filtering
- Agent interaction visualization (connections between agents)

## Performance Considerations

### Client-Side Rendering
- All visualization happens in browser (leverages Jetson Orin GPU)
- Server provides data only
- Reduces server load

### Large Dataset Handling
- Tested with 1000+ events
- D3.js efficiently updates DOM
- Filtering provides performance boost

### Optimization Strategies
- SVG-based rendering (hardware accelerated)
- Transition duration configurable
- Debounced resize handlers

## Usage Example

### 1. Generate Demo Data

```bash
python examples/timeline_demo.py
```

This creates two demo experiments:
- `demo_timeline_001` - Rich single-agent timeline
- `demo_multi_agent_001` - Multi-agent timeline

### 2. Start Web Server

```bash
python src/web/web_server.py
```

### 3. Access Timeline

Navigate to:
```
http://localhost:5000/experiment/demo_timeline_001/timeline
```

### 4. Interact

- Use zoom controls to explore details
- Click events to see full information
- Toggle filters to focus on specific event types
- Try playback mode to see events unfold chronologically
- Export timeline for documentation

## Customization

### Event Colors

Edit `timeline_viz.js`:

```javascript
this.eventTypes = {
    crash: { color: '#ff0000', label: 'Crash', icon: '💀' },
    // ... customize colors here
};
```

### Timeline Dimensions

Edit `timeline_viz.js` config:

```javascript
this.config = {
    width: 0,  // Auto-calculated from container
    height: 600,  // Adjust timeline height
    margin: { top: 40, right: 40, bottom: 60, left: 80 },
    eventRadius: 8,  // Event marker size
    rowHeight: 80,   // Height per cycle row
    // ...
};
```

### Styling

Edit `timeline.css` for visual customization:
- Colors, fonts, borders
- Hover effects
- Responsive breakpoints

## Technology Stack

### Frontend
- **D3.js v7** - Data visualization
- **html2canvas** - PNG export
- **Vanilla JavaScript** - No framework dependencies
- **CSS3** - Modern styling with animations

### Backend
- **Flask** - Web framework
- **SQLite** - Data storage
- **Python 3.8+** - Server logic

### Browser Compatibility
- Modern browsers (Chrome, Firefox, Safari, Edge)
- Requires ES6+ JavaScript support
- SVG rendering support

## Troubleshooting

### Timeline Not Loading

**Problem**: Blank timeline or "Loading..." forever

**Solutions**:
1. Check browser console for errors
2. Verify experiment exists: `GET /api/experiment/<id>`
3. Check event data: `GET /api/experiment/<id>/events`
4. Ensure database file exists: `logs/experiments.db`

### Events Not Appearing

**Problem**: Timeline loads but no events visible

**Solutions**:
1. Check event filters (ensure checkboxes are checked)
2. Verify experiment has event data
3. Try "Fit to Screen" button
4. Check browser console for JavaScript errors

### Export Not Working

**Problem**: Export buttons don't download files

**Solutions**:
1. Check browser popup blocker
2. Ensure CORS is configured (if running on different domain)
3. Check browser console for errors
4. For PNG: ensure html2canvas loaded correctly

### Performance Issues

**Problem**: Slow rendering with many events

**Solutions**:
1. Use event filters to reduce visible events
2. Adjust zoom level (less detail = faster)
3. Check browser performance tab
4. Consider batching events (future enhancement)

## Future Enhancements

### Planned Features
- [ ] Real-time event streaming (WebSocket integration)
- [ ] Annotation support (add notes to timeline)
- [ ] Comparison mode (overlay multiple experiments)
- [ ] Agent-specific coloring (for multi-agent)
- [ ] Heat map view (event density over time)
- [ ] Statistical overlays (moving averages, trends)
- [ ] Custom event types (user-defined)
- [ ] Collaborative annotations (multi-user)

### Research Opportunities
- Pattern detection algorithms
- Anomaly highlighting
- Predictive event modeling
- Correlation analysis between event types

## References

- [D3.js Documentation](https://d3js.org/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- Brain in a Jar Season 3 Paper (forthcoming)

## License

Part of the Brain in a Jar Digital Phenomenology Lab project.

## Contact

For issues or questions about the timeline visualization system, please open an issue in the repository.
