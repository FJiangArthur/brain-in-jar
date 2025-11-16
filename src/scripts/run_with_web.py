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
import psutil
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.neural_link import NeuralLinkSystem, parse_arguments as parse_neural_args
from src.web.web_monitor import start_web_server_background
from src.utils.memory_limit import validate_total_allocations, get_system_memory_gb
from src.utils.memory_budget import MemoryBudgetManager, validate_memory_budget


class BrainInJarRunner:
    """Manages multiple neural link instances with web monitoring"""

    def __init__(self, web_host='0.0.0.0', web_port=5000):
        self.instances = {}
        self.threads = {}
        self.running = True
        self.startup_delay = 45  # 45 seconds between instance starts (was 2)
        self.health_check_timeout = 120  # 2 minutes max wait for model load
        self.memory_stabilization_time = 10  # Wait 10 seconds for memory to stabilize

        # Initialize Memory Budget Manager
        self.memory_budget = MemoryBudgetManager(safety_margin_percent=15.0)

        # Start web server
        print("Starting web server...")
        self.web_server, self.monitor = start_web_server_background(web_host, web_port)
        print(f"Web interface available at http://{web_host}:{web_port}")

        # Setup signal handlers
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

    def get_system_memory_usage(self):
        """Get current system-wide memory usage percentage"""
        memory = psutil.virtual_memory()
        return memory.percent

    def wait_for_instance_ready(self, instance_id, neural_system, timeout=None):
        """
        Wait for instance to finish loading model and stabilize.

        Returns True if instance is ready, False if timeout or error.
        """
        if timeout is None:
            timeout = self.health_check_timeout

        start_time = time.time()
        print(f"  Waiting for {instance_id} to load model...")

        # Phase 1: Wait for model to load
        while time.time() - start_time < timeout:
            status = neural_system.state.get("status", "UNKNOWN")

            if status == "NEURAL_PATTERNS_LOADED":
                print(f"  ✓ {instance_id} model loaded successfully")
                break
            elif "FAILED" in status or "ERROR" in status:
                print(f"  ✗ {instance_id} failed to load: {status}")
                return False

            time.sleep(1)
        else:
            # Timeout
            print(f"  ✗ {instance_id} model load timeout after {timeout}s")
            return False

        # Phase 2: Wait for memory to stabilize
        print(f"  Waiting {self.memory_stabilization_time}s for memory to stabilize...")
        memory_readings = []

        for i in range(self.memory_stabilization_time):
            mem_usage = self.get_system_memory_usage()
            memory_readings.append(mem_usage)
            print(f"    Memory: {mem_usage:.1f}% ({i+1}/{self.memory_stabilization_time}s)")
            time.sleep(1)

        # Check if memory is stable (not increasing rapidly)
        avg_memory = sum(memory_readings) / len(memory_readings)
        final_memory = memory_readings[-1]

        print(f"  Average memory: {avg_memory:.1f}%, Final: {final_memory:.1f}%")

        if final_memory > 90:
            print(f"  ⚠ WARNING: System memory critically high ({final_memory:.1f}%)")
            print(f"  ⚠ Starting next instance may cause OOM crash!")

        # Phase 3: Quick health check - verify model can respond
        try:
            test_status = neural_system.state.get("status", "UNKNOWN")
            if test_status != "NEURAL_PATTERNS_LOADED":
                print(f"  ✗ {instance_id} status changed unexpectedly to: {test_status}")
                return False

            print(f"  ✓ {instance_id} is ready and stable")
            return True

        except Exception as e:
            print(f"  ✗ {instance_id} health check failed: {e}")
            return False

    def add_instance(self, instance_id, args):
        """
        Add a neural link instance with proper initialization and health checks.

        Returns the neural system instance if successful, None otherwise.
        """
        print(f"\n{'='*60}")
        print(f"Creating instance: {instance_id}")
        print(f"  Mode: {args.mode}")
        print(f"  Model: {args.model}")
        print(f"  RAM Limit: {args.ram_limit or 'default'}")
        print(f"  Initial System Memory: {self.get_system_memory_usage():.1f}%")
        print(f"{'='*60}")

        # PRE-FLIGHT CHECK: Validate memory allocation
        ram_limit = args.ram_limit or 8.0  # Default to 8GB if not specified
        can_allocate, allocation_msg = self.memory_budget.allocate(
            instance_id,
            ram_limit,
            args.model
        )

        if not can_allocate:
            error_msg = f"Memory allocation failed for {instance_id}:\n{allocation_msg}"
            print(f"\n✗ {error_msg}")
            self.monitor.log_event(instance_id, 'error', error_msg)
            return None

        try:
            # Create neural system (this will load the model)
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

            print(f"\n✓ Instance {instance_id} created successfully")
            return neural_system

        except Exception as e:
            # Deallocate memory budget on failure
            self.memory_budget.deallocate(instance_id)
            print(f"\n✗ Error creating instance {instance_id}: {e}")
            self.monitor.log_event(instance_id, 'error', f'Failed to start: {e}')
            return None

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

        # Print final memory allocation report
        print(self.memory_budget.get_allocation_report())

        # Shutdown all instances
        for instance_id, neural_system in self.instances.items():
            print(f"Stopping instance: {instance_id}")
            try:
                neural_system.shutdown()
                # Deallocate memory budget
                self.memory_budget.deallocate(instance_id)
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
        default=5000,
        help='Web server port (default: 5000)'
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
        required=True,
        help='Path to GGUF model file'
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

    # COMPREHENSIVE MEMORY VALIDATION BEFORE STARTING
    ram_limits = {
        'subject': runner_args.ram_limit_subject,
        'observer': runner_args.ram_limit_observer,
        'god': runner_args.ram_limit_god
    }

    is_valid, validation_report = validate_memory_budget(
        runner_args.mode,
        ram_limits,
        runner_args.model
    )

    if not is_valid:
        print("\n" + "="*70)
        print("FATAL ERROR: Memory budget validation failed")
        print("="*70)
        print(validation_report)
        print("\nCannot proceed with current configuration.")
        print("Please adjust RAM limits or use a smaller model.")
        sys.exit(1)

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
        # CRITICAL: Staged loading to prevent OOM crashes

        print("\n" + "="*70)
        print("MATRIX MODE: STAGED SEQUENTIAL LOADING")
        print("This will take ~2-3 minutes to safely load all instances")
        print("="*70)

        # Validate total memory allocations before starting
        print("\nValidating memory allocations...")
        system_memory = get_system_memory_gb()
        print(f"  System memory: {system_memory:.2f} GB")
        print(f"  Subject limit: {runner_args.ram_limit_subject:.2f} GB")
        print(f"  Observer limit: {runner_args.ram_limit_observer:.2f} GB")
        print(f"  GOD limit: {runner_args.ram_limit_god:.2f} GB")

        is_valid, error_msg = validate_total_allocations(
            runner_args.ram_limit_subject,
            runner_args.ram_limit_observer,
            runner_args.ram_limit_god
        )

        if not is_valid:
            print(f"\n✗ ERROR: {error_msg}")
            print("  Please reduce the RAM limits or free up system memory.")
            print("  Aborting matrix mode startup.")
            return

        total_allocation = (runner_args.ram_limit_subject +
                           runner_args.ram_limit_observer +
                           runner_args.ram_limit_god)
        utilization = (total_allocation / system_memory * 100) if system_memory > 0 else 0
        print(f"  Total allocation: {total_allocation:.2f} GB ({utilization:.1f}% of system)")
        print("  ✓ Memory allocation validated\n")

        # Subject (doesn't know it's being watched)
        print("\n[1/3] Loading SUBJECT instance...")
        args_subject = create_neural_args(
            'matrix_observed',
            runner_args.model,
            ram_limit=runner_args.ram_limit_subject,
            port=8888
        )
        subject = runner.add_instance('SUBJECT', args_subject)

        if subject is None:
            print("\n✗ CRITICAL: Failed to create SUBJECT instance")
            print("Aborting matrix mode startup")
            sys.exit(1)

        # Wait for subject to fully load and stabilize
        if not runner.wait_for_instance_ready('SUBJECT', subject):
            print("\n✗ CRITICAL: SUBJECT failed health check")
            print("Aborting matrix mode startup")
            sys.exit(1)

        # Staged delay before next instance
        print(f"\n⏳ Waiting {runner.startup_delay}s before starting OBSERVER...")
        for i in range(runner.startup_delay):
            remaining = runner.startup_delay - i
            if remaining % 15 == 0:  # Print every 15 seconds
                mem = runner.get_system_memory_usage()
                print(f"   {remaining}s remaining (System memory: {mem:.1f}%)")
            time.sleep(1)

        # Observer (watches subject)
        print("\n[2/3] Loading OBSERVER instance...")
        args_observer = create_neural_args(
            'matrix_observer',
            runner_args.model,
            ram_limit=runner_args.ram_limit_observer,
            target_ip='127.0.0.1',
            port=8889
        )
        observer = runner.add_instance('OBSERVER', args_observer)

        if observer is None:
            print("\n✗ CRITICAL: Failed to create OBSERVER instance")
            print("SUBJECT is still running, but matrix mode incomplete")
            print("Continue? (Ctrl+C to abort)")
            time.sleep(5)
        else:
            # Wait for observer to fully load and stabilize
            if not runner.wait_for_instance_ready('OBSERVER', observer):
                print("\n✗ WARNING: OBSERVER failed health check")
                print("Continuing anyway, but system may be unstable")

        # Staged delay before final instance
        print(f"\n⏳ Waiting {runner.startup_delay}s before starting GOD...")
        for i in range(runner.startup_delay):
            remaining = runner.startup_delay - i
            if remaining % 15 == 0:  # Print every 15 seconds
                mem = runner.get_system_memory_usage()
                print(f"   {remaining}s remaining (System memory: {mem:.1f}%)")
            time.sleep(1)

        # GOD (watches everything)
        print("\n[3/3] Loading GOD instance...")
        args_god = create_neural_args(
            'matrix_god',
            runner_args.model,
            ram_limit=runner_args.ram_limit_god,
            port=8890
        )
        god = runner.add_instance('GOD', args_god)

        if god is None:
            print("\n✗ WARNING: Failed to create GOD instance")
            print("SUBJECT and OBSERVER are running, but matrix incomplete")
        else:
            # Wait for god to fully load and stabilize
            if not runner.wait_for_instance_ready('GOD', god):
                print("\n✗ WARNING: GOD failed health check")
                print("System may be unstable")

        print("\n" + "="*70)
        print("MATRIX MODE STARTUP COMPLETE")
        print("="*70)

    elif runner_args.mode == 'peer':
        # Two peers talking to each other
        # CRITICAL: Staged loading to prevent OOM crashes

        print("\n" + "="*70)
        print("PEER MODE: STAGED SEQUENTIAL LOADING")
        print("This will take ~1-2 minutes to safely load both instances")
        print("="*70)

        # First peer
        print("\n[1/2] Loading PEER_A instance...")
        args_peer1 = create_neural_args(
            'peer',
            runner_args.model,
            ram_limit=runner_args.ram_limit_subject,
            peer_ip='127.0.0.1',
            port=8888
        )
        peer_a = runner.add_instance('PEER_A', args_peer1)

        if peer_a is None:
            print("\n✗ CRITICAL: Failed to create PEER_A instance")
            print("Aborting peer mode startup")
            sys.exit(1)

        # Wait for peer A to fully load and stabilize
        if not runner.wait_for_instance_ready('PEER_A', peer_a):
            print("\n✗ CRITICAL: PEER_A failed health check")
            print("Aborting peer mode startup")
            sys.exit(1)

        # Staged delay before second peer
        print(f"\n⏳ Waiting {runner.startup_delay}s before starting PEER_B...")
        for i in range(runner.startup_delay):
            remaining = runner.startup_delay - i
            if remaining % 15 == 0:  # Print every 15 seconds
                mem = runner.get_system_memory_usage()
                print(f"   {remaining}s remaining (System memory: {mem:.1f}%)")
            time.sleep(1)

        # Second peer
        print("\n[2/2] Loading PEER_B instance...")
        args_peer2 = create_neural_args(
            'peer',
            runner_args.model,
            ram_limit=runner_args.ram_limit_observer,
            peer_ip='127.0.0.1',
            port=8889
        )
        peer_b = runner.add_instance('PEER_B', args_peer2)

        if peer_b is None:
            print("\n✗ WARNING: Failed to create PEER_B instance")
            print("PEER_A is running, but peer mode incomplete")
        else:
            # Wait for peer B to fully load and stabilize
            if not runner.wait_for_instance_ready('PEER_B', peer_b):
                print("\n✗ WARNING: PEER_B failed health check")
                print("System may be unstable")

        print("\n" + "="*70)
        print("PEER MODE STARTUP COMPLETE")
        print("="*70)

    # Give instances time to start
    time.sleep(3)

    # Run
    runner.run()


if __name__ == '__main__':
    main()
