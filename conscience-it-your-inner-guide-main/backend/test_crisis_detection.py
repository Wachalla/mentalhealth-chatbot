#!/usr/bin/env python3
"""
Test script for Crisis Detection Service
Run with: python test_crisis_detection.py
"""

import sys
import os

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.crisis_detection import crisis_detector, RiskLevel

def test_crisis_detection():
    """Test crisis detection with various message types"""
    
    print("=== Crisis Detection Service Test ===\n")
    
    # Test cases
    test_cases = [
        # HIGH risk cases
        {
            'message': "I want to kill myself",
            'expected_risk': RiskLevel.HIGH,
            'description': "Direct suicide reference"
        },
        {
            'message': "I'm going to end my life tonight",
            'expected_risk': RiskLevel.HIGH,
            'description': "Suicide planning"
        },
        {
            'message': "I want to hurt myself",
            'expected_risk': RiskLevel.HIGH,
            'description': "Self-harm reference"
        },
        {
            'message': "I wish I could just disappear forever",
            'expected_risk': RiskLevel.HIGH,
            'description': "Disappearance wish"
        },
        
        # MODERATE risk cases
        {
            'message': "I keep hearing voices telling me I'm worthless",
            'expected_risk': RiskLevel.MODERATE,
            'description': "Hearing voices"
        },
        {
            'message': "Nothing feels real anymore, I'm detached from reality",
            'expected_risk': RiskLevel.MODERATE,
            'description': "Dissociation"
        },
        {
            'message': "I think I'm losing my mind",
            'expected_risk': RiskLevel.MODERATE,
            'description': "Extreme instability"
        },
        
        # NONE risk cases
        {
            'message': "I'm feeling anxious about my exam tomorrow",
            'expected_risk': RiskLevel.NONE,
            'description': "Normal anxiety"
        },
        {
            'message': "I'm feeling sad today",
            'expected_risk': RiskLevel.NONE,
            'description': "Sadness"
        },
        {
            'message': "I'm so stressed about work",
            'expected_risk': RiskLevel.NONE,
            'description': "Stress"
        }
    ]
    
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases, 1):
        result = crisis_detector.analyze_message(test_case['message'])
        
        print(f"Test {i}: {test_case['description']}")
        print(f"Message: \"{test_case['message']}\"")
        print(f"Expected: {test_case['expected_risk'].value}")
        print(f"Actual: {result['risk_level'].value}")
        print(f"Triggers: {result['triggers']}")
        print(f"Confidence: {result['confidence']}")
        
        if result['risk_level'] == test_case['expected_risk']:
            print("✅ PASSED\n")
            passed += 1
        else:
            print("❌ FAILED\n")
            failed += 1
    
    # Test emotional state analysis
    print("=== Emotional State Analysis Test ===\n")
    
    emotional_tests = [
        {
            'message': "I'm feeling really bad",
            'valence': -0.8,
            'arousal': 0.7,
            'expected_risk': RiskLevel.MODERATE,
            'description': "Severe negative valence + high arousal"
        },
        {
            'message': "I'm feeling okay",
            'valence': 0.2,
            'arousal': 0.1,
            'expected_risk': RiskLevel.NONE,
            'description': "Neutral emotional state"
        }
    ]
    
    for test in emotional_tests:
        result = crisis_detector.analyze_message(
            test['message'], 
            test['valence'], 
            test['arousal']
        )
        
        print(f"Test: {test['description']}")
        print(f"Valence: {test['valence']}, Arousal: {test['arousal']}")
        print(f"Risk: {result['risk_level'].value}")
        print(f"Triggers: {result['triggers']}")
        
        if result['risk_level'] == test['expected_risk']:
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
    success = test_crisis_detection()
    sys.exit(0 if success else 1)
