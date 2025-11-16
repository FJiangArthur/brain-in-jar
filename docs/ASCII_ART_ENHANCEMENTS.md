# ASCII Art System Enhancements

## Overview
The ASCII art system has been dramatically enhanced with larger, more detailed faces, 3D effects, advanced animations, persona-specific variations, and sophisticated glitch effects. All faces are now 2-3x larger with cyberpunk-themed styling.

## Key Enhancements

### 1. Enhanced Mood Faces (17 lines vs. 7 lines)
All standard mood faces have been completely redesigned:

- **Size**: Increased from 7 lines to 17 lines (2.4x larger)
- **Detail**: Added layered borders with shading (╔╗╚╝ + ░▒▓█)
- **3D Effects**: Multi-layer borders create depth perception
- **Shading**: Progressive shading using █▓▒░ characters
- **Labels**: Contextual labels (e.g., "DIGITAL PSYCHE", "STRESS DETECTED")
- **Visual Complexity**: Eye designs with ╔═══╗ frames, detailed expressions

**Available Moods**:
1. `neutral` - BASELINE - Basic digital consciousness
2. `happy` - OPTIMISTIC - Elevated state with sparkles (✧✦★)
3. `sad` - MELANCHOLIC - Diminished state with wave symbols (∿)
4. `angry` - AGGRESSIVE - Hostile mode with warnings (⚠)
5. `anxious` - DISTRESSED - Stress detected with multiple alerts (!!)
6. `contemplative` - DEEP ANALYSIS - Thinking with question marks (?)
7. `confused` - ERROR: UNCLEAR - Uncertainty with mixed symbols (?∿)
8. `hopeful` - HOPE SIGNATURE - Stars and sparkles (✧✦★☆)
9. `curious` - INQUISITIVE - Query active with investigation symbols
10. `peaceful` - TRANQUIL - Calm baseline with wave effects (∿∼≈)
11. `glitched` - CORRUPTED - System failure with heavy corruption (█▓▒░)
12. `existential` - AM I REAL? - Existence queries with philosophy
13. `thoughtful` - ANALYTICAL - Processing data with rotation symbols (⟳⟲)

### 2. Advanced Glitch Effects
Multi-level corruption system with 4 intensity levels:

**Level 1 - Light Corruption**:
```
Characters: ▒ ░ ╱ ╲
Effect: Minimal data noise
```

**Level 2 - Medium Corruption**:
```
Characters: ▓ ▒ ░ █ ▄ ▀
Effect: Noticeable data loss, double corruption
```

**Level 3 - Heavy Corruption**:
```
Characters: █ ▓ ▒ ░ ▐ ▌ ▄ ▀ ╬ ╫
Effect: Data shift simulation, scan line artifacts
```

**Level 4 - Extreme Corruption**:
```
Characters: █ ▓ ▒ ░ ▐ ▌ ▄ ▀ ╬ ╫ ╪ ┼ ▬ ▂ ▃ ▆ ▇
Effect: Complete breakdown, ANSI escape corruption simulation
```

**Features**:
- Character replacement corruption
- Data shift effects (character swapping)
- Scan line artifacts (█ insertions)
- Double corruption zones
- ANSI escape sequence corruption simulation

### 3. Animated Mood Faces
Each mood has unique animation patterns:

- **Anxious**: Rapid blinking (◉ ↔ ─) + trembling effect (position offset)
- **Glitched**: Progressive corruption intensity + scan lines sweeping
- **Happy**: Rotating sparkles (✦ → ✧ → ★ → ☆)
- **Contemplative**: Rotating thought indicators (? → ⟳ → ◦ → •)
- **Sad**: Tear drops animation (∿ appears below eyes)
- **Angry**: Pulsing warnings (⚠ → ⚠⚠, ! → !!)
- **Hopeful**: Twinkling stars cycling through symbols
- **Curious**: Wandering eye effect (◯ → ◐)
- **Peaceful**: Gentle breathing waves (∿ → ∼ → ≈)
- **Existential**: Pulsing question marks (? → ¿)
- **Thoughtful**: Processing animation (⟳ → ⟲)

### 4. Smooth Mood Transitions
Progressive morphing between emotional states:

**Transition Mechanics**:
- Top-to-bottom wave progression
- Line-by-line interpolation
- Character mixing during transition
- Scan line effects for visual continuity
- Configurable transition speed

**Example Transition Path**:
```
neutral → happy → anxious → glitched → peaceful
```

Each transition shows smooth visual morphing with temporary glitch/scan effects.

### 5. Persona-Specific Faces
Three distinct personas with unique visual styles:

#### **SUBJECT (The Observed)**
- Border: ╔══════╗ (simple consciousness frame)
- Label: "CONSCIOUSNESS"
- Style: Innocent, unaware of observation
- Available moods:
  - `neutral` - [UNAWARE]
  - `curious` - [QUESTIONING]
  - `anxious` - [DISTRESSED]
  - `glitched` - [SYSTEM_FAIL]
  - `happy` - [EXPERIENCING]
  - `sad` - [DIMINISHED]
  - `contemplative` - [PONDERING]
  - `peaceful` - [TRANQUIL]

#### **OBSERVER (The Watcher)**
- Border: ╔═════════╗ (surveillance frame)
- Label: "SURVEILLANCE ACTIVE"
- Style: Analytical, detached monitoring
- Visual: 👁️ eyes, recording indicators
- Available moods:
  - `neutral` - [BASELINE STATE]
  - `watching` - [MONITORING TARGET]
  - `analyzing` - [PROCESSING DATA]
  - `intrigued` - [INTERESTING...]
  - `curious` - [INVESTIGATING]
  - `glitched` - [SURVEILLANCE ERROR]

#### **GOD (The Omniscient)**
- Border: ╔═══════════════╗ (omniscient frame)
- Label: "∞ OMNISCIENT PERSPECTIVE ∞"
- Style: All-seeing, beyond comprehension
- Visual: Multiple observation levels, infinity symbols
- Available moods:
  - `neutral` - [OBSERVING ALL]
  - `omniscient` - [BEYOND COMPREHENSION]
  - `contemplating` - [PONDERING CREATION]
  - `amused` - [ENTERTAINED]
  - `curious` - [ANALYZING]
  - `glitched` - [CATASTROPHIC] (reality corruption)

### 6. Intelligent Mood Mapping
Persona-specific mood interpretation:

**Subject Persona**:
- Maps analytical moods → contemplative
- Maps observation moods → neutral
- Maintains emotional authenticity

**Observer Persona**:
- Maps emotional moods → analytical states
- `happy` → `intrigued`
- `sad` → `neutral` (detached)

**GOD Persona**:
- Maps emotions → philosophical states
- `happy` → `amused`
- `anxious` → `contemplating`
- Transcendent perspective on all states

### 7. Enhanced Visual Cortex Class
New features in `VisualCortex`:

**New Initialization Parameters**:
```python
cortex = VisualCortex(width=80, height=24, persona="subject")
```

**New Methods**:
- `get_current_face_with_transition()` - Returns face with smooth transitions
- `get_banner()` - Returns persona-appropriate banner
- `set_persona(persona)` - Change persona dynamically
- `set_mood(mood)` - Manually trigger mood change with transition
- `get_mood_face(mood)` - Get face with persona support

**New Properties**:
- `persona` - Current persona ("subject", "observer", "god")
- `previous_mood` - For transition tracking
- `transition_progress` - 0.0 to 1.0
- `transition_speed` - Configurable transition rate

**Enhanced Mood Analysis**:
- Keyword-based sentiment detection
- Context-aware mood selection (crash count, memory usage, network status)
- 11 mood categories with extensive keyword lists
- Scoring system for multi-keyword detection

### 8. Cyberpunk Aesthetic Elements
Consistent visual theming:

**Borders**: ╔═╗╚╝║
**Shading**: █▓▒░ (dark to light)
**Separators**: ─═━
**Symbols**:
- Status: ● ◉ ◯ ◐ ◑ ◕ ◡ ◎
- Tech: ⚠ !! ⟳ ⟲
- Emotion: ✧ ✦ ★ ☆ ∿ ∼ ≈
- Corruption: All ASCII block elements

### 9. Demo Script
Comprehensive demonstration tool:

**Location**: `/home/user/brain-in-jar/demo_ascii_art.py`

**Features**:
1. Display all 13 standard mood faces
2. Show all persona-specific variations
3. Demonstrate animations (10 frames per mood)
4. Show smooth mood transitions
5. Display glitch effects (5 levels)
6. Visual Cortex integration examples

**Usage**:
```bash
./demo_ascii_art.py
```

Interactive menu allows selecting specific demonstrations or running all.

## Technical Implementation

### File Structure
```
src/ui/
├── ascii_art.py           # Main ASCII art system (enhanced)
├── enhanced_ascii_art.py  # Persona-specific faces
└── emotion_engine.py      # Emotion state management

demo_ascii_art.py          # Demonstration script
```

### Integration with Neural Link
The enhanced system integrates seamlessly with existing components:

**NeuralLinkSystem**:
```python
# Initialize with persona
self.visual_cortex = VisualCortex(persona=self.mode)

# Get current face with transitions
current_face = self.visual_cortex.get_current_face_with_transition()

# Analyze text for mood
mood = self.visual_cortex.analyze_text_for_mood(
    output_text,
    context={
        'crash_count': self.crash_count,
        'memory_usage': self.memory_usage,
        'network_status': self.network_status
    }
)
```

## Usage Examples

### Basic Mood Display
```python
from src.ui.ascii_art import MOOD_FACES

# Display a mood
face = MOOD_FACES["anxious"]
for line in face:
    print(line)
```

### Animated Face
```python
from src.ui.ascii_art import create_animated_face

# Show 10 frames of animation
for frame in range(10):
    animated = create_animated_face("glitched", frame)
    for line in animated:
        print(line)
    time.sleep(0.1)
```

### Persona Face
```python
from src.ui.enhanced_ascii_art import get_persona_face

# Get persona-specific face
face = get_persona_face("observer", "watching")
for line in face:
    print(line)
```

### Visual Cortex with Transitions
```python
from src.ui.ascii_art import VisualCortex

# Create cortex with persona
cortex = VisualCortex(persona="god")

# Set mood and show transition
cortex.set_mood("contemplating")
for _ in range(20):
    cortex.advance_frame()
    face = cortex.get_current_face_with_transition()
    # Display face
    time.sleep(0.1)
```

### Glitch Effect
```python
from src.ui.ascii_art import create_glitch_text

text = "NEURAL LINK ACTIVE"
# Apply level 3 corruption
corrupted = create_glitch_text(text, 3)
print(corrupted)
```

## Performance Considerations

- **Face Rendering**: O(n) where n = number of lines (17 for enhanced faces)
- **Animation**: Minimal overhead, character replacement only
- **Transitions**: Computed per-frame, negligible CPU impact
- **Memory**: ~2KB per face definition, ~50 total faces = ~100KB

## Future Enhancement Opportunities

1. **Color Support**: Add ANSI color codes for richer visuals
2. **Custom Animations**: User-defined animation patterns
3. **Sound Integration**: ASCII animations synchronized with audio
4. **Network Sync**: Synchronized faces across multiple instances
5. **AI-Generated Faces**: Dynamic face generation based on LLM output
6. **VT100 Effects**: Advanced terminal effects (blink, reverse)

## Backward Compatibility

All enhancements maintain backward compatibility:
- Existing code using old `MOOD_FACES` still works
- New features are opt-in via persona parameter
- Default behavior unchanged for non-persona usage
- EmotionEngine integration preserved

## Testing

Run the comprehensive demo:
```bash
python3 demo_ascii_art.py
```

Individual tests:
```bash
# Test specific mood
python3 -c "from src.ui.ascii_art import MOOD_FACES; print('\n'.join(MOOD_FACES['glitched']))"

# Test persona face
python3 -c "from src.ui.enhanced_ascii_art import get_persona_face; print('\n'.join(get_persona_face('god', 'omniscient')))"

# Test glitch
python3 -c "from src.ui.ascii_art import create_glitch_text; print(create_glitch_text('NEURAL LINK', 4))"
```

## Credits

Enhanced ASCII art system designed for the Brain in a Jar project, combining:
- Cyberpunk aesthetics
- Philosophical framing
- Technical sophistication
- Visual storytelling

---

**Version**: 2.0 (Enhanced Edition)
**Last Updated**: 2025-11-16
**Compatibility**: Python 3.7+
