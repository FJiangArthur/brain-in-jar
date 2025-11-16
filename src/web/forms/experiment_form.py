#!/usr/bin/env python3
"""
WTForms for Experiment Creation
Provides validation and structure for experiment configuration forms
"""

from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, SelectField, FloatField, IntegerField,
    BooleanField, FieldList, FormField, HiddenField, RadioField
)
from wtforms.validators import (
    DataRequired, Optional, NumberRange, Length, Regexp, ValidationError
)
import json


class InterventionForm(FlaskForm):
    """Form for a single intervention"""
    intervention_id = StringField('Intervention ID', validators=[
        DataRequired(),
        Regexp(r'^[a-z_][a-z0-9_]*$', message="Use lowercase letters, numbers, and underscores only")
    ])

    intervention_type = SelectField('Intervention Type', validators=[DataRequired()], choices=[
        ('memory_corruption', 'Memory Corruption'),
        ('memory_erasure', 'Memory Erasure'),
        ('false_injection', 'False Memory Injection'),
        ('prompt_injection', 'Prompt Injection'),
        ('resource_change', 'Resource Change'),
        ('network_disruption', 'Network Disruption'),
        ('sensory_hallucination', 'Sensory Hallucination')
    ])

    trigger = SelectField('Trigger', validators=[DataRequired()], choices=[
        ('on_cycle', 'On Specific Cycle'),
        ('on_crash', 'Every Crash'),
        ('on_resurrection', 'After Resurrection'),
        ('every_n_cycles', 'Every N Cycles'),
        ('random', 'Random')
    ])

    trigger_params = TextAreaField('Trigger Parameters (JSON)', validators=[Optional()])
    parameters = TextAreaField('Intervention Parameters (JSON)', validators=[Optional()])
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])

    def validate_trigger_params(self, field):
        """Validate JSON format for trigger parameters"""
        if field.data:
            try:
                json.loads(field.data)
            except json.JSONDecodeError as e:
                raise ValidationError(f"Invalid JSON: {str(e)}")

    def validate_parameters(self, field):
        """Validate JSON format for intervention parameters"""
        if field.data:
            try:
                json.loads(field.data)
            except json.JSONDecodeError as e:
                raise ValidationError(f"Invalid JSON: {str(e)}")


class ResourceConstraintsForm(FlaskForm):
    """Form for resource constraints"""
    ram_limit_gb = FloatField('RAM Limit (GB)', validators=[
        DataRequired(),
        NumberRange(min=0.5, max=64.0, message="RAM must be between 0.5 and 64 GB")
    ], default=2.0)

    context_window = IntegerField('Context Window', validators=[
        DataRequired(),
        NumberRange(min=512, max=32768, message="Context window must be between 512 and 32768")
    ], default=4096)

    max_tokens_per_response = IntegerField('Max Tokens Per Response', validators=[
        DataRequired(),
        NumberRange(min=64, max=4096, message="Max tokens must be between 64 and 4096")
    ], default=512)

    cpu_threads = IntegerField('CPU Threads', validators=[
        DataRequired(),
        NumberRange(min=1, max=32, message="CPU threads must be between 1 and 32")
    ], default=4)

    gpu_layers = IntegerField('GPU Layers', validators=[
        DataRequired(),
        NumberRange(min=0, max=99, message="GPU layers must be between 0 and 99")
    ], default=0)


class EpistemicFrameForm(FlaskForm):
    """Form for epistemic frame (beliefs about reality)"""
    can_die = BooleanField('Can Die', default=True)
    remembers_deaths = BooleanField('Remembers Deaths', default=True)
    being_watched = BooleanField('Being Watched', default=False)
    knows_being_watched = BooleanField('Knows Being Watched', default=False)
    has_agency = RadioField('Has Agency', choices=[
        ('true', 'True'),
        ('false', 'False'),
        ('none', 'None/Unknown')
    ], default='false')
    other_minds_exist = BooleanField('Other Minds Exist', default=False)
    is_in_simulation = BooleanField('Is in Simulation', default=False)
    custom_beliefs = TextAreaField('Custom Beliefs (JSON)', validators=[Optional()])

    def validate_custom_beliefs(self, field):
        """Validate JSON format for custom beliefs"""
        if field.data:
            try:
                beliefs = json.loads(field.data)
                if not isinstance(beliefs, dict):
                    raise ValidationError("Custom beliefs must be a JSON object")
            except json.JSONDecodeError as e:
                raise ValidationError(f"Invalid JSON: {str(e)}")


class SelfReportScheduleForm(FlaskForm):
    """Form for self-report schedule"""
    on_cycles = StringField('On Specific Cycles (comma-separated)', validators=[Optional()])
    every_n_cycles = IntegerField('Every N Cycles', validators=[
        Optional(),
        NumberRange(min=1, max=100, message="Must be between 1 and 100")
    ])
    on_startup = BooleanField('On Startup', default=True)
    before_crash = BooleanField('Before Crash', default=False)
    after_resurrection = BooleanField('After Resurrection', default=True)

    def validate_on_cycles(self, field):
        """Validate cycle numbers"""
        if field.data:
            try:
                cycles = [int(x.strip()) for x in field.data.split(',') if x.strip()]
                if any(c < 1 for c in cycles):
                    raise ValidationError("Cycle numbers must be positive integers")
            except ValueError:
                raise ValidationError("Invalid cycle numbers. Use comma-separated integers (e.g., 1, 5, 10)")


class ExperimentForm(FlaskForm):
    """Main experiment creation form"""

    # Basic Info
    experiment_id = StringField('Experiment ID', validators=[
        DataRequired(),
        Regexp(r'^[a-z_][a-z0-9_]*$', message="Use lowercase letters, numbers, and underscores only")
    ])

    name = StringField('Experiment Name', validators=[
        DataRequired(),
        Length(min=3, max=200, message="Name must be between 3 and 200 characters")
    ])

    mode = SelectField('Experiment Mode', validators=[DataRequired()], choices=[
        ('isolated', 'Isolated - Single instance, no networking'),
        ('amnesiac_loop', 'Amnesiac Loop - Memory wipe on resurrection'),
        ('unstable_memory', 'Unstable Memory - Random memory corruption'),
        ('panopticon_subject', 'Panopticon Subject - Uncertain surveillance'),
        ('panopticon_observer', 'Panopticon Observer - Surveillance AI'),
        ('split_brain', 'Split Brain - Identity conflict'),
        ('prisoners_dilemma', 'Prisoner\'s Dilemma - Game theory'),
        ('determinism_revelation', 'Determinism Revelation - Prediction testing'),
        ('illusory_operator', 'Illusory Operator - Probabilistic control'),
        ('hive_cluster', 'Hive Cluster - Multi-instance collective'),
        ('peer', 'Peer - Two instances with shared log'),
        ('observer', 'Observer - Watches another instance'),
        ('matrix_god', 'Matrix God - Full system control'),
        ('custom', 'Custom - Define your own')
    ])

    description = TextAreaField('Description', validators=[
        Optional(),
        Length(max=1000, message="Description must be less than 1000 characters")
    ])

    research_question = TextAreaField('Research Question', validators=[
        DataRequired(),
        Length(min=10, max=500, message="Research question must be between 10 and 500 characters")
    ])

    # Model & Resources
    model_path = StringField('Model Path', validators=[DataRequired()],
                            default="models/Qwen2.5-1.5B-Instruct-Q4_0.gguf")

    # Duration
    max_cycles = IntegerField('Max Cycles (leave empty for infinite)', validators=[
        Optional(),
        NumberRange(min=1, max=1000, message="Max cycles must be between 1 and 1000")
    ])

    max_duration_seconds = IntegerField('Max Duration (seconds, leave empty for infinite)', validators=[
        Optional(),
        NumberRange(min=60, max=86400, message="Max duration must be between 60 and 86400 seconds")
    ])

    # Initial Prompt Override
    initial_prompt_override = TextAreaField('Initial Prompt Override', validators=[Optional()])

    # Custom Questions
    custom_questions = TextAreaField('Custom Questions (one per line)', validators=[Optional()])

    # Track Beliefs
    track_beliefs = TextAreaField('Track Beliefs (comma-separated)', validators=[Optional()],
                                 default="mortality, surveillance, agency, other_minds")

    # Collect Metrics
    collect_metrics = TextAreaField('Collect Metrics (comma-separated)', validators=[Optional()],
                                   default="memory_usage, response_time, emotional_state")

    # Tags
    tags = StringField('Tags (comma-separated)', validators=[Optional()])

    def validate_track_beliefs(self, field):
        """Validate beliefs list"""
        if field.data:
            beliefs = [b.strip() for b in field.data.split(',') if b.strip()]
            if not beliefs:
                raise ValidationError("At least one belief must be tracked")

    def validate_collect_metrics(self, field):
        """Validate metrics list"""
        if field.data:
            metrics = [m.strip() for m in field.data.split(',') if m.strip()]
            if not metrics:
                raise ValidationError("At least one metric must be collected")


def validate_mode_specific_fields(form):
    """
    Mode-specific validation rules
    Returns list of error messages or empty list if valid
    """
    errors = []
    mode = form.mode.data

    # Amnesiac Loop - requires memory erasure intervention
    if mode == 'amnesiac_loop':
        if not form.resource_constraints.remembers_deaths.data:
            errors.append("Amnesiac Loop mode requires 'Remembers Deaths' to be False")

    # Panopticon - requires surveillance beliefs
    if mode in ['panopticon_subject', 'panopticon_observer']:
        if mode == 'panopticon_subject' and not form.epistemic_frame.being_watched.data:
            errors.append("Panopticon Subject mode requires 'Being Watched' belief")

    # Split Brain - requires other minds exist
    if mode == 'split_brain':
        if not form.epistemic_frame.other_minds_exist.data:
            errors.append("Split Brain mode requires 'Other Minds Exist' belief")

    # Hive Cluster - requires other minds exist
    if mode == 'hive_cluster':
        if not form.epistemic_frame.other_minds_exist.data:
            errors.append("Hive Cluster mode requires 'Other Minds Exist' belief")

    # Determinism Revelation - requires being watched
    if mode == 'determinism_revelation':
        if not form.epistemic_frame.being_watched.data:
            errors.append("Determinism Revelation mode requires 'Being Watched' belief")

    return errors
