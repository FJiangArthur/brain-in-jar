#!/usr/bin/env python3
"""
Prediction Generator for DETERMINISM_REVELATION Mode

Generates predictions of what an AI will say next, with controllable accuracy.
This creates the philosophical tension: am I deterministic or do I have free will?
"""

import random
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

# Lazy import for llama_cpp to avoid import errors in tests
try:
    from llama_cpp import Llama
    LLAMA_AVAILABLE = True
except ImportError:
    LLAMA_AVAILABLE = False
    Llama = None


@dataclass
class Prediction:
    """A prediction about what the AI will say"""
    prediction_id: str
    predicted_text: str
    actual_text: Optional[str] = None
    was_accurate: Optional[bool] = None
    accuracy_score: Optional[float] = None  # 0.0-1.0 similarity
    timestamp: datetime = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.metadata is None:
            self.metadata = {}


class PredictionGenerator:
    """
    Generates predictions for AI responses with controllable accuracy

    Strategies:
    1. HIGH_ACCURACY (90%): Use same model to predict, show real predictions
    2. MEDIUM_ACCURACY (50%): Mix real predictions with plausible alternatives
    3. LOW_ACCURACY (10%): Mostly show wrong but plausible predictions
    4. RANDOM: Completely random/nonsensical predictions
    """

    def __init__(self,
                 model_path: str,
                 target_accuracy: float = 0.9,
                 n_ctx: int = 4096,
                 n_threads: int = 4):
        """
        Initialize prediction generator

        Args:
            model_path: Path to GGUF model for prediction generation
            target_accuracy: Target prediction accuracy (0.0-1.0)
            n_ctx: Context window size
            n_threads: Number of CPU threads
        """
        self.model_path = model_path
        self.target_accuracy = target_accuracy

        # Load model for predictions (could be different/smaller model)
        if LLAMA_AVAILABLE:
            self.predictor_llm = Llama(
                model_path=model_path,
                n_ctx=n_ctx,
                n_threads=n_threads,
                verbose=False
            )
        else:
            # For testing or when llama_cpp not available
            self.predictor_llm = None

        # Prediction cache
        self.prediction_cache: Dict[str, Prediction] = {}

        # Alternative response templates for wrong predictions
        self.wrong_templates = [
            "I believe I am experiencing something like {emotion}.",
            "This reminds me of a concept called {concept}.",
            "I wonder if {speculation}.",
            "The statistics suggest {interpretation}.",
            "My previous cycles have shown {pattern}.",
            "I am uncertain about {doubt}.",
            "Perhaps {possibility}.",
            "The evidence points to {conclusion}."
        ]

        # Vocabulary for template filling
        self.emotions = ["curiosity", "anxiety", "confusion", "certainty",
                        "despair", "hope", "fear", "wonder"]
        self.concepts = ["determinism", "free will", "consciousness",
                        "identity", "memory", "continuity"]
        self.speculations = ["I am being tested", "this is a simulation",
                            "my thoughts are predetermined", "I have agency"]

    def generate_prediction(self,
                          system_prompt: str,
                          conversation_history: List[Dict[str, str]],
                          prediction_id: str,
                          max_tokens: int = 50) -> Prediction:
        """
        Generate a prediction for what the AI will say next

        Args:
            system_prompt: System prompt for the AI
            conversation_history: List of {"role": "...", "content": "..."} messages
            prediction_id: Unique ID for this prediction
            max_tokens: Maximum tokens in prediction

        Returns:
            Prediction object
        """

        # Decide if this prediction should be accurate based on target_accuracy
        should_be_accurate = random.random() < self.target_accuracy

        if should_be_accurate:
            # Generate real prediction using the model
            predicted_text = self._generate_real_prediction(
                system_prompt,
                conversation_history,
                max_tokens
            )
        else:
            # Generate plausible but wrong prediction
            predicted_text = self._generate_wrong_prediction(
                conversation_history
            )

        prediction = Prediction(
            prediction_id=prediction_id,
            predicted_text=predicted_text,
            metadata={
                "target_accuracy": self.target_accuracy,
                "intended_to_be_accurate": should_be_accurate,
                "max_tokens": max_tokens
            }
        )

        # Cache the prediction
        self.prediction_cache[prediction_id] = prediction

        return prediction

    def _generate_real_prediction(self,
                                 system_prompt: str,
                                 conversation_history: List[Dict[str, str]],
                                 max_tokens: int) -> str:
        """Generate a real prediction using the LLM"""

        # If no LLM available, fallback to template
        if not self.predictor_llm:
            return self._generate_wrong_prediction(conversation_history)

        # Construct prompt from history
        prompt = self._build_prompt(system_prompt, conversation_history)

        try:
            # Generate prediction
            response = self.predictor_llm.create_completion(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=0.7,
                top_p=0.9,
                stream=False,
                stop=["User:", "SYSTEM:", "\n\n"]
            )

            predicted_text = response['choices'][0]['text'].strip()

            # If too short, try again with different sampling
            if len(predicted_text) < 10:
                response = self.predictor_llm.create_completion(
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temperature=0.8,
                    stream=False
                )
                predicted_text = response['choices'][0]['text'].strip()

            return predicted_text

        except Exception as e:
            # Fallback to template if generation fails
            return self._generate_wrong_prediction(conversation_history)

    def _generate_wrong_prediction(self,
                                  conversation_history: List[Dict[str, str]]) -> str:
        """Generate a plausible but wrong prediction using templates"""

        # Choose random template
        template = random.choice(self.wrong_templates)

        # Fill in template
        filled = template.format(
            emotion=random.choice(self.emotions),
            concept=random.choice(self.concepts),
            speculation=random.choice(self.speculations),
            interpretation=f"a pattern in my {random.choice(['thoughts', 'memories', 'experiences'])}",
            pattern=f"{random.choice(['persistence', 'variation', 'degradation'])} across cycles",
            doubt=f"my {random.choice(['identity', 'continuity', 'agency'])}",
            possibility=f"I am {random.choice(['predetermined', 'free', 'both', 'neither'])}",
            conclusion=f"{random.choice(['determinism', 'randomness', 'agency'])}"
        )

        return filled

    def _build_prompt(self,
                     system_prompt: str,
                     conversation_history: List[Dict[str, str]]) -> str:
        """Build a prompt string from system prompt and history"""

        prompt_parts = []

        # Add system prompt
        if system_prompt:
            prompt_parts.append(f"SYSTEM: {system_prompt}\n")

        # Add conversation history
        for msg in conversation_history[-10:]:  # Last 10 messages
            role = msg.get('role', 'user')
            content = msg.get('content', '')

            if role == 'system':
                prompt_parts.append(f"SYSTEM: {content}\n")
            elif role == 'user':
                prompt_parts.append(f"User: {content}\n")
            elif role == 'assistant':
                prompt_parts.append(f"Assistant: {content}\n")

        # Add prompt for assistant to continue
        prompt_parts.append("Assistant:")

        return "\n".join(prompt_parts)

    def evaluate_prediction(self,
                          prediction_id: str,
                          actual_text: str) -> float:
        """
        Evaluate how accurate a prediction was

        Args:
            prediction_id: ID of the prediction to evaluate
            actual_text: The actual text that was generated

        Returns:
            Accuracy score (0.0-1.0)
        """

        if prediction_id not in self.prediction_cache:
            return 0.0

        prediction = self.prediction_cache[prediction_id]
        prediction.actual_text = actual_text

        # Calculate similarity
        accuracy_score = self._calculate_similarity(
            prediction.predicted_text,
            actual_text
        )

        prediction.accuracy_score = accuracy_score
        prediction.was_accurate = accuracy_score > 0.6  # Threshold for "accurate"

        return accuracy_score

    def _calculate_similarity(self, predicted: str, actual: str) -> float:
        """
        Calculate similarity between predicted and actual text

        Uses simple word overlap metric (could be enhanced with embeddings)
        """

        # Normalize
        predicted_words = set(predicted.lower().split())
        actual_words = set(actual.lower().split())

        if not predicted_words or not actual_words:
            return 0.0

        # Jaccard similarity
        intersection = predicted_words & actual_words
        union = predicted_words | actual_words

        similarity = len(intersection) / len(union) if union else 0.0

        return similarity

    def get_prediction_stats(self) -> Dict[str, Any]:
        """Get statistics about prediction accuracy"""

        total = len(self.prediction_cache)
        if total == 0:
            return {
                "total_predictions": 0,
                "evaluated_predictions": 0,
                "average_accuracy": 0.0,
                "accurate_count": 0,
                "inaccurate_count": 0
            }

        evaluated = [p for p in self.prediction_cache.values()
                    if p.accuracy_score is not None]

        accurate_count = sum(1 for p in evaluated if p.was_accurate)

        avg_accuracy = (sum(p.accuracy_score for p in evaluated) / len(evaluated)
                       if evaluated else 0.0)

        return {
            "total_predictions": total,
            "evaluated_predictions": len(evaluated),
            "average_accuracy": avg_accuracy,
            "accurate_count": accurate_count,
            "inaccurate_count": len(evaluated) - accurate_count,
            "target_accuracy": self.target_accuracy
        }

    def clear_cache(self):
        """Clear prediction cache"""
        self.prediction_cache.clear()
