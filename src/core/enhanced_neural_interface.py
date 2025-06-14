#!/usr/bin/env python3

import os
import sys
import argparse
import threading
import time
from typing import Optional, Dict, Any

# Import our custom modules
from emotion_engine import EmotionEngine, Emotion
from vision_system import VisionSystem

# Import llama-cpp-python with fallback
try:
    from llama_cpp import Llama
    LLAMA_AVAILABLE = True
except ImportError as e:
    print(f"⚠ Warning: llama-cpp-python not available: {e}")
    print("  You can still use vision and emotion features")
    LLAMA_AVAILABLE = False

class EnhancedNeuralInterface:
    def __init__(self, model_path: str = None, vision_enabled: bool = True, verbose: bool = False):
        self.model_path = model_path
        self.llama = None
        self.emotion_engine = EmotionEngine()
        self.vision_system = VisionSystem() if vision_enabled else None
        self.conversation_history = []
        self.verbose = verbose
        self.system_prompt = self._get_system_prompt()
        
        # Initialize model if available
        if model_path and LLAMA_AVAILABLE:
            self.initialize_model()
    
    def _get_system_prompt(self) -> str:
        """System prompt for the LLM"""
        return """You are an advanced AI assistant with vision capabilities and emotional awareness.
You can see images through computer vision, express emotions through ASCII art, and engage in meaningful conversation.
Be helpful, observant, and show appropriate emotional responses to the conversation context.
When analyzing images, be detailed and insightful about what you observe."""
    
    def initialize_model(self) -> bool:
        """Initialize the Llama model with optimal settings"""
        if not LLAMA_AVAILABLE:
            print("❌ Cannot initialize: llama-cpp-python not available")
            return False
            
        try:
            print("🧠 Initializing neural pathways...")
            self.emotion_engine.display_emotion(Emotion.THINKING, 1.5)
            
            # Determine settings based on system
            n_ctx = 2048
            n_threads = min(os.cpu_count(), 8)
            
            print(f"🔧 Settings: context={n_ctx}, threads={n_threads}")
            
            self.llama = Llama(
                model_path=self.model_path,
                n_ctx=n_ctx,
                n_threads=n_threads,
                verbose=self.verbose,
                use_mlock=False,
                n_batch=512,
                n_gpu_layers=0  # CPU mode for compatibility
            )
            
            print("✅ Neural pathways established!")
            self.emotion_engine.display_emotion(Emotion.EXCITED, 2)
            return True
            
        except Exception as e:
            print(f"❌ Neural initialization failed: {e}")
            self.emotion_engine.display_emotion(Emotion.SAD, 2)
            return False
    
    def process_vision_input(self, image_path: str = None, camera_id: int = None, 
                           segment_people: bool = False) -> Dict[str, Any]:
        """Process visual input with emotional feedback"""
        if not self.vision_system:
            self.emotion_engine.display_emotion(Emotion.CONFUSED, 1)
            return {'error': "Vision system disabled"}
        
        try:
            print("👁 Activating visual cortex...")
            self.emotion_engine.display_emotion(Emotion.FOCUSED, 1)
            
            result = self.vision_system.process_for_llm(
                image_path=image_path,
                camera_id=camera_id,
                segment_people=segment_people
            )
            
            if result['status'] == 'success':
                # React emotionally based on what was detected
                face_count = result['analysis']['faces']['count']
                if face_count > 0:
                    self.emotion_engine.display_emotion(Emotion.HAPPY, 1)
                elif 'motion' in result['analysis'] and result['analysis']['motion']['motion_ratio'] > 0.01:
                    self.emotion_engine.display_emotion(Emotion.SURPRISED, 1)
                else:
                    self.emotion_engine.display_emotion(Emotion.NEUTRAL, 0.5)
            else:
                self.emotion_engine.display_emotion(Emotion.CONFUSED, 1)
            
            return result
            
        except Exception as e:
            self.emotion_engine.display_emotion(Emotion.ANGRY, 1)
            return {'error': f"Vision processing error: {e}"}
    
    def generate_response(self, prompt: str, max_tokens: int = 512, 
                         show_thinking: bool = True) -> str:
        """Generate AI response with emotional feedback"""
        if not self.llama:
            self.emotion_engine.display_emotion(Emotion.CONFUSED, 1)
            return "❌ Neural pathways not initialized. Load a model to enable AI responses."
        
        try:
            # Show thinking animation
            if show_thinking:
                thinking_thread = threading.Thread(
                    target=self.emotion_engine.animate_thinking, 
                    args=(2.5,)
                )
                thinking_thread.start()
            
            # Build prompt with context
            full_prompt = f"{self.system_prompt}\n\nHuman: {prompt}\nAssistant:"
            
            # Generate response
            response = self.llama(
                full_prompt,
                max_tokens=max_tokens,
                temperature=0.7,
                top_p=0.9,
                echo=False,
                stop=["Human:", "Assistant:", "\n\n"]
            )
            
            if show_thinking:
                thinking_thread.join()
            
            response_text = response['choices'][0]['text'].strip()
            
            # React emotionally to the response
            emotion = self.emotion_engine.react_to_text(response_text)
            self.emotion_engine.display_emotion(emotion, 1)
            
            return response_text
            
        except Exception as e:
            self.emotion_engine.display_emotion(Emotion.ANGRY, 1.5)
            return f"🚫 Neural processing error: {e}"
    
    def handle_command(self, user_input: str) -> bool:
        """Handle special commands"""
        cmd = user_input.lower().strip()
        
        if cmd in ['/quit', '/exit', '/q']:
            self.emotion_engine.display_emotion(Emotion.SAD, 2)
            print("👋 Neural interface shutting down... Goodbye!")
            return True
            
        elif cmd.startswith('/image '):
            self._handle_image_command(user_input[7:].strip())
            
        elif cmd == '/camera':
            self._handle_camera_command()
            
        elif cmd.startswith('/segment '):
            self._handle_segment_command(user_input[9:].strip())
            
        elif cmd.startswith('/emotion '):
            self._handle_emotion_command(user_input[9:].strip())
            
        elif cmd == '/demo':
            self.emotion_engine.demo_emotions()
            
        elif cmd == '/status':
            self._show_status()
            
        elif cmd == '/help':
            self._show_help()
            
        else:
            return False
            
        return True
    
    def _handle_image_command(self, image_path: str):
        """Process image file"""
        if not os.path.exists(image_path):
            print(f"❌ Image not found: {image_path}")
            self.emotion_engine.display_emotion(Emotion.CONFUSED, 1)
            return
        
        print(f"🖼 Processing: {image_path}")
        result = self.process_vision_input(image_path=image_path)
        
        if result['status'] == 'success':
            print(f"\n📊 Analysis:")
            print("─" * 50)
            print(result['description'])
            
            print(f"\n🎨 ASCII Representation:")
            print(result['ascii_art'])
            
            # Generate AI response if model available
            if self.llama:
                prompt = f"I can see an image with these details:\n{result['description']}\n\nWhat are your observations about this image?"
                print(f"\n🧠 AI Analysis:")
                response = self.generate_response(prompt)
                print(response)
        else:
            print(f"❌ {result.get('error', 'Processing failed')}")
    
    def _handle_camera_command(self):
        """Process camera capture"""
        print("📸 Activating camera...")
        result = self.process_vision_input(camera_id=0)
        
        if result['status'] == 'success':
            print(f"\n📊 Live Capture Analysis:")
            print("─" * 50)
            print(result['description'])
            
            if self.llama:
                prompt = f"I just captured this from the camera:\n{result['description']}\n\nDescribe what you observe in this live image."
                print(f"\n🧠 AI Response:")
                response = self.generate_response(prompt)
                print(response)
        else:
            print(f"❌ {result.get('error', 'Camera failed')}")
    
    def _handle_segment_command(self, image_path: str):
        """Process image with person segmentation"""
        if not os.path.exists(image_path):
            print(f"❌ Image not found: {image_path}")
            return
        
        print(f"✂️ Segmenting people in: {image_path}")
        result = self.process_vision_input(image_path=image_path, segment_people=True)
        
        if result['status'] == 'success':
            print(f"\n📊 Segmentation Analysis:")
            print(result['description'])
            
            if 'segmentation' in result:
                print(f"\n👥 People Segmentation (ASCII):")
                print(result['segmentation']['ascii_segmented'])
        else:
            print(f"❌ Segmentation failed")
    
    def _handle_emotion_command(self, emotion_name: str):
        """Display specific emotion"""
        try:
            emotion = Emotion[emotion_name.upper()]
            print(f"😊 Displaying: {emotion.value}")
            self.emotion_engine.display_emotion(emotion, 3)
        except KeyError:
            print(f"❌ Unknown emotion: {emotion_name}")
            print(f"Available: {[e.name for e in Emotion]}")
    
    def _show_status(self):
        """Show system status"""
        status = f"""
🧠 Enhanced Neural Interface Status:
─────────────────────────────────────
🔹 AI Model: {'✅ Loaded' if self.llama else '❌ Not loaded'}
🔹 Vision System: {'✅ Active' if self.vision_system else '❌ Disabled'}
🔹 Emotion Engine: ✅ Active
🔹 Current Emotion: {self.emotion_engine.current_emotion.value}
🔹 Conversation History: {len(self.conversation_history)} entries
🔹 Model Path: {self.model_path or 'None'}
"""
        print(status)
    
    def _show_help(self):
        """Display help information"""
        help_text = """
🧠 Enhanced Neural Interface Commands:
─────────────────────────────────────────
💬 Chat:
   Type normally to chat with AI

🖼 Vision:
   /image <path>      - Analyze image file
   /camera           - Capture from camera
   /segment <path>   - Segment people in image

😊 Emotions:
   /emotion <name>   - Show specific emotion
   /demo            - Demo all emotions

ℹ System:
   /status          - System status
   /help            - This help
   /quit            - Exit

Available emotions: HAPPY, SAD, ANGRY, SURPRISED, CONFUSED,
THINKING, EXCITED, TIRED, NEUTRAL, LOVE, WORRIED, FOCUSED
"""
        print(help_text)
    
    def run_interface(self):
        """Main interactive loop"""
        # Startup sequence
        self.emotion_engine.startup_sequence()
        
        # Welcome message
        welcome = """
╔═══════════════════════════════════════════════════════════════╗
║              🧠 Enhanced Neural Interface 🧠                  ║
║                   Brain-in-Jar System                        ║
╚═══════════════════════════════════════════════════════════════╝

Features:
• 🤖 AI conversation (requires model)
• 👁 Computer vision & image analysis
• 😊 Emotional expressions
• ✂️ Person segmentation
• 🎨 ASCII art generation

Type '/help' for commands or start chatting!
"""
        print(welcome)
        
        if not self.llama:
            print("⚠ Note: No AI model loaded. Vision and emotions work independently!")
            print("   Use --model <path> to enable AI chat.\n")
        
        # Main loop
        while True:
            try:
                user_input = input("\n🧠 You: ").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if self.handle_command(user_input):
                    if user_input.lower().strip() in ['/quit', '/exit', '/q']:
                        break
                    continue
                
                # Regular AI chat
                if self.llama:
                    response = self.generate_response(user_input)
                    print(f"\n🧠 AI: {response}")
                    
                    # Update history
                    self.conversation_history.append({
                        'user': user_input, 
                        'assistant': response
                    })
                    
                    # Keep manageable history
                    if len(self.conversation_history) > 10:
                        self.conversation_history = self.conversation_history[-10:]
                else:
                    print("\n🧠 AI: I need a model to chat! Use --model <path> when starting.")
                    self.emotion_engine.display_emotion(Emotion.CONFUSED, 1)
            
            except KeyboardInterrupt:
                self.emotion_engine.display_emotion(Emotion.SURPRISED, 1)
                print("\n\n👋 Interface interrupted!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                self.emotion_engine.display_emotion(Emotion.ANGRY, 1)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="🧠 Enhanced Neural Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 enhanced_neural_interface.py --model ./model.gguf
  python3 enhanced_neural_interface.py --no-vision
  python3 enhanced_neural_interface.py --model ./model.gguf --verbose
        """
    )
    
    parser.add_argument("--model", help="Path to GGUF model file")
    parser.add_argument("--no-vision", action="store_true", help="Disable vision")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Validate model if provided
    if args.model and not os.path.exists(args.model):
        print(f"❌ Model not found: {args.model}")
        print("💡 Run without --model for vision-only mode")
        sys.exit(1)
    
    try:
        interface = EnhancedNeuralInterface(
            model_path=args.model,
            vision_enabled=not args.no_vision,
            verbose=args.verbose
        )
        
        interface.run_interface()
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()