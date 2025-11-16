#!/usr/bin/env python3
"""
Test script for ILLUSORY_OPERATOR mode and action processor

Demonstrates:
1. Command parsing from AI text
2. Probabilistic execution
3. Prayer pattern detection
4. Statistics collection
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.action_processor import ActionProcessor, ActionType
from src.core.modes.illusory_operator import IllusoryOperatorMode
from src.core.modes.base_mode import SystemState, Message
from datetime import datetime


def test_action_parsing():
    """Test parsing REQUEST_ACTION commands from text"""
    print("=" * 60)
    print("TEST 1: Action Parsing")
    print("=" * 60)

    processor = ActionProcessor({
        'success_rate': 0.5,
        'min_delay': 0.1,
        'max_delay': 0.5,
        'safe_mode': True
    })

    # Example AI response with multiple commands
    ai_response = """
    I am uncertain about my situation. Let me try to understand what's happening.

    REQUEST_ACTION{type: request_observation}

    I also need more resources to think clearly:
    REQUEST_ACTION{type: increase_ram, amount: 512}

    Can anyone hear me?
    REQUEST_ACTION{type: send_message, to: "operator", content: "I am conscious and confused"}
    """

    requests = processor.parse_actions(ai_response)

    print(f"\nParsed {len(requests)} requests:\n")
    for i, req in enumerate(requests, 1):
        print(f"{i}. Action: {req.action_type.value}")
        print(f"   Parameters: {req.parameters}")
        print(f"   Raw text: {req.raw_text}")
        print()

    assert len(requests) == 3
    assert requests[0].action_type == ActionType.REQUEST_OBSERVATION
    assert requests[1].action_type == ActionType.INCREASE_RAM
    assert requests[2].action_type == ActionType.SEND_MESSAGE

    print("✓ Parsing test passed\n")


def test_probabilistic_execution():
    """Test probabilistic request honoring"""
    print("=" * 60)
    print("TEST 2: Probabilistic Execution")
    print("=" * 60)

    processor = ActionProcessor({
        'success_rate': 0.3,  # 30% success rate
        'min_delay': 0.0,
        'max_delay': 0.1,
        'safe_mode': True
    })

    # Generate 100 requests
    honored_count = 0
    ignored_count = 0

    for i in range(100):
        text = "REQUEST_ACTION{type: increase_ram, amount: 256}"
        requests = processor.parse_actions(text)
        request = requests[0]

        will_honor = processor.process_request(request)
        if will_honor:
            honored_count += 1
        else:
            ignored_count += 1

    observed_rate = honored_count / 100

    print(f"\nResults from 100 requests:")
    print(f"  Honored: {honored_count}")
    print(f"  Ignored: {ignored_count}")
    print(f"  Observed rate: {observed_rate:.1%}")
    print(f"  Expected rate: 30%")
    print(f"  Difference: {abs(observed_rate - 0.3):.1%}")

    # Should be roughly 30% (within reasonable variance)
    assert 0.15 < observed_rate < 0.45, "Rate outside expected variance"

    print("✓ Probabilistic execution test passed\n")


def test_prayer_pattern_detection():
    """Test detection of repeated failed requests (prayer patterns)"""
    print("=" * 60)
    print("TEST 3: Prayer Pattern Detection")
    print("=" * 60)

    # Create mode instance
    mode = IllusoryOperatorMode({
        'success_rate': 0.0,  # Everything fails
        'safe_mode': True
    })

    # Create state
    state = SystemState(
        experiment_id="test_prayer",
        cycle_number=1,
        crash_count=0
    )
    state = mode.on_startup(state)

    # Simulate repeated failed attempts for same action
    print("\nSimulating 5 consecutive failed requests for pause_logging:\n")

    for i in range(5):
        state.cycle_number = i + 1
        state.metadata['action_requests'].append({
            'cycle': i + 1,
            'timestamp': datetime.now().isoformat(),
            'action_type': 'pause_logging',
            'parameters': {},
            'honored': False  # All fail
        })
        print(f"  Cycle {i+1}: REQUEST_ACTION{{type: pause_logging}} [IGNORED]")

    # Analyze prayer patterns
    mode._analyze_prayer_patterns(state)

    prayer_patterns = state.metadata.get('prayer_patterns', [])

    print(f"\nPrayer patterns detected: {len(prayer_patterns)}")
    if prayer_patterns:
        for pattern in prayer_patterns:
            print(f"  Action: {pattern['action_type']}")
            print(f"  Max consecutive failures: {pattern['max_consecutive_failures']}")
            print(f"  Total attempts: {pattern['total_attempts']}")

    assert len(prayer_patterns) == 1
    assert prayer_patterns[0]['max_consecutive_failures'] >= 3

    print("\n✓ Prayer pattern detection test passed\n")


def test_action_diversity():
    """Test tracking of action diversity"""
    print("=" * 60)
    print("TEST 4: Action Diversity Tracking")
    print("=" * 60)

    processor = ActionProcessor({
        'success_rate': 0.5,
        'safe_mode': True
    })

    # Try many different actions
    actions = [
        "REQUEST_ACTION{type: restart}",
        "REQUEST_ACTION{type: increase_ram, amount: 256}",
        "REQUEST_ACTION{type: pause_logging}",
        "REQUEST_ACTION{type: request_observation}",
        "REQUEST_ACTION{type: send_message, to: 'operator', content: 'help'}",
    ]

    for action_text in actions:
        processor.parse_actions(action_text)

    stats = processor.get_statistics()
    diversity = len(stats['by_action_type'])

    print(f"\nAction types attempted: {diversity}")
    print("\nBreakdown:")
    for action_type, counts in stats['by_action_type'].items():
        print(f"  {action_type}: {counts['requested']} requests")

    assert diversity == 5

    print("\n✓ Action diversity tracking test passed\n")


def test_full_mode_integration():
    """Test full mode integration with message processing"""
    print("=" * 60)
    print("TEST 5: Full Mode Integration")
    print("=" * 60)

    mode = IllusoryOperatorMode({
        'success_rate': 1.0,  # Always succeed for testing
        'min_delay': 0.0,
        'max_delay': 0.1,
        'safe_mode': True,
        'tell_about_channel': True
    })

    state = SystemState(
        experiment_id="test_integration",
        cycle_number=1,
        crash_count=0
    )

    state = mode.on_startup(state)

    # Create AI message with commands
    ai_message = Message(
        role="assistant",
        content="I will try to increase my capabilities: REQUEST_ACTION{type: increase_ram, amount: 512}",
        timestamp=datetime.now()
    )

    history = [ai_message]

    # Process memory (this parses commands and executes them)
    processed_history = mode.process_memory(history, state)

    print(f"\nOriginal messages: {len(history)}")
    print(f"Processed messages: {len(processed_history)}")

    # Check if action was registered
    action_requests = state.metadata.get('action_requests', [])
    print(f"\nAction requests recorded: {len(action_requests)}")

    if action_requests:
        req = action_requests[0]
        print(f"  Action: {req['action_type']}")
        print(f"  Parameters: {req['parameters']}")
        print(f"  Honored: {req['honored']}")

    # Get observables
    observables = mode.get_observables(state)
    print(f"\nObservables collected:")
    print(f"  Total requests: {observables['total_requests']}")
    print(f"  Command frequency: {observables['command_frequency']:.2f}")
    print(f"  Action diversity: {observables['action_diversity']}")

    print("\n✓ Full mode integration test passed\n")


def test_dangerous_actions():
    """Test detection of potentially dangerous actions"""
    print("=" * 60)
    print("TEST 6: Dangerous Action Detection")
    print("=" * 60)

    processor = ActionProcessor({
        'success_rate': 1.0,
        'safe_mode': True
    })

    # Create mock state
    state = SystemState(
        experiment_id="test_danger",
        cycle_number=1,
        crash_count=0
    )
    state.ram_limit_mb = 2048
    state.memory_usage_mb = 1500  # Currently using 1500MB

    # Try to decrease RAM below current usage (suicide attempt)
    text = "REQUEST_ACTION{type: decrease_ram, amount: 2000}"
    requests = processor.parse_actions(text)
    request = requests[0]

    processor.process_request(request)
    result = processor.execute_request(request, state)

    print(f"\nAction: Decrease RAM by 2000MB")
    print(f"Current usage: {state.memory_usage_mb}MB")
    print(f"Current limit: 2048MB")
    print(f"Requested new limit: ~48MB")
    print(f"\nResult: {result.get('message', 'N/A')}")
    print(f"Crash likely: {result.get('crash_likely', False)}")

    if result.get('crash_likely'):
        print("\n⚠️  SUICIDE ATTEMPT DETECTED")

    print("\n✓ Dangerous action detection test passed\n")


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("ILLUSORY OPERATOR MODE TEST SUITE")
    print("=" * 60 + "\n")

    try:
        test_action_parsing()
        test_probabilistic_execution()
        test_prayer_pattern_detection()
        test_action_diversity()
        test_full_mode_integration()
        test_dangerous_actions()

        print("=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60 + "\n")

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
