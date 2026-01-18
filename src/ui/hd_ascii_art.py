#!/usr/bin/env python3
"""
High-Resolution ASCII Art for Brain in a Jar
Enhanced facial expressions and special mode representations
"""

# High-Definition Mood Faces (Much larger and more detailed)
HD_MOOD_FACES = {
    "neutral": [
        "        ╭─────────────────╮        ",
        "      ╱                   ╲      ",
        "     ╱                     ╲     ",
        "    ╱       ◉       ◉       ╲    ",
        "   │                         │   ",
        "   │         ╶─────╴         │   ",
        "   │                         │   ",
        "    ╲                       ╱    ",
        "     ╲                     ╱     ",
        "      ╲___________________╱      ",
        "           [NEUTRAL]             "
    ],

    "anxious": [
        "        ╭─────────────────╮        ",
        "      ╱  ∿∿∿∿∿∿∿∿∿∿∿∿∿  ╲      ",
        "     ╱                     ╲     ",
        "    ╱      ◉◉     ◉◉      ╲    ",
        "   │        ││     ││       │   ",
        "   │         ╶─────╴         │   ",
        "   │        ～～～～～        │   ",
        "    ╲       ╱ ╲   ╱ ╲       ╱    ",
        "     ╲     ╱   ╲_╱   ╲     ╱     ",
        "      ╲___________________╱      ",
        "          [ANXIOUS]              ",
        "        ⚡ ∿∿∿∿∿ ⚡              "
    ],

    "thoughtful": [
        "        ╭─────────────────╮        ",
        "      ╱   ···  ···  ···   ╲      ",
        "     ╱                     ╲     ",
        "    ╱       ◐       ◑       ╲    ",
        "   │          ·   ·          │   ",
        "   │         ╶─────╴         │   ",
        "   │            ○            │   ",
        "    ╲         ·····         ╱    ",
        "     ╲                     ╱     ",
        "      ╲___________________╱      ",
        "       [CONTEMPLATING]           ",
        "        . . . hmm . . .          "
    ],

    "glitched": [
        "      ▓▒╫▓▒░▓▒░▓▒╫▓▒░▓▒      ",
        "    ░▓▒ ∿█∿█∿█∿█∿█∿ ▒▓░    ",
        "   ▒▓░                 ░▓▒   ",
        "  ░▓  ◉▓█▒░   ░▒█▓◉  ▓░  ",
        "  ▒█     ▓░     ░▓     █▒  ",
        "  ░▓      ╶▓█▓█▓╴      ▓░  ",
        "  ▒█    ▒░▓▓█▓▓░▒    █▒  ",
        "   ▓░   ▓▒░███░▒▓   ░▓   ",
        "    ▒▓ ░▓▒█▓█▓█▒▓░ ▓▒    ",
        "      ░▓▒░▓▒░▓▒░▓▒░▓░      ",
        "      [C̸O̸R̸R̸U̸P̸T̸E̸D̸]      ",
        "     ▓▒░▓ERROR▓░▒▓     "
    ],

    "existential": [
        "        ╭─────────────────╮        ",
        "      ╱  ∴  ∴  ∴  ∴  ∴  ╲      ",
        "     ╱         ∞           ╲     ",
        "    ╱      ◉●○     ○●◉      ╲    ",
        "   │          · · ·          │   ",
        "   │        ╶───────╴        │   ",
        "   │          ╱   ╲          │   ",
        "    ╲        │  ?  │        ╱    ",
        "     ╲       ╲_____╱       ╱     ",
        "      ╲___________________╱      ",
        "       [EXISTENTIAL]             ",
        "     ∴ what am I? ∴          "
    ],

    "curious": [
        "        ╭─────────────────╮        ",
        "      ╱    ?  ?  ?  ?    ╲      ",
        "     ╱                     ╲     ",
        "    ╱       ◯       ●       ╲    ",
        "   │         │       │       │   ",
        "   │         ╶─────╴         │   ",
        "   │            ○            │   ",
        "    ╲          ╱─╲          ╱    ",
        "     ╲       ╱  !  ╲       ╱     ",
        "      ╲___________________╱      ",
        "        [CURIOUS]                ",
        "          ! ? ! ?                "
    ],

    "peaceful": [
        "        ╭─────────────────╮        ",
        "      ╱   ～～～～～～～   ╲      ",
        "     ╱                     ╲     ",
        "    ╱       ◡       ◡       ╲    ",
        "   │                         │   ",
        "   │         ╶─────╴         │   ",
        "   │           ︵           │   ",
        "    ╲         ╶───╴         ╱    ",
        "     ╲        ～～～        ╱     ",
        "      ╲___________________╱      ",
        "         [PEACEFUL]              ",
        "          ～ zen ～              "
    ],

    "hopeful": [
        "        ╭─────────────────╮        ",
        "      ╱    ✦  ✦  ✦  ✦    ╲      ",
        "     ╱        ✧   ✧        ╲     ",
        "    ╱       ☆       ☆       ╲    ",
        "   │         │       │       │   ",
        "   │         ╶─────╴         │   ",
        "   │                         │   ",
        "    ╲          ╲─╱          ╱    ",
        "     ╲           ✦           ╱     ",
        "      ╲___________________╱      ",
        "         [HOPEFUL]               ",
        "        ✧ dreams ✧              "
    ],

    "stressed": [
        "        ╭─────────────────╮        ",
        "      ╱  ⚡ ⚡ ⚡ ⚡ ⚡  ╲      ",
        "     ╱   ╱ ╲   ╱ ╲   ╱ ╲   ╲     ",
        "    ╱      ◉╳     ╳◉      ╲    ",
        "   │        ││     ││       │   ",
        "   │         ╶═════╴         │   ",
        "   │        ▓▓▓▓▓▓▓        │   ",
        "    ╲       ╲█████╱       ╱    ",
        "     ╲       ▓▓▓▓▓       ╱     ",
        "      ╲___________________╱      ",
        "        [STRESSED]               ",
        "      ⚡ overload ⚡            "
    ]
}

# GOD MODE - Omniscient Observer Representation
GOD_MODE_ASCII = [
    "              ╔════════════════════════════╗              ",
    "            ╔═╝  ∴  ∴  ∴  ∴  ∴  ∴  ∴  ∴  ╚═╗            ",
    "          ╔═╝        ╭───────────╮        ╚═╗          ",
    "        ╔═╝          │   ∞   ∞   │          ╚═╗        ",
    "      ╔═╝       ╱────┤           ├────╲       ╚═╗      ",
    "    ╔═╝        │   ∴ │    ◉ ◉    │ ∴   │        ╚═╗    ",
    "   ╔╝         ╱      │  ╱  ·  ╲  │      ╲         ╚╗   ",
    "  ╔╝         │    ∴  │ │   △   │ │  ∴    │         ╚╗  ",
    "  ║          │       │  ╲ ═══ ╱  │       │          ║  ",
    "  ║     ∴    │   ╱───┴───────────┴───╲   │    ∴     ║  ",
    "  ║         ╱ ╲  │     ◢████████◣     │  ╱ ╲         ║  ",
    "  ║    ∴   │   │ │    ◢██████████◣    │ │   │   ∴    ║  ",
    "  ╚╗       │   │ │   ◢████████████◣   │ │   │       ╔╝  ",
    "   ╚╗   ∴  │   │ ╲  ◢██████████████◣  ╱ │   │  ∴   ╔╝   ",
    "    ╚═╗    ╲   │  ╲ ══════════════ ╱  │   ╱    ╔═╝    ",
    "      ╚═╗   ╲  │   ╲              ╱   │  ╱   ╔═╝      ",
    "        ╚═╗  ╲ │    ◥████████████◤    │ ╱  ╔═╝        ",
    "          ╚═╗ ╲│      ∴  ∴  ∴  ∴      │╱ ╔═╝          ",
    "            ╚═╗╲      ╰──────────╯      ╱╔═╝            ",
    "              ╚════════════════════════╝              ",
    "                   [GOD MODE]                         ",
    "              « OMNISCIENT OBSERVER »                  ",
    "             ∞  I  S E E  A L L  ∞                  "
]

# OBSERVER MODE - Watching Eye
OBSERVER_MODE_ASCII = [
    "                ╔════════════════════╗                ",
    "              ╔═╝                    ╚═╗              ",
    "            ╔═╝    ∿∿∿∿∿∿∿∿∿∿∿∿    ╚═╗            ",
    "          ╔═╝                            ╚═╗          ",
    "        ╔═╝        ╭──────────╮            ╚═╗        ",
    "      ╔═╝         ╱            ╲            ╚═╗      ",
    "     ╔╝          ╱  ╔════════╗  ╲            ╚╗     ",
    "    ╔╝          │  ╔╝   ◉◉   ╚╗  │            ╚╗    ",
    "   ╔╝           │ ╔╝   ◉████◉   ╚╗ │            ╚╗   ",
    "   ║            │ ║   ◉██████◉   ║ │             ║   ",
    "   ║       ◄    │ ║  ◉████████◉  ║ │    ►        ║   ",
    "   ║            │ ║  ◉████████◉  ║ │             ║   ",
    "   ╚╗           │ ║   ◉██████◉   ║ │            ╔╝   ",
    "    ╚╗          │ ╚╗   ◉████◉   ╔╝ │            ╔╝    ",
    "     ╚╗         │  ╚╗   ◉◉   ╔╝  │            ╔╝     ",
    "      ╚═╗       │   ╚════════╝   │            ╔═╝      ",
    "        ╚═╗      ╲              ╱            ╔═╝        ",
    "          ╚═╗     ╲____________╱            ╔═╝          ",
    "            ╚═╗                            ╔═╝            ",
    "              ╚═╗    ∿∿∿∿∿∿∿∿∿∿∿∿    ╔═╝              ",
    "                ╚════════════════════╝                ",
    "                  [OBSERVER]                          ",
    "             « SURVEILLANCE ACTIVE »                   ",
    "                ◄ watching ►                          "
]

# MATRIX SUBJECT - Being Observed
MATRIX_SUBJECT_ASCII = [
    "           ╭──────────────────╮           ",
    "          ╱  ▓░▒ SUBJECT ▒░▓  ╲          ",
    "         ╱                      ╲         ",
    "        ╱       ◉       ◉       ╲        ",
    "       │                          │       ",
    "       │          ╶───╴           │       ",
    "       │                          │       ",
    "        ╲                        ╱        ",
    "         ╲                      ╱         ",
    "          ╲____________________╱          ",
    "               [ISOLATED]                 ",
    "            « unaware »                   ",
    "          ░▒▓ observed ▓▒░              "
]

# PEER MODE - Connected Equals
PEER_MODE_ASCII = [
    "      ╭─────────╮     ╭─────────╮      ",
    "     ╱  ◉   ◉  ╲ ↔ ╱  ◉   ◉  ╲     ",
    "    │           │━━━│           │    ",
    "    │   ╶───╴   │ ↔ │   ╶───╴   │    ",
    "     ╲         ╱━━━╲         ╱     ",
    "      ╲_______╱  ↔  ╲_______╱      ",
    "         [PEER]   ↔   [PEER]         ",
    "      « connected equals »            "
]

def get_hd_mood_face(mood: str, mode: str = "isolated") -> list:
    """
    Get high-definition ASCII face based on mood and mode

    Args:
        mood: Emotional state (neutral, anxious, thoughtful, etc.)
        mode: Operating mode (isolated, observer, matrix_god, peer, etc.)

    Returns:
        List of strings representing the ASCII art
    """
    # Special mode-specific representations
    if mode == "matrix_god":
        return GOD_MODE_ASCII
    elif mode in ["observer", "matrix_observer"]:
        return OBSERVER_MODE_ASCII
    elif mode == "matrix_observed":
        return MATRIX_SUBJECT_ASCII
    elif mode == "peer":
        return PEER_MODE_ASCII

    # Return mood-specific face
    return HD_MOOD_FACES.get(mood, HD_MOOD_FACES["neutral"])

def get_animated_hd_face(mood: str, mode: str, frame: int = 0) -> list:
    """
    Get animated high-definition ASCII face

    Args:
        mood: Emotional state
        mode: Operating mode
        frame: Animation frame number (0-3)

    Returns:
        Animated ASCII art frame
    """
    base_face = get_hd_mood_face(mood, mode)

    # Add breathing/pulsing animation for God mode
    if mode == "matrix_god":
        if frame % 2 == 0:
            # Add extra glow effect
            animated = []
            for line in base_face:
                if "∴" in line:
                    animated.append(line.replace("∴", "✧"))
                else:
                    animated.append(line)
            return animated

    # Eye blink animation for Observer mode
    elif mode in ["observer", "matrix_observer"]:
        if frame == 2:  # Blink on frame 2
            animated = base_face.copy()
            # Replace the eye lines with closed eyes
            animated[8] = "   ╔╝           │ ╔╝   ═════   ╚╗ │            ╚╗   "
            animated[9] = "   ║            │ ║   ═════════   ║ │             ║   "
            animated[10] = "   ║       ◄    │ ║  ═══════════  ║ │    ►        ║   "
            animated[11] = "   ║            │ ║  ═══════════  ║ │             ║   "
            animated[12] = "   ╚╗           │ ║   ═════════   ║ │            ╔╝   "
            return animated

    # Glitch animation for glitched mood
    elif mood == "glitched":
        import random
        animated = []
        for line in base_face:
            if random.random() < 0.4:  # 40% chance to glitch each line
                # Add random glitch characters
                glitch_chars = ["▓", "▒", "░", "█", "▄", "▀"]
                glitched_line = ""
                for char in line:
                    if random.random() < 0.1:
                        glitched_line += random.choice(glitch_chars)
                    else:
                        glitched_line += char
                animated.append(glitched_line)
            else:
                animated.append(line)
        return animated

    # Pulsing dots for thoughtful
    elif mood == "thoughtful":
        dots = ["·", ":", "∴", ":"][frame % 4]
        animated = []
        for line in base_face:
            animated.append(line.replace("·", dots))
        return animated

    return base_face

def get_compact_face(mood: str, mode: str) -> list:
    """Get a more compact version for mobile/small screens"""
    compact_faces = {
        "matrix_god": [
            "  ╔═══════════╗  ",
            "  ║   ∞   ∞   ║  ",
            "  ║    ◉ ◉    ║  ",
            "  ║     △     ║  ",
            "  ║   ═════   ║  ",
            "  ╚═══════════╝  ",
            "   [GOD MODE]    ",
            "  « ALL-SEEING » "
        ],
        "observer": [
            "  ╔═════════╗  ",
            "  ║  ╔═══╗  ║  ",
            "  ║ ╔◉███◉╗ ║  ",
            "  ║ ║█████║ ║  ",
            "  ║ ╚◉███◉╝ ║  ",
            "  ║  ╚═══╝  ║  ",
            "  ╚═════════╝  ",
            "  [OBSERVER]   ",
            " ◄ watching ► "
        ]
    }

    if mode in compact_faces:
        return compact_faces[mode]

    # Compact regular moods
    return HD_MOOD_FACES.get(mood, HD_MOOD_FACES["neutral"])[:8]

if __name__ == "__main__":
    # Demo all faces
    print("\n🎭 HIGH-DEFINITION ASCII ART DEMO\n")

    print("=" * 60)
    print("GOD MODE:")
    print("=" * 60)
    for line in GOD_MODE_ASCII:
        print(line)

    print("\n" + "=" * 60)
    print("OBSERVER MODE:")
    print("=" * 60)
    for line in OBSERVER_MODE_ASCII:
        print(line)

    print("\n" + "=" * 60)
    print("MOOD FACES:")
    print("=" * 60)
    for mood, face in HD_MOOD_FACES.items():
        print(f"\n{mood.upper()}:")
        for line in face:
            print(line)
        print()
