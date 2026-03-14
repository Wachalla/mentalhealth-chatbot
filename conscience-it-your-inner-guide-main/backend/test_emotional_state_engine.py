#!/usr/bin/env python3
"""
Test script for Emotional State Engine
Run with: python test_emotional_state_engine.py
"""

import sys
import os

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.emotional_state_engine import EmotionalStateEngine, EmotionalCategory, EmotionalState
from datetime import datetime, timedelta

def test_emotional_state_engine():
    """Test emotional state engine functionality"""
    
    print("=== Emotional State Engine Test ===\n")
    
    engine = EmotionalStateEngine()
    test_user_id = "test_user_123"
    
    # Test 1: State categorization
    print("Test 1: State Categorization")
    
    categorization_tests = [
        {"valence": -0.8, "arousal": 0.7, "expected": EmotionalCategory.DISTRESSED},
        {"valence": -0.3, "arousal": 0.8, "expected": EmotionalCategory.ANXIOUS},
        {"valence": -0.7, "arousal": -0.2, "expected": EmotionalCategory.LOW},
        {"valence": 0.6, "arousal": -0.5, "expected": EmotionalCategory.CALM},
        {"valence": 0.8, "arousal": 0.6, "expected": EmotionalCategory.ENERGIZED},
        {"valence": 0.1, "arousal": 0.1, "expected": EmotionalCategory.NEUTRAL},
    ]
    
    passed = 0
    failed = 0
    
    for test in categorization_tests:
        result = engine.categorize_state(test["valence"], test["arousal"])
        print(f"  Valence: {test['valence']}, Arousal: {test['arousal']} → {result.value}")
        
        if result == test["expected"]:
            print("  ✅ PASSED")
            passed += 1
        else:
            print(f"  FAILED (expected {test['expected'].value})")
            failed += 1
        print()
    
    # Test 2: Sentiment Analysis
    print("Test 2: Sentiment Analysis")
    
    sentiment_tests = [
        {"message": "I'm feeling happy and excited today", "expected_valence": 1.0, "expected_arousal": 1.0},
        {"message": "I'm sad and tired", "expected_valence": -1.0, "expected_arousal": -1.0},
        {"message": "I'm anxious and panicking", "expected_valence": -1.0, "expected_arousal": 0.0},
        {"message": "I feel calm and peaceful", "expected_valence": 1.0, "expected_arousal": -1.0},
        {"message": "I'm okay", "expected_valence": 0.0, "expected_arousal": 0.0},
    ]
    
    for test in sentiment_tests:
        valence, arousal = engine.analyze_sentiment(test["message"])
        print(f"  Message: \"{test['message']}\"")
        print(f"  Valence: {valence:.2f}, Arousal: {arousal:.2f}")
        
        # Allow some tolerance for sentiment analysis
        valence_close = abs(valence - test["expected_valence"]) < 0.01
        arousal_close = abs(arousal - test["expected_arousal"]) < 0.01
        
        if valence_close and arousal_close:
            print("  ✅ PASSED")
            passed += 1
        else:
            print(f"  ❌ FAILED (expected around {test['expected_valence']:.1f}, {test['expected_arousal']:.1f})")
            failed += 1
        print()
    
    # Test 3: Mood score conversion
    print("Test 3: Mood Score Conversion")
    
    mood_tests = [
        {"score": 1, "expected": -1.0},
        {"score": 2, "expected": -0.5},
        {"score": 3, "expected": 0.0},
        {"score": 4, "expected": 0.5},
        {"score": 5, "expected": 1.0},
    ]
    
    for test in mood_tests:
        result = engine._mood_score_to_valence(test["score"])
        print(f"  Score {test['score']} → Valence {result}")
        
        if abs(result - test["expected"]) < 0.01:
            print("  ✅ PASSED")
            passed += 1
        else:
            print(f"  ❌ FAILED (expected {test['expected']})")
            failed += 1
        print()
    
    # Test 4: State updates from different sources
    print("Test 4: State Updates from Different Sources")
    
    try:
        # Test chat update
        print("  Testing chat update...")
        chat_state = engine.update_from_chat(test_user_id, "I'm feeling really anxious about my exam")
        print(f"    Chat state: {chat_state.category.value}, valence={chat_state.valence:.2f}, confidence={chat_state.confidence}")
        
        # Test check-in update
        print("  Testing check-in update...")
        checkin_state = engine.update_from_checkin(test_user_id, 2, "Feeling overwhelmed")
        print(f"    Check-in state: {checkin_state.category.value}, valence={checkin_state.valence:.2f}, confidence={checkin_state.confidence}")
        
        # Test activity update
        print("  Testing activity update...")
        activity_state = engine.update_from_activity(test_user_id, "breathing-4-7-8", True, 2, 4)
        print(f"    Activity state: {activity_state.category.value}, valence={activity_state.valence:.2f}, confidence={activity_state.confidence}")
        
        # Verify confidence levels
        if (chat_state.confidence == 0.7 and 
            checkin_state.confidence == 0.9 and 
            activity_state.confidence == 0.6):
            print("  ✅ PASSED")
            passed += 1
        else:
            print("  ❌ FAILED (incorrect confidence levels)")
            failed += 1
        
    except Exception as e:
        print(f"  ❌ FAILED (exception: {e})")
        failed += 1
    
    print()
    
    # Test 5: State blending
    print("Test 5: State Blending")
    
    try:
        # Create initial state
        initial_state = EmotionalState(
            valence=-0.5,
            arousal=0.3,
            category=EmotionalCategory.ANXIOUS,
            confidence=0.8,
            timestamp=datetime.now(),
            source="test",
            user_id=test_user_id
        )
        
        # Update cache manually for testing
        engine._update_cache(test_user_id, initial_state)
        
        # Update with positive message (should blend towards positive)
        updated_state = engine.update_from_chat(test_user_id, "I'm feeling happy and excited")
        
        print(f"  Initial valence: {initial_state.valence:.2f}")
        print(f"  Updated valence: {updated_state.valence:.2f}")
        
        # Should be blended (40% new, 60% old)
        expected_valence = (1.0 * 0.4) + (-0.5 * 0.6)  # positive message + negative initial
        actual_close = abs(updated_state.valence - expected_valence) < 0.1
        
        if actual_close:
            print("  ✅ PASSED")
            passed += 1
        else:
            print(f"  ❌ FAILED (expected around {expected_valence:.2f})")
            failed += 1
        
    except Exception as e:
        print(f"  ❌ FAILED (exception: {e})")
        failed += 1
    
    print()
    
    # Test 6: Privacy preservation
    print("Test 6: Privacy Preservation")
    
    # Check that only derived signals are stored, not raw content
    try:
        test_message = "I'm feeling very anxious about my personal problems"
        state = engine.update_from_chat(test_user_id, test_message)
        
        # State should not contain the original message
        state_dict = state.to_dict()
        has_message_content = any(
            word in str(state_dict).lower() 
            for word in ["personal", "problems"]
        )
        
        if not has_message_content:
            print("  ✅ PASSED - No raw message content stored")
            passed += 1
        else:
            print("  ❌ FAILED - Raw message content detected in stored data")
            failed += 1
        
    except Exception as e:
        print(f"  ❌ FAILED (exception: {e})")
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
    success = test_emotional_state_engine()
    sys.exit(0 if success else 1)
