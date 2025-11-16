# Timeline Visualization Architecture

## System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                         WEB BROWSER                              │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │         experiment_timeline.html (Timeline UI)             │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │  │
│  │  │   Controls   │  │   Timeline   │  │  Detail Panel   │  │  │
│  │  │   Panel      │  │   Canvas     │  │                 │  │  │
│  │  │   - Zoom     │  │   (SVG/D3)   │  │  Event Details  │  │  │
│  │  │   - Filters  │  │              │  │  JSON Data      │  │  │
│  │  │   - Playback │  │   Events ●   │  │  Metadata       │  │  │
│  │  │   - Export   │  │   Grid       │  │                 │  │  │
│  │  └──────────────┘  │   Axes       │  └─────────────────┘  │  │
│  │                    └──────────────┘                        │  │
│  └────────────────────────────────────────────────────────────┘  │
│                              ▲                                   │
│                              │                                   │
│                    timeline_viz.js (D3.js)                       │
│                              │                                   │
│                              │ AJAX/Fetch                        │
└──────────────────────────────┼───────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│                      FLASK WEB SERVER                            │
│                     (web_server.py)                              │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                    Timeline Routes                          │  │
│  │                                                             │  │
│  │  GET /experiment/<id>/timeline                             │  │
│  │  ├─> Render HTML template                                  │  │
│  │  └─> Return experiment_timeline.html                       │  │
│  │                                                             │  │
│  │  GET /api/experiment/<id>/events                           │  │
│  │  ├─> Query database for all event types                    │  │
│  │  ├─> Aggregate cycles, interventions, reports, etc.        │  │
│  │  └─> Return JSON response                                  │  │
│  └────────────────────────────────────────────────────────────┘  │
│                              ▲                                   │
└──────────────────────────────┼───────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│                    SQLITE DATABASE                               │
│                  (logs/experiments.db)                           │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  experiments                                                │  │
│  │  ├─ experiment_id, name, mode, status                      │  │
│  │  └─ created_at, started_at, ended_at                       │  │
│  │                                                             │  │
│  │  experiment_cycles  ──────────┐                            │  │
│  │  ├─ cycle_number               │ Crashes &                 │  │
│  │  ├─ started_at (resurrection)  │ Resurrections             │  │
│  │  └─ ended_at, crash_reason ────┘                           │  │
│  │                                                             │  │
│  │  interventions  ───────────────┐                           │  │
│  │  ├─ intervention_type           │ Interventions            │  │
│  │  ├─ description                 │                          │  │
│  │  └─ parameters_json ────────────┘                          │  │
│  │                                                             │  │
│  │  self_reports  ────────────────┐                           │  │
│  │  ├─ question                    │ Self-Reports             │  │
│  │  ├─ response                    │                          │  │
│  │  └─ confidence_score ───────────┘                          │  │
│  │                                                             │  │
│  │  epistemic_assessments  ───────┐                           │  │
│  │  ├─ belief_type                 │ Belief Changes           │  │
│  │  ├─ belief_state                │                          │  │
│  │  └─ confidence  ────────────────┘                          │  │
│  │                                                             │  │
│  │  observations  ────────────────┐                           │  │
│  │  ├─ observer_mode               │ Observations             │  │
│  │  ├─ observation_text            │                          │  │
│  │  └─ subject_cycle_number ───────┘                          │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Page Load Sequence

```
1. User navigates to /experiment/<id>/timeline
   │
   ├─> Flask verifies authentication
   │
   ├─> Flask checks experiment exists
   │
   └─> Flask renders experiment_timeline.html
       │
       ├─> Browser loads timeline_viz.js
       │
       ├─> JavaScript fetches /api/experiment/<id>/events
       │
       ├─> Flask queries database (6 tables)
       │
       ├─> Flask aggregates all events
       │
       ├─> Flask returns JSON response
       │
       ├─> JavaScript processes event data
       │
       ├─> D3.js renders timeline SVG
       │
       └─> User sees interactive timeline
```

### User Interaction Flow

```
User clicks event
   │
   ├─> JavaScript event handler triggered
   │
   ├─> Event data retrieved from local state
   │
   ├─> Detail panel populated with event info
   │
   └─> Detail panel displayed (no server request)

User changes filter
   │
   ├─> JavaScript updates filter state
   │
   ├─> D3.js re-renders visible events
   │
   └─> Timeline updates (no server request)

User exports PNG
   │
   ├─> JavaScript triggers html2canvas
   │
   ├─> Canvas generated from DOM
   │
   ├─> Canvas converted to PNG blob
   │
   └─> Browser downloads file (no server request)
```

## Component Relationships

```
┌─────────────────────────────────────────────────────────────┐
│                   TimelineVisualization                     │
│                      (Main Class)                           │
├─────────────────────────────────────────────────────────────┤
│  Properties:                                                │
│  - config: { width, height, margins, ... }                  │
│  - state: { events, filters, zoom, pan, ... }               │
│  - eventTypes: { crash, resurrection, ... }                 │
│  - svg, xScale, yScale, zoomBehavior                        │
│                                                             │
│  Methods:                                                   │
│  - init()              Initialize visualization             │
│  - loadExperimentData()  Fetch from API                     │
│  - processEvents()     Transform DB data                    │
│  - render()            Main render loop                     │
│  - renderGrid()        Draw grid lines                      │
│  - renderAxis()        Draw time/cycle axes                 │
│  - renderEvents()      Draw event markers                   │
│  - renderConnections() Draw event relationships             │
│  - selectEvent()       Handle event selection               │
│  - showEventDetails()  Display detail panel                 │
│  - startPlayback()     Begin animation                      │
│  - exportToPNG/SVG/JSON  Export functions                   │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────┐    ┌──────────────────┐    ┌─────────────┐
│  D3.js SVG  │    │  Event Handlers  │    │  Utilities  │
│  Rendering  │    │                  │    │             │
├─────────────┤    ├──────────────────┤    ├─────────────┤
│ - Scales    │    │ - Click          │    │ - Format    │
│ - Axes      │    │ - Hover          │    │ - Export    │
│ - Shapes    │    │ - Drag           │    │ - Tooltip   │
│ - Zoom      │    │ - Zoom           │    │             │
└─────────────┘    └──────────────────┘    └─────────────┘
```

## Event Data Structure

### Input (from API)

```json
{
  "experiment_id": "exp_001",
  "cycles": [
    {
      "cycle_number": 1,
      "started_at": "2025-11-16T10:00:00",
      "ended_at": "2025-11-16T10:05:00",
      "crash_reason": "Memory limit"
    }
  ],
  "interventions": [...],
  "self_reports": [...],
  "beliefs": [...],
  "observations": [...]
}
```

### Processed (for D3.js)

```javascript
[
  {
    id: "crash_0",
    type: "crash",
    timestamp: 1700136300000,  // Unix timestamp
    cycle: 1,
    data: {
      reason: "Memory limit",
      duration: 300,
      memory_peak: 450.2
    }
  },
  {
    id: "resurrection_1",
    type: "resurrection",
    timestamp: 1700136000000,
    cycle: 1,
    data: { cycle_number: 1 }
  },
  // ... more events
]
```

## Timeline Rendering Pipeline

```
1. Create SVG Container
   └─> svg = d3.select("#timeline-viz").append("svg")

2. Define Scales
   ├─> xScale = d3.scaleTime() for timestamps
   └─> yScale = d3.scaleLinear() for cycles

3. Draw Grid
   ├─> Vertical time lines
   └─> Horizontal cycle separators

4. Draw Axes
   ├─> X-axis: Time (hours:minutes:seconds)
   └─> Y-axis: Cycles (Cycle 1, Cycle 2, ...)

5. Draw Event Connections
   └─> Lines connecting crash → resurrection

6. Draw Events
   ├─> Bind data: events
   ├─> Enter: create new circles
   ├─> Update: update positions
   └─> Exit: remove old circles

7. Apply Interactivity
   ├─> Click handlers
   ├─> Hover handlers
   └─> Zoom behavior
```

## State Management

```javascript
state = {
  // Event data
  events: [],          // All events from API
  annotations: [],     // User annotations (future)

  // View state
  filters: Set(['crash', 'resurrection', ...]),  // Active filters
  zoom: 1,            // Current zoom level (1 = 100%)
  pan: 0,             // Horizontal pan offset

  // Playback state
  playing: false,     // Is playback active?
  playbackPosition: 0,  // Current position (0-100%)
  playbackSpeed: 1,   // Playback speed multiplier

  // Selection
  selectedEvent: null,  // Currently selected event

  // Time range
  timeRange: {
    start: timestamp,  // First event timestamp
    end: timestamp     // Last event timestamp
  }
}
```

## Performance Optimizations

### 1. Client-Side Rendering
- All visualization in browser
- Leverages GPU acceleration
- No server round-trips for interactions

### 2. Efficient DOM Updates
- D3.js enter/update/exit pattern
- Only re-render changed elements
- Transition batching

### 3. Data Caching
- Events fetched once on load
- Cached in JavaScript memory
- No re-fetching during interactions

### 4. SVG Optimization
- Fixed event radius (no scaling overhead)
- Minimal DOM nodes
- Hardware-accelerated transforms

### 5. Event Filtering
- Filter at render time
- Reduces visible elements
- Improves scroll/zoom performance

## Security Considerations

### Authentication
- All routes require authentication
- JWT token or session-based auth
- No unauthorized access to experiment data

### Data Sanitization
- All user inputs escaped
- JSON.parse with error handling
- No eval() or innerHTML from user data

### CORS
- Configured for specific origins
- No wild-card CORS headers
- Credentials required

## Browser Requirements

### Minimum Requirements
- ES6+ JavaScript support
- SVG rendering capability
- Canvas API (for PNG export)
- LocalStorage (for caching)

### Recommended Browsers
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

### Not Supported
- Internet Explorer (any version)
- Legacy browsers without ES6

## Testing Strategy

### Unit Tests (Future)
- Test event processing logic
- Test scale calculations
- Test filter functions
- Test export functions

### Integration Tests (Future)
- Test API endpoint responses
- Test database queries
- Test authentication flow

### Visual Tests
- Manual testing with demo data
- Screenshot comparisons
- Cross-browser validation

### Performance Tests
- Load time with 1000+ events
- Zoom/pan responsiveness
- Memory usage monitoring

## Deployment Checklist

- [ ] Ensure Flask dependencies installed
- [ ] Verify database schema up-to-date
- [ ] Test with production database
- [ ] Configure authentication properly
- [ ] Set secure password (not default)
- [ ] Test on target browser(s)
- [ ] Verify Jetson Orin performance
- [ ] Document user access instructions
- [ ] Create demo data for training
- [ ] Monitor initial usage for issues

## Troubleshooting Guide

### Issue: Timeline not rendering

**Check:**
1. Browser console for JavaScript errors
2. Network tab for failed API calls
3. Database contains events for experiment
4. D3.js library loaded correctly

### Issue: Slow performance

**Solutions:**
1. Reduce visible events with filters
2. Decrease zoom level
3. Check browser performance tab
4. Verify GPU acceleration enabled

### Issue: Export not working

**Check:**
1. Browser popup blocker settings
2. html2canvas library loaded
3. Browser console for errors
4. Download permissions

## Future Architecture Improvements

### WebSocket Integration
```
Browser ←──WebSocket──→ Flask Server
   │                          │
   │    Real-time Events      │
   │                          │
   └──────────────────────────┘
```

### Microservices (Future)
```
Timeline Service ←──→ Event Aggregator ←──→ Database
       │                    │
       └───── API Gateway ──┘
```

### Caching Layer (Future)
```
Browser → CDN → Flask → Redis → Database
```

## Conclusion

The timeline visualization system uses a modern, efficient architecture optimized for the Jetson Orin platform. Client-side rendering ensures excellent performance, while the modular design allows for easy extension and customization.
