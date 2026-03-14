#!/usr/bin/env python3
"""
Test script for Emotional Mapper Service
Run with: python test_emotional_mapper.py
"""

import sys
import os

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.emotional_mapper import EmotionalMapper, EmotionalCategory

def test_emotional_mapper():
    """Test emotional mapping functionality"""
    
    print("=== Emotional Mapper Test ===\n")
    
    mapper = EmotionalMapper()
    
    # Test 1: Basic category mapping
    print("Test 1: Basic Category Mapping")
    
    mapping_tests = [
        {"valence": -0.8, "arousal": 0.7, "expected": EmotionalCategory.DISTRESSED, "description": "Negative + High arousal"},
        {"valence": -0.3, "arousal": 0.8, "expected": EmotionalCategory.ANXIOUS, "description": "Slightly negative + High arousal"},
        {"valence": -0.7, "arousal": -0.2, "expected": EmotionalCategory.LOW, "description": "Negative + Low arousal"},
        {"valence": 0.6, "arousal": -0.5, "expected": EmotionalCategory.CALM, "description": "Positive + Low arousal"},
        {"valence": 0.8, "arousal": 0.6, "expected": EmotionalCategory.ENERGIZED, "description": "Positive + High arousal"},
        {"valence": 0.1, "arousal": 0.1, "expected": EmotionalCategory.NEUTRAL, "description": "Near center"},
        {"valence": 0.4, "arousal": 0.2, "expected": EmotionalCategory.NEUTRAL, "description": "Mild positive + Low arousal"},
        {"valence": -0.2, "arousal": 0.4, "expected": EmotionalCategory.NEUTRAL, "description": "Mild negative + Medium arousal"}
    ]
    
    passed = 0
    failed = 0
    
    for test in mapping_tests:
        category, confidence = mapper.map_to_category(test["valence"], test["arousal"])
        
        print(f"  {test['description']}")
        print(f"    Valence: {test['valence']}, Arousal: {test['arousal']}")
        print(f"    Category: {category.value}, Confidence: {confidence:.2f}")
        
        if category == test["expected"]:
            print("    ✅ PASSED")
            passed += 1
        else:
            print(f"    ❌ FAILED (expected {test['expected'].value})")
            failed += 1
        print()
    
    # Test 2: Confidence scoring
    print("Test 2: Confidence Scoring")
    
    confidence_tests = [
        {"valence": 0.9, "arousal": 0.9, "min_confidence": 0.8, "description": "High intensity, far from center"},
        {"valence": 0.1, "arousal": 0.1, "max_confidence": 0.5, "description": "Low intensity, near center"},
        {"valence": 0.7, "arousal": -0.7, "min_confidence": 0.7, "description": "Strong diagonal placement"},
        {"valence": -0.8, "arousal": 0.0, "min_confidence": 0.6, "description": "Strong valence, neutral arousal"},
        {"valence": 0.0, "arousal": 0.8, "min_confidence": 0.6, "description": "Strong arousal, neutral valence"}
    ]
    
    for test in confidence_tests:
        category, confidence = mapper.map_to_category(test["valence"], test["arousal"])
        
        print(f"  {test['description']}")
        print(f"    Valence: {test['valence']}, Arousal: {test['arousal']}")
        print(f"    Confidence: {confidence:.2f}")
        
        passed_test = True
        if "min_confidence" in test:
            passed_test = confidence >= test["min_confidence"]
        elif "max_confidence" in test:
            passed_test = confidence <= test["max_confidence"]
        
        if passed_test:
            print("    ✅ PASSED")
            passed += 1
        else:
            print("    ❌ FAILED")
            failed += 1
        print()
    
    # Test 3: Category descriptions
    print("Test 3: Category Descriptions")
    
    for category in EmotionalCategory:
        description = mapper.get_category_description(category)
        
        print(f"  {category.value}:")
        print(f"    Description: {description['description']}")
        print(f"    Characteristics: {', '.join(description['characteristics'])}")
        print(f"    Valence range: {description['typical_valence_range']}")
        print(f"    Arousal range: {description['typical_arousal_range']}")
        print(f"    Color: {description['color']}")
        print(f"    Has recommendations: {len(description['recommendations']) > 0}")
        print("    ✅ PASSED")
        print()
        passed += 1
    
    # Test 4: Emotional distance calculation
    print("Test 4: Emotional Distance Calculation")
    
    distance_tests = [
        {
            "v1": -0.8, "a1": 0.7, "v2": -0.8, "a2": 0.7,
            "expected_distance": 0.0, "description": "Same point"
        },
        {
            "v1": 0.0, "a1": 0.0, "v2": 1.0, "a2": 0.0,
            "expected_distance": 1.0, "description": "Unit distance"
        },
        {
            "v1": -1.0, "a1": -1.0, "v2": 1.0, "a2": 1.0,
            "expected_distance": 2.828, "description": "Maximum distance"
        },
        {
            "v1": 0.5, "a1": 0.5, "v2": -0.5, "a2": -0.5,
            "expected_distance": 1.414, "description": "Diagonal distance"
        }
    ]
    
    for test in distance_tests:
        distance = mapper.get_emotional_distance(
            test["v1"], test["a1"], test["v2"], test["a2"]
        )
        
        print(f"  {test['description']}")
        print(f"    Distance: {distance:.3f} (expected: {test['expected_distance']:.3f})")
        
        if abs(distance - test["expected_distance"]) < 0.01:
            print("    ✅ PASSED")
            passed += 1
        else:
            print("    ❌ FAILED")
            failed += 1
        print()
    
    # Test 5: State similarity
    print("Test 5: State Similarity")
    
    similarity_tests = [
        {"v1": 0.5, "a1": 0.5, "v2": 0.6, "a2": 0.6, "expected": True, "threshold": 0.3, "description": "Close points"},
        {"v1": -0.8, "a1": 0.7, "v2": 0.8, "a2": -0.7, "expected": False, "threshold": 0.3, "description": "Far points"},
        {"v1": 0.0, "a1": 0.0, "v2": 0.2, "a2": 0.2, "expected": True, "threshold": 0.3, "description": "Near center"},
        {"v1": 0.5, "a1": 0.5, "v2": -0.5, "a2": -0.5, "expected": False, "threshold": 0.3, "description": "Opposite quadrants"}
    ]
    
    for test in similarity_tests:
        is_similar = mapper.is_similar_state(
            test["v1"], test["a1"], test["v2"], test["a2"], test["threshold"]
        )
        
        print(f"  {test['description']}")
        print(f"    Similar: {is_similar} (expected: {test['expected']})")
        
        if is_similar == test["expected"]:
            print("    ✅ PASSED")
            passed += 1
        else:
            print("    ❌ FAILED")
            failed += 1
        print()
    
    # Test 6: Transition probabilities
    print("Test 6: Transition Probabilities")
    
    transition_tests = [
        {"from_cat": EmotionalCategory.DISTRESSED, "to_cat": EmotionalCategory.CALM, "min_prob": 0.0, "max_prob": 0.2},
        {"from_cat": EmotionalCategory.ANXIOUS, "to_cat": EmotionalCategory.CALM, "min_prob": 0.2, "max_prob": 0.5},
        {"from_cat": EmotionalCategory.LOW, "to_cat": EmotionalCategory.CALM, "min_prob": 0.2, "max_prob": 0.5},
        {"from_cat": EmotionalCategory.CALM, "to_cat": EmotionalCategory.ENERGIZED, "min_prob": 0.2, "max_prob": 0.4},
        {"from_cat": EmotionalCategory.NEUTRAL, "to_cat": EmotionalCategory.NEUTRAL, "min_prob": 0.1, "max_prob": 0.2}
    ]
    
    for test in transition_tests:
        probability = mapper.get_transition_probability(test["from_cat"], test["to_cat"])
        
        print(f"  {test['from_cat'].value} → {test['to_cat'].value}")
        print(f"    Probability: {probability:.2f}")
        
        if "min_prob" in test and "max_prob" in test:
            in_range = test["min_prob"] <= probability <= test["max_prob"]
            if in_range:
                print("    ✅ PASSED")
                passed += 1
            else:
                print(f"    ❌ FAILED (expected {test['min_prob']}-{test['max_prob']})")
                failed += 1
        print()
    
    # Test 7: Edge cases and boundary conditions
    print("Test 7: Edge Cases and Boundary Conditions")
    
    edge_tests = [
        {"valence": -1.0, "arousal": 1.0, "expected": EmotionalCategory.DISTRESSED, "description": "Extreme negative + high arousal"},
        {"valence": 1.0, "arousal": -1.0, "expected": EmotionalCategory.CALM, "description": "Extreme positive + low arousal"},
        {"valence": -0.5, "arousal": 0.5, "expected": EmotionalCategory.DISTRESSED, "description": "Exact boundary - distressed"},
        {"valence": -0.49, "arousal": 0.51, "expected": EmotionalCategory.ANXIOUS, "description": "Near boundary - anxious"},
        {"valence": 0.0, "arousal": 0.0, "expected": EmotionalCategory.NEUTRAL, "description": "Exact center"},
        {"valence": 999, "arousal": -999, "expected": EmotionalCategory.CALM, "description": "Out of bounds values (should normalize)"}
    ]
    
    for test in edge_tests:
        category, confidence = mapper.map_to_category(test["valence"], test["arousal"])
        
        print(f"  {test['description']}")
        print(f"    Input: ({test['valence']}, {test['arousal']}) → {category.value}")
        
        # For out of bounds test, we expect neutral due to normalization
        if category == test["expected"]:
            print("    ✅ PASSED")
            passed += 1
        else:
            print(f"    ❌ FAILED (expected {test['expected'].value})")
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
    success = test_emotional_mapper()
    sys.exit(0 if success else 1)
