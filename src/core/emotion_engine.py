#!/usr/bin/env python3

import time
import random
import os
from enum import Enum
from typing import Dict, List

class Emotion(Enum):
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    SURPRISED = "surprised"
    CONFUSED = "confused"
    THINKING = "thinking"
    EXCITED = "excited"
    TIRED = "tired"
    NEUTRAL = "neutral"
    LOVE = "love"
    WORRIED = "worried"
    FOCUSED = "focused"

class EmotionEngine:
    def __init__(self):
        self.current_emotion = Emotion.NEUTRAL
        self.emotion_history = []
        self.faces = self._create_faces()
        self.emotion_intensity = 0.5  # Default intensity
    
    def _create_faces(self) -> Dict[Emotion, List[str]]:
        """Create ASCII art faces for each emotion"""
        return {
            Emotion.HAPPY: [
                "    ◕   ◕    ",
                "  ◕  ◡  ◕  ",
                "      ◡      ",
                "   \\  ___  /  ",
                "     \\___/    "
            ],
            Emotion.SAD: [
                "    ◔   ◔    ",
                "  ◔  ╥  ◔  ",
                "      ╥      ",
                "   /  ___  \\  ",
                "     /___\\    "
            ],
            Emotion.ANGRY: [
                "  ▸       ◂  ",
                " ▸  ●   ●  ◂ ",
                "      ▲      ",
                "   ╰ ███ ╯   ",
                "    GRRRR!   "
            ],
            Emotion.SURPRISED: [
                "    ○   ○    ",
                "  ○  ○  ○  ",
                "      ○      ",
                "   \\  ○  /   ",
                "     \\○/     "
            ],
            Emotion.CONFUSED: [
                "    ?   ?    ",
                "  ?  @  ?  ",
                "      ~      ",
                "   \\  ?  /   ",
                "     \\?/     "
            ],
            Emotion.THINKING: [
                "    ◐   ◑    ",
                "  ◐  ·  ◑  ",
                "      ·      ",
                "   ╰  ...  ╯ ",
                "    hmm...   "
            ],
            Emotion.EXCITED: [
                "    ★   ★    ",
                "  ★  !  ★  ",
                "      !      ",
                "   \\  !!!  / ",
                "    WOW!!!   "
            ],
            Emotion.TIRED: [
                "    ◔   ◔    ",
                "  ◔  z  ◔  ",
                "      z      ",
                "   ╰  ___  ╯ ",
                "    zzz...   "
            ],
            Emotion.NEUTRAL: [
                "    ◉   ◉    ",
                "  ◉  ◦  ◉  ",
                "      ◦      ",
                "   ╰  ___  ╯ ",
                "             "
            ],
            Emotion.LOVE: [
                "    ♥   ♥    ",
                "  ♥  ◡  ♥  ",
                "      ♥      ",
                "   \\  ♥♥♥  / ",
                "    <3<3<3   "
            ],
            Emotion.WORRIED: [
                "    ◔   ◔    ",
                "  ◔  ≈  ◔  ",
                "      ≈      ",
                "   ╰  ~~~  ╯ ",
                "    worry... "
            ],
            Emotion.FOCUSED: [
                "    ◆   ◆    ",
                "  ◆  ■  ◆  ",
                "      ■      ",
                "   ╰  ===  ╯ ",
                "   analyzing "
            ]
        }
    
    def display_emotion(self, emotion: Emotion, duration: float = 2.0, clear_screen: bool = False):
        """Display emotion with ASCII art"""
        if clear_screen:
            os.system('clear' if os.name == 'posix' else 'cls')
        
        face = self.faces.get(emotion, self.faces[Emotion.NEUTRAL])
        
        print("\n" + "="*16)
        for line in face:
            print(f"│ {line} │")
        print("="*16)
        print(f"🧠 Status: {emotion.value.capitalize()}")
        
        self.current_emotion = emotion
        self.emotion_history.append((emotion, time.time()))
        
        if duration > 0:
            time.sleep(duration)
    
    def animate_thinking(self, duration: float = 3.0):
        """Animated thinking process"""
        frames = [
            ["    ◐   ◑    ", "  ◐  ·  ◑  ", "      ·      ", "   ╰  .    ╯ ", "   thinking  "],
            ["    ◓   ◒    ", "  ◓  ·  ◒  ", "      ·      ", "   ╰  ..   ╯ ", "   thinking. "],
            ["    ◑   ◐    ", "  ◑  ·  ◐  ", "      ·      ", "   ╰  ...  ╯ ", "   thinking.."],
            ["    ◒   ◓    ", "  ◒  ·  ◓  ", "      ·      ", "   ╰   ... ╯ ", "   thinking..."]
        ]
        
        end_time = time.time() + duration
        frame_idx = 0
        
        while time.time() < end_time:
            print("\033[H\033[2J", end="")  # Clear screen
            frame = frames[frame_idx % len(frames)]
            
            print("\n" + "="*16)
            for line in frame:
                print(f"│ {line} │")
            print("="*16)
            print("🧠 Processing...")
            
            time.sleep(0.4)
            frame_idx += 1
    
    def react_to_text(self, text: str) -> Emotion:
        """Analyze text and return appropriate emotion"""
        text_lower = text.lower()
        
        emotion_keywords = {
            Emotion.HAPPY: ['happy', 'joy', 'great', 'awesome', 'wonderful', 'excellent', 'love', 'amazing'],
            Emotion.SAD: ['sad', 'sorry', 'terrible', 'awful', 'bad', 'disappointed', 'depressed'],
            Emotion.ANGRY: ['angry', 'mad', 'furious', 'hate', 'annoyed', 'frustrated', 'rage'],
            Emotion.SURPRISED: ['wow', 'amazing', 'incredible', 'unbelievable', 'shocking'],
            Emotion.CONFUSED: ['confused', 'unclear', "don't understand", 'puzzled', 'what'],
            Emotion.THINKING: ['thinking', 'consider', 'analyze', 'process', 'hmm', 'let me'],
            Emotion.EXCITED: ['excited', 'thrilled', 'enthusiastic', 'pumped', 'energetic'],
            Emotion.TIRED: ['tired', 'exhausted', 'sleepy', 'weary', 'drained'],
            Emotion.LOVE: ['love', 'adore', 'cherish', 'heart', 'romance', 'beautiful'],
            Emotion.WORRIED: ['worried', 'concerned', 'anxious', 'nervous', 'trouble'],
            Emotion.FOCUSED: ['focus', 'concentrate', 'attention', 'detail', 'precise']
        }
        
        scores = {}
        for emotion, keywords in emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                scores[emotion] = score
        
        return max(scores.items(), key=lambda x: x[1])[0] if scores else Emotion.NEUTRAL
    
    def startup_sequence(self):
        """Show startup animation"""
        sequence = [
            (Emotion.THINKING, 1.0),
            (Emotion.SURPRISED, 0.5),
            (Emotion.EXCITED, 1.0),
            (Emotion.HAPPY, 1.5)
        ]
        
        print("🧠 Brain-in-Jar Neural Link Initializing...")
        for emotion, duration in sequence:
            self.display_emotion(emotion, duration, clear_screen=True)
    
    def demo_emotions(self):
        """Demonstrate all emotions"""
        print("🎭 Emotion Engine Demo")
        for emotion in Emotion:
            print(f"\nDemonstrating: {emotion.value}")
            self.display_emotion(emotion, 1.5)
    
    def get_emotion_intensity(self) -> float:
        """Get current emotion intensity (0.0 to 1.0)"""
        # Randomly vary intensity slightly for more dynamic emotions
        base_intensity = 0.5
        variation = random.uniform(-0.2, 0.2)
        return max(0.0, min(1.0, base_intensity + variation))

if __name__ == "__main__":
    engine = EmotionEngine()
    
    print("🧠 Emotion Engine Test")
    engine.startup_sequence()
    engine.demo_emotions()
    
    # Test text reactions
    test_texts = [
        "I'm so happy today!",
        "This is confusing me.",
        "I'm thinking about this problem.",
        "Wow, that's incredible!",
        "I feel sad about this.",
        "This makes me angry!"
    ]
    
    print("\n🧠 Testing text reactions:")
    for text in test_texts:
        print(f"\nText: '{text}'")
        emotion = engine.react_to_text(text)
        engine.display_emotion(emotion, 1.0)