#!/usr/bin/env python3
"""
Test script for Malaysian Support Resources Module
Tests the support resource registry and formatting functions
Run with: python test_support_resources.py
"""

import sys
import os

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.support_resources import (
    malaysian_support_resources, 
    ServiceCategory, 
    ServiceAvailability
)

def test_support_resources():
    """Test Malaysian support resources module"""
    
    print("=== Malaysian Support Resources Test ===")
    print("Testing support resource registry and formatting\n")
    
    passed = 0
    failed = 0
    
    # Test 1: Basic service loading
    print("Test 1: Basic Service Loading")
    
    all_services = malaysian_support_resources.services
    
    print(f"  Total services loaded: {len(all_services)}")
    
    if len(all_services) >= 9:  # Should have at least the major services
        print("  ✅ Sufficient services loaded")
        passed += 1
    else:
        print("  ❌ Insufficient services loaded")
        failed += 1
    
    print(f"  Services: {[service.name for service in all_services]}")
    print()
    
    # Test 2: Required services presence
    print("Test 2: Required Services Presence")
    
    required_services = [
        "Befrienders Kuala Lumpur",
        "Talian HEAL", 
        "Malaysian Mental Health Association",
        "MIASA Crisis Helpline"
    ]
    
    for service_name in required_services:
        service = malaysian_support_resources.get_service_by_name(service_name)
        if service:
            print(f"  ✅ {service_name} found")
            passed += 1
        else:
            print(f"  ❌ {service_name} not found")
            failed += 1
    
    print()
    
    # Test 3: Service categories
    print("Test 3: Service Categories")
    
    category_tests = [
        (ServiceCategory.CRISIS_HOTLINE, "Crisis Hotlines"),
        (ServiceCategory.COUNSELING, "Counseling Services"),
        (ServiceCategory.PROFESSIONAL_SUPPORT, "Professional Support"),
        (ServiceCategory.GOVERNMENT, "Government Services")
    ]
    
    for category, description in category_tests:
        services = malaysian_support_resources.get_services_by_category(category)
        print(f"  {description}: {len(services)} services")
        
        if len(services) > 0:
            print(f"    ✅ Services found in {category.value}")
            passed += 1
        else:
            print(f"    ❌ No services found in {category.value}")
            failed += 1
        
        print(f"    Services: {[service.name for service in services]}")
    
    print()
    
    # Test 4: Crisis services
    print("Test 4: Crisis Services")
    
    crisis_services = malaysian_support_resources.get_crisis_services()
    
    print(f"  Crisis services found: {len(crisis_services)}")
    
    if len(crisis_services) >= 3:
        print("  ✅ Sufficient crisis services")
        passed += 1
    else:
        print("  ❌ Insufficient crisis services")
        failed += 1
    
    # Verify key crisis services
    crisis_names = [service.name for service in crisis_services]
    key_crisis = ["MIASA Crisis Helpline", "Befrienders Kuala Lumpur", "Life Line Malaysia"]
    
    for crisis in key_crisis:
        if crisis in crisis_names:
            print(f"    ✅ {crisis} available")
            passed += 1
        else:
            print(f"    ❌ {crisis} not available")
            failed += 1
    
    print()
    
    # Test 5: 24/7 services
    print("Test 5: 24/7 Services")
    
    services_24_7 = malaysian_support_resources.get_24_7_services()
    
    print(f"  24/7 services found: {len(services_24_7)}")
    
    if len(services_24_7) >= 2:
        print("  ✅ Sufficient 24/7 services")
        passed += 1
    else:
        print("  ❌ Insufficient 24/7 services")
        failed += 1
    
    print(f"  24/7 Services: {[service.name for service in services_24_7]}")
    print()
    
    # Test 6: Free services
    print("Test 6: Free Services")
    
    free_services = malaysian_support_resources.get_free_services()
    
    print(f"  Free services found: {len(free_services)}")
    
    if len(free_services) >= 5:
        print("  ✅ Sufficient free services")
        passed += 1
    else:
        print("  ❌ Insufficient free services")
        failed += 1
    
    print(f"  Free Services: {[service.name for service in free_services]}")
    print()
    
    # Test 7: Language support
    print("Test 7: Language Support")
    
    languages = ["Malay", "English", "Mandarin", "Tamil"]
    
    for language in languages:
        lang_services = malaysian_support_resources.get_services_by_language(language)
        print(f"  {language} services: {len(lang_services)}")
        
        if len(lang_services) >= 3:
            print(f"    ✅ Sufficient {language} support")
            passed += 1
        else:
            print(f"    ❌ Insufficient {language} support")
            failed += 1
    
    print()
    
    # Test 8: Target audience
    print("Test 8: Target Audience")
    
    audiences = ["general_public", "youth", "crisis_situations", "women"]
    
    for audience in audiences:
        audience_services = malaysian_support_resources.get_services_by_target_audience(audience)
        print(f"  {audience.replace('_', ' ').title()}: {len(audience_services)} services")
        
        if len(audience_services) >= 1:
            print(f"    ✅ Services available for {audience}")
            passed += 1
        else:
            print(f"    ❌ No services for {audience}")
            failed += 1
    
    print()
    
    # Test 9: Search functionality
    print("Test 9: Search Functionality")
    
    search_tests = [
        ("anxiety", "Should find services with anxiety specialization"),
        ("crisis", "Should find crisis services"),
        ("befrienders", "Should find Befrienders service"),
        ("counseling", "Should find counseling services"),
        ("malay", "Should find Malay language services")
    ]
    
    for query, description in search_tests:
        results = malaysian_support_resources.search_services(query)
        print(f"  Search '{query}': {len(results)} results - {description}")
        
        if len(results) >= 1:
            print(f"    ✅ Search found results")
            passed += 1
        else:
            print(f"    ❌ Search found no results")
            failed += 1
        
        print(f"    Found: {[service.name for service in results[:3]]}")
    
    print()
    
    # Test 10: Crisis response formatting
    print("Test 10: Crisis Response Formatting")
    
    crisis_response = malaysian_support_resources.format_for_crisis_response()
    
    print(f"  Crisis response length: {len(crisis_response)} characters")
    
    if len(crisis_response) > 500:
        print("  ✅ Comprehensive crisis response")
        passed += 1
    else:
        print("  ❌ Crisis response too short")
        failed += 1
    
    # Check for key elements
    key_elements = [
        "Immediate Support",
        "Professional Mental Health Services", 
        "Emergency Services",
        "999",
        "112"
    ]
    
    for element in key_elements:
        if element in crisis_response:
            print(f"    ✅ Contains {element}")
            passed += 1
        else:
            print(f"    ❌ Missing {element}")
            failed += 1
    
    print()
    
    # Test 11: Contact summary formatting
    print("Test 11: Contact Summary Formatting")
    
    test_services = [
        "Befrienders Kuala Lumpur",
        "Talian HEAL",
        "Malaysian Mental Health Association"
    ]
    
    for service_name in test_services:
        summary = malaysian_support_resources.get_contact_summary(service_name)
        
        print(f"  {service_name} summary:")
        print(f"    Length: {len(summary)} characters")
        
        if len(summary) > 200:
            print(f"    ✅ Comprehensive summary")
            passed += 1
        else:
            print(f"    ❌ Summary too short")
            failed += 1
        
        # Check for key information
        key_info = ["Organization:", "Category:", "Contact Methods:", "Languages:"]
        missing_info = [info for info in key_info if info not in summary]
        
        if not missing_info:
            print(f"    ✅ All key information included")
            passed += 1
        else:
            print(f"    ❌ Missing information: {missing_info}")
            failed += 1
        
        print(f"    Preview: {summary[:100]}...")
    
    print()
    
    # Test 12: Service data integrity
    print("Test 12: Service Data Integrity")
    
    integrity_issues = []
    
    for service in all_services:
        # Check required fields
        if not service.name:
            integrity_issues.append(f"{service}: Missing name")
        
        if not service.contact_methods:
            integrity_issues.append(f"{service.name}: No contact methods")
        
        if not service.languages:
            integrity_issues.append(f"{service.name}: No languages specified")
        
        if not service.target_audience:
            integrity_issues.append(f"{service.name}: No target audience")
        
        # Check contact methods
        for contact in service.contact_methods:
            if not contact.type or not contact.value:
                integrity_issues.append(f"{service.name}: Invalid contact method")
    
    if not integrity_issues:
        print("  ✅ All service data integrity checks passed")
        passed += 1
    else:
        print(f"  ❌ Found {len(integrity_issues)} integrity issues:")
        for issue in integrity_issues[:5]:  # Show first 5 issues
            print(f"    - {issue}")
        failed += 1
    
    print()
    
    # Test 13: Specific requested services
    print("Test 13: Specifically Requested Services")
    
    requested_services = {
        "Befrienders Worldwide": "Should find Befrienders Kuala Lumpur",
        "Talian HEAL": "Should find exact match",
        "Malaysian Mental Health Association": "Should find exact match"
    }
    
    for search_term, description in requested_services.items():
        results = malaysian_support_resources.search_services(search_term)
        print(f"  Searching for '{search_term}': {len(results)} results")
        
        if len(results) > 0:
            print(f"    ✅ Found: {results[0].name}")
            passed += 1
        else:
            print(f"    ❌ No results found")
            failed += 1
    
    print()
    
    # Summary
    print("=== Support Resources Test Summary ===")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total: {passed + failed}")
    
    if failed == 0:
        print("🎉 All support resources tests passed!")
        print("\n✅ Support Resources Module Working Correctly:")
        print("   1. All major Malaysian services included")
        print("   2. Proper categorization and filtering")
        print("   3. Crisis services readily available")
        print("   4. 24/7 and free services identified")
        print("   5. Multi-language support verified")
        print("   6. Search functionality working")
        print("   7. Crisis response formatting complete")
        print("   8. Contact summaries comprehensive")
        print("   9. Data integrity maintained")
        print("   10. Specifically requested services available")
        return True
    else:
        print(f"⚠️ {failed} support resources test(s) failed")
        return False

if __name__ == "__main__":
    success = test_support_resources()
    sys.exit(0 if success else 1)
