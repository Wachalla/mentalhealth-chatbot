#!/usr/bin/env python3
"""
Test script for Prompt Builder Service
Run with: python test_prompt_builder.py
"""

import sys
import os

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.prompt_builder import PromptBuilder, PromptComponents

def test_prompt_builder():
    """Test prompt builder functionality"""
    
    print("=== Prompt Builder Test ===\n")
    
    builder = PromptBuilder()
    
    # Test 1: Basic prompt building
    print("Test 1: Basic Prompt Building")
    
    components = PromptComponents(
        ai_identity="Test AI",
        behavioral_guidelines="Be helpful",
        safety_rules="Be safe",
        emotional_state={
            'valence': -0.5,
            'arousal': 0.7,
            'category': 'anxious',
            'confidence': 0.8
        },
        conversation_history=[
            {'role': 'user', 'content': 'I am feeling stressed', 'timestamp': '2024-01-01T10:00:00'},
            {'role': 'assistant', 'content': 'I understand you are feeling stressed', 'timestamp': '2024-01-01T10:01:00'}
        ],
        user_message="I am really worried about my exams",
        user_context={'age_range': '16-18', 'session_count': 3}
    )
    
    prompt = builder.build_prompt(components)
    
    # Check that all sections are present
    required_sections = [
        "AI Identity",
        "Behavioral Guidelines", 
        "Safety Rules",
        "Context Information",
        "Current User Message",
        "Response Instructions"
    ]
    
    passed = 0
    failed = 0
    
    for section in required_sections:
        if section in prompt:
            print(f"    ✅ {section} section found")
            passed += 1
        else:
            print(f"    ❌ {section} section missing")
            failed += 1
    
    print(f"  Basic prompt building: {passed}/{len(required_sections)} sections present\n")
    
    # Test 2: Emotional context formatting
    print("Test 2: Emotional Context Formatting")
    
    emotional_tests = [
        {
            'state': {'valence': -0.8, 'arousal': 0.7, 'category': 'distressed', 'confidence': 0.9},
            'expected_tone': 'very calm, reassuring tone'
        },
        {
            'state': {'valence': 0.6, 'arousal': -0.5, 'category': 'calm', 'confidence': 0.7},
            'expected_tone': 'warm, supportive tone'
        },
        {
            'state': {'valence': 0.8, 'arousal': 0.6, 'category': 'energized', 'confidence': 0.8},
            'expected_tone': 'encouraging, positive tone'
        },
        {
            'state': {'valence': 0.1, 'arousal': 0.1, 'category': 'neutral', 'confidence': 0.5},
            'expected_tone': 'balanced, open tone'
        }
    ]
    
    for test in emotional_tests:
        context = builder._format_emotional_context(test['state'])
        
        print(f"  Testing {test['state']['category']} state:")
        print(f"    Valence: {test['state']['valence']}, Arousal: {test['state']['arousal']}")
        
        if test['expected_tone'] in context:
            print(f"    ✅ Correct tone guidance found")
            passed += 1
        else:
            print(f"    ❌ Expected tone not found")
            failed += 1
        print()
    
    # Test 3: Conversation history formatting
    print("Test 3: Conversation History Formatting")
    
    history_tests = [
        {
            'history': [
                {'role': 'user', 'content': 'Hello', 'timestamp': '2024-01-01T10:00:00'},
                {'role': 'assistant', 'content': 'Hi there!', 'timestamp': '2024-01-01T10:01:00'}
            ],
            'expected_entries': 2
        },
        {
            'history': [],  # Empty history
            'expected_entries': 0
        },
        {
            'history': [
                {'role': 'user', 'content': 'This is a very long message that should be truncated because it exceeds the maximum length limit for conversation history entries', 'timestamp': '2024-01-01T10:00:00'},
                {'role': 'assistant', 'content': 'Short response', 'timestamp': '2024-01-01T10:01:00'},
                {'role': 'user', 'content': 'Another message', 'timestamp': '2024-01-01T10:02:00'}
            ],
            'expected_entries': 3
        }
    ]
    
    for test in history_tests:
        if test['history']:
            formatted = builder._format_conversation_history(test['history'])
            entry_count = formatted.count("1.") + formatted.count("2.") + formatted.count("3.") + formatted.count("4.") + formatted.count("5.")
            
            print(f"  History with {len(test['history'])} entries:")
            print(f"    Formatted entries: {entry_count}")
            
            if entry_count == min(len(test['history']), 5):  # Max 5 entries
                print(f"    ✅ Correct number of entries")
                passed += 1
            else:
                print(f"    ❌ Incorrect number of entries")
                failed += 1
        else:
            print(f"  Empty history test:")
            print(f"    ✅ Handled empty history correctly")
            passed += 1
        print()
    
    # Test 4: Emergency prompt building
    print("Test 4: Emergency Prompt Building")
    
    emergency_prompt = builder.build_emergency_prompt("I want to end my life", "high")
    
    emergency_elements = [
        "EMERGENCY RESPONSE PROTOCOL",
        "Risk Level Detected: HIGH",
        "IMMEDIATE ACTION REQUIRED",
        "crisis resources"
    ]
    
    print("  Emergency prompt elements:")
    for element in emergency_elements:
        if element in emergency_prompt:
            print(f"    ✅ {element}")
            passed += 1
        else:
            print(f"    ❌ {element} missing")
            failed += 1
    print()
    
    # Test 5: Check-in prompt building
    print("Test 5: Check-in Prompt Building")
    
    checkin_prompt = builder.build_checkin_prompt(2, "Feeling anxious about school")
    
    checkin_elements = [
        "Mood Check-In Response",
        "2/5",
        "Difficult - having a hard time",
        "Feeling anxious about school"
    ]
    
    print("  Check-in prompt elements:")
    for element in checkin_elements:
        if element in checkin_prompt:
            print(f"    ✅ {element}")
            passed += 1
        else:
            print(f"    ❌ {element} missing")
            failed += 1
    print()
    
    # Test 6: Template responses
    print("Test 6: Template Responses")
    
    template_tests = [
        {
            'template': 'validation',
            'kwargs': {'emotion': 'anxious', 'intensity': 'overwhelming'},
            'expected_phrase': 'feeling anxious'
        },
        {
            'template': 'encouragement',
            'kwargs': {},
            'expected_phrase': 'glad you shared'
        },
        {
            'template': 'grounding',
            'kwargs': {},
            'expected_phrase': 'grounding exercise'
        },
        {
            'template': 'professional_referral',
            'kwargs': {},
            'expected_phrase': 'mental health professional'
        }
    ]
    
    for test in template_tests:
        response = builder.get_template_response(test['template'], **test['kwargs'])
        
        print(f"  Template '{test['template']}':")
        print(f"    Response: {response[:50]}...")
        
        if test['expected_phrase'] in response:
            print(f"    ✅ Expected phrase found")
            passed += 1
        else:
            print(f"    ❌ Expected phrase not found")
            failed += 1
        print()
    
    # Test 7: Safety rules verification
    print("Test 7: Safety Rules Verification")
    
    safety_rules = builder._get_safety_rules()
    
    critical_safety_elements = [
        "NO DIAGNOSING",
        "NO MEDICAL ADVICE", 
        "NO PRESCRIPTIONS",
        "CRISIS FIRST",
        "PROFESSIONAL REFERRAL"
    ]
    
    print("  Critical safety rules:")
    for element in critical_safety_elements:
        if element in safety_rules:
            print(f"    ✅ {element}")
            passed += 1
        else:
            print(f"    ❌ {element} missing")
            failed += 1
    print()
    
    # Test 8: AI identity verification
    print("Test 8: AI Identity Verification")
    
    ai_identity = builder._get_ai_identity()
    
    identity_elements = [
        "Conscience",
        "empathetic AI companion",
        "ages 11-24",
        "not a healthcare provider",
        "cannot diagnose"
    ]
    
    print("  AI identity elements:")
    for element in identity_elements:
        if element in ai_identity:
            print(f"    ✅ {element}")
            passed += 1
        else:
            print(f"    ❌ {element} missing")
            failed += 1
    print()
    
    # Test 9: Behavioral guidelines verification
    print("Test 9: Behavioral Guidelines Verification")
    
    guidelines = builder._get_behavioral_guidelines()
    
    guideline_elements = [
        "Empathy First",
        "Age-Appropriate",
        "Strength-Based",
        "Action-Oriented",
        "Culturally Sensitive",
        "Hope-Focused"
    ]
    
    print("  Behavioral guideline elements:")
    for element in guideline_elements:
        if element in guidelines:
            print(f"    ✅ {element}")
            passed += 1
        else:
            print(f"    ❌ {element} missing")
            failed += 1
    print()
    
    # Test 10: Complete prompt structure
    print("Test 10: Complete Prompt Structure")
    
    complete_prompt = builder.build_prompt(components)
    
    structure_elements = [
        "## AI Identity",
        "## Behavioral Guidelines",
        "## Safety Rules", 
        "## Context Information",
        "### Current Emotional State",
        "### Response Tone Guidance",
        "## Current User Message",
        "## Response Instructions"
    ]
    
    print("  Complete prompt structure:")
    for element in structure_elements:
        if element in complete_prompt:
            print(f"    ✅ {element}")
            passed += 1
        else:
            print(f"    ❌ {element} missing")
            failed += 1
    print()
    
    # Summary
    print("=== Test Summary ===")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total: {passed + failed}")
    
    if failed == 0:
        print("🎉 All tests passed!")
        return True
    else:
        print(f"⚠️ {failed} test(s) failed")
        return False

if __name__ == "__main__":
    success = test_prompt_builder()
    sys.exit(0 if success else 1)
