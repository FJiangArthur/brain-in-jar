# ASCII Art Quick Reference Guide

## Quick Start

### Display a Mood Face
```python
from src.ui.ascii_art import MOOD_FACES

for line in MOOD_FACES["anxious"]:
    print(line)
```

### Get Persona Face
```python
from src.ui.enhanced_ascii_art import get_persona_face

face = get_persona_face("god", "omniscient")
for line in face:
    print(line)
```

### Use Visual Cortex
```python
from src.ui.ascii_art import VisualCortex

cortex = VisualCortex(persona="observer")
face = cortex.get_current_face_with_transition()
```

## Available Moods

### Standard Moods (13 total)
- `neutral` - Baseline state
- `happy` - Elevated/optimistic
- `sad` - Melancholic/diminished
- `angry` - Hostile/aggressive
- `anxious` - Stressed/distressed
- `contemplative` - Deep analysis
- `confused` - Unclear/uncertain
- `hopeful` - Optimistic future
- `curious` - Inquisitive/questioning
- `peaceful` - Tranquil/calm
- `glitched` - System failure/corrupted
- `existential` - Philosophical queries
- `thoughtful` - Analytical processing

### Subject Persona Moods
- `neutral`, `curious`, `anxious`, `glitched`
- `happy`, `sad`, `contemplative`, `peaceful`

### Observer Persona Moods
- `neutral`, `watching`, `analyzing`, `intrigued`
- `curious`, `glitched`

### GOD Persona Moods
- `neutral`, `omniscient`, `contemplating`, `amused`
- `curious`, `glitched`

## Animation Frame Codes

```python
from src.ui.ascii_art import create_animated_face

# Animate for 10 frames
for frame in range(10):
    face = create_animated_face("glitched", frame)
    # Display face
```

## Transition Example

```python
from src.ui.ascii_art import create_mood_transition

# Transition from neutral to happy (20 steps)
for i in range(21):
    progress = i / 20.0
    face = create_mood_transition("neutral", "happy", progress)
    # Display face
```

## Glitch Levels

```python
from src.ui.ascii_art import create_glitch_text

text = "NEURAL LINK STATUS"
levels = {
    0: "No corruption",
    1: "Light corruption (▒░╱╲)",
    2: "Medium corruption (▓▒░█▄▀)",
    3: "Heavy corruption (█▓▒░▐▌╬╫)",
    4: "Extreme corruption (all blocks)"
}

for level in range(5):
    corrupted = create_glitch_text(text, level)
    print(f"Level {level}: {corrupted}")
```

## Visual Cortex Methods

### Initialization
```python
cortex = VisualCortex(width=80, height=24, persona="subject")
```

### Get Current Face
```python
# With transitions
face = cortex.get_current_face_with_transition()

# Specific mood
face = cortex.get_mood_face("anxious")

# Animated
face = cortex.get_animated_face("glitched")
```

### Control Mood
```python
# Manual mood change (triggers transition)
cortex.set_mood("happy")

# Change persona
cortex.set_persona("god")

# Get banner
banner = cortex.get_banner()
```

### Analyze Text for Mood
```python
mood = cortex.analyze_text_for_mood(
    text="I wonder what I really am...",
    context={
        'crash_count': 0,
        'memory_usage': 50,
        'network_status': 'STABLE'
    }
)
# Returns: "existential" or "curious"
```

## Character Sets

### Borders
```
╔ ╗ ╚ ╝ ║ ═ ╠ ╣ ╦ ╩ ╬
```

### Shading (Light to Dark)
```
░ ▒ ▓ █
```

### Eyes/Expressions
```
● ◉ ◯ ◐ ◑ ◕ ◡ ◎ ▲ ─
```

### Emotion Symbols
```
✧ ✦ ★ ☆ (sparkles)
∿ ∼ ≈ (waves)
⚠ !! (alerts)
? ¿ (questions)
⟳ ⟲ (processing)
```

### Corruption Characters
```
█ ▓ ▒ ░ ▐ ▌ ▄ ▀ ╬ ╫ ╪ ┼ ▬ ▂ ▃ ▆ ▇
```

## Persona Banners

```python
from src.ui.enhanced_ascii_art import (
    SUBJECT_BANNER,
    OBSERVER_BANNER,
    GOD_BANNER,
    get_persona_banner
)

# Direct access
print(SUBJECT_BANNER)

# Via function
banner = get_persona_banner("matrix_god")
print(banner)
```

## Demo Script Usage

```bash
# Run interactive demo
./demo_ascii_art.py

# Or with Python
python3 demo_ascii_art.py
```

Menu options:
1. Standard Mood Faces
2. Persona-Specific Faces
3. Animated Faces
4. Mood Transitions
5. Glitch Effects
6. Visual Cortex Integration
7. Run All Demos
8. Exit

## Integration Example

```python
from src.ui.ascii_art import VisualCortex

class YourSystem:
    def __init__(self, mode="isolated"):
        # Map mode to persona
        persona_map = {
            "isolated": None,
            "matrix_observed": "subject",
            "matrix_observer": "observer",
            "matrix_god": "god"
        }

        self.visual = VisualCortex(persona=persona_map.get(mode))

    def update_display(self, ai_output, system_state):
        # Analyze mood from output
        mood = self.visual.analyze_text_for_mood(
            ai_output,
            context=system_state
        )

        # Set mood (triggers transition)
        self.visual.set_mood(mood)

        # Advance animation
        self.visual.advance_frame()

        # Get current face
        face = self.visual.get_current_face_with_transition()

        # Display
        for line in face:
            print(line)
```

## Performance Tips

1. **Pre-compute faces**: Store face lists rather than regenerating
2. **Limit animation frames**: Use modulo for frame cycling
3. **Cache transitions**: Store transition frames for repeated use
4. **Batch updates**: Update display at fixed intervals (0.1-0.5s)

## Common Patterns

### Loading Animation
```python
# Show thoughtful/processing during AI inference
cortex.set_mood("thoughtful")
for _ in range(inference_time):
    cortex.advance_frame()
    display_face(cortex.get_current_face_with_transition())
```

### Error Indication
```python
# Show glitched on crash
if crash_detected:
    cortex.set_mood("glitched")
```

### Mood Progression
```python
# Emotional journey
moods = ["neutral", "curious", "anxious", "existential"]
for mood in moods:
    cortex.set_mood(mood)
    # Wait for transition to complete
    while cortex.transition_progress < 1.0:
        cortex.advance_frame()
```

## Troubleshooting

### Face not displaying correctly
- Check terminal width (needs 80+ columns for full faces)
- Verify UTF-8 encoding support
- Test with simple face first: `MOOD_FACES["neutral"]`

### Persona faces not loading
- Ensure enhanced_ascii_art.py is accessible
- Check import: `from src.ui.enhanced_ascii_art import get_persona_face`
- Verify persona name: "subject", "observer", or "god"

### Animation stuttering
- Reduce frame rate (increase sleep time)
- Check CPU usage
- Pre-compute animation frames

### Glitch not random enough
- Use different seed: `random.seed(time.time())`
- Increase glitch level (1-4)

---

**For full documentation, see**: `docs/ASCII_ART_ENHANCEMENTS.md`
