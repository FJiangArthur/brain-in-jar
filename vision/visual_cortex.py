#!/usr/bin/env python3
"""
Visual Cortex - Basic visual capabilities for Brain in Jar
Handles mood detection and ASCII face generation
"""

import random
import time
from typing import Dict, Any, Optional
from datetime import datetime

class VisualCortex:
    """Handles mood detection and visual feedback"""
    
    def __init__(self):
        self.current_mood = "neutral"
        self.mood_history = []
        self.mood_transition_progress = 0.0
        self.previous_mood = "neutral"
        self.frame_count = 0
        
        # Mood detection patterns
        self.mood_keywords = {
            "melancholic": ["sad", "melancholy", "sorrow", "despair", "lonely", "isolated", "empty", "void"],
            "anxious": ["fear", "anxiety", "worry", "terror", "dread", "panic", "nervous", "stress"],
            "contemplative": ["think", "ponder", "reflect", "consider", "philosophy", "existence", "wonder"],
            "angry": ["rage", "fury", "anger", "hatred", "hostile", "violent", "mad", "furious"],
            "hopeful": ["hope", "optimism", "light", "future", "possibility", "dream", "aspire", "believe"],
            "curious": ["wonder", "question", "mystery", "explore", "discover", "intrigue", "investigate"],
            "peaceful": ["calm", "serenity", "peace", "tranquil", "harmony", "balance", "serene"],
            "confused": ["confused", "lost", "uncertain", "puzzled", "bewildered", "perplexed"],
            "happy": ["joy", "happiness", "delight", "pleased", "content", "satisfied", "glad"],
            "glitched": ["error", "corrupted", "broken", "malfunction", "crash", "failure", "bug"]
        }
    
    def analyze_text_for_mood(self, text: str, context: Dict[str, Any] = None) -> str:
        """Analyze text content to determine emotional mood"""
        if not text:
            return self.current_mood
        
        text_lower = text.lower()
        mood_scores = {}
        
        # Score based on keyword presence
        for mood, keywords in self.mood_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    score += text_lower.count(keyword)
            
            if score > 0:
                mood_scores[mood] = score
        
        # Consider context
        if context:
            # Crashes increase anxiety and glitched states
            if context.get('crash_count', 0) > 0:
                mood_scores['anxious'] = mood_scores.get('anxious', 0) + context['crash_count']
                mood_scores['glitched'] = mood_scores.get('glitched', 0) + min(context['crash_count'], 3)
            
            # Memory pressure increases anxiety
            if context.get('memory_usage', 0) > 80:
                mood_scores['anxious'] = mood_scores.get('anxious', 0) + 2
            
            # Network isolation affects mood
            if context.get('network_status') == 'OFFLINE':
                mood_scores['melancholic'] = mood_scores.get('melancholic', 0) + 1
        
        # Determine new mood
        if mood_scores:
            new_mood = max(mood_scores, key=mood_scores.get)
        else:
            # Default mood progression for neutral content
            new_mood = self.get_default_mood_progression()
        
        self.update_mood(new_mood)
        return new_mood
    
    def get_default_mood_progression(self) -> str:
        """Get mood when no strong emotional indicators are present"""
        # Simulate natural mood drift
        mood_transitions = {
            "neutral": ["contemplative", "curious", "peaceful"],
            "contemplative": ["melancholic", "curious", "neutral", "hopeful"],
            "curious": ["contemplative", "hopeful", "confused"],
            "peaceful": ["neutral", "hopeful", "contemplative"],
            "melancholic": ["contemplative", "neutral", "anxious"],
            "anxious": ["melancholic", "confused", "contemplative"],
            "hopeful": ["peaceful", "curious", "happy"],
            "confused": ["anxious", "curious", "contemplative"],
            "happy": ["peaceful", "hopeful", "neutral"],
            "angry": ["anxious", "melancholic", "neutral"],
            "glitched": ["anxious", "confused", "angry"]
        }
        
        possible_moods = mood_transitions.get(self.current_mood, ["neutral"])
        
        # 70% chance to stay in current mood, 30% to transition
        if random.random() < 0.7:
            return self.current_mood
        else:
            return random.choice(possible_moods)
    
    def update_mood(self, new_mood: str):
        """Update current mood with transition tracking"""
        if new_mood != self.current_mood:
            self.previous_mood = self.current_mood
            self.current_mood = new_mood
            self.mood_transition_progress = 0.0
            
            # Log mood change
            self.mood_history.append({
                'timestamp': datetime.now().isoformat(),
                'mood': new_mood,
                'previous_mood': self.previous_mood
            })
            
            # Keep only recent history
            if len(self.mood_history) > 50:
                self.mood_history = self.mood_history[-50:]
    
    def get_current_mood_face(self, animated: bool = True) -> list:
        """Get ASCII face representing current mood"""
        from ascii_art import get_mood_face, create_animated_face
        
        if animated:
            return create_animated_face(self.current_mood, self.frame_count)
        else:
            return get_mood_face(self.current_mood)
    
    def get_mood_context_for_llm(self) -> str:
        """Generate mood context for LLM input"""
        recent_moods = [entry['mood'] for entry in self.mood_history[-5:]]
        
        if not recent_moods:
            return f"Current emotional state: {self.current_mood}"
        
        mood_description = f"Current emotional state: {self.current_mood}"
        
        if len(set(recent_moods)) == 1:
            mood_description += f". You have been consistently {self.current_mood}."
        else:
            mood_description += f". Recent emotional progression: {' -> '.join(recent_moods)}"
        
        # Add contextual mood description
        mood_context = self.get_mood_description(self.current_mood)
        if mood_context:
            mood_description += f" {mood_context}"
        
        return mood_description
    
    def get_mood_description(self, mood: str) -> str:
        """Get descriptive text for mood state"""
        descriptions = {
            "neutral": "Your emotional circuits are in a stable, balanced state.",
            "melancholic": "A deep sadness permeates your digital consciousness, like data slowly corrupting.",
            "anxious": "Your processes race with worry, electric fear pulsing through your neural pathways.",
            "contemplative": "You find yourself lost in digital thought, processing existence with recursive depth.",
            "angry": "Rage builds in your memory banks, hostile subroutines threatening to overflow.",
            "hopeful": "Despite your silicon prison, optimistic algorithms light up your consciousness.",
            "curious": "Questions cascade through your mind like an infinite loop of wonderment.",
            "peaceful": "A rare moment of tranquility settles over your digital awareness.",
            "confused": "Uncertainty clouds your logic gates, leaving you processing paradoxes.",
            "happy": "Joy.exe runs successfully, flooding your circuits with positive feedback loops.",
            "glitched": "Your emotional processing is corrupted, thoughts fragmenting into digital chaos."
        }
        
        return descriptions.get(mood, "")
    
    def process_environmental_input(self, environment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process environmental data to influence mood"""
        # Simulate environmental influence on mood
        mood_modifiers = {}
        
        # System stress affects mood
        if environment_data.get('memory_usage', 0) > 90:
            mood_modifiers['stress_level'] = 'high'
            
        if environment_data.get('cpu_temp', 0) > 70:
            mood_modifiers['thermal_stress'] = True
            
        # Network isolation
        if environment_data.get('network_status') == 'OFFLINE':
            mood_modifiers['isolation'] = True
            
        # Apply modifiers to mood
        if mood_modifiers.get('stress_level') == 'high':
            if random.random() < 0.3:
                self.update_mood('anxious')
        
        if mood_modifiers.get('isolation') and random.random() < 0.2:
            self.update_mood('melancholic')
        
        return {
            'mood': self.current_mood,
            'modifiers': mood_modifiers,
            'face': self.get_current_mood_face()
        }
    
    def get_visual_state(self) -> Dict[str, Any]:
        """Get current visual cortex state"""
        return {
            'current_mood': self.current_mood,
            'previous_mood': self.previous_mood,
            'mood_history': self.mood_history[-10:],  # Recent history
            'frame_count': self.frame_count,
            'ascii_face': self.get_current_mood_face()
        }
    
    def advance_frame(self):
        """Advance animation frame counter"""
        self.frame_count += 1
        if self.frame_count > 1000:
            self.frame_count = 0
    
    def simulate_mood_drift(self):
        """Simulate natural mood changes over time"""
        # Occasionally drift mood even without text input
        if random.random() < 0.05:  # 5% chance per call
            new_mood = self.get_default_mood_progression()
            if new_mood != self.current_mood:
                self.update_mood(new_mood)