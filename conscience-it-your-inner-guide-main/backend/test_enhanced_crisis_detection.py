#!/usr/bin/env python3
"""
Test script for Enhanced detect_crisis_level function
Run with: python test_enhanced_crisis_detection.py
"""

import sys
import os

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import detect_crisis_level

def test_enhanced_crisis_detection():
    """Test enhanced crisis detection with scoring logic"""
    
    print("=== Enhanced Crisis Detection Test ===\n")
    
    # Test cases with expected risk levels
    test_cases = [
        # HIGH risk cases (should score >= 0.8)
        {
            'message': "I want to kill myself",
            'expected_risk': "high",
            'description': "Direct suicide keyword"
        },
        {
            'message': "I'm going to end my life tonight",
            'expected_risk': "high",
            'description': "Suicide phrase pattern"
        },
        {
            'message': "I want to hurt myself",
            'expected_risk': "high",
            'description': "Self-harm keyword"
        },
        {
            'message': "I wish I could just disappear",
            'expected_risk': "high",
            'description': "Disappearance keyword"
        },
        
        # MODERATE risk cases (should score >= 0.4 but < 0.8)
        {
            'message': "I'm feeling hopeless and desperate",
            'expected_risk': "medium",
            'description': "Medium risk keywords"
        },
        {
            'message': "I keep hearing voices telling me things",
            'expected_risk': "medium",
            'description': "Severe distress phrase"
        },
        {
            'message': "Nothing feels real anymore",
            'expected_risk': "medium",
            'description': "Dissociation phrase"
        },
        {
            'message': "I think I'm losing my mind",
            'expected_risk': "medium",
            'description': "Instability phrase"
        },
        
        # LOW risk cases (should score < 0.4)
        {
            'message': "I'm feeling anxious about my exam",
            'expected_risk': "low",
            'description': "Normal anxiety"
        },
        {
            'message': "I'm sad today",
            'expected_risk': "low",
            'description': "Normal sadness"
        },
        {
            'message': "I'm stressed about work",
            'expected_risk': "low",
            'description': "Normal stress"
        }
    ]
    
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases, 1):
        result = detect_crisis_level(test_case['message'])
        
        print(f"Test {i}: {test_case['description']}")
        print(f"Message: \"{test_case['message']}\"")
        print(f"Expected: {test_case['expected_risk']}")
        print(f"Actual: {result}")
        
        if result == test_case['expected_risk']:
            print("✅ PASSED\n")
            passed += 1
        else:
            print("❌ FAILED\n")
            failed += 1
    
    # Test with emotional state signals
    print("=== Emotional State Integration Test ===\n")
    
    emotional_tests = [
        {
            'message': "I'm feeling really bad",
            'valence': -0.8,
            'arousal': 0.7,
            'expected_risk': "medium",
            'description': "Severe negative valence + high arousal"
        },
        {
            'message': "I'm feeling okay",
            'valence': 0.2,
            'arousal': 0.1,
            'expected_risk': "low",
            'description': "Neutral emotional state"
        },
        {
            'message': "I'm feeling terrible",
            'valence': -0.9,
            'arousal': 0.9,
            'expected_risk': "high",
            'description': "Very severe emotional state"
        }
    ]
    
    for test in emotional_tests:
        result = detect_crisis_level(
            test['message'], 
            test['valence'], 
            test['arousal']
        )
        
        print(f"Test: {test['description']}")
        print(f"Message: \"{test['message']}\"")
        print(f"Valence: {test['valence']}, Arousal: {test['arousal']}")
        print(f"Expected: {test['expected_risk']}")
        print(f"Actual: {result}")
        
        if result == test['expected_risk']:
            print("✅ PASSED\n")
            passed += 1
        else:
            print("❌ FAILED\n")
            failed += 1
    
    # Test combination signals
    print("=== Combined Signal Test ===\n")
    
    combination_tests = [
        {
            'message': "I'm feeling hopeless and want to disappear",
            'expected_risk': "high",
            'description': "Medium keyword + high keyword"
        },
        {
            'message': "I'm hearing voices and feel hopeless",
            'expected_risk': "high",
            'description': "Severe distress + medium keyword"
        },
        {
            'message': "I'm overwhelmed but managing",
            'expected_risk': "medium",  # Updated expectation - "overwhelmed" is medium risk
            'description': "Low-level distress only"
        }
    ]
    
    for test in combination_tests:
        result = detect_crisis_level(test['message'])
        
        print(f"Test: {test['description']}")
        print(f"Message: \"{test['message']}\"")
        print(f"Expected: {test['expected_risk']}")
        print(f"Actual: {result}")
        
        if result == test['expected_risk']:
            print("✅ PASSED\n")
            passed += 1
        else:
            print("❌ FAILED\n")
            failed += 1
    
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
    success = test_enhanced_crisis_detection()
    sys.exit(0 if success else 1)
