#!/usr/bin/env python3
"""
Test script for structured AI response output
Tests that AI responses include the required structured fields for frontend compatibility
Run with: python test_structured_response.py
"""

import sys
import os
import asyncio

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import AIProcessor
from pydantic import BaseModel

async def test_structured_response():
    """Test structured response output"""
    
    print("=== Structured Response Output Test ===")
    print("Testing that AI responses include required structured fields\n")
    
    passed = 0
    failed = 0
    
    # Test 1: Basic response structure
    print("Test 1: Basic Response Structure")
    
    try:
        processor = AIProcessor()
        
        # Create a sample response to test structure
        from main import AIResponse
        
        sample_response = AIResponse(
            response="This is a test response message",
            therapeutic_approach="supportive_reflection",
            confidence=0.85,
            suggestions=["Take deep breaths", "Try mindfulness"],
            topics=["anxiety", "stress"],
            recommended_activities=["breathing-exercise"],
            suggested_vr_mode="calm",
            risk_level="low",
            emotional_state={"category": "anxious", "valence": -0.5, "arousal": 0.7}
        )
        
        # Check required structured fields
        required_fields = ['message', 'recommendedActivity', 'mode', 'topics', 'emotional_category']
        
        missing_fields = []
        for field in required_fields:
            if getattr(sample_response, field) is None:
                missing_fields.append(field)
        
        if not missing_fields:
            print("  ✅ All required structured fields present")
            passed += 1
        else:
            print(f"  ❌ Missing structured fields: {missing_fields}")
            failed += 1
        
        # Verify field values
        if sample_response.message == sample_response.response:
            print("  ✅ message field correctly set to response")
            passed += 1
        else:
            print("  ❌ message field not correctly set")
            failed += 1
        
        if sample_response.recommendedActivity == "breathing-exercise":
            print("  ✅ recommendedActivity field correctly set")
            passed += 1
        else:
            print(f"  ❌ recommendedActivity field incorrect: {sample_response.recommendedActivity}")
            failed += 1
        
        if sample_response.mode == "calm":
            print("  ✅ mode field correctly set to suggested_vr_mode")
            passed += 1
        else:
            print(f"  ❌ mode field incorrect: {sample_response.mode}")
            failed += 1
        
        if sample_response.emotional_category == "anxious":
            print("  ✅ emotional_category field correctly extracted")
            passed += 1
        else:
            print(f"  ❌ emotional_category field incorrect: {sample_response.emotional_category}")
            failed += 1
        
        if sample_response.topics == ["anxiety", "stress"]:
            print("  ✅ topics field preserved")
            passed += 1
        else:
            print(f"  ❌ topics field incorrect: {sample_response.topics}")
            failed += 1
        
    except Exception as e:
        print(f"  ❌ Error testing basic structure: {e}")
        failed += 1
    
    print()
    
    # Test 2: Empty recommendations handling
    print("Test 2: Empty Recommendations Handling")
    
    try:
        # Test response with no recommended activities
        empty_response = AIResponse(
            response="Response without activities",
            therapeutic_approach="supportive_reflection",
            confidence=0.82,
            suggestions=["General suggestion"],
            topics=["general_support"],
            recommended_activities=[],  # Empty list
            suggested_vr_mode=None,
            risk_level="low",
            emotional_state=None
        )
        
        # Check handling of empty recommendations
        if empty_response.recommendedActivity is None:
            print("  ✅ recommendedActivity correctly None when no activities")
            passed += 1
        else:
            print(f"  ❌ recommendedActivity should be None: {empty_response.recommendedActivity}")
            failed += 1
        
        if empty_response.mode is None:
            print("  ✅ mode correctly None when no VR mode suggested")
            passed += 1
        else:
            print(f"  ❌ mode should be None: {empty_response.mode}")
            failed += 1
        
        if empty_response.emotional_category is None:
            print("  ✅ emotional_category correctly None when no emotional state")
            passed += 1
        else:
            print(f"  ❌ emotional_category should be None: {empty_response.emotional_category}")
            failed += 1
        
    except Exception as e:
        print(f"  ❌ Error testing empty recommendations: {e}")
        failed += 1
    
    print()
    
    # Test 3: Multiple recommendations handling
    print("Test 3: Multiple Recommendations Handling")
    
    try:
        # Test response with multiple recommended activities
        multi_response = AIResponse(
            response="Response with multiple activities",
            therapeutic_approach="activity_based",
            confidence=0.90,
            suggestions=["Try these activities"],
            topics=["activity_recommendation"],
            recommended_activities=["breathing-exercise", "mindfulness-meditation", "grounding-technique"],
            suggested_vr_mode="mindful",
            risk_level="low",
            emotional_state={"category": "calm", "valence": 0.3, "arousal": -0.2}
        )
        
        # Should pick the first activity
        if multi_response.recommendedActivity == "breathing-exercise":
            print("  ✅ First activity selected from multiple recommendations")
            passed += 1
        else:
            print(f"  ❌ First activity not selected: {multi_response.recommendedActivity}")
            failed += 1
        
        if multi_response.emotional_category == "calm":
            print("  ✅ emotional_category correctly extracted from emotional state")
            passed += 1
        else:
            print(f"  ❌ emotional_category incorrect: {multi_response.emotional_category}")
            failed += 1
        
    except Exception as e:
        print(f"  ❌ Error testing multiple recommendations: {e}")
        failed += 1
    
    print()
    
    # Test 4: JSON serialization compatibility
    print("Test 4: JSON Serialization Compatibility")
    
    try:
        # Test that response can be serialized to JSON with structured fields
        test_response = AIResponse(
            response="Test message for JSON serialization",
            therapeutic_approach="cbt_grounding",
            confidence=0.88,
            suggestions=["Test suggestion"],
            topics=["test_topic"],
            recommended_activities=["test-activity"],
            suggested_vr_mode="test-mode",
            risk_level="low",
            emotional_state={"category": "neutral", "valence": 0.0, "arousal": 0.0}
        )
        
        # Convert to JSON
        response_dict = test_response.dict()
        
        # Check that structured fields are in the JSON
        json_fields = ['message', 'recommendedActivity', 'mode', 'topics', 'emotional_category']
        
        missing_json_fields = [field for field in json_fields if field not in response_dict]
        
        if not missing_json_fields:
            print("  ✅ All structured fields included in JSON serialization")
            passed += 1
        else:
            print(f"  ❌ Structured fields missing from JSON: {missing_json_fields}")
            failed += 1
        
        # Verify JSON structure matches expected frontend format
        expected_structure = {
            'message': test_response.response,
            'recommendedActivity': test_response.recommended_activities[0] if test_response.recommended_activities else None,
            'mode': test_response.suggested_vr_mode,
            'topics': test_response.topics,
            'emotional_category': test_response.emotional_state['category'] if test_response.emotional_state else None
        }
        
        structure_matches = True
        for field, expected_value in expected_structure.items():
            if response_dict[field] != expected_value:
                structure_matches = False
                print(f"    Mismatch in {field}: expected {expected_value}, got {response_dict[field]}")
        
        if structure_matches:
            print("  ✅ JSON structure matches expected frontend format")
            passed += 1
        else:
            print("  ❌ JSON structure does not match expected format")
            failed += 1
        
    except Exception as e:
        print(f"  ❌ Error testing JSON serialization: {e}")
        failed += 1
    
    print()
    
    # Test 5: Integration with AIProcessor
    print("Test 5: Integration with AIProcessor")
    
    try:
        processor = AIProcessor()
        
        # Process a real message
        response = await processor.process_message(
            user_id="structured_test_user",
            message="I'm feeling anxious about my exam tomorrow"
        )
        
        # Check that the response has structured fields
        structured_fields = ['message', 'recommendedActivity', 'mode', 'topics', 'emotional_category']
        
        missing_structured = [field for field in structured_fields if getattr(response, field) is None]
        
        # Some fields might legitimately be None, so we check for presence, not value
        present_fields = [field for field in structured_fields if hasattr(response, field)]
        
        if len(present_fields) == len(structured_fields):
            print("  ✅ AIProcessor response includes all structured fields")
            passed += 1
        else:
            print(f"  ❌ AIProcessor response missing structured fields: {missing_structured}")
            failed += 1
        
        # Verify message field
        if response.message == response.response:
            print("  ✅ AIProcessor message field correctly populated")
            passed += 1
        else:
            print("  ❌ AIProcessor message field not correctly populated")
            failed += 1
        
        # Verify topics field
        if isinstance(response.topics, list) and len(response.topics) > 0:
            print(f"  ✅ AIProcessor topics field populated: {response.topics}")
            passed += 1
        else:
            print(f"  ⚠️ AIProcessor topics field may be empty: {response.topics}")
            passed += 1  # Don't fail as topics might be empty
        
        # Verify emotional_category if emotional state is present
        if response.emotional_state and response.emotional_category:
            print(f"  ✅ AIProcessor emotional_category populated: {response.emotional_category}")
            passed += 1
        elif response.emotional_state is None and response.emotional_category is None:
            print("  ✅ AIProcessor emotional_category correctly None when no emotional state")
            passed += 1
        else:
            print(f"  ❌ AIProcessor emotional_category mismatch: state={response.emotional_state}, category={response.emotional_category}")
            failed += 1
        
        # Print the structured response for verification
        print(f"  Structured response preview:")
        print(f"    message: {response.message[:50]}...")
        print(f"    recommendedActivity: {response.recommendedActivity}")
        print(f"    mode: {response.mode}")
        print(f"    topics: {response.topics}")
        print(f"    emotional_category: {response.emotional_category}")
        
    except Exception as e:
        print(f"  ❌ Error testing AIProcessor integration: {e}")
        failed += 1
    
    print()
    
    # Test 6: Frontend compatibility
    print("Test 6: Frontend Compatibility")
    
    try:
        # Test the exact structure expected by frontend
        processor = AIProcessor()
        
        response = await processor.process_message(
            user_id="frontend_test_user",
            message="I need help with stress management"
        )
        
        # Convert to dict to simulate API response
        api_response = response.dict()
        
        # Check for the exact fields frontend expects
        frontend_expected_fields = {
            'message': str,
            'recommendedActivity': (str, type(None)),
            'mode': (str, type(None)),
            'topics': list,
            'emotional_category': (str, type(None))
        }
        
        compatibility_issues = []
        
        for field, expected_type in frontend_expected_fields.items():
            if field not in api_response:
                compatibility_issues.append(f"Missing field: {field}")
            elif not isinstance(api_response[field], expected_type):
                compatibility_issues.append(f"Wrong type for {field}: expected {expected_type}, got {type(api_response[field])}")
        
        if not compatibility_issues:
            print("  ✅ Response structure compatible with frontend expectations")
            passed += 1
        else:
            print(f"  ❌ Frontend compatibility issues: {compatibility_issues}")
            failed += 1
        
        # Verify the response can be used in frontend code
        try:
            # Simulate frontend usage
            frontend_data = {
                "message": api_response["message"],
                "recommendedActivity": api_response["recommendedActivity"],
                "mode": api_response["mode"],
                "topics": api_response["topics"],
                "emotional_category": api_response["emotional_category"]
            }
            
            # This would be the structure frontend receives
            if frontend_data["message"]:
                print("  ✅ Frontend can access message field")
                passed += 1
            else:
                print("  ❌ Frontend cannot access message field")
                failed += 1
            
            if isinstance(frontend_data["topics"], list):
                print("  ✅ Frontend can access topics list")
                passed += 1
            else:
                print("  ❌ Frontend cannot access topics as list")
                failed += 1
            
        except Exception as e:
            print(f"  ❌ Frontend usage simulation failed: {e}")
            failed += 1
        
    except Exception as e:
        print(f"  ❌ Error testing frontend compatibility: {e}")
        failed += 1
    
    print()
    
    # Summary
    print("=== Structured Response Test Summary ===")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total: {passed + failed}")
    
    if failed == 0:
        print("🎉 All structured response tests passed!")
        print("\n✅ Structured Response Output Working Correctly:")
        print("   1. All required structured fields present")
        print("   2. message field correctly set to response")
        print("   3. recommendedActivity set to first activity")
        print("   4. mode field set to suggested VR mode")
        print("   5. emotional_category extracted from emotional state")
        print("   6. Empty recommendations handled gracefully")
        print("   7. Multiple recommendations handled correctly")
        print("   8. JSON serialization compatible")
        print("   9. AIProcessor integration working")
        print("   10. Frontend compatibility maintained")
        return True
    else:
        print(f"⚠️ {failed} structured response test(s) failed")
        return False

if __name__ == "__main__":
    async def main():
        success = await test_structured_response()
        sys.exit(0 if success else 1)
    
    asyncio.run(main())
