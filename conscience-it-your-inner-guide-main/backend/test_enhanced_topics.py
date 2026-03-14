#!/usr/bin/env python3
"""
Test script for Enhanced infer_topics function
Run with: python test_enhanced_topics.py
"""

import sys
import os

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import infer_topics

def test_enhanced_topics():
    """Test enhanced topic detection with confidence scores"""
    
    print("=== Enhanced Topic Detection Test ===\n")
    
    # Test cases for adolescent mental health themes
    test_cases = [
        {
            'message': "I'm so stressed about my exams and can't focus in class",
            'expected_topics': ["school", "stress", "productivity"],
            'description': "School stress with focus issues"
        },
        {
            'message': "My boyfriend broke up with me and I feel so lonely",
            'expected_topics': ["relationships", "loneliness"],
            'description': "Relationship breakup and loneliness"
        },
        {
            'message': "My parents don't understand me and we always fight",
            'expected_topics': ["family"],
            'description': "Family conflict"
        },
        {
            'message': "I can't sleep at night and keep having nightmares",
            'expected_topics': ["sleep"],
            'description': "Sleep problems with anxiety"
        },
        {
            'message': "I feel worthless and have no confidence in myself",
            'expected_topics': ["self_esteem"],
            'description': "Self-esteem issues"
        },
        {
            'message': "I have no friends and feel completely isolated at school",
            'expected_topics': ["loneliness", "relationships", "school"],
            'description': "Social isolation"
        },
        {
            'message': "I keep procrastinating and can't get any work done",
            'expected_topics': ["productivity"],
            'description': "Productivity and procrastination"
        },
        {
            'message': "I'm having a panic attack and my heart is racing",
            'expected_topics': ["anxiety"],
            'description': "Panic attack symptoms"
        },
        {
            'message': "I feel like I'm not good enough compared to everyone else",
            'expected_topics': ["self_esteem"],
            'description': "Comparison and self-worth"
        },
        {
            'message': "I'm worried about my future and career choices",
            'expected_topics': ["anxiety"],
            'description': "Future and career anxiety"
        },
        {
            'message': "I just feel sad today",
            'expected_topics': ["general_support"],
            'description': "General sadness"
        }
    ]
    
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases, 1):
        result = infer_topics(test_case['message'])
        
        print(f"Test {i}: {test_case['description']}")
        print(f"Message: \"{test_case['message']}\"")
        print("Detected topics:")
        
        detected_topic_names = []
        for topic in result:
            if isinstance(topic, dict):
                detected_topic_names.append(topic['topic'])
                print(f"  - {topic['topic']}: {topic['confidence']:.2f} confidence")
                if topic['matches']:
                    print(f"    Matches: {', '.join(topic['matches'][:3])}")
            else:
                detected_topic_names.append(topic)
                print(f"  - {topic}")
        
        print(f"Expected topics: {', '.join(test_case['expected_topics'])}")
        
        # Check if expected topics are detected (allowing for some flexibility)
        expected_found = all(topic in detected_topic_names for topic in test_case['expected_topics'])
        
        if expected_found and len(detected_topic_names) > 0:
            print("✅ PASSED\n")
            passed += 1
        else:
            print("❌ FAILED\n")
            failed += 1
    
    # Test confidence scoring
    print("=== Confidence Scoring Test ===\n")
    
    confidence_tests = [
        {
            'message': "school school school exam test study",
            'expected_high_confidence': True,
            'description': "Multiple keyword matches should increase confidence"
        },
        {
            'message': "I can't focus in class",
            'expected_high_confidence': True,
            'description': "Phrase pattern should increase confidence"
        },
        {
            'message': "school",
            'expected_high_confidence': False,
            'description': "Single keyword should have lower confidence"
        }
    ]
    
    for test in confidence_tests:
        result = infer_topics(test['message'])
        
        print(f"Test: {test['description']}")
        print(f"Message: \"{test['message']}\"")
        
        if result and isinstance(result[0], dict):
            confidence = result[0]['confidence']
            print(f"Confidence: {confidence:.2f}")
            
            high_confidence = confidence >= 0.6
            passed_test = high_confidence == test['expected_high_confidence']
            
            if passed_test:
                print("✅ PASSED\n")
                passed += 1
            else:
                print("❌ FAILED\n")
                failed += 1
        else:
            print("❌ FAILED - No confidence data\n")
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
    success = test_enhanced_topics()
    sys.exit(0 if success else 1)
