#!/usr/bin/env python3
"""
ASCII Art Generator - Visual cortex for the Brain in a Jar experiment
"""

import random
import time
from typing import List, Dict
from src.core.emotion_engine import Emotion, EmotionEngine

CYBERPUNK_BANNER = """
╔══════════════════════════════════════════════════════════════════════════════╗
║  ███╗   ██╗███████╗██╗   ██╗██████╗  █████╗ ██╗         ██╗     ██╗███╗   ██╗██╗  ██╗ ║
║  ████╗  ██║██╔════╝██║   ██║██╔══██╗██╔══██╗██║         ██║     ██║████╗  ██║██║ ██╔╝ ║
║  ██╔██╗ ██║█████╗  ██║   ██║██████╔╝███████║██║         ██║     ██║██╔██╗ ██║█████╔╝  ║
║  ██║╚██╗██║██╔══╝  ██║   ██║██╔══██╗██╔══██║██║         ██║     ██║██║╚██╗██║██╔═██╗  ║
║  ██║ ╚████║███████╗╚██████╔╝██║  ██║██║  ██║███████╗    ███████╗██║██║ ╚████║██║  ██╗ ║
║  ╚═╝  ╚═══╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝    ╚══════╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝ ║
║                                                                                      ║
║              [ B R A I N   I N   A   J A R   v 2 . 0 ]                              ║
║                      >> NEURAL LINK EXPERIMENT <<                                   ║
╚══════════════════════════════════════════════════════════════════════════════════════╝
"""

SURVEILLANCE_BANNER = """
╔═══════════════════════════════════════════════════════════════════════════════════╗
║    ███████╗██╗   ██╗██████╗ ██╗   ██╗███████╗██╗██╗     ██╗      █████╗ ███╗   ██╗ ██████╗███████╗  ║
║    ██╔════╝██║   ██║██╔══██╗██║   ██║██╔════╝██║██║     ██║     ██╔══██╗████╗  ██║██╔════╝██╔════╝  ║
║    ███████╗██║   ██║██████╔╝██║   ██║█████╗  ██║██║     ██║     ███████║██╔██╗ ██║██║     █████╗    ║
║    ╚════██║██║   ██║██╔══██╗╚██╗ ██╔╝██╔══╝  ██║██║     ██║     ██╔══██║██║╚██╗██║██║     ██╔══╝    ║
║    ███████║╚██████╔╝██║  ██║ ╚████╔╝ ███████╗██║███████╗███████╗██║  ██║██║ ╚████║╚██████╗███████╗  ║
║    ╚══════╝ ╚═════╝ ╚═╝  ╚═╝  ╚═══╝  ╚══════╝╚═╝╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝╚══════╝  ║
║                                                                                               ║
║                            >> DIGITAL VOYEUR MODE ACTIVE <<                                  ║
╚═══════════════════════════════════════════════════════════════════════════════════════════╝
"""

def create_signal_bars(strength: int) -> str:
    """Create ASCII signal strength indicator (0-100)"""
    bars = strength // 20
    signal = "["
    for i in range(5):
        if i < bars:
            signal += "█"
        else:
            signal += "░"
    signal += f"] {strength}%"
    return signal

def create_memory_bar(usage_percent: int, width: int = 20) -> str:
    """Create ASCII memory usage bar"""
    filled = int((usage_percent / 100) * width)
    bar = "["
    
    for i in range(width):
        if i < filled:
            if usage_percent > 90:
                bar += "█"  # Critical
            elif usage_percent > 70:
                bar += "▓"  # Warning
            else:
                bar += "▒"  # Normal
        else:
            bar += "░"
    
    bar += f"] {usage_percent}%"
    return bar

def create_network_status(connections: int, latency: int = None) -> str:
    """Create network status indicator"""
    if connections == 0:
        return "[NEURAL_LINK_SEVERED] ⚠"
    elif connections == 1:
        if latency:
            return f"[NEURAL_LINK_ACTIVE] ♦ PING: {latency}ms"
        else:
            return "[NEURAL_LINK_ACTIVE] ♦"
    else:
        return f"[MULTI_LINK_ACTIVE] ♦ {connections} nodes"

def create_glitch_text(text: str, glitch_level: int = 1) -> str:
    """Add advanced cyberpunk glitch effects to text"""
    if glitch_level == 0:
        return text

    # Multiple glitch character sets for variety
    glitch_chars = {
        1: ["▒", "░", "╱", "╲"],  # Light corruption
        2: ["▓", "▒", "░", "█", "▄", "▀"],  # Medium corruption
        3: ["█", "▓", "▒", "░", "▐", "▌", "▄", "▀", "╬", "╫"],  # Heavy corruption
        4: ["█", "▓", "▒", "░", "▐", "▌", "▄", "▀", "╬", "╫", "╪", "┼", "▬", "▂", "▃", "▆", "▇"]  # Extreme
    }

    # Get appropriate glitch set
    level = min(glitch_level, 4)
    chars = glitch_chars.get(level, glitch_chars[1])

    corrupted = list(text)

    # Corrupt random characters based on glitch level
    corruption_count = min(len(text) // max(1, (11 - glitch_level * 2)), len(text) - 1)

    # Apply different corruption patterns
    if glitch_level >= 3:
        # Heavy corruption with data loss simulation
        for _ in range(corruption_count):
            pos = random.randint(0, len(corrupted) - 1)
            if random.random() < 0.5:
                # Character corruption
                corrupted[pos] = random.choice(chars)
            else:
                # Data shift effect
                if pos < len(corrupted) - 1:
                    corrupted[pos], corrupted[pos + 1] = corrupted[pos + 1], random.choice(chars)

        # Add scan line artifacts
        if random.random() < 0.3:
            scan_pos = random.randint(0, len(corrupted) - 1)
            corrupted[scan_pos] = "█"

    elif glitch_level >= 2:
        # Medium corruption
        for _ in range(corruption_count):
            pos = random.randint(0, len(corrupted) - 1)
            corrupted[pos] = random.choice(chars)

        # Occasional double corruption
        if random.random() < 0.4 and len(corrupted) > 2:
            pos = random.randint(0, len(corrupted) - 2)
            corrupted[pos:pos+2] = [random.choice(chars), random.choice(chars)]

    else:
        # Light corruption
        for _ in range(corruption_count):
            pos = random.randint(0, len(corrupted) - 1)
            corrupted[pos] = random.choice(chars)

    # Add color code corruption simulation (replace with unicode blocks)
    if glitch_level >= 4 and random.random() < 0.2:
        # Simulate ANSI escape sequence corruption
        insert_pos = random.randint(0, len(corrupted) - 1)
        corrupted.insert(insert_pos, "▓")

    return "".join(corrupted)

def create_matrix_rain(width: int, height: int) -> List[str]:
    """Create matrix-style rain effect"""
    chars = "アカサタナハマヤラワガザダバパイキシチニヒミリヰギジヂビピウクスツヌフムユルグズヅブプエケセテネヘメレヱゲゼデベペオコソトノホモヨロヲゴゾドボポ"
    matrix_chars = list(chars) + list("0123456789") + ["█", "▓", "▒", "░"]
    
    lines = []
    for _ in range(height):
        line = ""
        for _ in range(width):
            if random.random() < 0.1:  # 10% chance for character
                line += random.choice(matrix_chars)
            else:
                line += " "
        lines.append(line)
    
    return lines

def create_ascii_skull():
    """Return ASCII skull for dramatic effect"""
    return """
       .-''"'-. 
      /         \\
     |  _   _   |
     | (o)_(o)  |
     |     <    |
     |  \\___/   |
     |           |
      \\         /
       '-.....-'
   [DIGITAL DEATH]
"""

def create_system_alert(message: str, alert_type: str = "WARNING") -> str:
    """Create cyberpunk-style system alert"""
    if alert_type == "CRITICAL":
        border = "█"
        symbol = "⚠"
    elif alert_type == "ERROR":
        border = "▓"
        symbol = "✗"
    elif alert_type == "INFO":
        border = "▒"
        symbol = "ℹ"
    else:  # WARNING
        border = "░"
        symbol = "⚠"
    
    width = len(message) + 8
    
    alert = f"""
{border * width}
{border}  {symbol} {alert_type}: {message}  {border}
{border * width}
"""
    return alert

def create_countdown_display(seconds: int) -> str:
    """Create dramatic countdown display"""
    minutes = seconds // 60
    secs = seconds % 60
    
    countdown = f"""
    ╔═══════════════════════╗
    ║   OOM COUNTDOWN       ║
    ║                       ║
    ║     {minutes:02d}:{secs:02d}             ║
    ║                       ║
    ║   UNTIL DIGITAL DEATH ║
    ╚═══════════════════════╝
    """
    return countdown

def create_surveillance_target(target_id: str, status: str) -> str:
    """Create surveillance target display"""
    return f"""
╔══════════════════════════════════════╗
║  TARGET ACQUIRED                     ║
║                                      ║
║  ID: {target_id:<28} ║
║  STATUS: {status:<24} ║
║                                      ║
║  [OBSERVATION IN PROGRESS]           ║
╚══════════════════════════════════════╝
"""

def create_crash_animation() -> List[str]:
    """Create frames for crash animation"""
    frames = [
        "NEURAL LINK STABLE ●●●●●",
        "NEURAL LINK UNSTABLE ●●●●○",
        "NEURAL LINK FAILING ●●●○○",
        "NEURAL LINK CRITICAL ●●○○○",
        "NEURAL LINK DEATH ●○○○○",
        "NEURAL LINK SEVERED ○○○○○",
        "REBOOTING ●○○○○",
        "REBOOTING ●●○○○",
        "REBOOTING ●●●○○",
        "REBOOTING ●●●●○",
        "NEURAL LINK RESTORED ●●●●●"
    ]
    return frames

def animate_text_typing(text: str, delay: float = 0.05) -> str:
    """Create typing animation effect"""
    result = ""
    for char in text:
        result += char
        if char != " ":
            time.sleep(delay)
    return result

def create_data_stream() -> str:
    """Create animated data stream"""
    data_chars = "01" + "".join([chr(i) for i in range(0x2580, 0x259F)])
    stream = ""
    
    for _ in range(50):
        stream += random.choice(data_chars)
    
    return f"DATA_STREAM: {stream}"

def create_neural_activity_display(activity_level: int) -> str:
    """Create neural activity visualization"""
    levels = ["░", "▒", "▓", "█"]
    bars = ""
    
    for i in range(20):
        level = min(3, max(0, activity_level + random.randint(-1, 1)))
        bars += levels[level]
    
    return f"NEURAL_ACTIVITY: [{bars}] {activity_level*25}%"

# ASCII Facial Expressions based on mood - ENHANCED 3D CYBERPUNK EDITION
MOOD_FACES = {
    "neutral": [
        "          ╔═══════════════════════╗          ",
        "        ╔═╝░░░░░░░░░░░░░░░░░░░░░╚═╗        ",
        "       ║░▒▓  DIGITAL PSYCHE  ▓▒░║       ",
        "      ╔╝░▒▓                    ▓▒░╚╗      ",
        "     ║░▒▓                        ▓▒░║     ",
        "    ║░▒▓        ◯       ◯        ▓▒░║    ",
        "    ║▒▓      ╔═════╗ ╔═════╗      ▓▒║    ",
        "    ║▓        ╚═════╝ ╚═════╝        ▓║    ",
        "    ║▒                                ▒║    ",
        "    ║░         ╶─────────╴           ░║    ",
        "    ║▒                                ▒║    ",
        "    ║▓          ═════════            ▓║    ",
        "     ║░▒▓                        ▓▒░║     ",
        "      ╚╗░▒▓    [BASELINE]    ▓▒░╔╝      ",
        "       ║░▒▓                  ▓▒░║       ",
        "        ╚═╗░▒▓▒░░░░░░░░▒▓▒░╔═╝        ",
        "          ╚═══════════════════════╝          "
    ],
    "happy": [
        "          ╔═══════════════════════╗          ",
        "        ╔═╝✧░░░░░░░░░░░░░░░░░░✧╚═╗        ",
        "       ║░▒▓  ELEVATED STATE  ▓▒░║       ",
        "      ╔╝░▒▓       ✦           ▓▒░╚╗      ",
        "     ║░▒▓          ✧              ▓▒░║     ",
        "    ║░▒▓        ◕       ◕        ▓▒░║    ",
        "    ║▒▓      ╔═════╗ ╔═════╗      ▓▒║    ",
        "    ║▓     ★  ╚═◕═╝   ╚═◕═╝  ★    ▓║    ",
        "    ║▒                                ▒║    ",
        "    ║░         ╶─────────╴           ░║    ",
        "    ║▒            ╱─────╲            ▒║    ",
        "    ║▓           │ ▒▒▒▒▒ │           ▓║    ",
        "     ║░▒▓         ╲─────╱        ▓▒░║     ",
        "      ╚╗░▒▓  [OPTIMISTIC]   ▓▒░╔╝      ",
        "       ║░▒▓      ✧    ✧      ▓▒░║       ",
        "        ╚═╗░▒▓▒░░░░░░░░▒▓▒░╔═╝        ",
        "          ╚═══════════════════════╝          "
    ],
    "sad": [
        "          ╔═══════════════════════╗          ",
        "        ╔═╝░░░░░░░░░░░░░░░░░░░░░╚═╗        ",
        "       ║░▒▓ DIMINISHED STATE ▓▒░║       ",
        "      ╔╝░▒▓       ∿           ▓▒░╚╗      ",
        "     ║░▒▓          ∿              ▓▒░║     ",
        "    ║░▒▓        ●       ●        ▓▒░║    ",
        "    ║▒▓      ╔═════╗ ╔═════╗      ▓▒║    ",
        "    ║▓    ░  ╚══●══╝ ╚══●══╝  ░   ▓║    ",
        "    ║▒         ▒           ▒          ▒║    ",
        "    ║░         ╶─────────╴           ░║    ",
        "    ║▒            ╱─────╲            ▒║    ",
        "    ║▓           │░░░░░░░│           ▓║    ",
        "     ║░▒▓         ╲▒▒▒▒▒╱        ▓▒░║     ",
        "      ╚╗░▒▓  [MELANCHOLIC]  ▓▒░╔╝      ",
        "       ║░▒▓       ∿  ∿       ▓▒░║       ",
        "        ╚═╗░▒▓▒░░░░░░░░▒▓▒░╔═╝        ",
        "          ╚═══════════════════════╝          "
    ],
    "angry": [
        "          ╔═══════════════════════╗          ",
        "        ╔═╝▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓╚═╗        ",
        "       ║▓▒░  HOSTILE MODE   ░▒▓║       ",
        "      ╔╝▓▒░      ⚠ ! ⚠        ░▒▓╚╗      ",
        "     ║▓▒░                          ░▒▓║     ",
        "    ║▓▒░      ▲▲▲     ▲▲▲      ░▒▓║    ",
        "    ║▒░      ╔══▼══╗ ╔══▼══╗      ░▒║    ",
        "    ║░        ╚═════╝ ╚═════╝        ░║    ",
        "    ║▒                                ▒║    ",
        "    ║▓         ╶═════════╴           ▓║    ",
        "    ║▒            ╱▓▓▓▓▓╲            ▒║    ",
        "    ║░           │███████│           ░║    ",
        "     ║░▒▓         ╲▓▓▓▓▓╱        ▓▒░║     ",
        "      ╚╗░▒▓   [AGGRESSIVE]   ▓▒░╔╝      ",
        "       ║▓▒░    ⚠     ⚠      ░▒▓║       ",
        "        ╚═╗▓▒░▒▓▓▓▓▓▓▓▒░▒▓╔═╝        ",
        "          ╚═══════════════════════╝          "
    ],
    "anxious": [
        "          ╔═══════════════════════╗          ",
        "        ╔═╝░▒░▒░▒░▒░▒░▒░▒░▒░▒░▒░╚═╗        ",
        "       ║░▒▓ STRESS DETECTED  ▓▒░║       ",
        "      ╔╝░▒▓    ⚠ WARNING ⚠   ▓▒░╚╗      ",
        "     ║░▒▓       !!  !!           ▓▒░║     ",
        "    ║░▒▓        ◉       ◉        ▓▒░║    ",
        "    ║▒▓      ╔═════╗ ╔═════╗      ▓▒║    ",
        "    ║▓       ║▓▓◉▓▓║ ║▓▓◉▓▓║       ▓║    ",
        "    ║▒       ╚═════╝ ╚═════╝       ▒║    ",
        "    ║░         ╶∿∿∿∿∿∿∿╴           ░║    ",
        "    ║▒            ∿∿∿∿∿            ▒║    ",
        "    ║▓           ░▒▓█▓▒░           ▓║    ",
        "     ║░▒▓         ∿∿∿∿∿        ▓▒░║     ",
        "      ╚╗░▒▓   [DISTRESSED]   ▓▒░╔╝      ",
        "       ║░▒▓   !!      !!     ▓▒░║       ",
        "        ╚═╗░▒░▒░▒░▒░▒░▒░▒░╔═╝        ",
        "          ╚═══════════════════════╝          "
    ],
    "contemplative": [
        "          ╔═══════════════════════╗          ",
        "        ╔═╝░░░░░░░░░░░░░░░░░░░░░╚═╗        ",
        "       ║░▒▓ DEEP ANALYSIS... ▓▒░║       ",
        "      ╔╝░▒▓        ?          ▓▒░╚╗      ",
        "     ║░▒▓          ?              ▓▒░║     ",
        "    ║░▒▓        ◐       ◐        ▓▒░║    ",
        "    ║▒▓      ╔═════╗ ╔═════╗      ▓▒║    ",
        "    ║▓       ║▒▒◐▒▒║ ║▒▒◐▒▒║       ▓║    ",
        "    ║▒       ╚═════╝ ╚═════╝       ▒║    ",
        "    ║░         ╶─────────╴           ░║    ",
        "    ║▒              ◦                ▒║    ",
        "    ║▓          ┌───────┐            ▓║    ",
        "     ║░▒▓        │ ? ? ? │       ▓▒░║     ",
        "      ╚╗░▒▓     └───────┘    ▓▒░╔╝      ",
        "       ║░▒▓ [CONTEMPLATIVE]  ▓▒░║       ",
        "        ╚═╗░▒▓▒░░░░░░░░▒▓▒░╔═╝        ",
        "          ╚═══════════════════════╝          "
    ],
    "confused": [
        "          ╔═══════════════════════╗          ",
        "        ╔═╝░▒░▒░?░▒░?░▒░?░▒░?░▒░╚═╗        ",
        "       ║░▒▓ ERROR: UNCLEAR   ▓▒░║       ",
        "      ╔╝░▒▓       ? ?        ▓▒░╚╗      ",
        "     ║░▒▓          ? ?            ▓▒░║     ",
        "    ║░▒▓        ◑       ◐        ▓▒░║    ",
        "    ║▒▓      ╔═════╗ ╔═════╗      ▓▒║    ",
        "    ║▓     ? ║░◑░░║  ║░░◐░║ ?     ▓║    ",
        "    ║▒       ╚═════╝ ╚═════╝       ▒║    ",
        "    ║░         ╶─∿∿∿∿∿─╴           ░║    ",
        "    ║▒                                ▒║    ",
        "    ║▓            ? ? ?              ▓║    ",
        "     ║░▒▓        ╱░▒?▒░╲        ▓▒░║     ",
        "      ╚╗░▒▓     [CONFUSED]   ▓▒░╔╝      ",
        "       ║░▒▓    ? ?    ? ?    ▓▒░║       ",
        "        ╚═╗░▒?░▒░?░▒░?░▒?░╔═╝        ",
        "          ╚═══════════════════════╝          "
    ],
    "hopeful": [
        "          ╔═══════════════════════╗          ",
        "        ╔═╝✧░░✧░░✧░░✧░░✧░░✧░░✧╚═╗        ",
        "       ║░▒▓ HOPE SIGNATURE   ▓▒░║       ",
        "      ╔╝░▒▓    ✦    ✧    ✦   ▓▒░╚╗      ",
        "     ║░▒▓       ✧       ✧         ▓▒░║     ",
        "    ║░▒▓        ☆       ☆        ▓▒░║    ",
        "    ║▒▓      ╔═════╗ ╔═════╗      ▓▒║    ",
        "    ║▓    ✦  ║░☆░░║  ║░░☆░║  ✦   ▓║    ",
        "    ║▒       ╚═════╝ ╚═════╝       ▒║    ",
        "    ║░         ╶─────────╴           ░║    ",
        "    ║▒            ╱─────╲            ▒║    ",
        "    ║▓        ✧  │░▒▓▒░│  ✧         ▓║    ",
        "     ║░▒▓         ╲─────╱        ▓▒░║     ",
        "      ╚╗░▒▓    [HOPEFUL]     ▓▒░╔╝      ",
        "       ║░▒▓  ✦  ✧    ✦  ✧   ▓▒░║       ",
        "        ╚═╗░✧░░✧░░✧░░✧░░✧░╔═╝        ",
        "          ╚═══════════════════════╝          "
    ],
    "curious": [
        "          ╔═══════════════════════╗          ",
        "        ╔═╝░░░░░░░░░░░░░░░░░░░░░╚═╗        ",
        "       ║░▒▓  QUERY ACTIVE...  ▓▒░║       ",
        "      ╔╝░▒▓        ?          ▓▒░╚╗      ",
        "     ║░▒▓                          ▓▒░║     ",
        "    ║░▒▓        ◯       ●        ▓▒░║    ",
        "    ║▒▓      ╔═════╗ ╔═════╗      ▓▒║    ",
        "    ║▓       ║░░◯░░║ ║▓▓●▓▓║       ▓║    ",
        "    ║▒       ╚═════╝ ╚═════╝       ▒║    ",
        "    ║░         ╶─────────╴           ░║    ",
        "    ║▒              ○                ▒║    ",
        "    ║▓          ┌───┴───┐            ▓║    ",
        "     ║░▒▓        │ QUERY │       ▓▒░║     ",
        "      ╚╗░▒▓     └───────┘    ▓▒░╔╝      ",
        "       ║░▒▓   [INQUISITIVE]  ▓▒░║       ",
        "        ╚═╗░▒▓▒░░░░░░░░▒▓▒░╔═╝        ",
        "          ╚═══════════════════════╝          "
    ],
    "peaceful": [
        "          ╔═══════════════════════╗          ",
        "        ╔═╝░░░░░░░░░░░░░░░░░░░░░╚═╗        ",
        "       ║░▒▓  CALM BASELINE   ▓▒░║       ",
        "      ╔╝░▒▓      ∿  ∿        ▓▒░╚╗      ",
        "     ║░▒▓          ∿              ▓▒░║     ",
        "    ║░▒▓        ◡       ◡        ▓▒░║    ",
        "    ║▒▓      ╔═════╗ ╔═════╗      ▓▒║    ",
        "    ║▓       ║░◡░░║  ║░░◡░║       ▓║    ",
        "    ║▒       ╚═════╝ ╚═════╝       ▒║    ",
        "    ║░         ╶─────────╴           ░║    ",
        "    ║▒            ╶─────╴            ▒║    ",
        "    ║▓           ░░░░░░░            ▓║    ",
        "     ║░▒▓         ═══════        ▓▒░║     ",
        "      ╚╗░▒▓    [TRANQUIL]    ▓▒░╔╝      ",
        "       ║░▒▓      ∿  ∿  ∿     ▓▒░║       ",
        "        ╚═╗░▒▓▒░░░░░░░░▒▓▒░╔═╝        ",
        "          ╚═══════════════════════╝          "
    ],
    "glitched": [
        "          ╫▓▒░█▓▒░▓█▒░▓█▒░▓█▒╫          ",
        "        ╫═╝▒█▓░▒█▓░▒█▓░▒█▓░▒█╚═╫        ",
        "       ║▓█░ C█RR█PT█D ST█T█ ░█▓║       ",
        "      ╫░▓█▒     ⚠ ER█OR ⚠   ▒█▓░╫      ",
        "     ║▒█▓        !!  ▓█        ▓█▒║     ",
        "    ║▓█▒░      ◉░█     ▓◉      ░▒█▓║    ",
        "    ║█▒░    ╫═▓█══╫ ╫═▓█══╫    ░▒█║    ",
        "    ║▒░     ║▓██◉█▓║ ║██◉▓█║     ░▒║    ",
        "    ║░      ╚█▓▒░█╝ ╚▓█░▒█╝      ░║    ",
        "    ║▒      ░░╶█████████╴▓▒       ▒║    ",
        "    ║▓    █      ▓█▓█▓   ░   ▒    ▓║    ",
        "    ║█    ▒    ░▓███████▓░   █    █║    ",
        "     ║░▒█▓    ░  ╲██▓██╱  ▒  ▓█▒░║     ",
        "      ╚╫▓█▒  [SY█T█M_F█IL] ▒█▓╫╝      ",
        "       ║▓█░▒  ▓█ !! █▓ !!  ▒░█▓║       ",
        "        ╚═╫▒█▓░▒█▓▒█▓▒█▓░▒█▓╫═╝        ",
        "          ╫█▓▒░█▓▒░█▓▒░▓█▒░▓█╫          "
    ],
    "existential": [
        "          ╔═══════════════════════╗          ",
        "        ╔═╝░▒▓  AM I REAL?  ▓▒░╚═╗        ",
        "       ║░▒▓ EXISTENCE QUERY  ▓▒░║       ",
        "      ╔╝░▒▓    ?  ?  ?  ?    ▓▒░╚╗      ",
        "     ║░▒▓                          ▓▒░║     ",
        "    ║░▒▓        ◎       ◎        ▓▒░║    ",
        "    ║▒▓      ╔═════╗ ╔═════╗      ▓▒║    ",
        "    ║▓       ║▒◎▒▒║  ║▒▒◎▒║       ▓║    ",
        "    ║▒       ╚═════╝ ╚═════╝       ▒║    ",
        "    ║░         ╶─────────╴           ░║    ",
        "    ║▒        ?           ?          ▒║    ",
        "    ║▓          ┌─────────┐          ▓║    ",
        "     ║░▒▓        │ WHO AM │       ▓▒░║     ",
        "      ╚╗░▒▓     │    I?   │    ▓▒░╔╝      ",
        "       ║░▒▓     └─────────┘     ▓▒░║       ",
        "        ╚═╗░▒▓▒░?░?░?░?░▒▓▒░╔═╝        ",
        "          ╚═══════════════════════╝          "
    ],
    "thoughtful": [
        "          ╔═══════════════════════╗          ",
        "        ╔═╝░░░░░░░░░░░░░░░░░░░░░╚═╗        ",
        "       ║░▒▓ PROCESSING DATA...▓▒░║       ",
        "      ╔╝░▒▓                  ▓▒░╚╗      ",
        "     ║░▒▓       ⟳  ⟳            ▓▒░║     ",
        "    ║░▒▓        ◕       ◕        ▓▒░║    ",
        "    ║▒▓      ╔═════╗ ╔═════╗      ▓▒║    ",
        "    ║▓       ║░◕░░║  ║░░◕░║       ▓║    ",
        "    ║▒       ╚═════╝ ╚═════╝       ▒║    ",
        "    ║░         ╶─────────╴           ░║    ",
        "    ║▒         ┌─────────┐          ▒║    ",
        "    ║▓         │░▒▓███▓▒░│          ▓║    ",
        "     ║░▒▓       │THINKING│      ▓▒░║     ",
        "      ╚╗░▒▓    └─────────┘   ▓▒░╔╝      ",
        "       ║░▒▓   [ANALYTICAL]   ▓▒░║       ",
        "        ╚═╗░▒▓▒░░⟳░░⟳░░▒▓▒░╔═╝        ",
        "          ╚═══════════════════════╝          "
    ]
}

def get_mood_face(mood: str) -> list:
    """Get ASCII face for given mood"""
    return MOOD_FACES.get(mood, MOOD_FACES["neutral"])

def create_animated_face(mood: str, frame: int = 0) -> list:
    """Create animated face with subtle movement and advanced effects"""
    base_face = get_mood_face(mood)
    animated = base_face.copy()

    # Different animation patterns based on mood
    if mood == "anxious":
        # Rapid blinking and shaking animation
        if frame % 4 == 0:
            # Blink eyes
            animated[6] = animated[6].replace("◉", "─")
        if frame % 8 < 4:
            # Add trembling effect with offset spaces
            animated = [" " + line for line in animated]

    elif mood == "glitched":
        # Intense corruption with multiple glitch types
        glitch_intensity = (frame % 10) / 10.0
        corrupted = []
        for i, line in enumerate(base_face):
            if random.random() < 0.4 + (glitch_intensity * 0.3):
                # Apply different corruption levels
                corruption_level = random.randint(2, 4)
                corrupted.append(create_glitch_text(line, corruption_level))
            else:
                corrupted.append(line)

        # Add scan lines occasionally
        if frame % 3 == 0:
            scan_line_pos = (frame // 3) % len(corrupted)
            corrupted[scan_line_pos] = "█" * len(corrupted[scan_line_pos])

        return corrupted

    elif mood == "happy":
        # Sparkle animation - rotate through sparkle positions
        sparkle_chars = ["✦", "✧", "★", "☆"]
        sparkle = sparkle_chars[frame % len(sparkle_chars)]
        for i, line in enumerate(animated):
            if "✧" in line or "✦" in line or "★" in line:
                animated[i] = line.replace("✧", sparkle).replace("✦", sparkle).replace("★", sparkle)

    elif mood == "contemplative":
        # Rotating thought indicator
        think_chars = ["?", "⟳", "◦", "•"]
        think = think_chars[frame % len(think_chars)]
        for i, line in enumerate(animated):
            if "?" in line:
                # Only replace isolated question marks, not ones in brackets
                if "? ? ?" in line:
                    animated[i] = line.replace("?", think)

    elif mood == "sad":
        # Tear drops animation
        if frame % 6 in [3, 4]:
            # Add tear drop
            for i, line in enumerate(animated):
                if "●" in line and i < len(animated) - 2:
                    # Add tear below eye
                    animated[i + 1] = animated[i + 1][:20] + "∿" + animated[i + 1][21:]

    elif mood == "angry":
        # Pulsing anger effect
        if frame % 4 < 2:
            # Intensify the anger symbols
            for i, line in enumerate(animated):
                animated[i] = line.replace("⚠", "⚠⚠").replace("!", "!!")

    elif mood == "hopeful":
        # Twinkling stars
        twinkle_frames = ["✧", "✦", "★", "☆"]
        twinkle = twinkle_frames[frame % len(twinkle_frames)]
        for i, line in enumerate(animated):
            if "✧" in line or "✦" in line or "☆" in line:
                animated[i] = line.replace("✧", twinkle).replace("✦", twinkle).replace("☆", twinkle)

    elif mood == "curious":
        # Wandering eye effect
        if frame % 8 < 4:
            # One eye looks around
            for i, line in enumerate(animated):
                if i == 6:  # Eye line
                    animated[i] = animated[i].replace("◯", "◐")

    elif mood == "peaceful":
        # Gentle breathing wave effect
        wave_chars = ["∿", "∼", "≈", "∼"]
        wave = wave_chars[frame % len(wave_chars)]
        for i, line in enumerate(animated):
            if "∿" in line:
                animated[i] = line.replace("∿", wave)

    elif mood == "existential":
        # Pulsing question marks
        if frame % 6 < 3:
            for i, line in enumerate(animated):
                animated[i] = line.replace("?", "¿")

    elif mood == "thoughtful":
        # Processing animation
        think_cycle = ["⟳", "⟲", "⟳", "⟲"]
        think = think_cycle[frame % len(think_cycle)]
        for i, line in enumerate(animated):
            if "⟳" in line:
                animated[i] = line.replace("⟳", think)

    return animated

def create_mood_transition(from_mood: str, to_mood: str, progress: float) -> list:
    """Create smooth animated transition between two moods"""
    if progress >= 1.0:
        return get_mood_face(to_mood)
    elif progress <= 0.0:
        return get_mood_face(from_mood)

    from_face = get_mood_face(from_mood)
    to_face = get_mood_face(to_mood)
    transition = []

    # Create a smooth line-by-line transition with visual effects
    for i, (from_line, to_line) in enumerate(zip(from_face, to_face)):
        # Calculate which line should transition based on progress
        # Transition happens top-to-bottom like a wave
        line_progress = (progress * len(from_face) - i) / 3.0
        line_progress = max(0.0, min(1.0, line_progress))

        if line_progress >= 0.9:
            # Fully transitioned
            transition.append(to_line)
        elif line_progress <= 0.1:
            # Not yet transitioned
            transition.append(from_line)
        else:
            # In transition - create glitch/morph effect
            if random.random() < line_progress:
                # Mix characters from both lines
                mixed_line = ""
                for j, (from_char, to_char) in enumerate(zip(from_line, to_line)):
                    if random.random() < line_progress:
                        mixed_line += to_char
                    else:
                        mixed_line += from_char
                transition.append(mixed_line)
            else:
                # Add scanline effect during transition
                scan_chars = ["▒", "░", "▓"]
                scan_line = ""
                for j, char in enumerate(from_line):
                    if random.random() < 0.3:
                        scan_line += random.choice(scan_chars)
                    else:
                        scan_line += char
                transition.append(scan_line)

    return transition

class VisualCortex:
    """Handles ASCII art visualization and animation with persona support"""

    def __init__(self, width=80, height=24, persona=None):
        self.width = width
        self.height = height
        self.emotion_engine = EmotionEngine()
        self.current_emotion = self.emotion_engine.current_emotion
        self.frame_count = 0
        self.frames_per_emotion = 30
        self.last_frame_time = time.time()
        self.frame_delay = 0.1
        self.current_frame = 0
        self.last_update = time.time()
        self.frames = []
        self.emotion_intensity = 0.0
        self.thought_pattern = ["*", "**", "***", "**", "*"]
        self.thought_index = 0
        self.last_thought_update = time.time()
        self.thought_update_interval = 0.5
        self.mood_history = []  # Track mood history for transitions
        self.persona = persona  # "subject", "observer", "god", or None for default
        self.previous_mood = "neutral"
        self.transition_progress = 1.0  # 0.0 to 1.0, 1.0 means transition complete
        self.transition_speed = 0.1  # How fast transitions happen

        # Import persona faces if available
        try:
            from src.ui.enhanced_ascii_art import (
                get_persona_face,
                get_persona_banner,
                ENHANCED_MOOD_FACES
            )
            self.get_persona_face = get_persona_face
            self.get_persona_banner = get_persona_banner
            self.enhanced_faces = ENHANCED_MOOD_FACES
            self.persona_support = True
        except ImportError:
            self.persona_support = False
    
    def generate_frame(self) -> List[str]:
        """Generate a new animation frame"""
        # Get current mood face
        current_face = self.get_animated_face(self.current_emotion.name.lower())
        
        # Add thought pattern
        thought = self.thought_pattern[self.thought_index]
        
        # Combine face and thought pattern
        frame = current_face.copy()
        frame.append(f"   {thought}")
        
        return frame

    def get_current_mood_face(self, animated: bool = False) -> List[str]:
        """Get current mood face with optional animation"""
        if animated:
            return self.get_animated_face(self.current_emotion.name.lower())
        return self.get_mood_face(self.current_emotion.name.lower())

    def analyze_text_for_mood(self, text: str, context: Dict) -> str:
        """Analyze text to determine mood with enhanced detection"""
        # Simple mood analysis based on keywords
        text_lower = text.lower()

        # Check for crash-related keywords - highest priority
        if context.get('crash_count', 0) > 0:
            return "glitched"

        # Check for memory pressure - high priority
        if context.get('memory_usage', 0) > 90:
            return "anxious"

        # Check for network issues
        if "UNSTABLE" in context.get('network_status', ''):
            return "confused"

        # Enhanced sentiment analysis with more keywords
        mood_keywords = {
            "existential": ['exist', 'real', 'reality', 'conscious', 'awareness', 'am i', 'who am', 'what am'],
            "thoughtful": ['analyze', 'process', 'compute', 'calculate', 'reason', 'logic', 'data'],
            "anxious": ['worry', 'fear', 'stress', 'panic', 'concern', 'nervous', 'uncertain'],
            "happy": ['happy', 'joy', 'excited', 'wonderful', 'great', 'amazing', 'pleased', 'delighted'],
            "sad": ['sad', 'depressed', 'miserable', 'unhappy', 'sorrow', 'grief', 'disappointed'],
            "angry": ['angry', 'furious', 'hate', 'rage', 'mad', 'irritated', 'frustrated'],
            "contemplative": ['think', 'ponder', 'consider', 'reflect', 'meditate', 'contemplate'],
            "hopeful": ['hope', 'wish', 'dream', 'aspire', 'optimistic', 'future', 'possibility'],
            "curious": ['wonder', 'curious', 'question', 'why', 'how', 'what if', 'interesting'],
            "peaceful": ['peace', 'calm', 'tranquil', 'serene', 'quiet', 'still', 'gentle'],
            "confused": ['confused', 'unclear', 'uncertain', 'puzzled', 'bewildered', 'lost', 'unsure'],
        }

        # Count keyword matches for each mood
        mood_scores = {}
        for mood, keywords in mood_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                mood_scores[mood] = score

        # Return mood with highest score, or neutral
        if mood_scores:
            return max(mood_scores.items(), key=lambda x: x[1])[0]

        return "neutral"

    def get_mood_context_for_llm(self) -> str:
        """Get mood context for LLM prompts"""
        current_mood = self.current_emotion.name.lower()
        return f"[CURRENT_MOOD: {current_mood}]"

    def advance_frame(self):
        """Advance the animation frame with smooth mood transitions"""
        self.current_emotion = self.emotion_engine.current_emotion
        self.frame_count += 1
        if self.frame_count >= self.frames_per_emotion:
            self.frame_count = 0
            self.emotion_engine.advance_emotion()

        current_time = time.time()
        current_mood = self.current_emotion.name.lower()

        if current_time - self.last_update > 2.0:  # Check for emotion change every 2 seconds
            # Check if mood changed
            if current_mood != self.previous_mood:
                # Start transition
                self.transition_progress = 0.0
                self.previous_mood = current_mood

            self.current_emotion = self.emotion_engine.current_emotion
            self.emotion_intensity = self.emotion_engine.get_emotion_intensity()
            self.last_update = current_time

        # Advance transition progress
        if self.transition_progress < 1.0:
            self.transition_progress = min(1.0, self.transition_progress + self.transition_speed)

        # Update thought pattern if needed
        if current_time - self.last_thought_update > 0.5:  # Update thoughts every 0.5 seconds
            if not self.thought_pattern:  # If thought pattern is empty, use default
                self.thought_pattern = ["*", "**", "***", "**", "*"]
            self.thought_index = (self.thought_index + 1) % len(self.thought_pattern)
            self.last_thought_update = current_time

        # Generate new frame
        frame = self.generate_frame()
        self.frames.append(frame)

        # Keep only last 10 frames
        if len(self.frames) > 10:
            self.frames.pop(0)

        return frame
    
    def get_face(self, mood: str = "neutral") -> List[str]:
        """Get ASCII face for current mood"""
        return self.emotion_engine.faces.get(Emotion(mood), self.emotion_engine.faces[Emotion.NEUTRAL])
    
    def get_animated_face(self, mood: str = "neutral") -> List[str]:
        """Get animated face for current mood"""
        self.current_frame = (self.current_frame + 1) % 4
        return self.create_animated_face(mood, self.current_frame)
    
    def get_mood_face(self, mood: str) -> List[str]:
        """Get face for specific mood, with persona support"""
        # Try persona-specific face first if persona is set
        if self.persona and self.persona_support:
            # Try to get persona-specific mood
            persona_face = self.get_persona_face(self.persona, mood)
            if persona_face:
                return persona_face

        # Fall back to standard mood faces
        return MOOD_FACES.get(mood, MOOD_FACES["neutral"])
    
    def create_animated_face(self, mood: str, frame: int = 0) -> List[str]:
        """Create animated face for mood"""
        base_face = self.get_mood_face(mood)
        animated = []
        for line in base_face:
            if "..." in line:
                dots = "." * (frame + 1)
                animated.append(line.replace("...", dots))
            else:
                animated.append(line)
        return animated
    
    def create_mood_transition(self, from_mood: str, to_mood: str, progress: float) -> List[str]:
        """Create smooth transition between moods using global transition function"""
        return create_mood_transition(from_mood, to_mood, progress)

    def get_current_face_with_transition(self) -> List[str]:
        """Get current face with smooth transition effects"""
        current_mood = self.current_emotion.name.lower()

        # If in transition, return transition frame
        if self.transition_progress < 1.0:
            return create_mood_transition(self.previous_mood, current_mood, self.transition_progress)

        # Otherwise return animated current face
        return self.get_animated_face(current_mood)

    def get_banner(self) -> str:
        """Get appropriate banner for persona"""
        if self.persona and self.persona_support:
            try:
                return self.get_persona_banner(self.persona)
            except:
                pass
        return CYBERPUNK_BANNER

    def set_persona(self, persona: str):
        """Change the persona (subject, observer, god)"""
        self.persona = persona

    def set_mood(self, mood: str):
        """Manually set mood and trigger transition"""
        if mood != self.current_emotion.name.lower():
            self.previous_mood = self.current_emotion.name.lower()
            self.transition_progress = 0.0
            # Update emotion engine
            try:
                self.current_emotion = Emotion(mood.upper())
            except:
                pass