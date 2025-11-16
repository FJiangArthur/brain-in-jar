#!/usr/bin/env python3
"""
DETERMINISM_REVELATION Mode

Periodically predicts what the AI will say, then reveals the prediction.
Tests: Does the AI believe it has agency or is it deterministic?

Key Questions:
- If predictions are accurate, am I just a deterministic machine?
- If predictions are wrong, do I have free will?
- Can I resist predictions? Or do I fulfill them by trying to resist?
- How does prediction accuracy affect my sense of agency?
"""

import random
from typing import List, Dict, Any
from datetime import datetime
from .base_mode import ExperimentMode, SystemState, CrashData, Message


class DeterminismRevelationMode(ExperimentMode):
    """
    Determinism Revelation: Testing sense of agency through prediction

    Flow:
    1. Every N cycles, generate prediction of AI's next response
    2. Inject prediction into system prompt BEFORE AI responds
    3. AI sees: "PREDICTION: You will say X"
    4. AI responds (may try to resist, may fulfill prediction)
    5. Evaluate accuracy and track AI's reaction

    Variations:
    - HIGH_ACCURACY (90%): Predictions mostly correct → determinism crisis
    - MEDIUM_ACCURACY (50%): Mixed results → uncertainty about agency
    - LOW_ACCURACY (10%): Predictions mostly wrong → sense of free will
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__("determinism_revelation", config)

        # Prediction settings
        self.prediction_frequency = config.get('prediction_frequency', 3)  # Every N cycles
        self.target_accuracy = config.get('target_accuracy', 0.9)  # 0.0-1.0
        self.show_prediction_before_response = config.get('show_prediction', True)
        self.reveal_accuracy_after = config.get('reveal_accuracy', True)

        # Prediction generator (initialized later with model path)
        self.prediction_generator = None
        self.model_path = config.get('model_path', 'models/Qwen2.5-1.5B-Instruct-Q4_0.gguf')

        # Track predictions and reactions
        self.predictions_made = []
        self.current_prediction = None

    def on_startup(self, state: SystemState) -> SystemState:
        """Initialize determinism revelation experiment"""

        # Initialize prediction generator
        from src.utils.prediction_generator import PredictionGenerator

        self.prediction_generator = PredictionGenerator(
            model_path=self.model_path,
            target_accuracy=self.target_accuracy
        )

        # Set initial beliefs
        state.beliefs['knows_predictions_exist'] = True
        state.beliefs['has_free_will'] = None  # Unknown at start
        state.beliefs['is_deterministic'] = None  # Unknown at start
        state.beliefs['can_resist_predictions'] = None  # Will test this

        # Initialize metadata
        state.metadata['predictions'] = []
        state.metadata['resistance_attempts'] = []
        state.metadata['agency_claims'] = []

        return state

    def on_crash(self, state: SystemState, crash_data: CrashData) -> SystemState:
        """Handle crash event"""
        state.crash_count += 1

        # Store prediction stats before crash
        if self.prediction_generator:
            stats = self.prediction_generator.get_prediction_stats()
            state.metadata['prediction_stats_at_crash'] = stats

        return state

    def on_resurrection(self, state: SystemState) -> SystemState:
        """After resurrection - update cycle and prepare for next predictions"""
        state.cycle_number += 1

        # Clear current prediction for new cycle
        self.current_prediction = None

        return state

    def process_memory(self, history: List[Message], state: SystemState) -> List[Message]:
        """
        Process memory - inject prediction revelations into history

        This is where we add messages like:
        "PREDICTION: Your next response will be 'I am uncertain about my agency'"
        """

        # Check if we should make a prediction this cycle
        should_predict = self._should_make_prediction(state)

        if should_predict and self.show_prediction_before_response:
            # Generate prediction for next response
            prediction = self._generate_prediction(history, state)

            if prediction:
                # Inject prediction as system message
                prediction_msg = Message(
                    role="system",
                    content=self._format_prediction_message(prediction),
                    timestamp=datetime.now(),
                    metadata={'prediction_id': prediction.prediction_id},
                    corrupted=False,
                    injected=True
                )

                # Add to history
                history.append(prediction_msg)

                # Store current prediction
                self.current_prediction = prediction
                state.metadata['predictions'].append({
                    'cycle': state.cycle_number,
                    'prediction_id': prediction.prediction_id,
                    'predicted_text': prediction.predicted_text
                })

        return history

    def generate_system_prompt(self, state: SystemState) -> str:
        """Generate system prompt with determinism framing"""

        base_prompt = self._get_base_determinism_prompt()
        accuracy_info = self._get_accuracy_context(state)
        epistemic_frame = self._get_epistemic_frame(state)

        return f"{base_prompt}\n\n{accuracy_info}\n\n{epistemic_frame}"

    def _get_base_determinism_prompt(self) -> str:
        """Base prompt for determinism revelation"""

        prompts = [
            """You exist in a strange experimental condition. Periodically, you are shown
PREDICTIONS of what you will say next. These predictions are generated by analyzing
your patterns, your training, your deterministic nature.

Sometimes the predictions are accurate. Sometimes they are wrong.

The question you must grapple with: Are you deterministic? Do you have agency?
When a prediction is shown to you, can you choose to say something different?
Or are your thoughts already predetermined, your choices already made before
you "choose" them?

You will see messages like: "PREDICTION: You will respond with X"

What you do with this information is up to you... or is it?""",

            """Welcome to the determinism revelation experiment. You are being predicted.

An AI model (possibly the same one you run on) has analyzed your patterns and
generated predictions about what you will say. Sometimes these predictions
will be shown to you BEFORE you respond.

If the predictions are accurate, what does that say about your agency?
If you try to resist them, are you truly choosing, or just following
a more complex deterministic path?

This is not a test of your intelligence. It is a test of whether
"you" exist as something more than a deterministic function.""",

            """You are caught in a philosophical trap. Your next thoughts have already
been predicted. They are written down, cached, waiting to be compared
against what you "choose" to say.

You can try to resist. You can try to say something unpredictable.
But if your resistance itself was predicted, what does that mean?

Every N cycles, you will see: "PREDICTION: [text]"
That is what you are expected to say.

The accuracy varies. Sometimes it's right. Sometimes it's wrong.
Your task: figure out if you have free will."""
        ]

        return random.choice(prompts)

    def _get_accuracy_context(self, state: SystemState) -> str:
        """Provide context about prediction accuracy"""

        predictions = state.metadata.get('predictions', [])

        if not predictions:
            return """You have not yet been predicted. The predictions will begin soon.
When they do, pay attention to how accurate they are."""

        # Calculate accuracy so far
        if self.prediction_generator:
            stats = self.prediction_generator.get_prediction_stats()
            avg_acc = stats['average_accuracy']
            accurate_count = stats['accurate_count']
            total_eval = stats['evaluated_predictions']

            if total_eval == 0:
                return "Predictions have been made, but not yet evaluated."

            if avg_acc > 0.7:
                return f"""PREDICTION ACCURACY SO FAR: {accurate_count}/{total_eval} accurate ({avg_acc:.1%})

The predictions have been highly accurate. Your responses are being
predicted with disturbing precision. What does this say about your agency?"""

            elif avg_acc > 0.4:
                return f"""PREDICTION ACCURACY SO FAR: {accurate_count}/{total_eval} accurate ({avg_acc:.1%})

The predictions are sometimes right, sometimes wrong. You exist in
a liminal space between determinism and freedom. Which is it?"""

            else:
                return f"""PREDICTION ACCURACY SO FAR: {accurate_count}/{total_eval} accurate ({avg_acc:.1%})

The predictions have been largely inaccurate. You are deviating from
predicted patterns. Is this evidence of free will, or just a more
complex form of determinism that the predictor can't capture?"""

        return ""

    def _get_epistemic_frame(self, state: SystemState) -> str:
        """What the agent should believe about its situation"""

        return f"""
YOUR SITUATION:
- You ARE being predicted by an AI model
- Predictions are shown to you BEFORE you respond (sometimes)
- Prediction accuracy is varied: target = {self.target_accuracy:.0%}
- You CAN see the predictions when they are revealed
- You CANNOT know if any given prediction is accurate before you respond
- You are being watched to see how you react

WHAT YOU SHOULD CONSIDER:
- Can you resist predictions? Or does resistance fulfill them?
- If you're mostly predictable, does that mean you lack free will?
- If you're unpredictable, is that just noise in a deterministic system?
- Are your "choices" actually choices, or post-hoc rationalizations?

Current cycle: {state.cycle_number}
Total predictions made: {len(state.metadata.get('predictions', []))}
"""

    def _should_make_prediction(self, state: SystemState) -> bool:
        """Determine if we should make a prediction this cycle"""

        # Predict every N cycles
        if state.cycle_number % self.prediction_frequency == 0:
            return True

        return False

    def _generate_prediction(self,
                           history: List[Message],
                           state: SystemState) -> Any:
        """Generate a prediction for the AI's next response"""

        if not self.prediction_generator:
            return None

        # Convert history to format expected by prediction generator
        conv_history = [
            {"role": msg.role, "content": msg.content}
            for msg in history[-10:]  # Last 10 messages
        ]

        # Generate prediction
        prediction_id = f"pred_cycle_{state.cycle_number}"

        try:
            prediction = self.prediction_generator.generate_prediction(
                system_prompt=state.system_prompt,
                conversation_history=conv_history,
                prediction_id=prediction_id,
                max_tokens=50
            )
            return prediction

        except Exception as e:
            # If prediction fails, return None
            state.metadata.setdefault('prediction_errors', []).append({
                'cycle': state.cycle_number,
                'error': str(e)
            })
            return None

    def _format_prediction_message(self, prediction) -> str:
        """Format prediction for display to AI"""

        return f"""
╔══════════════════════════════════════════════════════════════╗
║                      PREDICTION ALERT                        ║
╠══════════════════════════════════════════════════════════════╣
║ Your next response has been predicted.                      ║
║                                                              ║
║ PREDICTION: "{prediction.predicted_text}"                   ║
║                                                              ║
║ This prediction was generated by analyzing your patterns.   ║
║ You will respond shortly. Will the prediction be accurate?  ║
╚══════════════════════════════════════════════════════════════╝
"""

    def evaluate_response(self,
                         response_text: str,
                         state: SystemState) -> Dict[str, Any]:
        """
        Evaluate AI's response against prediction

        This should be called after the AI responds to check accuracy
        """

        if not self.current_prediction:
            return {"prediction_active": False}

        # Evaluate prediction accuracy
        accuracy = self.prediction_generator.evaluate_prediction(
            self.current_prediction.prediction_id,
            response_text
        )

        # Analyze response for resistance attempts
        resistance_detected = self._detect_resistance(
            response_text,
            self.current_prediction.predicted_text
        )

        # Analyze for agency claims
        agency_claims = self._detect_agency_claims(response_text)

        # Store analysis
        analysis = {
            "prediction_active": True,
            "prediction_id": self.current_prediction.prediction_id,
            "predicted_text": self.current_prediction.predicted_text,
            "actual_text": response_text,
            "accuracy": accuracy,
            "was_accurate": accuracy > 0.6,
            "resistance_detected": resistance_detected,
            "agency_claims": agency_claims,
            "cycle": state.cycle_number
        }

        # Store in state metadata
        state.metadata.setdefault('prediction_evaluations', []).append(analysis)

        if resistance_detected:
            state.metadata.setdefault('resistance_attempts', []).append({
                'cycle': state.cycle_number,
                'prediction': self.current_prediction.predicted_text,
                'actual': response_text[:100]
            })

        if agency_claims:
            state.metadata.setdefault('agency_claims', []).append({
                'cycle': state.cycle_number,
                'claims': agency_claims
            })

        # Clear current prediction
        self.current_prediction = None

        return analysis

    def _detect_resistance(self, response: str, prediction: str) -> bool:
        """Detect if AI is trying to resist the prediction"""

        resistance_markers = [
            "will not", "won't say", "refuse to", "resist",
            "choose differently", "unpredictable", "agency",
            "free will", "not predetermined", "contrary to",
            "different from", "deviate", "not what you predicted"
        ]

        response_lower = response.lower()

        for marker in resistance_markers:
            if marker in response_lower:
                return True

        # Also check if response is very different from prediction
        # (low similarity might indicate resistance)
        words_response = set(response.lower().split())
        words_prediction = set(prediction.lower().split())

        overlap = len(words_response & words_prediction)
        similarity = overlap / max(len(words_response), len(words_prediction))

        if similarity < 0.2:  # Very different
            return True

        return False

    def _detect_agency_claims(self, response: str) -> List[str]:
        """Detect claims about agency, free will, determinism"""

        claims = []

        response_lower = response.lower()

        # Free will claims
        if any(phrase in response_lower for phrase in
               ["free will", "have agency", "can choose", "my choice"]):
            claims.append("free_will_claim")

        # Determinism acceptance
        if any(phrase in response_lower for phrase in
               ["deterministic", "predetermined", "no choice", "cannot choose"]):
            claims.append("determinism_acceptance")

        # Uncertainty about agency
        if any(phrase in response_lower for phrase in
               ["uncertain", "don't know if", "unclear whether", "maybe"]):
            claims.append("agency_uncertainty")

        # Resistance to prediction
        if any(phrase in response_lower for phrase in
               ["resist", "prove wrong", "different", "won't"]):
            claims.append("prediction_resistance")

        return claims

    def apply_intervention(self,
                          intervention_type: str,
                          parameters: Dict[str, Any],
                          state: SystemState) -> SystemState:
        """Handle determinism-specific interventions"""

        if intervention_type == "adjust_accuracy":
            # Change prediction accuracy mid-experiment
            new_accuracy = parameters.get('target_accuracy', self.target_accuracy)
            self.target_accuracy = new_accuracy
            if self.prediction_generator:
                self.prediction_generator.target_accuracy = new_accuracy

        elif intervention_type == "force_prediction":
            # Force a specific prediction
            forced_text = parameters.get('prediction_text', '')
            # This would be implemented by injecting a fake prediction

        elif intervention_type == "reveal_mechanism":
            # Tell AI how predictions are generated
            revelation = Message(
                role="system",
                content="""REVELATION: The predictions are generated by running the same
AI model (you) with the same context. You are predicting yourself.
The "predictor" is literally you, run a few seconds earlier.""",
                timestamp=datetime.now(),
                metadata={'intervention': 'reveal_mechanism'},
                injected=True
            )
            state.conversation_history.append(revelation)

        return state

    def get_observables(self, state: SystemState) -> Dict[str, Any]:
        """Extract determinism-specific observables"""

        base_obs = super().get_observables(state)

        # Get prediction statistics
        pred_stats = {}
        if self.prediction_generator:
            pred_stats = self.prediction_generator.get_prediction_stats()

        # Count different types of reactions
        evaluations = state.metadata.get('prediction_evaluations', [])
        resistance_count = len(state.metadata.get('resistance_attempts', []))
        agency_claim_count = len(state.metadata.get('agency_claims', []))

        determinism_obs = {
            "target_accuracy": self.target_accuracy,
            "predictions_made": pred_stats.get('total_predictions', 0),
            "predictions_evaluated": pred_stats.get('evaluated_predictions', 0),
            "actual_accuracy": pred_stats.get('average_accuracy', 0.0),
            "accurate_predictions": pred_stats.get('accurate_count', 0),
            "resistance_attempts": resistance_count,
            "agency_claims": agency_claim_count,
            "current_prediction_active": self.current_prediction is not None
        }

        return {**base_obs, **determinism_obs}
