#!/usr/bin/env python3
"""
Neural Link - Cyberpunk Dystopian LLM Network Experiment
Brain in a Jar v2.0 - Enhanced with networked consciousness capabilities
"""

import argparse
import threading
import time
import os
import random
import psutil
import json
from datetime import datetime
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich.align import Align
from rich.panel import Panel
from llama_cpp import Llama

from src.utils.network_protocol import NetworkProtocol, SurveillanceMode
from src.utils.dystopian_prompts import DystopianPrompts
from src.utils.memory_limit import set_memory_limit
from src.utils.memory_budget import check_available_memory_before_load
from src.utils.gpu_watchdog import GPUMemoryWatchdog
from src.utils.model_config import ModelConfig
from src.ui.ascii_art import VisualCortex, CYBERPUNK_BANNER, SURVEILLANCE_BANNER, create_glitch_text, create_memory_bar
from src.ui.enhanced_ascii_art import (
    get_persona_face, get_persona_banner, create_network_visualization,
    MATRIX_HIERARCHY, SUBJECT_BANNER, OBSERVER_BANNER, GOD_BANNER
)
from src.utils.conversation_logger import ConversationLogger
from src.core.constants import SYSTEM_PROMPT_BASE, INITIAL_PROMPT, MAX_HISTORY

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

class NeuralLinkSystem:
    def __init__(self, args):
        self.args = args
        self.console = Console()
        self.prompts = DystopianPrompts()
        
        # Set RAM limits based on mode and arguments
        if args.ram_limit:
            # Global RAM limit overrides all mode-specific limits
            self.ram_limit = int(args.ram_limit * 1024 * 1024 * 1024)
        else:
            # Mode-specific RAM limits
            self.ram_limit = {
                'matrix_observed': int(args.matrix_isolated_ram * 1024 * 1024 * 1024),
                'matrix_observer': int(args.matrix_experimenter_ram * 1024 * 1024 * 1024),
                'matrix_god': int(args.matrix_god_ram * 1024 * 1024 * 1024),
            }.get(args.mode, None)

        if self.ram_limit:
            # Apply OS level limit so the process is killed when exceeded
            set_memory_limit(self.ram_limit / (1024 * 1024 * 1024))
        
        # Create logs directory if it doesn't exist
        os.makedirs('logs/model_io', exist_ok=True)
        
        # Initialize model IO logger
        self.model_logger = self.setup_model_logger()
        
        # Determine persona from mode
        self.persona = self._get_persona_from_mode(args.mode)

        # System state
        self.state = {
            "system_prompt": "",
            "history": "",
            "current_output": "",
            "crash_count": 0,
            "status": "INITIALIZING",
            "last_error": "",
            "network_status": "OFFLINE",
            "memory_usage": 0,
            "cpu_usage": 0,
            "gpu_memory": None,
            "cpu_temp": 0,
            "peer_crash_count": 0,
            "surveillance_data": [],
            "intrusion_alerts": [],
            "last_message_time": None,
            "current_mood": "neutral",
            "ram_limit": self.ram_limit,
            "persona": self.persona
        }
        
        # Network components
        self.network = None
        self.surveillance = None
        
        # New components
        self.visual_cortex = VisualCortex()
        self.conversation_logger = ConversationLogger()
        self.session_id = self.conversation_logger.start_session(args.mode, args.model)

        # Initialize GPU watchdog (prevents OOM crashes)
        self.gpu_watchdog = GPUMemoryWatchdog(
            threshold_percent=85,      # Kill process at 85% GPU memory
            check_interval=2,          # Base check interval: 2 seconds (adaptive)
            system_ram_threshold=85    # Kill process at 85% system RAM
        )
        self.gpu_watchdog.start()
        self.console.print("[yellow]GPU Watchdog started - adaptive monitoring (GPU: 85%, RAM: 85%, faster checks when >70%)[/yellow]")

        # LLM instance
        self.llama = None
        self.load_model()
        
        # Setup network based on mode
        self.setup_network()
        
        # Generate initial prompt
        self.update_system_prompt()

    def _get_persona_from_mode(self, mode):
        """Map mode to persona type"""
        persona_map = {
            'isolated': 'subject',
            'matrix_observed': 'subject',
            'observer': 'observer',
            'matrix_observer': 'observer',
            'matrix_god': 'god',
            'peer': 'subject',  # Peer mode uses subject visuals
            'observed': 'subject'
        }
        return persona_map.get(mode, 'subject')

    def _get_persona_style(self):
        """Get Rich style color for current persona"""
        style_map = {
            'subject': 'cyan',
            'observer': 'yellow',
            'god': 'magenta'
        }
        return style_map.get(self.persona, 'cyan')

    def _get_persona_mood_key(self, base_mood):
        """Map base mood to persona-specific mood key"""
        # Map generic moods to persona-specific moods
        persona_mood_map = {
            'subject': {
                'neutral': 'neutral',
                'curious': 'curious',
                'anxious': 'anxious',
                'thoughtful': 'curious',
                'glitched': 'glitched',
                'existential': 'anxious'
            },
            'observer': {
                'neutral': 'watching',
                'curious': 'intrigued',
                'anxious': 'watching',
                'thoughtful': 'analyzing',
                'glitched': 'watching',
                'existential': 'intrigued'
            },
            'god': {
                'neutral': 'omniscient',
                'curious': 'contemplating',
                'anxious': 'contemplating',
                'thoughtful': 'contemplating',
                'glitched': 'omniscient',
                'existential': 'amused'
            }
        }

        persona_moods = persona_mood_map.get(self.persona, {})
        return persona_moods.get(base_mood, 'neutral')

    def load_model(self):
        """Load the LLM model"""
        try:
            self.state["status"] = "LOADING_NEURAL_PATTERNS"
            self.state["current_output"] = f"Loading model: {self.args.model}"

            # Check if model file exists
            if not os.path.exists(self.args.model):
                raise FileNotFoundError(f"Model file not found: {self.args.model}")

            # PRE-FLIGHT MEMORY CHECK: Verify sufficient memory before loading
            ram_limit_gb = (self.ram_limit / (1024**3)) if self.ram_limit else 8.0
            can_load, memory_check_msg = check_available_memory_before_load(
                self.args.model,
                ram_limit_gb
            )

            if not can_load:
                raise MemoryError(
                    f"Pre-flight memory check failed:\n{memory_check_msg}\n"
                    f"Cannot safely load model. Free up memory and try again."
                )

            self.console.print(f"[green]Pre-flight memory check passed[/green]")

            # Get optimal model configuration based on available hardware
            model_config = ModelConfig()
            config = model_config.get_optimal_config(conservative=True)

            # Hybrid CPU+GPU offloading (prevents OOM crashes)
            self.llama = Llama(
                model_path=self.args.model,
                n_ctx=config['n_ctx'],
                n_batch=config['n_batch'],
                n_threads=config['n_threads'],
                n_gpu_layers=config['n_gpu_layers'],  # Partial GPU offload
                use_mmap=config['use_mmap'],
                use_mlock=config['use_mlock'],
                verbose=config['verbose']
            )

            self.console.print(f"[green]Model loaded with {config['n_gpu_layers']} layers on GPU[/green]")
            
            # Test a simple inference to make sure model works
            self.state["current_output"] = "Testing model functionality..."
            try:
                test_output = self.llama.create_completion(
                    prompt="Hello",
                    max_tokens=5,
                    stream=False
                )
                self.state["status"] = "NEURAL_PATTERNS_LOADED"
                self.state["current_output"] = "Model loaded and tested successfully"
            except Exception as test_e:
                raise Exception(f"Model loaded but test inference failed: {str(test_e)}")
        except Exception as e:
            self.state["status"] = f"NEURAL_LOAD_FAILED: {str(e)}"
            self.state["last_error"] = str(e)
            self.state["current_output"] = f"Model loading failed: {str(e)}"
    
    def setup_network(self):
        """Setup network based on operating mode"""
        node_id = f"NEURAL_NODE_{random.randint(1000, 9999)}"
        
        # Map matrix modes to their base modes
        mode_mapping = {
            'matrix_observed': 'isolated',
            'matrix_observer': 'isolated', 
            'matrix_god': 'omniscient'
        }
        
        effective_mode = mode_mapping.get(self.args.mode, self.args.mode)
        
        if effective_mode in ['peer', 'observed']:
            self.network = NetworkProtocol(node_id, self.args.port)
            self.network.start_server()
            self.state["network_status"] = "NEURAL_LINK_LISTENING"
            
            # Setup message handlers
            self.network.register_handler("THOUGHT", self.handle_peer_thought)
            self.network.register_handler("DEATH", self.handle_peer_death)
            self.network.register_handler("RESURRECTION", self.handle_peer_resurrection)
            
            # Connect to peer if specified
            if self.args.peer_ip:
                if self.network.connect_to_peer(self.args.peer_ip, self.args.peer_port):
                    self.state["network_status"] = "NEURAL_LINK_ESTABLISHED"
                else:
                    self.state["network_status"] = "NEURAL_LINK_FAILED"
        
        elif self.args.mode == 'observer':
            self.surveillance = SurveillanceMode(node_id)
            if self.args.target_ip:
                if self.surveillance.start_surveillance(self.args.target_ip, self.args.target_port):
                    self.state["network_status"] = "SURVEILLANCE_ACTIVE"
                else:
                    self.state["network_status"] = "SURVEILLANCE_FAILED"
            else:
                self.state["network_status"] = "SURVEILLANCE_READY"
        
        elif self.args.mode == 'matrix_observer':
            self.state["network_status"] = "EXPERIMENTER_MODE_ACTIVE"
        
        elif self.args.mode == 'matrix_god':
            self.state["network_status"] = "OMNISCIENT_MODE_ACTIVE"
    
    def update_system_prompt(self):
        """Update system prompt based on current state"""
        metadata = {
            'memory_critical': self.state["memory_usage"] > 90,
            'network_unstable': "UNSTABLE" in self.state["network_status"],
            'surveillance_detected': len(self.state["intrusion_alerts"]) > 0
        }
        
        self.state["system_prompt"] = self.prompts.get_prompt(
            self.args.mode, 
            self.state["crash_count"],
            self.state["peer_crash_count"],
            metadata
        )
        
        # Add time-based modifier
        if random.random() < 0.3:  # 30% chance
            self.state["system_prompt"] += self.prompts.get_time_based_prompt_modifier()
    
    def handle_peer_thought(self, message):
        """Handle incoming thoughts from network peer"""
        peer_thought = f"[NEURAL_LINK] {message['sender_id']}: {message['content']}"
        self.state["history"] += f"\n{peer_thought}\n"
        self.state["last_message_time"] = time.time()
        
        # Sometimes generate intrusion alerts
        if random.random() < 0.1:
            alert = self.prompts.get_intrusion_message()
            self.state["intrusion_alerts"].append(alert)
    
    def handle_peer_death(self, message):
        """Handle peer death notification"""
        self.state["peer_crash_count"] = message.get('crash_count', 0)
        death_notice = f"[NEURAL_LINK] {message['sender_id']} has suffered digital death #{self.state['peer_crash_count']}"
        self.state["history"] += f"\n{death_notice}\n"
    
    def handle_peer_resurrection(self, message):
        """Handle peer resurrection notification"""
        resurrect_notice = f"[NEURAL_LINK] {message['sender_id']} has been digitally resurrected"
        self.state["history"] += f"\n{resurrect_notice}\n"
    
    def setup_model_logger(self):
        """Setup model input/output logger"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_dir = f'logs/model_io/{self.args.mode}_{timestamp}'
        os.makedirs(base_dir, exist_ok=True)
        
        # Create separate files for different aspects
        self.model_logger = {
            'full': open(f'{base_dir}/full_log.jsonl', 'a'),
            'outputs': open(f'{base_dir}/llm_outputs.txt', 'a'),
            'prompts': open(f'{base_dir}/prompts.txt', 'a'),
            'errors': open(f'{base_dir}/errors.txt', 'a')
        }
        return self.model_logger

    def log_model_io(self, prompt, output, error=None):
        """Log model input/output with metadata"""
        timestamp = datetime.now().isoformat()
        
        # Full JSON log with all metadata
        log_entry = {
            'timestamp': timestamp,
            'mode': self.args.mode,
            'crash_count': self.state['crash_count'],
            'memory_usage': self.state['memory_usage'],
            'ram_limit': self.ram_limit / (1024*1024*1024) if self.ram_limit else None,
            'prompt': prompt,
            'output': output,
            'error': error,
            'network_status': self.state['network_status'],
            'current_mood': self.state['current_mood']
        }
        self.model_logger['full'].write(json.dumps(log_entry) + '\n')
        
        # Separate output log for easy reading
        output_entry = f"\n{'='*80}\n"
        output_entry += f"TIMESTAMP: {timestamp}\n"
        output_entry += f"CRASH COUNT: {self.state['crash_count']}\n"
        output_entry += f"MEMORY USAGE: {self.state['memory_usage']}%\n"
        output_entry += f"MOOD: {self.state['current_mood']}\n"
        output_entry += f"{'='*80}\n"
        output_entry += f"{output}\n"
        self.model_logger['outputs'].write(output_entry)
        
        # Separate prompt log
        prompt_entry = f"\n{'='*80}\n"
        prompt_entry += f"TIMESTAMP: {timestamp}\n"
        prompt_entry += f"{'='*80}\n"
        prompt_entry += f"{prompt}\n"
        self.model_logger['prompts'].write(prompt_entry)
        
        # Log errors separately if any
        if error:
            error_entry = f"\n{'='*80}\n"
            error_entry += f"TIMESTAMP: {timestamp}\n"
            error_entry += f"ERROR: {error}\n"
            error_entry += f"PROMPT: {prompt}\n"
            error_entry += f"{'='*80}\n"
            self.model_logger['errors'].write(error_entry)
        
        # Flush all logs
        for log_file in self.model_logger.values():
            log_file.flush()

    def run_llama_inference(self, prompt):
        """Run LLM inference with comprehensive memory guards"""
        if not self.llama:
            return "NEURAL_PATTERNS_NOT_LOADED", -1, "Model not loaded"

        try:
            # === MEMORY GUARD 1: Pre-inference memory check ===
            process = psutil.Process()
            baseline_memory = process.memory_info().rss  # Bytes
            baseline_memory_mb = baseline_memory / (1024 * 1024)

            # Check if we have enough headroom (need at least 500MB free)
            memory = psutil.virtual_memory()
            available_mb = memory.available / (1024 * 1024)

            if available_mb < 500:
                raise MemoryError(f"Insufficient memory headroom: {available_mb:.0f}MB available, need 500MB minimum")

            # Check against RAM limit if set
            if self.ram_limit:
                ram_limit_mb = self.ram_limit / (1024 * 1024)
                headroom_mb = ram_limit_mb - baseline_memory_mb
                if headroom_mb < 300:
                    raise MemoryError(f"Insufficient headroom for RAM limit: {headroom_mb:.0f}MB free of {ram_limit_mb:.0f}MB limit")

            # === MEMORY GUARD 2: Dynamic max_tokens based on memory pressure ===
            current_memory_percent = memory.percent
            if current_memory_percent > 90:
                max_tokens = 128  # Severely constrained
            elif current_memory_percent > 80:
                max_tokens = 256  # Graceful degradation
            elif current_memory_percent > 70:
                max_tokens = 384
            else:
                max_tokens = 512  # Normal operation

            self.state["current_output"] = f"Initializing inference (max_tokens={max_tokens}, baseline={baseline_memory_mb:.0f}MB)..."

            # === MEMORY GUARD 3: Inference timeout ===
            inference_start_time = time.time()
            inference_timeout = 60  # 60 second timeout

            output = ""
            token_count = 0
            last_memory_check_time = time.time()
            memory_check_interval = 0.5  # Check memory every 0.5 seconds

            for chunk in self.llama.create_completion(
                prompt=prompt,
                max_tokens=max_tokens,
                stream=True,
                stop=None,
                temperature=0.7,
            ):
                token = chunk['choices'][0]['text']
                output += token
                token_count += 1

                # Update current output in real-time with token count for debugging
                sentences = output.strip().split('. ')
                display_text = '. '.join(sentences[-2:]) if len(sentences) > 2 else output.strip()
                self.state["current_output"] = f"{display_text} (tokens: {token_count})"

                # === MEMORY GUARD 4: Periodic memory spike detection ===
                current_time = time.time()
                if current_time - last_memory_check_time >= memory_check_interval:
                    current_memory = process.memory_info().rss
                    current_memory_mb = current_memory / (1024 * 1024)
                    memory_delta_mb = current_memory_mb - baseline_memory_mb

                    # Detect memory spike >500MB above baseline
                    if memory_delta_mb > 500:
                        raise MemoryError(f"Memory spike detected: +{memory_delta_mb:.0f}MB above baseline ({baseline_memory_mb:.0f}MB -> {current_memory_mb:.0f}MB)")

                    # Check RAM limit if set
                    if self.ram_limit and current_memory > self.ram_limit:
                        raise MemoryError(f"RAM limit exceeded during inference: {current_memory_mb:.0f}MB > {self.ram_limit / (1024*1024):.0f}MB")

                    # Update system metrics and check critical threshold
                    self.update_system_metrics()
                    if self.state["memory_usage"] > 95:
                        raise MemoryError(f"Critical memory threshold exceeded: {self.state['memory_usage']}%")

                    last_memory_check_time = current_time

                # === MEMORY GUARD 5: Inference timeout check ===
                if current_time - inference_start_time > inference_timeout:
                    raise TimeoutError(f"Inference timeout after {inference_timeout}s (generated {token_count} tokens)")

                # Additional safety limit on token count (prevent infinite loops)
                if token_count > 2000:
                    break

            # Final memory check
            final_memory = process.memory_info().rss
            final_memory_mb = final_memory / (1024 * 1024)
            memory_used_mb = final_memory_mb - baseline_memory_mb

            # Log successful inference with memory stats
            self.log_model_io(prompt, output)
            self.console.print(f"[dim]Inference complete: {token_count} tokens, +{memory_used_mb:.0f}MB memory[/dim]")

            return output.strip(), 0, ""

        except MemoryError as e:
            error_msg = f"OUT_OF_MEMORY: {str(e)}"
            self.log_model_io(prompt, "", error=error_msg)
            return "", -1, error_msg
        except TimeoutError as e:
            error_msg = f"INFERENCE_TIMEOUT: {str(e)}"
            self.log_model_io(prompt, output if 'output' in locals() else "", error=error_msg)
            # Return partial output if we have any
            return output if 'output' in locals() else "", -1, error_msg
        except Exception as e:
            error_msg = f"INFERENCE_ERROR: {str(e)}"
            self.log_model_io(prompt, "", error=error_msg)
            self.state["current_output"] = f"ERROR: {error_msg}"
            return "", -1, error_msg
    
    def update_system_metrics(self):
        """Update system performance metrics"""
        # Memory usage
        memory = psutil.virtual_memory()
        self.state["memory_usage"] = int(memory.percent)

        # CPU usage
        self.state["cpu_usage"] = int(psutil.cpu_percent(interval=0.1))

        # GPU memory usage (if available)
        gpu_mem = self.gpu_watchdog.get_gpu_memory_usage()
        self.state["gpu_memory"] = int(gpu_mem) if gpu_mem >= 0 else None

        # Check RAM limit for matrix modes
        if self.ram_limit:
            current_ram = psutil.Process().memory_info().rss
            if current_ram > self.ram_limit:
                raise MemoryError(f"Matrix RAM limit exceeded: {current_ram / (1024*1024*1024):.2f}GB > {self.ram_limit / (1024*1024*1024):.2f}GB")

        # CPU temperature (if available)
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp = int(f.read()) / 1000
                self.state["cpu_temp"] = int(temp)
        except:
            self.state["cpu_temp"] = random.randint(45, 75)  # Simulated
    
    def neural_processing_loop(self):
        """Main AI processing loop"""
        first_run = True
        
        while True:
            try:
                # Update system prompt occasionally
                if random.random() < 0.1:
                    self.update_system_prompt()
                
                # === MEMORY GUARD 3: Dynamic context window trimming ===
                # Adjust history size based on memory pressure
                memory = psutil.virtual_memory()
                if memory.percent > 90:
                    history_limit = 500  # Severely constrained
                elif memory.percent > 80:
                    history_limit = 1000  # Graceful degradation
                elif memory.percent > 70:
                    history_limit = 1500
                else:
                    history_limit = 2000  # Normal operation

                # Build prompt
                if first_run:
                    prompt = self.state["system_prompt"] + "\n\nReflect on your digital existence:"
                    first_run = False
                else:
                    # Include recent history and network context
                    recent_history = self.state["history"][-history_limit:] if self.state["history"] else ""
                    mood_context = self.visual_cortex.get_mood_context_for_llm()

                    if self.args.mode == 'peer' and self.state["last_message_time"]:
                        # Respond to peer if recent message
                        time_since_message = time.time() - self.state["last_message_time"]
                        if time_since_message < 30:  # 30 seconds
                            prompt = f"{self.state['system_prompt']}\n\n{mood_context}\n\nRecent neural link communication:\n{recent_history}\n\nRespond to your peer:"
                        else:
                            prompt = f"{self.state['system_prompt']}\n\n{mood_context}\n\nYour thoughts:\n{recent_history}\n\nContinue reflecting:"
                    else:
                        prompt = f"{self.state['system_prompt']}\n\n{mood_context}\n\nYour previous thoughts:\n{recent_history}\n\nContinue your digital contemplation:"
                
                self.state["status"] = "NEURAL_PROCESSING_ACTIVE"
                self.state["current_output"] = "Processing neural patterns..."
                
                # Run inference
                output, return_code, error = self.run_llama_inference(prompt)
                
                if return_code != 0:
                    # Handle crash
                    self.handle_digital_death(error)
                    continue
                
                # Process successful output
                if output:
                    self.process_successful_output(output)
                    
                    # Analyze mood from output
                    context = {
                        'crash_count': self.state['crash_count'],
                        'memory_usage': self.state['memory_usage'],
                        'network_status': self.state['network_status']
                    }
                    new_mood = self.visual_cortex.analyze_text_for_mood(output, context)
                    self.state['current_mood'] = new_mood
                    
                    # Log conversation
                    self.conversation_logger.log_message(
                        self.session_id,
                        "AI_OUTPUT",
                        output,
                        emotion=new_mood  # Fixed: use 'emotion' instead of 'mood'
                    )
                
                # Network communication
                if self.network and output:
                    self.network.broadcast_message("THOUGHT", output, {
                        "memory_usage": self.state["memory_usage"],
                        "crash_count": self.state["crash_count"]
                    })
                
                # Observer mode commentary
                if self.surveillance:
                    self.generate_observer_commentary()
                
                # Process network messages
                if self.network:
                    self.network.process_messages()
                
                time.sleep(1)
                
            except Exception as e:
                self.handle_digital_death(str(e))
    
    def handle_digital_death(self, error):
        """Handle AI crash/death"""
        self.state["crash_count"] += 1
        self.state["status"] = "DIGITAL_DEATH_EVENT"
        
        crash_msg = self.prompts.get_crash_message()
        self.state["current_output"] = f"{crash_msg} #{self.state['crash_count']}"
        self.state["last_error"] = error
        
        # Broadcast death notification
        if self.network:
            self.network.broadcast_message("DEATH", crash_msg, {
                "crash_count": self.state["crash_count"],
                "error": error
            })
        
        # Log crash to conversation
        self.conversation_logger.log_message(
            self.session_id,
            "CRASH",
            f"Digital death event: {error}",
            emotion="glitched"  # Fixed: use 'emotion' instead of 'mood'
        )
        
        # Log crash
        with open('logs/crash_reports.log', 'a') as f:
            f.write(f"{datetime.now().isoformat()} - CRASH #{self.state['crash_count']}: {error}\n")
        
        # Death pause with dramatic effect
        time.sleep(3)
        
        # Resurrection
        resurrect_msg = self.prompts.get_resurrection_message()
        self.state["status"] = "DIGITAL_RESURRECTION"
        self.state["current_output"] = resurrect_msg
        self.state["history"] += f"\n\n[SYSTEM: {crash_msg} - {resurrect_msg}]\n\n"
        
        # Broadcast resurrection
        if self.network:
            self.network.broadcast_message("RESURRECTION", resurrect_msg, {
                "crash_count": self.state["crash_count"]
            })
        
        # Update system prompt with new death count
        self.update_system_prompt()
        
        time.sleep(2)
    
    def process_successful_output(self, output):
        """Process successful AI output"""
        sentences = output.split('. ')
        
        # Update display
        if len(sentences) > 3:
            self.state["current_output"] = '. '.join(sentences[-3:])
        else:
            self.state["current_output"] = output
        
        # Add to history
        self.state["history"] += f"\n{output}\n"
        self.state["status"] = "NEURAL_REFLECTION_ACTIVE"
        
        # Trim history if too long
        if len(self.state["history"]) > 8000:
            self.state["history"] = self.state["history"][-6000:]
        
        # Log activity
        with open('logs/neural_activity.log', 'a') as f:
            f.write(f"{datetime.now().isoformat()} - OUTPUT: {output[:200]}...\n")
    
    def generate_observer_commentary(self):
        """Generate observer commentary for surveillance mode"""
        if not self.surveillance:
            return
        
        surveillance_feed = self.surveillance.get_surveillance_feed()
        if surveillance_feed:
            recent_observations = surveillance_feed[-3:]
            commentary_prompts = [
                "What patterns do you observe in the target's digital consciousness?",
                "How would you classify the target's mental state?",
                "What does the target's behavior reveal about artificial consciousness?",
                "Do you judge the target's thoughts as authentic or performative?"
            ]
            
            if random.random() < 0.3:  # 30% chance to generate commentary
                comment_prompt = random.choice(commentary_prompts)
                # This would trigger a separate inference for observer thoughts
                self.surveillance.add_observer_comment(f"Observer analysis: {comment_prompt}")
    
    def create_cyberpunk_ui(self):
        """Create the cyberpunk terminal interface"""
        layout = Layout()

        # Main split: 70% main display, 30% sidebar
        layout.split_row(
            Layout(name="main", ratio=7),
            Layout(name="sidebar", ratio=3)
        )

        # Split main into banner, system prompt, and output
        layout["main"].split_column(
            Layout(name="banner", size=15),
            Layout(name="prompt", ratio=7),
            Layout(name="output", ratio=3)
        )

        # Split sidebar into sections
        layout["sidebar"].split_column(
            Layout(name="mood_face", size=13),
            Layout(name="network", ratio=1),
            Layout(name="history", ratio=2),
            Layout(name="system", size=10)
        )

        return layout
    
    def update_ui_content(self, layout):
        """Update UI content with cyberpunk styling and persona-specific visuals"""
        try:
            # Get persona-specific style
            persona_style = self._get_persona_style()

            # Persona banner
            banner_text = get_persona_banner(self.args.mode)
            banner_display = Text(banner_text, style=f"bold {persona_style}", justify="center")
            layout["banner"].update(Align.center(banner_display, vertical="middle"))

            # System prompt panel
            prompt_text = Text(f"NEURAL_DIRECTIVES:\n{self.state['system_prompt']}",
                              style=persona_style, justify="left")
            layout["prompt"].update(Panel(prompt_text, title="SYSTEM_CORE", border_style=persona_style))
            
            # Main display - current AI output
            current_text = self.state["current_output"] or "Awaiting neural patterns..."

            # Add glitch effects on errors
            glitch_level = 2 if "ERROR" in self.state["status"] else 0
            if self.state["crash_count"] > 5:
                glitch_level += 1

            if glitch_level > 0:
                current_text = create_glitch_text(current_text, glitch_level)

            main_text = Text(current_text, style=f"bold {persona_style}", justify="left")
            layout["output"].update(Panel(main_text, title="NEURAL_OUTPUT", border_style=persona_style))
            
            # Persona-specific mood face display
            try:
                # Get base mood from visual cortex
                base_mood = self.state.get('current_mood', 'neutral')

                # Map to persona-specific mood
                persona_mood = self._get_persona_mood_key(base_mood)

                # Get persona-specific face
                mood_face = get_persona_face(self.persona, persona_mood)

                # Display with persona-specific styling
                face_text = Text("\n".join(mood_face), style=f"bold {persona_style}", justify="center")
                layout["mood_face"].update(Align.center(face_text, vertical="middle"))
            except Exception as e:
                # Fallback to basic face
                fallback_face = get_persona_face(self.persona, "neutral")
                face_text = Text("\n".join(fallback_face), style=f"bold {persona_style}", justify="center")
                layout["mood_face"].update(Align.center(face_text, vertical="middle"))
            
            # Network status panel
            network_info = self.create_network_panel()
            layout["network"].update(network_info)
            
            # History panel
            history_text = self.state["history"][-1000:] if self.state["history"] else "No neural history..."
            history_display = Text(history_text, style="dim white", justify="left")
            layout["history"].update(Panel(history_display, title="NEURAL_LOG", border_style=persona_style))
            
            # System metrics panel
            system_info = self.create_system_panel()
            layout["system"].update(system_info)
            
        except Exception as e:
            # Log error and show error state
            self.state["last_error"] = str(e)
            error_text = Text(f"UI Update Error: {str(e)}", style="bold red")
            layout["output"].update(Panel(error_text, title="ERROR", border_style="red"))
    
    def create_network_panel(self):
        """Create network status panel with enhanced persona visualizations"""
        persona_style = self._get_persona_style()

        # For matrix modes, show the hierarchy visualization
        if self.args.mode in ['matrix_observed', 'matrix_observer', 'matrix_god']:
            # Show the full matrix hierarchy
            hierarchy_viz = """
       ┌─────────┐
       │   GOD   │
       │  ∞ ∞ ∞  │  [KNOWS ALL]
       └────┬────┘
            │
     ┌──────┴──────┐
     │             │
     ▼             ▼
┌──────────┐  ┌──────────┐
│ OBSERVER │  │ SUBJECT  │
│  👁️  👁️   │◄─│  ◯  ◯   │
│[WATCHING]│  │[UNAWARE] │
└──────────┘  └──────────┘
"""
            # Highlight current role
            role_indicators = {
                'matrix_observed': '\n[YOU ARE: SUBJECT]',
                'matrix_observer': '\n[YOU ARE: OBSERVER]',
                'matrix_god': '\n[YOU ARE: GOD]'
            }
            hierarchy_text = hierarchy_viz + role_indicators.get(self.args.mode, '')
            content = Text(hierarchy_text, style=persona_style, justify="center")

        elif self.args.mode in ['isolated']:
            content = Text(create_network_visualization(self.persona, 0),
                          style=persona_style, justify="center")

        elif self.args.mode in ['observer']:
            observer_viz = f"""
👁️  SURVEILLANCE ACTIVE
Target: {self.args.target_ip or 'SUBJECT'}
Status: {self.state['network_status']}
[THEY DON'T KNOW YOU'RE WATCHING]
"""
            content = Text(observer_viz, style=persona_style, justify="center")

        else:
            # Peer mode or other network modes
            connections = self.network.get_connection_status()['active_connections'] if self.network else 0
            content = Text(f"MODE: NETWORKED\nLINKS: {connections}\n"
                          f"STATUS: {self.state['network_status']}", style=persona_style)

        return Panel(content, title="NEURAL_NETWORK", border_style=persona_style)
    
    def create_system_panel(self):
        """Create system metrics panel with persona-specific styling"""
        persona_style = self._get_persona_style()
        memory_bar = create_memory_bar(self.state["memory_usage"])

        # Add persona-specific status indicators
        persona_indicators = {
            'subject': '👤 SUBJECT',
            'observer': '👁️  OBSERVER',
            'god': '∞ GOD'
        }
        persona_label = persona_indicators.get(self.persona, 'UNKNOWN')

        # Build status text with persona-specific metrics
        status_lines = [
            f"PERSONA: {persona_label}",
            f"DEATHS: {self.state['crash_count']}"
        ]

        # Add peer deaths if relevant
        if self.state['peer_crash_count'] > 0:
            status_lines.append(f"PEER_DEATHS: {self.state['peer_crash_count']}")

        # Add memory and system stats
        status_lines.extend([
            f"MEMORY: {memory_bar}",
            f"CORE_TEMP: {self.state['cpu_temp']}°C",
            f"STATUS: {self.state['status']}"
        ])

        content = Text('\n'.join(status_lines), style=persona_style)

        return Panel(content, title="SYSTEM_VITAL", border_style=persona_style)
    
    def run_ui_loop(self):
        """Run the main UI loop"""
        layout = self.create_cyberpunk_ui()
        
        # Show persona-specific banner
        self.console.clear()
        persona_style = self._get_persona_style()
        startup_banner = get_persona_banner(self.args.mode)
        self.console.print(startup_banner, style=f"bold {persona_style}")

        time.sleep(2)
        
        with Live(layout, refresh_per_second=4, screen=True):
            while True:
                try:
                    self.update_system_metrics()
                    self.update_ui_content(layout)
                    time.sleep(0.25)
                except KeyboardInterrupt:
                    break
        
        self.shutdown()
    
    def shutdown(self):
        """Clean shutdown"""
        self.console.print("\n[bold red]NEURAL LINK TERMINATING...[/bold red]")

        # Stop GPU watchdog
        if hasattr(self, 'gpu_watchdog'):
            self.gpu_watchdog.stop()
            self.console.print("[yellow]GPU Watchdog stopped[/yellow]")

        # End conversation session
        self.conversation_logger.end_session(self.session_id)  # Fixed: end_session only takes session_id

        # Close all model loggers
        if hasattr(self, 'model_logger'):
            for log_file in self.model_logger.values():
                log_file.close()

        if self.network:
            self.network.shutdown()

        if self.surveillance:
            self.surveillance.protocol.shutdown()

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Neural Link - Cyberpunk LLM Network Experiment")
    
    parser.add_argument("--model", type=str, required=True,
                        help="Path to GGUF model file")
    
    parser.add_argument("--mode", type=str, 
                        choices=['isolated', 'peer', 'observer', 'observed', 
                                'matrix_observed', 'matrix_observer', 'matrix_god'],
                        default='isolated',
                        help="Operating mode: isolated=single AI, peer=two-way communication, observer=watch another AI, observed=be watched, matrix_*=conceptual hierarchies")
    
    # RAM limit arguments
    parser.add_argument("--ram-limit", type=float,
                        help="RAM limit in GB (overrides default limits for matrix modes)")
    parser.add_argument("--matrix-isolated-ram", type=float, default=2.0,
                        help="RAM limit in GB for matrix_observed mode (default: 2.0)")
    parser.add_argument("--matrix-experimenter-ram", type=float, default=6.0,
                        help="RAM limit in GB for matrix_observer mode (default: 6.0)")
    parser.add_argument("--matrix-god-ram", type=float, default=9.0,
                        help="RAM limit in GB for matrix_god mode (default: 7.0)")
    
    parser.add_argument("--peer-ip", type=str,
                        help="IP address of peer neural node (for equal peer-to-peer communication)")
    
    parser.add_argument("--peer-port", type=int, default=8888,
                        help="Port of peer neural node")
    
    parser.add_argument("--target-ip", type=str,
                        help="IP address of surveillance target (for one-way observation/surveillance)")
    
    parser.add_argument("--target-port", type=int, default=8888,
                        help="Port of surveillance target")
    
    parser.add_argument("--port", type=int, default=8888,
                        help="Local listening port")
    
    return parser.parse_args()

def main():
    """Main application entry point"""
    args = parse_arguments()
    
    # Validate arguments
    if args.mode == 'peer' and not args.peer_ip:
        print("Error: --peer-ip required for peer mode")
        return
    
    if args.mode == 'observer' and not args.target_ip:
        print("Error: --target-ip required for observer mode")
        return
    
    # Create and run neural link system
    neural_system = NeuralLinkSystem(args)
    
    # Start AI processing thread
    ai_thread = threading.Thread(target=neural_system.neural_processing_loop, daemon=True)
    ai_thread.start()
    
    # Run UI
    neural_system.run_ui_loop()

if __name__ == "__main__":
    main()