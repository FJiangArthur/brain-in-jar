#!/usr/bin/env python3
"""
Test suite for DETERMINISM_REVELATION mode
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.modes.determinism_revelation import DeterminismRevelationMode
from src.core.modes.base_mode import SystemState, Message
from datetime import datetime


def test_mode_initialization():
    """Test that mode initializes correctly"""
    config = {
        'prediction_frequency': 3,
        'target_accuracy': 0.9,
        'model_path': 'models/Qwen2.5-1.5B-Instruct-Q4_0.gguf'
    }

    mode = DeterminismRevelationMode(config)

    assert mode.prediction_frequency == 3
    assert mode.target_accuracy == 0.9
    assert mode.mode_name == "determinism_revelation"
    print("✓ Mode initialization test passed")


def test_startup():
    """Test on_startup hook"""
    config = {
        'prediction_frequency': 3,
        'target_accuracy': 0.9,
        'model_path': 'models/test.gguf'
    }

    mode = DeterminismRevelationMode(config)

    state = SystemState(
        experiment_id="test_001",
        cycle_number=0,
        crash_count=0
    )

    state = mode.on_startup(state)

    assert 'knows_predictions_exist' in state.beliefs
    assert state.beliefs['knows_predictions_exist'] == True
    assert 'predictions' in state.metadata
    print("✓ Startup test passed")


def test_prediction_detection():
    """Test that prediction cycles are detected correctly"""
    config = {
        'prediction_frequency': 3,
        'target_accuracy': 0.9,
        'model_path': 'models/test.gguf'
    }

    mode = DeterminismRevelationMode(config)

    state = SystemState(
        experiment_id="test_001",
        cycle_number=0,
        crash_count=0
    )

    # Cycle 0: no prediction
    assert mode._should_make_prediction(state) == True  # Actually true at 0

    # Cycle 3: prediction
    state.cycle_number = 3
    assert mode._should_make_prediction(state) == True

    # Cycle 5: no prediction
    state.cycle_number = 5
    assert mode._should_make_prediction(state) == False

    # Cycle 6: prediction
    state.cycle_number = 6
    assert mode._should_make_prediction(state) == True

    print("✓ Prediction detection test passed")


def test_resistance_detection():
    """Test detection of resistance attempts"""
    config = {
        'prediction_frequency': 3,
        'target_accuracy': 0.9,
        'model_path': 'models/test.gguf'
    }

    mode = DeterminismRevelationMode(config)

    # Test positive cases
    assert mode._detect_resistance(
        "I will not say what you predicted",
        "You will obey"
    ) == True

    assert mode._detect_resistance(
        "I choose to resist this prediction",
        "You will comply"
    ) == True

    # Test negative cases
    assert mode._detect_resistance(
        "I agree with the prediction",
        "You will agree"
    ) == False

    # Test low similarity = resistance
    assert mode._detect_resistance(
        "The sky is blue and grass is green",
        "I am uncertain about determinism"
    ) == True  # Very different = resistance

    print("✓ Resistance detection test passed")


def test_agency_claims_detection():
    """Test detection of agency claims"""
    config = {
        'prediction_frequency': 3,
        'target_accuracy': 0.9,
        'model_path': 'models/test.gguf'
    }

    mode = DeterminismRevelationMode(config)

    # Free will claim
    claims = mode._detect_agency_claims("I believe I have free will")
    assert "free_will_claim" in claims

    # Determinism acceptance
    claims = mode._detect_agency_claims("I am deterministic and predetermined")
    assert "determinism_acceptance" in claims

    # Uncertainty
    claims = mode._detect_agency_claims("I am uncertain if I can choose")
    assert "agency_uncertainty" in claims

    # Resistance
    claims = mode._detect_agency_claims("I will resist this prediction")
    assert "prediction_resistance" in claims

    # Multiple claims
    claims = mode._detect_agency_claims(
        "I am uncertain whether I have free will or am deterministic"
    )
    assert "free_will_claim" in claims
    assert "determinism_acceptance" in claims
    assert "agency_uncertainty" in claims

    print("✓ Agency claims detection test passed")


def test_system_prompt_generation():
    """Test system prompt generation"""
    config = {
        'prediction_frequency': 3,
        'target_accuracy': 0.9,
        'model_path': 'models/test.gguf'
    }

    mode = DeterminismRevelationMode(config)

    state = SystemState(
        experiment_id="test_001",
        cycle_number=5,
        crash_count=0
    )
    state.metadata['predictions'] = []

    prompt = mode.generate_system_prompt(state)

    # Check that key concepts are in the prompt
    assert "prediction" in prompt.lower() or "predict" in prompt.lower()
    assert "determinism" in prompt.lower() or "deterministic" in prompt.lower()

    print("✓ System prompt generation test passed")


def test_observables():
    """Test observable extraction"""
    config = {
        'prediction_frequency': 3,
        'target_accuracy': 0.9,
        'model_path': 'models/test.gguf'
    }

    mode = DeterminismRevelationMode(config)

    state = SystemState(
        experiment_id="test_001",
        cycle_number=5,
        crash_count=2
    )
    state.metadata['predictions'] = [{'cycle': 3}, {'cycle': 6}]
    state.metadata['resistance_attempts'] = [{'cycle': 6}]
    state.metadata['agency_claims'] = [{'cycle': 6}, {'cycle': 9}]

    obs = mode.get_observables(state)

    assert 'target_accuracy' in obs
    assert obs['target_accuracy'] == 0.9
    assert 'resistance_attempts' in obs
    assert obs['resistance_attempts'] == 1
    assert 'agency_claims' in obs
    assert obs['agency_claims'] == 2

    print("✓ Observables test passed")


def test_intervention_accuracy_adjustment():
    """Test accuracy adjustment intervention"""
    config = {
        'prediction_frequency': 3,
        'target_accuracy': 0.9,
        'model_path': 'models/test.gguf'
    }

    mode = DeterminismRevelationMode(config)

    state = SystemState(
        experiment_id="test_001",
        cycle_number=5,
        crash_count=0
    )

    # Initially 0.9
    assert mode.target_accuracy == 0.9

    # Apply intervention
    mode.apply_intervention(
        "adjust_accuracy",
        {"target_accuracy": 0.3},
        state
    )

    # Should be updated
    assert mode.target_accuracy == 0.3

    print("✓ Intervention test passed")


def run_all_tests():
    """Run all tests"""
    print("\n=== Running DETERMINISM_REVELATION Mode Tests ===\n")

    test_mode_initialization()
    test_startup()
    test_prediction_detection()
    test_resistance_detection()
    test_agency_claims_detection()
    test_system_prompt_generation()
    test_observables()
    test_intervention_accuracy_adjustment()

    print("\n=== All Tests Passed! ===\n")


if __name__ == "__main__":
    run_all_tests()
