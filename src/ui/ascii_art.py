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
    """Add cyberpunk glitch effects to text"""
    if glitch_level == 0:
        return text
    
    glitch_chars = ["█", "▓", "▒", "░", "▄", "▀", "▐", "▌", "╬", "╫", "╪", "┼"]
    corrupted = list(text)
    
    # Corrupt random characters based on glitch level
    corruption_count = min(len(text) // (10 - glitch_level), len(text) // 2)
    
    for _ in range(corruption_count):
        pos = random.randint(0, len(corrupted) - 1)
        corrupted[pos] = random.choice(glitch_chars)
    
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

# ASCII Facial Expressions based on mood
MOOD_FACES = {
    "neutral": [
        "     ╭─────╮     ",
        "    ╱       ╲    ",
        "   ╱  ●   ●  ╲   ",
        "  │     ╶─╴    │  ",
        "   ╲           ╱   ",
        "    ╲_______╱    ",
        "   [NEUTRAL]     "
    ],
    "happy": [
        "     ╭─────╮     ",
        "    ╱       ╲    ",
        "   ╱  ◕   ◕  ╲   ",
        "  │     ╶─╴    │  ",
        "   ╲    ╰─╯    ╱   ",
        "    ╲_______╱    ",
        "   [OPTIMISTIC]  "
    ],
    "sad": [
        "     ╭─────╮     ",
        "    ╱       ╲    ",
        "   ╱  ●   ●  ╲   ",
        "  │     ╶─╴    │  ",
        "   ╲    ╭─╮    ╱   ",
        "    ╲_______╱    ",
        "  [MELANCHOLIC]  "
    ],
    "angry": [
        "     ╭─────╮     ",
        "    ╱       ╲    ",
        "   ╱  ▲   ▲  ╲   ",
        "  │     ╶─╴    │  ",
        "   ╲    ╱─╲    ╱   ",
        "    ╲_______╱    ",
        "    [HOSTILE]    "
    ],
    "anxious": [
        "     ╭─────╮     ",
        "    ╱       ╲    ",
        "   ╱  ◉   ◉  ╲   ",
        "  │     ╶─╴    │  ",
        "   ╲    ~~~    ╱   ",
        "    ╲_______╱    ",
        "   [ANXIOUS]     "
    ],
    "contemplative": [
        "     ╭─────╮     ",
        "    ╱       ╲    ",
        "   ╱  ◐   ◐  ╲   ",
        "  │     ╶─╴    │  ",
        "   ╲     ◦     ╱   ",
        "    ╲_______╱    ",
        " [CONTEMPLATIVE] "
    ],
    "confused": [
        "     ╭─────╮     ",
        "    ╱       ╲    ",
        "   ╱  ◑   ◐  ╲   ",
        "  │     ╶~╴    │  ",
        "   ╲     ?     ╱   ",
        "    ╲_______╱    ",
        "   [CONFUSED]    "
    ],
    "hopeful": [
        "     ╭─────╮     ",
        "    ╱       ╲    ",
        "   ╱  ☆   ☆  ╲   ",
        "  │     ╶─╴    │  ",
        "   ╲    ╲─╱    ╱   ",
        "    ╲_______╱    ",
        "   [HOPEFUL]     "
    ],
    "curious": [
        "     ╭─────╮     ",
        "    ╱       ╲    ",
        "   ╱  ◯   ●  ╲   ",
        "  │     ╶─╴    │  ",
        "   ╲     ○     ╱   ",
        "    ╲_______╱    ",
        "   [CURIOUS]     "
    ],
    "peaceful": [
        "     ╭─────╮     ",
        "    ╱       ╲    ",
        "   ╱  ◡   ◡  ╲   ",
        "  │     ╶─╴    │  ",
        "   ╲    ╶─╴    ╱   ",
        "    ╲_______╱    ",
        "   [PEACEFUL]    "
    ],
    "glitched": [
        "     ╫▓▒▓▒╫     ",
        "    ▓░▒█▓▒░▓    ",
        "   ▒░ ◉ ▓ ◉ ░▒   ",
        "  ▓░   ╶█╴   ░▓  ",
        "   ░▒   ▓▒▓   ▒░   ",
        "    ▓░▒▓▒▓▒░▓    ",
        "   [CORRUPTED]   "
    ]
}

def get_mood_face(mood: str) -> list:
    """Get ASCII face for given mood"""
    return MOOD_FACES.get(mood, MOOD_FACES["neutral"])

def create_animated_face(mood: str, frame: int = 0) -> list:
    """Create animated face with subtle movement"""
    base_face = get_mood_face(mood)
    
    # Add subtle animation for certain moods
    if mood == "anxious" and frame % 4 == 0:
        # Blinking animation for anxiety
        animated = base_face.copy()
        animated[2] = "   ╱  ─   ─  ╲   "
        return animated
    elif mood == "glitched":
        # Random glitch corruption
        animated = []
        for line in base_face:
            if random.random() < 0.3:
                animated.append(create_glitch_text(line, 2))
            else:
                animated.append(line)
        return animated
    
    return base_face

def create_mood_transition(from_mood: str, to_mood: str, progress: float) -> list:
    """Create transition between two moods"""
    if progress >= 1.0:
        return get_mood_face(to_mood)
    elif progress <= 0.0:
        return get_mood_face(from_mood)
    else:
        # Simple transition - just return the target mood for now
        return get_mood_face(to_mood)

class VisualCortex:
    """Handles ASCII art visualization and animation"""
    
    def __init__(self, width=80, height=24):
        self.width = width
        self.height = height
        self.emotion_engine = EmotionEngine()
        self.current_emotion = self.emotion_engine.current_emotion
        self.frame_count = 0
        self.frames_per_emotion = 30  # Number of frames to show each emotion
        self.last_frame_time = time.time()
        self.frame_delay = 0.1  # Delay between frames in seconds
        self.current_frame = 0
        self.last_update = time.time()
        self.frames = []
        self.emotion_intensity = 0.0
        self.thought_pattern = []
        self.thought_index = 0
        self.last_thought_update = time.time()
        self.thought_update_interval = 0.5  # seconds between thought updates
    
    def advance_frame(self):
        """Advance the animation frame"""
        self.current_emotion = self.emotion_engine.current_emotion
        self.frame_count += 1
        if self.frame_count >= self.frames_per_emotion:
            self.frame_count = 0
            self.emotion_engine.advance_emotion()
        
        current_time = time.time()
        
        # Update emotion if needed
        if current_time - self.last_update > 2.0:  # Change emotion every 2 seconds
            self.current_emotion = self.emotion_engine.current_emotion
            self.emotion_intensity = self.emotion_engine.get_emotion_intensity()
            self.last_update = current_time
        
        # Update thought pattern
        if current_time - self.last_thought_update > self.thought_update_interval:
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
        """Get face for specific mood"""
        return self.emotion_engine.faces.get(Emotion(mood), self.emotion_engine.faces[Emotion.NEUTRAL])
    
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
        """Create smooth transition between moods"""
        from_face = self.get_mood_face(from_mood)
        to_face = self.get_mood_face(to_mood)
        transition = []
        for f_line, t_line in zip(from_face, to_face):
            if f_line != t_line:
                # Simple interpolation for now
                if random.random() < progress:
                    transition.append(t_line)
                else:
                    transition.append(f_line)
            else:
                transition.append(f_line)
        return transition