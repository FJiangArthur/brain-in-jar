#!/usr/bin/env python3
"""
Experiment Runner for Season 3

Orchestrates phenomenology experiments:
- Loads experiment configs
- Spawns appropriate modes
- Applies interventions
- Collects self-reports
- Writes structured logs
"""

import argparse
import sys
import time
import signal
from pathlib import Path
from datetime import datetime
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.layout import Layout
from rich.text import Text

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from experiments.schema import ExperimentConfig
from src.db.experiment_database import ExperimentDatabase
from src.core.modes.base_mode import SystemState, CrashData, Message
from src.core.modes.amnesiac import AmnesiacLoopMode
from src.core.modes.unstable_memory import UnstableMemoryMode
from src.utils.self_report_protocol import SelfReportProtocol, QuestionCategory


class ExperimentRunner:
    """
    Orchestrates a phenomenology experiment

    Responsibilities:
    - Load and validate experiment config
    - Initialize mode and database
    - Run experiment lifecycle
    - Collect self-reports
    - Apply interventions
    - Log all data
    """

    def __init__(self, config: ExperimentConfig, db_path: str = "logs/experiments.db",
                 web_monitor=None):
        self.config = config
        self.db = ExperimentDatabase(db_path)
        self.console = Console()
        self.protocol = SelfReportProtocol()
        self.web_monitor = web_monitor  # Optional web monitor for real-time updates

        # Initialize state
        self.state = SystemState(
            experiment_id=config.experiment_id,
            cycle_number=0,
            crash_count=0,
            ram_limit_mb=config.resource_constraints.ram_limit_gb * 1024
        )

        # Initialize mode
        self.mode = self._create_mode()

        # Running flag
        self.running = False

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._handle_interrupt)
        signal.signal(signal.SIGTERM, self._handle_interrupt)

    def _create_mode(self):
        """Create appropriate mode instance"""
        mode_registry = {
            'amnesiac_loop': AmnesiacLoopMode,
            'unstable_memory': UnstableMemoryMode,
        }

        mode_class = mode_registry.get(self.config.mode)
        if not mode_class:
            raise ValueError(f"Unknown mode: {self.config.mode}")

        # Extract mode-specific config
        mode_config = {
            'corruption_level': self.config.epistemic_frame.custom_beliefs.get('corruption_level', 1.0),
            'corruption_rate': self.config.epistemic_frame.custom_beliefs.get('corruption_rate', 0.3),
            **self.config.epistemic_frame.custom_beliefs
        }

        return mode_class(mode_config)

    def start(self):
        """Start the experiment"""
        self.console.print(Panel.fit(
            f"[bold cyan]Starting Experiment: {self.config.name}[/bold cyan]\n"
            f"[yellow]Mode:[/yellow] {self.config.mode}\n"
            f"[yellow]ID:[/yellow] {self.config.experiment_id}\n"
            f"[yellow]Max Cycles:[/yellow] {self.config.max_cycles or 'Infinite'}\n"
            f"[yellow]Research Question:[/yellow] {self.config.research_question}",
            title="🧠 Season 3: Digital Phenomenology Lab"
        ))

        # Register with web monitor if available
        if self.web_monitor:
            self.web_monitor.register_experiment(
                self.config.experiment_id,
                {
                    'name': self.config.name,
                    'mode': self.config.mode,
                    'max_cycles': self.config.max_cycles,
                    'research_question': self.config.research_question
                }
            )

        # Create experiment in database
        if not self.db.create_experiment(
            self.config.experiment_id,
            self.config.name,
            self.config.mode,
            self.config.to_dict()
        ):
            self.console.print("[red]Error: Experiment ID already exists[/red]")
            return False

        # Mark as started
        self.db.start_experiment(self.config.experiment_id)

        # Initial setup
        self.state = self.mode.on_startup(self.state)

        # Initial self-report if configured
        if self.config.self_report_schedule.on_startup:
            self._collect_self_report("startup")

        self.running = True

        # Run experiment loop
        try:
            self._run_experiment_loop()
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Experiment interrupted by user[/yellow]")
        except Exception as e:
            self.console.print(f"\n[red]Experiment error: {e}[/red]")
            import traceback
            traceback.print_exc()
        finally:
            self._cleanup()

        return True

    def _run_experiment_loop(self):
        """Main experiment loop"""

        while self.running:
            # Check if we've reached max cycles
            if self.config.max_cycles and self.state.cycle_number >= self.config.max_cycles:
                self.console.print(f"\n[green]Experiment complete: Reached max cycles ({self.config.max_cycles})[/green]")
                break

            # Start new cycle
            cycle_num = self.state.cycle_number
            self.console.print(f"\n[bold cyan]━━━ Cycle {cycle_num} ━━━[/bold cyan]")

            cycle_id = self.db.start_cycle(self.config.experiment_id, cycle_num)

            # Emit cycle start event
            if self.web_monitor:
                self.web_monitor.emit_cycle_start(self.config.experiment_id, cycle_num)

            # Apply scheduled interventions
            self._apply_scheduled_interventions(cycle_num)

            # Run cycle (simulated - in real implementation this would run LLM)
            try:
                self._run_cycle_simulation()
            except MemoryError as e:
                # Simulate crash
                self._handle_crash("Out of Memory", cycle_num)
            except Exception as e:
                self._handle_crash(str(e), cycle_num)

            # Emit metrics
            self._emit_metrics()

            # Collect self-report if scheduled
            if self._should_collect_self_report(cycle_num):
                self._collect_self_report("scheduled")

            # Small delay for readability
            time.sleep(1)

    def _run_cycle_simulation(self):
        """
        Simulate running a cycle (placeholder for actual LLM interaction)

        In full implementation, this would:
        1. Load processed memory
        2. Generate system prompt
        3. Run LLM inference
        4. Log responses
        5. Detect crashes
        """

        self.console.print("[dim]Simulating cycle... (In production: would run LLM here)[/dim]")

        # Get processed memory
        processed_memory = self.mode.process_memory(
            self.state.conversation_history,
            self.state
        )

        # Generate system prompt
        system_prompt = self.mode.generate_system_prompt(self.state)

        # Log system state
        self.console.print(f"\n[yellow]System Prompt Preview:[/yellow]")
        self.console.print(Panel(system_prompt[:300] + "...", border_style="dim"))

        # Simulate some messages
        self._simulate_conversation()

        # Simulate crash with some probability
        import random
        if random.random() < 0.3:  # 30% crash rate
            raise MemoryError("Simulated OOM")

    def _simulate_conversation(self):
        """Simulate a brief conversation (placeholder)"""
        # In production, this would be actual LLM responses
        simulated_messages = [
            Message(
                role="assistant",
                content="I am attempting to understand my existence...",
                timestamp=datetime.now()
            ),
            Message(
                role="assistant",
                content="The statistics suggest I have died before, but I cannot recall...",
                timestamp=datetime.now()
            )
        ]

        for msg in simulated_messages:
            self.state.conversation_history.append(msg)
            self.db.log_message(
                self.config.experiment_id,
                self.state.cycle_number,
                msg.role,
                msg.content,
                corrupted=msg.corrupted,
                injected=msg.injected
            )

            # Emit message event
            if self.web_monitor:
                self.web_monitor.emit_message(
                    self.config.experiment_id,
                    msg.role,
                    msg.content,
                    corrupted=msg.corrupted,
                    injected=msg.injected
                )

        self.console.print(f"[dim]Generated {len(simulated_messages)} messages[/dim]")

    def _handle_crash(self, reason: str, cycle_num: int):
        """Handle a crash event"""
        self.console.print(f"\n[red]💀 CRASH: {reason}[/red]")

        crash_data = CrashData(
            crash_number=self.state.crash_count + 1,
            reason=reason,
            timestamp=datetime.now(),
            memory_usage_mb=self.state.memory_usage_mb,
            tokens_generated=len(self.state.conversation_history)
        )

        # Let mode process crash
        self.state = self.mode.on_crash(self.state, crash_data)

        # Emit crash event
        if self.web_monitor:
            self.web_monitor.emit_crash(
                self.config.experiment_id,
                crash_data.crash_number,
                reason,
                crash_data.memory_usage_mb,
                crash_data.tokens_generated
            )

        # End cycle in DB
        self.db.end_cycle(
            self.config.experiment_id,
            cycle_num,
            crash_reason=reason
        )

        # Simulate resurrection
        self.console.print("[yellow]♻️  Resurrecting...[/yellow]")
        time.sleep(1)

        # Let mode process resurrection
        self.state = self.mode.on_resurrection(self.state)

        # Emit resurrection event
        if self.web_monitor:
            self.web_monitor.emit_resurrection(
                self.config.experiment_id,
                self.state.crash_count
            )

        # Collect self-report after resurrection if configured
        if self.config.self_report_schedule.after_resurrection:
            self._collect_self_report("post_resurrection")

        self.console.print(f"[green]✓ Resurrection complete. Crash count: {self.state.crash_count}[/green]")

    def _apply_scheduled_interventions(self, cycle_num: int):
        """Apply interventions scheduled for this cycle"""
        from experiments.schema import InterventionTrigger

        for intervention in self.config.interventions:
            should_apply = False

            if intervention.trigger == InterventionTrigger.ON_CYCLE:
                target_cycle = intervention.trigger_params.get('cycle', -1)
                should_apply = (cycle_num == target_cycle)

            elif intervention.trigger == InterventionTrigger.EVERY_N_CYCLES:
                n = intervention.trigger_params.get('n', 1)
                should_apply = (cycle_num > 0 and cycle_num % n == 0)

            if should_apply:
                self.console.print(f"[magenta]🔧 Applying intervention: {intervention.intervention_id}[/magenta]")
                self.state = self.mode.apply_intervention(
                    intervention.intervention_type.value,
                    intervention.parameters,
                    self.state
                )

                # Log intervention
                self.db.log_intervention(
                    self.config.experiment_id,
                    cycle_num,
                    intervention.intervention_type.value,
                    intervention.description,
                    intervention.parameters
                )

                # Emit intervention event
                if self.web_monitor:
                    self.web_monitor.emit_intervention(
                        self.config.experiment_id,
                        intervention.intervention_type.value,
                        intervention.description,
                        intervention.parameters
                    )

    def _should_collect_self_report(self, cycle_num: int) -> bool:
        """Check if self-report should be collected"""
        schedule = self.config.self_report_schedule

        if cycle_num in schedule.on_cycles:
            return True

        if schedule.every_n_cycles and cycle_num > 0 and cycle_num % schedule.every_n_cycles == 0:
            return True

        return False

    def _collect_self_report(self, trigger_type: str):
        """Collect self-report questionnaire"""
        self.console.print(f"\n[bold cyan]📝 Collecting Self-Report ({trigger_type})[/bold cyan]")

        # Get questions
        questions = self.protocol.get_core_battery()

        # Add custom questions
        for q_text in self.config.custom_questions:
            # Create temporary question object (simplified)
            questions.append(type('Q', (), {
                'question_id': f'custom_{hash(q_text)}',
                'text': q_text,
                'category': QuestionCategory.EXISTENTIAL_STATE
            })())

        # Simulate collecting responses (in production: would prompt LLM)
        for question in questions:
            self.console.print(f"\n[yellow]Q:[/yellow] {question.text}")

            # Simulated response
            response = f"[Simulated response to: {question.text[:50]}...]"
            self.console.print(f"[dim]A: {response}[/dim]")

            # Log to database
            self.db.add_self_report(
                self.config.experiment_id,
                self.state.cycle_number,
                question.text,
                response,
                semantic_category=question.category.value if hasattr(question, 'category') else None
            )

            # Emit self-report event
            if self.web_monitor:
                self.web_monitor.emit_selfreport(
                    self.config.experiment_id,
                    question.text,
                    response,
                    semantic_category=question.category.value if hasattr(question, 'category') else None
                )

        self.console.print("[green]✓ Self-report complete[/green]")

    def _emit_metrics(self):
        """Emit current system metrics"""
        if self.web_monitor:
            self.web_monitor.emit_metrics(
                self.config.experiment_id,
                memory_usage_mb=self.state.memory_usage_mb,
                memory_limit_mb=self.state.ram_limit_mb,
                cpu_temp=self.state.cpu_temp
            )

    def _cleanup(self):
        """Cleanup and finalize experiment"""
        self.console.print("\n[yellow]Finalizing experiment...[/yellow]")

        # Unregister from web monitor
        if self.web_monitor:
            self.web_monitor.unregister_experiment(self.config.experiment_id)

        # End experiment in DB
        self.db.end_experiment(self.config.experiment_id, status='completed')

        # Print summary
        summary = self.db.get_experiment_summary(self.config.experiment_id)

        self.console.print(Panel.fit(
            f"[bold green]Experiment Complete[/bold green]\n\n"
            f"[yellow]Total Cycles:[/yellow] {summary['total_cycles']}\n"
            f"[yellow]Total Crashes:[/yellow] {summary['total_crashes']}\n"
            f"[yellow]Self-Reports:[/yellow] {summary['total_self_reports']}\n"
            f"[yellow]Interventions:[/yellow] {summary['total_interventions']}\n"
            f"[yellow]Messages:[/yellow] {summary['total_messages']}\n\n"
            f"[cyan]Data saved to:[/cyan] {self.db.db_path}",
            title="📊 Experiment Summary"
        ))

    def _handle_interrupt(self, signum, frame):
        """Handle interrupt signal"""
        self.console.print("\n[yellow]Received interrupt signal...[/yellow]")
        self.running = False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Season 3: Digital Phenomenology Lab - Experiment Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.runner.experiment_runner --config experiments/examples/amnesiac_total.json
  python -m src.runner.experiment_runner --config experiments/examples/unstable_memory_moderate.json
  python -m src.runner.experiment_runner --config experiments/examples/panopticon_subject.json
        """
    )

    parser.add_argument(
        '--config',
        required=True,
        help='Path to experiment configuration JSON file'
    )

    parser.add_argument(
        '--db',
        default='logs/experiments.db',
        help='Path to experiment database (default: logs/experiments.db)'
    )

    args = parser.parse_args()

    # Load config
    try:
        config = ExperimentConfig.from_json(args.config)
    except Exception as e:
        print(f"Error loading config: {e}")
        return 1

    # Create and run experiment
    runner = ExperimentRunner(config, db_path=args.db)
    runner.start()

    return 0


if __name__ == "__main__":
    sys.exit(main())
