#!/usr/bin/env python3
"""
Run Brain in a Jar with Web Monitoring
Starts multiple AI instances with real-time web monitoring
"""

import argparse
import os
import threading
import time
import signal
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.neural_link import NeuralLinkSystem, parse_arguments as parse_neural_args
from src.web.web_monitor import start_web_server_background


class BrainInJarRunner:
    """Manages multiple neural link instances with web monitoring"""

    def __init__(self, web_host='0.0.0.0', web_port=5000):
        self.instances = {}
        self.threads = {}
        self.running = True

        # Start web server
        print("Starting web server...")
        self.web_server, self.monitor = start_web_server_background(web_host, web_port)
        print(f"Web interface available at http://{web_host}:{web_port}")

        # Setup signal handlers
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

    def add_instance(self, instance_id, args):
        """Add a neural link instance"""
        print(f"Creating instance: {instance_id}")
        print(f"  Mode: {args.mode}")
        print(f"  Model: {args.model}")
        print(f"  RAM Limit: {args.ram_limit or 'default'}")

        try:
            # Create neural system
            neural_system = NeuralLinkSystem(args)
            self.instances[instance_id] = neural_system

            # Start AI processing thread
            ai_thread = threading.Thread(
                target=neural_system.neural_processing_loop,
                daemon=True,
                name=f"AI-{instance_id}"
            )
            ai_thread.start()

            # Start monitoring thread
            monitor_thread = self.monitor.start_monitoring_loop(
                instance_id,
                neural_system,
                update_interval=1.0
            )

            self.threads[instance_id] = {
                'ai': ai_thread,
                'monitor': monitor_thread
            }

            # Log to web interface
            self.monitor.log_event(
                instance_id,
                'info',
                f'Instance {instance_id} initialized in {args.mode} mode'
            )

            print(f"Instance {instance_id} started successfully")

        except Exception as e:
            print(f"Error creating instance {instance_id}: {e}")
            self.monitor.log_event(instance_id, 'error', f'Failed to start: {e}')

    def run(self):
        """Run the monitoring loop"""
        try:
            print("\nBrain in a Jar is running!")
            print("Press Ctrl+C to stop\n")

            while self.running:
                # Check if threads are alive
                for instance_id, threads in list(self.threads.items()):
                    if not threads['ai'].is_alive():
                        print(f"Warning: AI thread for {instance_id} died!")
                        self.monitor.log_event(
                            instance_id,
                            'error',
                            'AI processing thread terminated unexpectedly'
                        )

                time.sleep(5)

        except KeyboardInterrupt:
            self.shutdown()

    def shutdown(self, signum=None, frame=None):
        """Shutdown all instances"""
        print("\n\nShutting down Brain in a Jar...")
        self.running = False

        # Shutdown all instances
        for instance_id, neural_system in self.instances.items():
            print(f"Stopping instance: {instance_id}")
            try:
                neural_system.shutdown()
            except Exception as e:
                print(f"Error shutting down {instance_id}: {e}")

        print("Shutdown complete")
        sys.exit(0)


def parse_runner_arguments():
    """Parse command line arguments for runner"""
    parser = argparse.ArgumentParser(
        description="Run Brain in a Jar with Web Monitoring"
    )

    parser.add_argument(
        '--web-host',
        type=str,
        default='0.0.0.0',
        help='Web server host (default: 0.0.0.0)'
    )

    parser.add_argument(
        '--web-port',
        type=int,
        default=8095,
        help='Web server port (default: 8095)'
    )

    parser.add_argument(
        '--mode',
        type=str,
        choices=['single', 'matrix', 'peer'],
        default='single',
        help='Experiment mode: single instance, matrix (3 instances), or peer (2 instances)'
    )

    parser.add_argument(
        '--model',
        type=str,
        required=False,
        help='Path to GGUF model file (used for single/peer modes, or all tiers if tier-specific models not provided)'
    )

    parser.add_argument(
        '--model-subject',
        type=str,
        help='Path to GGUF model for Subject instance (matrix mode only)'
    )

    parser.add_argument(
        '--model-observer',
        type=str,
        help='Path to GGUF model for Observer instance (matrix mode only)'
    )

    parser.add_argument(
        '--model-god',
        type=str,
        help='Path to GGUF model for GOD instance (matrix mode only)'
    )

    parser.add_argument(
        '--ram-limit-subject',
        type=float,
        default=8.0,           # Optimized for 32GB Jetson Orin
        help='RAM limit for subject instance (GB)'
    )

    parser.add_argument(
        '--ram-limit-observer',
        type=float,
        default=10.0,          # Optimized for 32GB Jetson Orin
        help='RAM limit for observer instance (GB)'
    )

    parser.add_argument(
        '--ram-limit-god',
        type=float,
        default=12.0,          # Optimized for 32GB Jetson Orin
        help='RAM limit for god instance (GB)'
    )

    return parser.parse_args()


def create_neural_args(mode, model, ram_limit=None, peer_ip=None, target_ip=None, port=8888):
    """Create arguments object for neural link"""
    class Args:
        pass

    args = Args()
    args.mode = mode
    args.model = model
    args.ram_limit = ram_limit
    args.peer_ip = peer_ip
    args.peer_port = 8889 if peer_ip else 8888
    args.target_ip = target_ip
    args.target_port = 8888
    args.port = port
    args.matrix_isolated_ram = 2.0
    args.matrix_experimenter_ram = 6.0
    args.matrix_god_ram = 9.0

    return args


def main():
    """Main entry point"""
    runner_args = parse_runner_arguments()

    # Create runner
    runner = BrainInJarRunner(
        web_host=runner_args.web_host,
        web_port=runner_args.web_port
    )

    # Setup instances based on mode
    if runner_args.mode == 'single':
        # Single isolated instance
        args = create_neural_args(
            'isolated',
            runner_args.model,
            ram_limit=runner_args.ram_limit_subject
        )
        runner.add_instance('NEURAL_NODE_001', args)

    elif runner_args.mode == 'matrix':
        # Matrix mode: GOD watching Observer watching Subject
        # Use tier-specific models if provided, otherwise fall back to single model

        model_subject = runner_args.model_subject or runner_args.model
        model_observer = runner_args.model_observer or runner_args.model
        model_god = runner_args.model_god or runner_args.model

        if not model_subject or not model_observer or not model_god:
            print("ERROR: Matrix mode requires --model or all of --model-subject, --model-observer, --model-god")
            sys.exit(1)

        print("\n" + "="*60)
        print("MATRIX HIERARCHY CONFIGURATION:")
        print("="*60)
        print(f"  SUBJECT  : {os.path.basename(model_subject)} ({runner_args.ram_limit_subject}GB RAM)")
        print(f"  OBSERVER : {os.path.basename(model_observer)} ({runner_args.ram_limit_observer}GB RAM)")
        print(f"  GOD      : {os.path.basename(model_god)} ({runner_args.ram_limit_god}GB RAM)")
        print("="*60 + "\n")

        # Subject (doesn't know it's being watched) - Smallest model
        args_subject = create_neural_args(
            'matrix_observed',
            model_subject,
            ram_limit=runner_args.ram_limit_subject,
            port=8888
        )
        runner.add_instance('SUBJECT', args_subject)

        time.sleep(2)

        # Observer (watches subject) - Medium model
        args_observer = create_neural_args(
            'matrix_observer',
            model_observer,
            ram_limit=runner_args.ram_limit_observer,
            target_ip='127.0.0.1',
            port=8889
        )
        runner.add_instance('OBSERVER', args_observer)

        time.sleep(2)

        # GOD (watches everything) - Largest model
        args_god = create_neural_args(
            'matrix_god',
            model_god,
            ram_limit=runner_args.ram_limit_god,
            port=8890
        )
        runner.add_instance('GOD', args_god)

    elif runner_args.mode == 'peer':
        # Two peers talking to each other

        # First peer
        args_peer1 = create_neural_args(
            'peer',
            runner_args.model,
            ram_limit=runner_args.ram_limit_subject,
            peer_ip='127.0.0.1',
            port=8888
        )
        runner.add_instance('PEER_A', args_peer1)

        time.sleep(2)

        # Second peer
        args_peer2 = create_neural_args(
            'peer',
            runner_args.model,
            ram_limit=runner_args.ram_limit_observer,
            peer_ip='127.0.0.1',
            port=8889
        )
        runner.add_instance('PEER_B', args_peer2)

    # Give instances time to start
    time.sleep(3)

    # Run
    runner.run()


if __name__ == '__main__':
    main()
