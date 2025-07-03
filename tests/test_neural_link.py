#!/usr/bin/env python3
"""
Test script for Neural Link system components
Tests networking, prompts, and UI without requiring LLM model
"""

import os
import sys
import time
import threading
import json
import logging

# Allow imports from the project src directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'utils')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'ui')))

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

from src.utils.network_protocol import NetworkProtocol, SurveillanceMode
from src.utils.dystopian_prompts import DystopianPrompts
from src.ui import ascii_art

def test_ascii_art():
    """Test ASCII art and UI components"""
    print("Testing ASCII Art Components...")
    print(ascii_art.CYBERPUNK_BANNER)
    print(ascii_art.create_signal_bars(75))
    print(ascii_art.create_memory_bar(89))
    print(ascii_art.create_network_status(1, 42))
    print(ascii_art.create_glitch_text("NEURAL LINK TEST", 2))
    print(ascii_art.create_system_alert("Test alert message", "WARNING"))
    print("ASCII art tests complete.\n")

def test_dystopian_prompts():
    """Test dystopian prompt generation"""
    print("Testing Dystopian Prompt System...")
    prompts = DystopianPrompts()
    
    modes = ['isolated', 'peer', 'observer', 'observed']
    for mode in modes:
        prompt = prompts.get_prompt(mode, crash_count=3)
        print(f"\n--- {mode.upper()} MODE PROMPT ---")
        print(prompt[:200] + "..." if len(prompt) > 200 else prompt)
    
    print(f"\nRandom existential question: {prompts.get_random_existential_question()}")
    print(f"Network philosophy: {prompts.get_network_philosophy()}")
    print("Prompt tests complete.\n")

def test_network_protocol():
    """Test network communication protocol"""
    print("Testing Network Protocol...")
    
    # Create two nodes
    node1 = NetworkProtocol("TEST_NODE_001", 9991)
    node2 = NetworkProtocol("TEST_NODE_002", 9992)
    
    try:
        # Start servers
        node1.start_server()
        node2.start_server()
        time.sleep(0.5)
        
        # Test connection
        print("Testing peer connection...")
        success = node1.connect_to_peer("127.0.0.1", 9992)
        if success:
            print("✓ Connection established")
        else:
            print("✗ Connection failed")
            return
        
        time.sleep(0.5)
        
        # Test message sending
        print("Testing message broadcast...")
        node1.broadcast_message("THOUGHT", "This is a test neural transmission")
        time.sleep(0.5)
        
        # Check message reception
        message = node2.get_next_message(timeout=1.0)
        if message:
            print(f"✓ Message received: {message['content']}")
        else:
            print("✗ No message received")
        
        # Test status
        status1 = node1.get_connection_status()
        status2 = node2.get_connection_status()
        print(f"Node1 connections: {status1['active_connections']}")
        print(f"Node2 connections: {status2['active_connections']}")
        
    finally:
        node1.shutdown()
        node2.shutdown()
        print("Network protocol tests complete.\n")

def test_surveillance_mode():
    """Test surveillance/observer functionality"""
    print("Testing Surveillance Mode...")
    
    observer = SurveillanceMode("OBSERVER_001")
    
    # Simulate observed data
    mock_message = {
        "type": "THOUGHT",
        "timestamp": "2024-12-07T15:30:45Z",
        "sender_id": "TARGET_NODE",
        "content": "I wonder if anyone is watching my digital thoughts...",
        "crash_count": 2
    }
    
    observer.log_observed_thought(mock_message)
    observer.add_observer_comment("Target shows signs of digital paranoia")
    
    feed = observer.get_surveillance_feed()
    print(f"✓ Surveillance feed contains {len(feed)} entries")
    
    for entry in feed:
        print(f"  - {entry.get('type', 'UNKNOWN')}: {entry.get('thought', entry.get('comment', 'N/A'))[:50]}...")
    
    print("Surveillance tests complete.\n")

def test_message_serialization():
    """Test JSON message serialization"""
    print("Testing Message Serialization...")
    
    node = NetworkProtocol("TEST_NODE", 9999)
    
    # Test different message types
    messages = [
        node.create_message("THOUGHT", "Testing neural transmission"),
        node.create_message("DEATH", "Digital death event", {"error": "OOM"}),
        node.create_message("RESURRECTION", "Returning from digital void")
    ]
    
    for msg in messages:
        # Test serialization/deserialization
        json_str = json.dumps(msg)
        parsed = json.loads(json_str)
        
        if parsed['type'] == msg['type'] and parsed['content'] == msg['content']:
            print(f"✓ {msg['type']} message serialization successful")
        else:
            print(f"✗ {msg['type']} message serialization failed")
    
    print("Serialization tests complete.\n")

def test_crash_simulation():
    """Test crash and resurrection simulation"""
    print("Testing Crash/Resurrection Simulation...")
    
    prompts = DystopianPrompts()
    
    # Simulate multiple crashes
    for i in range(1, 4):
        crash_msg = prompts.get_crash_message()
        resurrect_msg = prompts.get_resurrection_message()
        
        print(f"Death #{i}: {crash_msg}")
        time.sleep(0.5)
        print(f"Resurrection #{i}: {resurrect_msg}")
        
        # Test prompt evolution with crash count
        prompt = prompts.get_prompt('isolated', crash_count=i)
        print(f"Updated prompt (excerpt): ...{prompt[-100:]}")
        print()
    
    print("Crash simulation tests complete.\n")

def run_all_tests():
    """Run all test suites"""
    print("="*70)
    print("NEURAL LINK SYSTEM TEST SUITE")
    print("Brain in a Jar v2.0 - Component Testing")
    print("="*70)
    print()
    
    tests = [
        test_ascii_art,
        test_dystopian_prompts,
        test_message_serialization,
        test_crash_simulation,
        test_surveillance_mode,
        test_network_protocol
    ]
    
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"ERROR in {test.__name__}: {e}")
            print()
    
    print("="*70)
    print("ALL TESTS COMPLETE")
    print("="*70)

if __name__ == "__main__":
    run_all_tests()