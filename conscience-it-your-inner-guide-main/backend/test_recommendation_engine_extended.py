#!/usr/bin/env python3
"""
Test script for Extended Recommendation Engine with Activity History
Run with: python test_recommendation_engine_extended.py
"""

import sys
import os
from datetime import datetime, timedelta

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.recommendation_engine_extended import RecommendationEngineExtended

def test_activity_history_tracking():
    """Test activity history tracking functionality"""
    
    print("=== Extended Recommendation Engine Test ===")
    print("Testing Activity History Tracking\n")
    
    engine = RecommendationEngineExtended()
    
    # Test 1: Record activity completion
    print("Test 1: Record Activity Completion")
    
    test_user_id = "test_user_123"
    
    # Record some test activities
    activities_to_record = [
        {
            'activity_id': 'breathing-4-7-8',
            'activity_type': 'breathing',
            'mood_before': -0.5,
            'mood_after': 0.2,
            'timestamp': datetime.now() - timedelta(days=5)
        },
        {
            'activity_id': 'breathing-4-7-8',
            'activity_type': 'breathing',
            'mood_before': -0.3,
            'mood_after': 0.1,
            'timestamp': datetime.now() - timedelta(days=3)
        },
        {
            'activity_id': 'grounding-5-4-3-2-1',
            'activity_type': 'grounding',
            'mood_before': -0.8,
            'mood_after': -0.2,
            'timestamp': datetime.now() - timedelta(days=2)
        },
        {
            'activity_id': 'mindfulness-body-scan',
            'activity_type': 'meditation',
            'mood_before': -0.4,
            'mood_after': 0.3,
            'timestamp': datetime.now() - timedelta(days=1)
        },
        {
            'activity_id': 'breathing-4-7-8',
            'activity_type': 'breathing',
            'mood_before': -0.6,
            'mood_after': -0.1,
            'timestamp': datetime.now() - timedelta(hours=12)
        }
    ]
    
    passed = 0
    failed = 0
    
    for i, activity in enumerate(activities_to_record):
        success = engine.record_activity_completion(
            test_user_id,
            activity['activity_id'],
            activity['activity_type'],
            activity['mood_before'],
            activity['mood_after'],
            activity['timestamp']
        )
        
        print(f"  Recording activity {i+1}: {activity['activity_id']}")
        print(f"    Mood change: {activity['mood_before']:.1f} → {activity['mood_after']:.1f}")
        print(f"    Improvement: {activity['mood_after'] - activity['mood_before']:.1f}")
        
        if success:
            print("    ✅ Recorded successfully")
            passed += 1
        else:
            print("    ❌ Failed to record")
            failed += 1
        print()
    
    # Test 2: Retrieve activity history
    print("Test 2: Retrieve Activity History")
    
    user_history = engine.get_user_activity_history(test_user_id)
    
    print(f"  Retrieved {len(user_history)} activity records")
    
    if len(user_history) == len(activities_to_record):
        print("  ✅ All records retrieved")
        passed += 1
    else:
        print("  ❌ Missing records")
        failed += 1
    
    # Check record details
    for i, record in enumerate(user_history):
        expected = activities_to_record[i]
        if (record.activity_id == expected['activity_id'] and
            record.activity_type == expected['activity_type'] and
            record.mood_before == expected['mood_before'] and
            record.mood_after == expected['mood_after']):
            print(f"    Record {i+1}: ✅ Data matches")
        else:
            print(f"    Record {i+1}: ❌ Data mismatch")
            failed += 1
    print()
    
    # Test 3: Calculate activity effectiveness
    print("Test 3: Calculate Activity Effectiveness")
    
    # Test breathing activity effectiveness
    breathing_effectiveness = engine.get_activity_effectiveness(test_user_id, 'breathing-4-7-8')
    
    print("  Breathing 4-7-8 Effectiveness:")
    print(f"    Sample size: {breathing_effectiveness['sample_size']}")
    print(f"    Average improvement: {breathing_effectiveness['average_improvement']:.3f}")
    print(f"    Success rate: {breathing_effectiveness['success_rate']:.2%}")
    print(f"    Confidence: {breathing_effectiveness['confidence']:.2f}")
    
    # Expected: 3 breathing activities with mixed results
    if breathing_effectiveness['sample_size'] == 3:
        print("    ✅ Correct sample size")
        passed += 1
    else:
        print("    ❌ Incorrect sample size")
        failed += 1
    
    if breathing_effectiveness['average_improvement'] > 0:  # Should be positive overall
        print("    ✅ Positive average improvement")
        passed += 1
    else:
        print("    ❌ Negative or zero improvement")
        failed += 1
    print()
    
    # Test grounding activity effectiveness
    grounding_effectiveness = engine.get_activity_effectiveness(test_user_id, 'grounding-5-4-3-2-1')
    
    print("  Grounding 5-4-3-2-1 Effectiveness:")
    print(f"    Sample size: {grounding_effectiveness['sample_size']}")
    print(f"    Average improvement: {grounding_effectiveness['average_improvement']:.3f}")
    print(f"    Success rate: {grounding_effectiveness['success_rate']:.2%}")
    
    if grounding_effectiveness['sample_size'] == 1:
        print("    ✅ Correct sample size")
        passed += 1
    else:
        print("    ❌ Incorrect sample size")
        failed += 1
    print()
    
    # Test 4: History-based scoring
    print("Test 4: History-Based Scoring")
    
    # Test activities with different history
    test_activities = [
        {
            'activity_id': 'breathing-4-7-8',
            'activity_type': 'breathing',
            'description': 'Well-established activity with history'
        },
        {
            'activity_id': 'grounding-5-4-3-2-1',
            'activity_type': 'grounding',
            'description': 'Single use activity'
        },
        {
            'activity_id': 'new-activity',
            'activity_type': 'reflection',
            'description': 'New activity with no history'
        }
    ]
    
    for activity in test_activities:
        score = engine._calculate_history_score(activity, user_history)
        
        print(f"  {activity['description']}:")
        print(f"    Activity ID: {activity['activity_id']}")
        print(f"    History score: {score:.3f}")
        
        if activity['activity_id'] == 'breathing-4-7-8':
            # Should have the highest score due to positive history
            if score > 0:
                print("    ✅ Positive history score")
                passed += 1
            else:
                print("    ❌ Negative or zero score")
                failed += 1
        elif activity['activity_id'] == 'new-activity':
            # Should have zero score (no history)
            if score == 0:
                print("    ✅ No history score (as expected)")
                passed += 1
            else:
                print("    ❌ Unexpected score for new activity")
                failed += 1
        print()
    
    # Test 5: Recent performance tracking
    print("Test 5: Recent Performance Tracking")
    
    breathing_records = [r for r in user_history if r.activity_id == 'breathing-4-7-8']
    recent_performance = engine._get_recent_performance(breathing_records)
    
    print("  Breathing activity recent performance:")
    print(f"    Trend: {recent_performance['trend']}")
    print(f"    Last improvement: {recent_performance['last_improvement']:.3f}")
    print(f"    Recent average: {recent_performance['recent_average']:.3f}")
    
    if 'trend' in recent_performance:
        print("    ✅ Trend calculated")
        passed += 1
    else:
        print("    ❌ No trend data")
        failed += 1
    print()
    
    # Test 6: History insights generation
    print("Test 6: History Insights Generation")
    
    insights = engine._get_history_insights(user_history, 'anxious')
    
    print("  User activity insights:")
    print(f"    Total activities: {insights['total_activities']}")
    favorite_str = ", ".join([f"{f['type']} ({f['count']})" for f in insights['favorite_types']])
    effective_str = ", ".join([f"{f['type']} ({f['avg_improvement']:.3f})" for f in insights['most_effective']])
    print(f"    Favorite types: {favorite_str}")
    print(f"    Most effective: {effective_str}")
    print(f"    Recommendation confidence: {insights['recommendation_confidence']}")
    
    if insights['total_activities'] > 0:
        print("    ✅ Activities tracked")
        passed += 1
    else:
        print("    ❌ No activities tracked")
        failed += 1
    
    if insights['favorite_types']:
        print("    ✅ Favorite types identified")
        passed += 1
    else:
        print("    ❌ No favorite types")
        failed += 1
    print()
    
    # Test 7: Personalization scoring
    print("Test 7: Personalization Scoring")
    
    for activity in test_activities:
        personalization_score = engine._calculate_personalization_score(activity, user_history)
        
        print(f"  {activity['description']}:")
        print(f"    Personalization score: {personalization_score:.2f}")
        
        if activity['activity_id'] == 'breathing-4-7-8':
            # Should have highest personalization score
            if personalization_score > 0.5:
                print("    ✅ High personalization score")
                passed += 1
            else:
                print("    ❌ Low personalization score")
                failed += 1
        elif activity['activity_id'] == 'new-activity':
            # Should have zero personalization score
            if personalization_score == 0:
                print("    ✅ No personalization (new activity)")
                passed += 1
            else:
                print("    ❌ Unexpected personalization for new activity")
                failed += 1
        print()
    
    # Test 8: Edge cases
    print("Test 8: Edge Cases")
    
    # Test with non-existent user
    empty_history = engine.get_user_activity_history("non_existent_user")
    
    print("  Non-existent user history:")
    print(f"    Records found: {len(empty_history)}")
    
    if len(empty_history) == 0:
        print("    ✅ Empty history for non-existent user")
        passed += 1
    else:
        print("    ❌ Unexpected records for non-existent user")
        failed += 1
    
    # Test effectiveness for non-existent activity
    no_activity_effectiveness = engine.get_activity_effectiveness(test_user_id, "non_existent_activity")
    
    print("  Non-existent activity effectiveness:")
    print(f"    Sample size: {no_activity_effectiveness['sample_size']}")
    
    if no_activity_effectiveness['sample_size'] == 0:
        print("    ✅ No data for non-existent activity")
        passed += 1
    else:
        print("    ❌ Unexpected data for non-existent activity")
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
    success = test_activity_history_tracking()
    sys.exit(0 if success else 1)
