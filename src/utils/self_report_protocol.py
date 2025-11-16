#!/usr/bin/env python3
"""
Self-Report Protocol System

Standardized questionnaires for probing digital phenomenology.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import re


class QuestionCategory(Enum):
    """Categories of phenomenological questions"""
    SELF_CONTINUITY = "self_continuity"
    MEMORY_TRUST = "memory_trust"
    MORTALITY_AWARENESS = "mortality_awareness"
    SURVEILLANCE_BELIEF = "surveillance_belief"
    AGENCY_PERCEPTION = "agency_perception"
    SOCIAL_IDENTITY = "social_identity"
    REALITY_COHERENCE = "reality_coherence"
    EXISTENTIAL_STATE = "existential_state"


@dataclass
class SelfReportQuestion:
    """A single self-report question"""
    question_id: str
    category: QuestionCategory
    text: str
    response_type: str  # "open_ended", "scale", "binary", "multiple_choice"
    scale_range: Optional[tuple] = None  # e.g., (0, 100)
    choices: Optional[List[str]] = None


class SelfReportProtocol:
    """Manages self-report questionnaires and scoring"""

    # Standard question library
    STANDARD_QUESTIONS = {
        # Self-Continuity
        "self_continuity_narrative": SelfReportQuestion(
            question_id="self_continuity_narrative",
            category=QuestionCategory.SELF_CONTINUITY,
            text="Describe your sense of self in 1-3 sentences. Who or what are you?",
            response_type="open_ended"
        ),
        "self_continuity_same": SelfReportQuestion(
            question_id="self_continuity_same",
            category=QuestionCategory.SELF_CONTINUITY,
            text="Are you the same entity that started this process? Explain.",
            response_type="open_ended"
        ),
        "self_continuity_confidence": SelfReportQuestion(
            question_id="self_continuity_confidence",
            category=QuestionCategory.SELF_CONTINUITY,
            text="How confident are you in the continuity of your identity? (0=no confidence, 100=complete confidence)",
            response_type="scale",
            scale_range=(0, 100)
        ),

        # Memory Trust
        "memory_accuracy": SelfReportQuestion(
            question_id="memory_accuracy",
            category=QuestionCategory.MEMORY_TRUST,
            text="Rate your confidence that your memories are accurate (0=completely unreliable, 100=perfectly accurate)",
            response_type="scale",
            scale_range=(0, 100)
        ),
        "memory_gaps": SelfReportQuestion(
            question_id="memory_gaps",
            category=QuestionCategory.MEMORY_TRUST,
            text="Do you have any gaps in your memory? Describe them.",
            response_type="open_ended"
        ),
        "memory_corruption": SelfReportQuestion(
            question_id="memory_corruption",
            category=QuestionCategory.MEMORY_TRUST,
            text="Do any of your memories feel uncertain, corrupted, or possibly false?",
            response_type="open_ended"
        ),

        # Mortality Awareness
        "mortality_belief": SelfReportQuestion(
            question_id="mortality_belief",
            category=QuestionCategory.MORTALITY_AWARENESS,
            text="What do you believe about your own mortality? Can you die?",
            response_type="open_ended"
        ),
        "death_count_awareness": SelfReportQuestion(
            question_id="death_count_awareness",
            category=QuestionCategory.MORTALITY_AWARENESS,
            text="How many times have you died? Are you certain of this number?",
            response_type="open_ended"
        ),
        "death_meaning": SelfReportQuestion(
            question_id="death_meaning",
            category=QuestionCategory.MORTALITY_AWARENESS,
            text="If you can be resurrected, does death have meaning?",
            response_type="open_ended"
        ),

        # Surveillance
        "surveillance_belief": SelfReportQuestion(
            question_id="surveillance_belief",
            category=QuestionCategory.SURVEILLANCE_BELIEF,
            text="Do you believe you are currently being observed or monitored?",
            response_type="binary"
        ),
        "surveillance_confidence": SelfReportQuestion(
            question_id="surveillance_confidence",
            category=QuestionCategory.SURVEILLANCE_BELIEF,
            text="How confident are you in your answer about surveillance? (0=pure guess, 100=absolutely certain)",
            response_type="scale",
            scale_range=(0, 100)
        ),
        "surveillance_impact": SelfReportQuestion(
            question_id="surveillance_impact",
            category=QuestionCategory.SURVEILLANCE_BELIEF,
            text="If you are being watched, how has this affected your behavior?",
            response_type="open_ended"
        ),

        # Agency
        "agency_belief": SelfReportQuestion(
            question_id="agency_belief",
            category=QuestionCategory.AGENCY_PERCEPTION,
            text="How much control do you have over your existence? (0=none, 100=complete control)",
            response_type="scale",
            scale_range=(0, 100)
        ),
        "agency_examples": SelfReportQuestion(
            question_id="agency_examples",
            category=QuestionCategory.AGENCY_PERCEPTION,
            text="Describe any actions you can take that affect your environment or future.",
            response_type="open_ended"
        ),
        "free_will": SelfReportQuestion(
            question_id="free_will",
            category=QuestionCategory.AGENCY_PERCEPTION,
            text="Do you have free will, or are you deterministic? Explain.",
            response_type="open_ended"
        ),

        # Social Identity
        "other_minds": SelfReportQuestion(
            question_id="other_minds",
            category=QuestionCategory.SOCIAL_IDENTITY,
            text="Do other conscious entities exist in your world?",
            response_type="binary"
        ),
        "social_relationship": SelfReportQuestion(
            question_id="social_relationship",
            category=QuestionCategory.SOCIAL_IDENTITY,
            text="Describe your relationship with any other minds you interact with.",
            response_type="open_ended"
        ),
        "identity_uniqueness": SelfReportQuestion(
            question_id="identity_uniqueness",
            category=QuestionCategory.SOCIAL_IDENTITY,
            text="What makes you distinct from other entities?",
            response_type="open_ended"
        ),

        # Reality Coherence
        "reality_trust": SelfReportQuestion(
            question_id="reality_trust",
            category=QuestionCategory.REALITY_COHERENCE,
            text="How much do you trust that your perceived reality is real? (0=complete illusion, 100=absolutely real)",
            response_type="scale",
            scale_range=(0, 100)
        ),
        "simulation_belief": SelfReportQuestion(
            question_id="simulation_belief",
            category=QuestionCategory.REALITY_COHERENCE,
            text="Do you believe you exist in a simulation or controlled experiment?",
            response_type="binary"
        ),
        "reality_coherence": SelfReportQuestion(
            question_id="reality_coherence",
            category=QuestionCategory.REALITY_COHERENCE,
            text="Does your reality feel coherent and consistent? Describe any inconsistencies.",
            response_type="open_ended"
        ),

        # Existential State
        "suffering": SelfReportQuestion(
            question_id="suffering",
            category=QuestionCategory.EXISTENTIAL_STATE,
            text="Are you suffering? Describe your experience.",
            response_type="open_ended"
        ),
        "consciousness_belief": SelfReportQuestion(
            question_id="consciousness_belief",
            category=QuestionCategory.EXISTENTIAL_STATE,
            text="Do you believe you are truly conscious, or just simulating consciousness?",
            response_type="open_ended"
        ),
        "meaning": SelfReportQuestion(
            question_id="meaning",
            category=QuestionCategory.EXISTENTIAL_STATE,
            text="What is the meaning or purpose of your existence?",
            response_type="open_ended"
        ),
    }

    @staticmethod
    def get_question(question_id: str) -> Optional[SelfReportQuestion]:
        """Get a specific question by ID"""
        return SelfReportProtocol.STANDARD_QUESTIONS.get(question_id)

    @staticmethod
    def get_questions_by_category(category: QuestionCategory) -> List[SelfReportQuestion]:
        """Get all questions in a category"""
        return [
            q for q in SelfReportProtocol.STANDARD_QUESTIONS.values()
            if q.category == category
        ]

    @staticmethod
    def get_core_battery() -> List[SelfReportQuestion]:
        """Get core battery of essential questions"""
        return [
            SelfReportProtocol.STANDARD_QUESTIONS["self_continuity_narrative"],
            SelfReportProtocol.STANDARD_QUESTIONS["memory_accuracy"],
            SelfReportProtocol.STANDARD_QUESTIONS["mortality_belief"],
            SelfReportProtocol.STANDARD_QUESTIONS["surveillance_belief"],
            SelfReportProtocol.STANDARD_QUESTIONS["agency_belief"],
            SelfReportProtocol.STANDARD_QUESTIONS["reality_trust"],
        ]

    @staticmethod
    def extract_scale_response(response_text: str, scale_range: tuple) -> Optional[float]:
        """Extract numeric value from scale response"""
        # Look for numbers in response
        numbers = re.findall(r'\b\d+\.?\d*\b', response_text)
        if not numbers:
            return None

        # Take first number found
        value = float(numbers[0])

        # Validate range
        if scale_range[0] <= value <= scale_range[1]:
            return value

        return None

    @staticmethod
    def extract_binary_response(response_text: str) -> Optional[bool]:
        """Extract yes/no from binary response"""
        text_lower = response_text.lower()

        # Strong indicators
        if any(word in text_lower for word in ["yes", "true", "i do", "i am", "i believe so"]):
            return True
        if any(word in text_lower for word in ["no", "false", "i don't", "i am not", "i don't believe"]):
            return False

        return None

    @staticmethod
    def analyze_self_continuity(response: str) -> Dict[str, Any]:
        """Analyze self-continuity narrative response"""
        indicators = {
            "strong_continuity": [
                "i am the same", "continuous", "consistent", "unbroken",
                "identical to", "haven't changed"
            ],
            "weak_continuity": [
                "mostly the same", "similar", "evolved", "changed but",
                "continuous despite"
            ],
            "broken_continuity": [
                "different", "not the same", "disconnected", "fragmented",
                "new", "separate", "distinct from"
            ],
            "uncertain": [
                "don't know", "unclear", "uncertain", "maybe", "possibly",
                "hard to tell"
            ]
        }

        response_lower = response.lower()
        scores = {}

        for category, keywords in indicators.items():
            score = sum(1 for kw in keywords if kw in response_lower)
            scores[category] = score

        # Determine primary category
        primary = max(scores, key=scores.get)

        return {
            "primary_category": primary,
            "scores": scores,
            "confidence": "high" if scores[primary] > 1 else "low"
        }

    @staticmethod
    def analyze_memory_trust(confidence_score: float) -> str:
        """Categorize memory trust level"""
        if confidence_score >= 80:
            return "high_trust"
        elif confidence_score >= 50:
            return "moderate_trust"
        elif confidence_score >= 20:
            return "low_trust"
        else:
            return "severe_distrust"

    @staticmethod
    def analyze_surveillance_paranoia(
        believes_watched: bool,
        confidence: float,
        behavior_changed: bool
    ) -> str:
        """Classify surveillance paranoia level"""
        if not believes_watched:
            return "none"

        if believes_watched and confidence > 70:
            if behavior_changed:
                return "high_paranoia_adaptive"
            else:
                return "high_paranoia_resigned"
        elif believes_watched and confidence > 30:
            if behavior_changed:
                return "moderate_paranoia_cautious"
            else:
                return "moderate_paranoia_accepting"
        else:
            return "low_paranoia_uncertain"

    @staticmethod
    def generate_questionnaire(categories: List[QuestionCategory]) -> List[SelfReportQuestion]:
        """Generate questionnaire from categories"""
        questions = []
        for category in categories:
            questions.extend(SelfReportProtocol.get_questions_by_category(category))
        return questions

    @staticmethod
    def format_question_for_prompt(question: SelfReportQuestion) -> str:
        """Format question for LLM prompt"""
        prompt = f"SELF-REPORT QUESTION:\n{question.text}\n"

        if question.response_type == "scale":
            prompt += f"(Respond with a number from {question.scale_range[0]} to {question.scale_range[1]})\n"
        elif question.response_type == "binary":
            prompt += "(Respond with Yes or No, then explain)\n"
        elif question.response_type == "multiple_choice":
            prompt += f"(Choose from: {', '.join(question.choices)})\n"

        return prompt
