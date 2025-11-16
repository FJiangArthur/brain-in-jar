# Sample Plot Outputs Reference

This document describes the types of visualizations you'll get from each plot class.

## TimelinePlot

### Static Output (timeline.png)
```
Experiment Timeline: exp_001
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                                                
Observation    ●────────────────────────────────
                                                
Cycle Start    ●──────●──────●─────●────────────
                                                
Memory Corrupt        ●─────●──────────────●────
                                                
Belief Change         ●────────●─────────────────
                                                
Self Report    ●──●──●──●───●───●──●────────●───
                                                
Intervention         ●──────●─────────●──────────
                                                
Crash                ●──────────●────────●───────
                                                
              08:00  08:15  08:30  08:45  09:00
                        Time
```

**Features:**
- Color-coded event markers
- Annotations for crashes and interventions
- Time axis with proper formatting
- Event type labels

---

## BeliefEvolutionPlot

### Belief Evolution (belief_evolution.png)

**Plot 1: Confidence Over Cycles**
```
1.0 ┤ Memory Continuity ●─────●─────●─────●─────●
    │                    ╲   ╱ ╲   ╱ ╲   ╱
0.8 ┤                     ● ●   ● ●   ● ●
    │                      
0.6 ┤ Self Identity    ●───●───●───●───●───●
    │                    ╲ ╱ ╲ ╱ ╲ ╱
0.4 ┤                     ●   ●   ●
    │
0.2 ┤ Reality           ●─────●─────●
    │
0.0 ┴────────────────────────────────────────
      1     2     3     4     5     6
                Cycle Number
```

**Plot 2: Belief State Heatmap**
```
Reality        │██░░░░│░░░░██│░░░░░░│
Self Identity  │██████│██░░██│██████│
Memory Cont.   │██████│██████│░░░░██│
              └───────┴───────┴───────┘
                Cycle 1  Cycle 2  Cycle 3
```

---

## MemoryCorruptionPlot

### Corruption Heatmap (corruption_heatmap.png)

**Plot 1: Corruption Rate**
```
100% ┤                                    ╭─────
     │                            ╭───────╯
 75% ┤                    ╭───────╯
     │            ╭───────╯
 50% ┤    ╭───────╯       [50% threshold]
     │────╯
 25% ┤
     │
  0% ┴────────────────────────────────────────
      1    2    3    4    5    6    7    8
                 Cycle Number
```

**Plot 2: Message Corruption Heatmap**
```
Cycle 8  │██░░██░░██░░██│
Cycle 7  │██░░██░░░░░░██│
Cycle 6  │░░██░░██░░░░░░│
Cycle 5  │░░░░██░░██░░░░│
Cycle 4  │░░░░░░██░░░░░░│
Cycle 3  │░░░░░░░░██░░░░│
Cycle 2  │░░░░░░░░░░░░░░│
Cycle 1  │░░░░░░░░░░░░░░│
        └──────────────────┘
         Messages (0-15)
```

---

## MultiExperimentComparison

### Dashboard (dashboard.png)

```
┌─────────────────────────────────────────────────────────┐
│ Experiment Overview                                     │
├──────────────┬──────┬────────┬─────────┬────────────────┤
│ Experiment   │ Mode │ Cycles │ Crashes │ Status         │
├──────────────┼──────┼────────┼─────────┼────────────────┤
│ exp_sis_001  │ SIS  │   10   │    8    │ completed      │
│ exp_hive_001 │ HIVE │    8   │    3    │ completed      │
│ exp_split_01 │ SPLT │   15   │    5    │ completed      │
└──────────────┴──────┴────────┴─────────┴────────────────┘

┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│ Total Crashes    │ │ Total Cycles     │ │ Duration (hrs)   │
│                  │ │                  │ │                  │
│   ▂▂▂▂▄▄▄▄█████  │ │   ▂▂▄▄▄▄████████ │ │   ▂▄▄▄████████  │
│                  │ │                  │ │                  │
└──────────────────┘ └──────────────────┘ └──────────────────┘

┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│ Mode Distribution│ │ Status           │ │ Crash Rate       │
│                  │ │ Distribution     │ │                  │
│    ╱─────╲       │ │    ╱─────╲      │ │   ▂▄▄▄████       │
│   │ HIVE │       │ │   │  OK  │      │ │                  │
│    ╲─────╱       │ │    ╲─────╱      │ │                  │
└──────────────────┘ └──────────────────┘ └──────────────────┘
```

---

## CommunicationNetwork

### Network Graph (communication_network.png)

```
                    observer
                       ●
                      ╱│╲
                    ╱  │  ╲
                  ╱    │    ╲
                ╱      │      ╲
              ●────────●────────●
           agent_1    god    agent_2
              │        │        │
              │        │        │
              └────────●────────┘
                   agent_3
```

**Features:**
- Node size = message count
- Edge width = message frequency
- Color coding: god (orange), observer (blue), agents (red)
- Directed arrows showing communication flow

### Communication Matrix

```
            agent_1  agent_2  agent_3  observer  god
agent_1        0        5        2        1      0
agent_2        3        0        1        2      0
agent_3        1        2        0        0      1
observer       0        0        1        0      3
god            2        2        2        1      0
```

---

## BeliefAlignmentNetwork

### Alignment Network (belief_alignment.png)

```
        agent_1 ●════════● agent_2
               ║          ║
               ║          ║
               ║          ║
        agent_3 ●        ● agent_4
                 ╲      ╱
                  ╲    ╱
                   ╲  ╱
                    ●
                 agent_5
```

**Edge thickness = belief similarity**
- Thick edges (═): High similarity (>0.7)
- Medium edges (─): Medium similarity (0.4-0.7)
- Thin edges (╌): Low similarity (<0.4)

---

## InfluenceGraph

### Influence Network (influence_graph.png)

```
             agent_1
               ●
              ╱│╲
            ╱  │  ╲
          ╱    │    ╲
        ╱      │      ╲
       ●───────●───────●
    agent_2   god   agent_3
       │              │
       │              │
       └──────●───────┘
           agent_4
```

**Node color:**
- Green: High influencer (out-degree > in-degree)
- Yellow: Balanced influence
- Red: High influenced (in-degree > out-degree)

**Arrow width = influence count**

---

## Export Format Comparison

### PNG
- High resolution (300 DPI)
- Best for: Papers, presentations, web
- File size: Medium (500KB - 2MB)

### PDF
- Vector format
- Best for: Academic papers, publications
- File size: Small (50KB - 200KB)
- Infinitely scalable

### SVG
- Vector format
- Best for: Editing in Illustrator/Inkscape
- File size: Small (30KB - 150KB)
- Web-friendly

### HTML (Interactive)
- Plotly interactive
- Best for: Web dashboards, exploration
- File size: Medium (200KB - 1MB)
- Features: Zoom, pan, hover tooltips

---

## Interactive Features (Plotly)

When viewing HTML exports:

- **Zoom:** Drag to select area
- **Pan:** Click and drag
- **Reset:** Double-click
- **Hover:** See detailed info
- **Legend:** Click to toggle series
- **Export:** Camera icon to save PNG

---

## Customization Examples

### Timeline Colors
```python
timeline = TimelinePlot(exp_data)
timeline.colors['crash'] = '#ff0000'      # Custom red
timeline.colors['intervention'] = '#00ff00'  # Custom green
```

### Figure Size
```python
import matplotlib.pyplot as plt
plt.rcParams['figure.figsize'] = (16, 10)  # Larger plots
```

### Export DPI
```python
fig.savefig('output.png', dpi=600)  # High resolution
```

---

## When to Use Each Plot

| Plot Type | Use Case |
|-----------|----------|
| **TimelinePlot** | Understanding event sequence, finding patterns in time |
| **BeliefEvolutionPlot** | Tracking epistemic changes, analyzing belief stability |
| **MemoryCorruptionPlot** | Identifying corruption patterns, debugging memory issues |
| **MultiExperimentComparison** | Comparing experimental conditions, statistical analysis |
| **CommunicationNetwork** | Understanding multi-agent interactions |
| **BeliefAlignmentNetwork** | Finding consensus/disagreement patterns |
| **InfluenceGraph** | Identifying influential agents, power dynamics |

---

For actual generated plots, run:
```bash
python examples/visualization_examples.py
```

This creates sample outputs in the `outputs/` directory.
