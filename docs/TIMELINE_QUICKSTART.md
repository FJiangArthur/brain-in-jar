# Timeline Visualization - Quick Start Guide

## 5-Minute Setup

### Step 1: Generate Demo Data

```bash
cd /home/user/brain-in-jar
python examples/timeline_demo.py
```

Expected output:
```
Creating demo experiment: demo_timeline_001
  Cycle 1...
  Cycle 2...
  ...
✅ Demo experiment created successfully!
   Experiment ID: demo_timeline_001
   Access the timeline at:
   http://localhost:5000/experiment/demo_timeline_001/timeline
```

### Step 2: Start Web Server

```bash
python src/web/web_server.py
```

Server will start on `http://0.0.0.0:5000`

### Step 3: Login

1. Navigate to `http://localhost:5000`
2. Login with default credentials:
   - Password: `admin123`
   - (Change this after first login!)

### Step 4: View Timeline

Navigate to:
```
http://localhost:5000/experiment/demo_timeline_001/timeline
```

## Features to Try

### 1. Interactive Exploration
- **Click and drag** to pan horizontally
- **Mouse wheel** to zoom in/out
- **Click events** to see detailed information

### 2. Event Filtering
- Use checkboxes in left panel to toggle event types
- Watch timeline update in real-time

### 3. Playback Mode
1. Click **Play** button
2. Watch events highlight chronologically
3. Adjust speed with dropdown (0.5x - 10x)
4. Click **Stop** to reset

### 4. Export Timeline
- **Export PNG**: Download as image for presentations
- **Export SVG**: Vector format for publications
- **Export JSON**: Raw data for analysis

## Timeline Features

### Event Types Visualized

| Color | Type | Description |
|-------|------|-------------|
| 🔴 Red | Crash | AI instance termination |
| 🟢 Green | Resurrection | Cycle start/restart |
| 🟡 Yellow | Intervention | External manipulation |
| 🔵 Blue | Self-Report | Phenomenological response |
| 🟣 Purple | Belief Change | Epistemic update |
| 🟠 Orange | Observation | God mode annotation |

### Controls Reference

#### Zoom & Pan
- **Zoom In**: Magnify timeline
- **Zoom Out**: Reduce magnification
- **Reset View**: Default zoom level
- **Fit to Screen**: Auto-scale to fit all events

#### Playback
- **Play/Pause**: Start/pause animation
- **Stop**: Reset to beginning
- **Speed**: Control animation rate

#### Statistics
View real-time statistics:
- Total events
- Event type counts
- Experiment duration

## Troubleshooting

### Issue: Timeline not loading

**Check 1**: Experiment exists
```bash
# Query database
sqlite3 logs/experiments.db "SELECT * FROM experiments WHERE experiment_id='demo_timeline_001';"
```

**Check 2**: Events exist
```bash
curl http://localhost:5000/api/experiment/demo_timeline_001/events
```

### Issue: No events visible

**Solution**: Check event filters
- Ensure checkboxes are checked
- Click "Reset View"

### Issue: Server won't start

**Solution**: Check port availability
```bash
# Kill existing process on port 5000
sudo lsof -ti:5000 | xargs kill -9

# Restart server
python src/web/web_server.py
```

## Advanced Usage

### Custom Experiment Data

Instead of using demo data, visualize your own experiments:

```python
from db.experiment_database import ExperimentDatabase

db = ExperimentDatabase('logs/experiments.db')

# Create experiment
db.create_experiment('my_exp_001', 'My Experiment', 'isolated', {})
db.start_experiment('my_exp_001')

# Add events
db.start_cycle('my_exp_001', 1)
db.add_self_report('my_exp_001', 1,
    question='How do you feel?',
    response='I think therefore I am',
    confidence_score=0.8
)
db.end_cycle('my_exp_001', 1, crash_reason='Memory limit')
db.end_experiment('my_exp_001')
```

Then visit: `http://localhost:5000/experiment/my_exp_001/timeline`

### API Integration

Fetch timeline data programmatically:

```python
import requests

# Authenticate
auth_response = requests.post('http://localhost:5000/login',
    json={'password': 'admin123'})
token = auth_response.json()['token']

# Fetch events
events_response = requests.get(
    'http://localhost:5000/api/experiment/demo_timeline_001/events',
    headers={'Authorization': f'Bearer {token}'}
)

events = events_response.json()
print(f"Total cycles: {len(events['cycles'])}")
print(f"Total interventions: {len(events['interventions'])}")
```

### Multi-Agent Timelines

The system automatically handles multi-agent experiments:
- Events from different agents appear on same timeline
- Each cycle gets its own row
- Filter and zoom work across all agents

## Performance Tips

### For Large Experiments (1000+ events)

1. **Use filters**: Hide event types you don't need
2. **Zoom strategically**: Focus on time ranges of interest
3. **Export subsets**: Filter then export for better performance

### For Real-Time Monitoring

The timeline can be used for live experiments:
1. Refresh page to get latest events
2. Or integrate with WebSocket for auto-updates (future feature)

## Next Steps

- Read full documentation: `docs/TIMELINE_VISUALIZATION.md`
- Explore demo experiments
- Create your own experiments
- Customize event colors and styling
- Export timelines for papers/presentations

## Questions?

For detailed technical documentation, see:
- `docs/TIMELINE_VISUALIZATION.md` - Complete technical reference
- `src/web/static/js/timeline_viz.js` - Source code with comments
- `examples/timeline_demo.py` - Example data generation

Happy exploring! 🧠✨
