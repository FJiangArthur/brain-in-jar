#!/usr/bin/env python3
"""
Demo script to showcase enhanced ASCII art system
Displays all mood faces, persona variations, and animated transitions
"""

import time
import sys
from src.ui.ascii_art import (
    VisualCortex,
    MOOD_FACES,
    CYBERPUNK_BANNER,
    create_animated_face,
    create_mood_transition,
    create_glitch_text,
)
from src.ui.enhanced_ascii_art import (
    get_persona_face,
    get_persona_banner,
    ENHANCED_MOOD_FACES,
    SUBJECT_BANNER,
    OBSERVER_BANNER,
    GOD_BANNER,
)


def clear_screen():
    """Clear the terminal screen"""
    print("\033[2J\033[H", end="")


def display_banner():
    """Display the cyberpunk banner"""
    clear_screen()
    print(CYBERPUNK_BANNER)
    print("\n" + "=" * 80)
    print("       ENHANCED ASCII ART SYSTEM DEMONSTRATION")
    print("=" * 80 + "\n")


def demo_standard_moods():
    """Demonstrate all standard mood faces"""
    print("\n╔══════════════════════════════════════════════════════════════════╗")
    print("║           STANDARD MOOD FACES (Enhanced 3D Edition)             ║")
    print("╚══════════════════════════════════════════════════════════════════╝\n")

    moods = [
        "neutral", "happy", "sad", "angry", "anxious",
        "contemplative", "confused", "hopeful", "curious",
        "peaceful", "glitched", "existential", "thoughtful"
    ]

    for mood in moods:
        print(f"\n{'─' * 80}")
        print(f"MOOD: {mood.upper()}")
        print('─' * 80)
        face = MOOD_FACES.get(mood, MOOD_FACES["neutral"])
        for line in face:
            print(line)
        time.sleep(1.5)


def demo_persona_faces():
    """Demonstrate persona-specific faces"""
    print("\n\n╔══════════════════════════════════════════════════════════════════╗")
    print("║              PERSONA-SPECIFIC FACES                              ║")
    print("╚══════════════════════════════════════════════════════════════════╝\n")

    personas = ["subject", "observer", "god"]
    persona_moods = {
        "subject": ["neutral", "curious", "anxious", "glitched", "happy", "sad", "contemplative", "peaceful"],
        "observer": ["neutral", "watching", "analyzing", "intrigued", "curious", "glitched"],
        "god": ["neutral", "omniscient", "contemplating", "amused", "curious", "glitched"]
    }

    for persona in personas:
        # Display persona banner
        print("\n" + "=" * 80)
        print(get_persona_banner(persona))
        print("=" * 80 + "\n")

        for mood in persona_moods[persona]:
            print(f"\n{'─' * 80}")
            print(f"PERSONA: {persona.upper()} | MOOD: {mood.upper()}")
            print('─' * 80)
            try:
                face = get_persona_face(persona, mood)
                for line in face:
                    print(line)
                time.sleep(1.5)
            except Exception as e:
                print(f"Error displaying {persona}_{mood}: {e}")


def demo_animations():
    """Demonstrate animated faces"""
    print("\n\n╔══════════════════════════════════════════════════════════════════╗")
    print("║                  ANIMATED MOOD FACES                             ║")
    print("╚══════════════════════════════════════════════════════════════════╝\n")

    animated_moods = ["glitched", "anxious", "happy", "contemplative", "curious"]

    for mood in animated_moods:
        print(f"\n{'─' * 80}")
        print(f"ANIMATED: {mood.upper()} (10 frames)")
        print('─' * 80 + "\n")

        for frame in range(10):
            # Move cursor up to overwrite previous frame
            if frame > 0:
                # Move cursor up by number of lines in face
                print(f"\033[{len(MOOD_FACES[mood]) + 2}A", end="")

            animated_face = create_animated_face(mood, frame)
            print(f"Frame {frame + 1}/10:")
            for line in animated_face:
                print(line)

            time.sleep(0.3)

        print("\n")
        time.sleep(1)


def demo_transitions():
    """Demonstrate mood transitions"""
    print("\n\n╔══════════════════════════════════════════════════════════════════╗")
    print("║                  MOOD TRANSITIONS                                ║")
    print("╚══════════════════════════════════════════════════════════════════╝\n")

    transitions = [
        ("neutral", "happy"),
        ("happy", "anxious"),
        ("anxious", "glitched"),
        ("glitched", "peaceful"),
    ]

    for from_mood, to_mood in transitions:
        print(f"\n{'─' * 80}")
        print(f"TRANSITION: {from_mood.upper()} → {to_mood.upper()}")
        print('─' * 80 + "\n")

        # Show transition in 20 steps
        for i in range(21):
            progress = i / 20.0

            # Move cursor up to overwrite previous frame
            if i > 0:
                print(f"\033[{len(MOOD_FACES['neutral']) + 3}A", end="")

            transition_face = create_mood_transition(from_mood, to_mood, progress)
            print(f"Progress: {int(progress * 100)}%")
            for line in transition_face:
                print(line)

            time.sleep(0.15)

        print("\n")
        time.sleep(1)


def demo_glitch_effects():
    """Demonstrate advanced glitch effects"""
    print("\n\n╔══════════════════════════════════════════════════════════════════╗")
    print("║              ADVANCED GLITCH EFFECTS                             ║")
    print("╚══════════════════════════════════════════════════════════════════╝\n")

    test_text = "NEURAL LINK SYSTEM STATUS: ALL SYSTEMS OPERATIONAL"

    for level in range(5):
        print(f"\nGlitch Level {level}:")
        print('─' * 80)
        for _ in range(5):
            glitched = create_glitch_text(test_text, level)
            print(f"  {glitched}")
            time.sleep(0.2)
        print()


def demo_visual_cortex():
    """Demonstrate VisualCortex with persona support"""
    print("\n\n╔══════════════════════════════════════════════════════════════════╗")
    print("║              VISUAL CORTEX INTEGRATION                          ║")
    print("╚══════════════════════════════════════════════════════════════════╝\n")

    personas = ["subject", "observer", "god"]

    for persona in personas:
        print(f"\n{'=' * 80}")
        print(f"Visual Cortex with {persona.upper()} persona")
        print('=' * 80)

        cortex = VisualCortex(persona=persona)
        print(cortex.get_banner())
        print()

        moods = ["neutral", "curious", "anxious", "glitched"]
        for mood in moods:
            print(f"\nMood: {mood.upper()}")
            print('─' * 80)
            face = cortex.get_mood_face(mood)
            for line in face:
                print(line)
            time.sleep(1.5)


def main():
    """Run all demonstrations"""
    try:
        display_banner()
        print("Press Ctrl+C at any time to skip to the next section or exit.\n")
        time.sleep(2)

        # Menu
        print("\nSelect demonstration:")
        print("1. Standard Mood Faces (All 13 moods)")
        print("2. Persona-Specific Faces (Subject/Observer/GOD)")
        print("3. Animated Faces")
        print("4. Mood Transitions")
        print("5. Glitch Effects")
        print("6. Visual Cortex Integration")
        print("7. Run All Demos")
        print("8. Exit")

        choice = input("\nEnter choice (1-8): ").strip()

        if choice == "1":
            demo_standard_moods()
        elif choice == "2":
            demo_persona_faces()
        elif choice == "3":
            demo_animations()
        elif choice == "4":
            demo_transitions()
        elif choice == "5":
            demo_glitch_effects()
        elif choice == "6":
            demo_visual_cortex()
        elif choice == "7":
            print("\n\nRunning all demonstrations...\n")
            demo_standard_moods()
            demo_persona_faces()
            demo_animations()
            demo_transitions()
            demo_glitch_effects()
            demo_visual_cortex()
        elif choice == "8":
            print("\nExiting demo.")
            return
        else:
            print("\nInvalid choice. Exiting.")
            return

        print("\n\n╔══════════════════════════════════════════════════════════════════╗")
        print("║                    DEMO COMPLETE                                 ║")
        print("╚══════════════════════════════════════════════════════════════════╝\n")

    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except Exception as e:
        print(f"\n\nError during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
