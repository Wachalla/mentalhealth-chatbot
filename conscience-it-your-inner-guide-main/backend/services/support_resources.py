"""
Malaysian Mental Health Support Resources Module
Provides structured contact information for crisis escalation and support services
"""

from typing import List, Dict, Optional
from enum import Enum
from dataclasses import dataclass
from datetime import time

class ServiceCategory(Enum):
    """Categories of mental health support services"""
    CRISIS_HOTLINE = "crisis_hotline"
    COUNSELING = "counseling"
    PROFESSIONAL_SUPPORT = "professional_support"
    EMERGENCY = "emergency"
    PEER_SUPPORT = "peer_support"
    GOVERNMENT = "government"
    NGO = "ngo"

class ServiceAvailability(Enum):
    """Service availability patterns"""
    TWENTY_FOUR_SEVEN = "24/7"
    BUSINESS_HOURS = "business_hours"
    LIMITED_HOURS = "limited_hours"
    APPOINTMENT_ONLY = "appointment_only"

@dataclass
class ContactMethod:
    """Contact method for a service"""
    type: str  # "phone", "whatsapp", "email", "website", "walk_in"
    value: str
    description: str
    availability: Optional[str] = None

@dataclass
class SupportService:
    """Mental health support service information"""
    name: str
    category: ServiceCategory
    organization: str
    description: str
    contact_methods: List[ContactMethod]
    availability: ServiceAvailability
    cost: str
    languages: List[str]
    target_audience: List[str]
    specializations: List[str]
    website: Optional[str] = None
    notes: Optional[str] = None

class MalaysianSupportResources:
    """Malaysian mental health support services registry"""
    
    def __init__(self):
        self.services = self._initialize_services()
    
    def _initialize_services(self) -> List[SupportService]:
        """Initialize all Malaysian mental health support services"""
        
        services = []
        
        # Befrienders Worldwide Malaysia
        services.append(SupportService(
            name="Befrienders Kuala Lumpur",
            category=ServiceCategory.CRISIS_HOTLINE,
            organization="Befrienders Worldwide",
            description="Emotional support and crisis intervention through confidential listening",
            contact_methods=[
                ContactMethod(
                    type="phone",
                    value="03-7627-2929",
                    description="Main helpline",
                    availability="12:00 PM - 10:00 PM daily"
                ),
                ContactMethod(
                    type="email",
                    value="sam@befrienders.org.my",
                    description="Email support",
                    availability="Response within 24 hours"
                ),
                ContactMethod(
                    type="website",
                    value="https://www.befrienders.org.my/",
                    description="Online resources and chat"
                )
            ],
            availability=ServiceAvailability.LIMITED_HOURS,
            cost="Free",
            languages=["English", "Malay", "Mandarin", "Tamil"],
            target_audience=["general_public", "students", "workers"],
            specializations=["emotional_support", "crisis_intervention", "suicide_prevention"],
            website="https://www.befrienders.org.my/",
            notes="Part of international Befrienders Worldwide network. Trained volunteers provide emotional support."
        ))
        
        # Talian HEAL (Mental Health Psychosocial Support)
        services.append(SupportService(
            name="Talian HEAL",
            category=ServiceCategory.COUNSELING,
            organization="Ministry of Health Malaysia",
            description="Tele-counseling service for mental health and psychosocial support",
            contact_methods=[
                ContactMethod(
                    type="phone",
                    value="15555",
                    description="National tele-counseling hotline",
                    availability="8:00 AM - 12:00 AM daily"
                ),
                ContactMethod(
                    type="whatsapp",
                    value="019-639 4455",
                    description="WhatsApp counseling support",
                    availability="8:00 AM - 12:00 AM daily"
                ),
                ContactMethod(
                    type="website",
                    value="https://www.heal.gov.my/",
                    description="Online booking and resources"
                )
            ],
            availability=ServiceAvailability.LIMITED_HOURS,
            cost="Free",
            languages=["Malay", "English", "Mandarin", "Tamil"],
            target_audience=["general_public", "youth", "elderly", "frontliners"],
            specializations=["depression", "anxiety", "stress", "family_issues", "trauma"],
            website="https://www.heal.gov.my/",
            notes="Government-run service with professional counselors and psychologists"
        ))
        
        # Malaysian Mental Health Association (MMHA)
        services.append(SupportService(
            name="Malaysian Mental Health Association",
            category=ServiceCategory.PROFESSIONAL_SUPPORT,
            organization="Malaysian Mental Health Association",
            description="Professional mental health services, support groups, and advocacy",
            contact_methods=[
                ContactMethod(
                    type="phone",
                    value="03-7782-5499",
                    description="Main office and appointments",
                    availability="9:00 AM - 5:00 PM weekdays"
                ),
                ContactMethod(
                    type="phone",
                    value="03-7782-5498",
                    description="Crisis line",
                    availability="9:00 AM - 5:00 PM weekdays"
                ),
                ContactMethod(
                    type="email",
                    value="mmha@po.jaring.my",
                    description="General inquiries"
                ),
                ContactMethod(
                    type="website",
                    value="https://www.mmha.org.my/",
                    description="Online resources and programs"
                )
            ],
            availability=ServiceAvailability.BUSINESS_HOURS,
            cost="Free (crisis) / Nominal fee (services)",
            languages=["English", "Malay", "Mandarin"],
            target_audience=["general_public", "patients", "families", "professionals"],
            specializations=["depression", "anxiety_disorders", "bipolar_disorder", "schizophrenia", "support_groups"],
            website="https://www.mmha.org.my/",
            notes="Oldest mental health NGO in Malaysia. Offers support groups, counseling, and advocacy."
        ))
        
        # MIASA (Mental Illness Awareness and Support Association)
        services.append(SupportService(
            name="MIASA Crisis Helpline",
            category=ServiceCategory.CRISIS_HOTLINE,
            organization="Mental Illness Awareness and Support Association",
            description="24/7 crisis support for mental health emergencies",
            contact_methods=[
                ContactMethod(
                    type="phone",
                    value="1-800-18-0066",
                    description="Free nationwide crisis helpline",
                    availability="24/7"
                ),
                ContactMethod(
                    type="whatsapp",
                    value="+6018-727-4454",
                    description="WhatsApp crisis support",
                    availability="24/7"
                ),
                ContactMethod(
                    type="website",
                    value="https://www.miasa.org.my/",
                    description="Resources and support information"
                )
            ],
            availability=ServiceAvailability.TWENTY_FOUR_SEVEN,
            cost="Free",
            languages=["Malay", "English", "Mandarin"],
            target_audience=["crisis_situations", "suicide_prevention", "families"],
            specializations=["crisis_intervention", "suicide_prevention", "peer_support"],
            website="https://www.miasa.org.my/",
            notes="Run by people with lived experience of mental health issues"
        ))
        
        # Talian Kasih (Social Support Helpline)
        services.append(SupportService(
            name="Talian Kasih",
            category=ServiceCategory.GOVERNMENT,
            organization="Ministry of Women, Family and Community Development",
            description="Government social support helpline for various issues including mental health",
            contact_methods=[
                ContactMethod(
                    type="phone",
                    value="15999",
                    description="National social support hotline",
                    availability="24/7"
                ),
                ContactMethod(
                    type="website",
                    value="https://www.kpwkm.gov.my/",
                    description="Ministry resources and information"
                )
            ],
            availability=ServiceAvailability.TWENTY_FOUR_SEVEN,
            cost="Free",
            languages=["Malay", "English"],
            target_audience=["general_public", "families", "children", "elderly"],
            specializations=["social_support", "family_issues", "child_protection", "elderly_care"],
            website="https://www.kpwkm.gov.my/",
            notes="Government-run service connecting to various social support services"
        ))
        
        # Life Line Malaysia
        services.append(SupportService(
            name="Life Line Malaysia",
            category=ServiceCategory.CRISIS_HOTLINE,
            organization="Life Line Association Malaysia",
            description="24-hour emotional support and crisis intervention",
            contact_methods=[
                ContactMethod(
                    type="phone",
                    value="03-4265-7995",
                    description="Crisis and emotional support hotline",
                    availability="12:00 PM - 10:00 PM daily"
                ),
                ContactMethod(
                    type="email",
                    value="lifeline.malaysia@gmail.com",
                    description="Email support"
                )
            ],
            availability=ServiceAvailability.LIMITED_HOURS,
            cost="Free",
            languages=["English", "Malay", "Mandarin"],
            target_audience=["general_public", "youth", "elderly"],
            specializations=["emotional_support", "crisis_intervention", "suicide_prevention"],
            notes="Affiliated with Befrienders Worldwide"
        ))
        
        # University Malaya Centre for Addiction Sciences (UMCAS)
        services.append(SupportService(
            name="UMCAS Counseling Services",
            category=ServiceCategory.PROFESSIONAL_SUPPORT,
            organization="University of Malaya",
            description="Professional counseling and addiction treatment services",
            contact_methods=[
                ContactMethod(
                    type="phone",
                    value="03-7967-6666",
                    description="Main appointment line",
                    availability="8:30 AM - 4:30 PM weekdays"
                ),
                ContactMethod(
                    type="phone",
                    value="03-7967-6622",
                    description="Emergency hotline",
                    availability="24/7 for existing patients"
                ),
                ContactMethod(
                    type="website",
                    value="https://umcas.um.edu.my/",
                    description="Online information and appointments"
                )
            ],
            availability=ServiceAvailability.BUSINESS_HOURS,
            cost="Fee-based (sliding scale available)",
            languages=["Malay", "English", "Mandarin"],
            target_audience=["addiction", "substance_abuse", "general_mental_health"],
            specializations=["addiction_treatment", "rehabilitation", "counseling", "detox"],
            website="https://umcas.um.edu.my/",
            notes="University-based center with professional addiction specialists"
        ))
        
        # Childline Malaysia
        services.append(SupportService(
            name="Childline Malaysia",
            category=ServiceCategory.PEER_SUPPORT,
            organization="Childline Malaysia Association",
            description="24-hour helpline for children and teens in need of support",
            contact_methods=[
                ContactMethod(
                    type="phone",
                    value="15999",
                    description="Children's helpline",
                    availability="24/7"
                ),
                ContactMethod(
                    type="whatsapp",
                    value="019-269 8143",
                    description="WhatsApp support for children",
                    availability="24/7"
                ),
                ContactMethod(
                    type="email",
                    value="info@childline.org.my",
                    description="Email support"
                )
            ],
            availability=ServiceAvailability.TWENTY_FOUR_SEVEN,
            cost="Free",
            languages=["Malay", "English"],
            target_audience=["children", "teenagers", "parents", "teachers"],
            specializations=["child_protection", "bullying", "abuse", "emotional_support"],
            website="https://www.childline.org.my/",
            notes="Specialized support for children and young people"
        ))
        
        # Women's Aid Organisation (WAO)
        services.append(SupportService(
            name="Women's Aid Organisation",
            category=ServiceCategory.NGO,
            organization="Women's Aid Organisation",
            description="Support services for women experiencing crisis, including mental health support",
            contact_methods=[
                ContactMethod(
                    type="phone",
                    value="03-7956 3488",
                    description="Main helpline",
                    availability="24/7"
                ),
                ContactMethod(
                    type="whatsapp",
                    value="018-988 8058",
                    description="WhatsApp crisis support",
                    availability="24/7"
                ),
                ContactMethod(
                    type="sms",
                    value="014-322 3385",
                    description="SMS crisis support",
                    availability="24/7"
                )
            ],
            availability=ServiceAvailability.TWENTY_FOUR_SEVEN,
            cost="Free",
            languages=["Malay", "English", "Tamil", "Punjabi"],
            target_audience=["women", "domestic_violence", "sexual_assault", "trauma"],
            specializations=["crisis_intervention", "counseling", "legal_support", "shelter"],
            website="https://wao.org.my/",
            notes="Comprehensive support for women in crisis, including mental health services"
        ))
        
        # Mercy Malaysia Mental Health Support
        services.append(SupportService(
            name="Mercy Malaysia Mental Health Support",
            category=ServiceCategory.NGO,
            organization="Mercy Malaysia",
            description="Mental health and psychosocial support services",
            contact_methods=[
                ContactMethod(
                    type="phone",
                    value="03-4251 9999",
                    description="Main office line",
                    availability="9:00 AM - 5:00 PM weekdays"
                ),
                ContactMethod(
                    type="website",
                    value="https://www.mercy.org.my/",
                    description="Online resources and program information"
                )
            ],
            availability=ServiceAvailability.BUSINESS_HOURS,
            cost="Free (disaster response) / Nominal (programs)",
            languages=["Malay", "English"],
            target_audience=["disaster_victims", "refugees", "general_public"],
            specializations=["trauma", "disaster_response", "psychosocial_support"],
            website="https://www.mercy.org.my/",
            notes="Focus on disaster mental health and psychosocial support"
        ))
        
        return services
    
    def get_services_by_category(self, category: ServiceCategory) -> List[SupportService]:
        """Get all services in a specific category"""
        return [service for service in self.services if service.category == category]
    
    def get_crisis_services(self) -> List[SupportService]:
        """Get all crisis and emergency services"""
        crisis_categories = [ServiceCategory.CRISIS_HOTLINE, ServiceCategory.EMERGENCY]
        return [service for service in self.services 
                if service.category in crisis_categories]
    
    def get_free_services(self) -> List[SupportService]:
        """Get all free services"""
        return [service for service in self.services if service.cost == "Free"]
    
    def get_services_by_language(self, language: str) -> List[SupportService]:
        """Get services that support a specific language"""
        return [service for service in self.services 
                if language.lower() in [lang.lower() for lang in service.languages]]
    
    def get_services_by_target_audience(self, audience: str) -> List[SupportService]:
        """Get services for a specific target audience"""
        return [service for service in self.services 
                if audience.lower() in [aud.lower() for aud in service.target_audience]]
    
    def get_24_7_services(self) -> List[SupportService]:
        """Get all available 24/7 services"""
        return [service for service in self.services 
                if service.availability == ServiceAvailability.TWENTY_FOUR_SEVEN]
    
    def search_services(self, query: str) -> List[SupportService]:
        """Search services by name, description, or specializations"""
        query_lower = query.lower()
        matching_services = []
        
        for service in self.services:
            # Search in name
            if query_lower in service.name.lower():
                matching_services.append(service)
                continue
            
            # Search in organization
            if query_lower in service.organization.lower():
                matching_services.append(service)
                continue
            
            # Search in description
            if query_lower in service.description.lower():
                matching_services.append(service)
                continue
            
            # Search in specializations
            if any(query_lower in spec.lower() for spec in service.specializations):
                matching_services.append(service)
                continue
            
            # Search in target audience
            if any(query_lower in aud.lower() for aud in service.target_audience):
                matching_services.append(service)
                continue
        
        return matching_services
    
    def get_service_by_name(self, name: str) -> Optional[SupportService]:
        """Get a specific service by name"""
        for service in self.services:
            if name.lower() in service.name.lower():
                return service
        return None
    
    def format_for_crisis_response(self) -> str:
        """Format crisis services for immediate escalation response"""
        crisis_services = self.get_crisis_services()
        
        response_text = "**Immediate Support - Malaysia:**\n"
        
        for service in crisis_services:
            response_text += f"• **{service.name}**: "
            
            # Add primary phone contact
            phone_contacts = [cm for cm in service.contact_methods if cm.type == "phone"]
            if phone_contacts:
                phone = phone_contacts[0]
                response_text += f"{phone.value} ({phone.availability})\n"
            else:
                response_text += "Contact via available methods\n"
        
        response_text += "\n**Professional Mental Health Services:**\n"
        
        # Add professional counseling services
        professional_services = self.get_services_by_category(ServiceCategory.COUNSELING)
        professional_services.extend(self.get_services_by_category(ServiceCategory.PROFESSIONAL_SUPPORT))
        
        for service in professional_services[:3]:  # Limit to top 3
            response_text += f"• **{service.name}**: "
            
            phone_contacts = [cm for cm in service.contact_methods if cm.type == "phone"]
            if phone_contacts:
                phone = phone_contacts[0]
                response_text += f"{phone.value} ({phone.availability})\n"
        
        response_text += "\n**Emergency Services:**\n"
        response_text += "If you're in immediate danger or having thoughts of harming yourself, "
        response_text += "please call **999** or **112** for emergency services, "
        response_text += "or go to your nearest hospital emergency department.\n"
        
        return response_text
    
    def get_contact_summary(self, service_name: str) -> str:
        """Get formatted contact summary for a specific service"""
        service = self.get_service_by_name(service_name)
        if not service:
            return "Service not found."
        
        summary = f"**{service.name}**\n"
        summary += f"Organization: {service.organization}\n"
        summary += f"Category: {service.category.value.replace('_', ' ').title()}\n"
        summary += f"Availability: {service.availability.value}\n"
        summary += f"Cost: {service.cost}\n"
        summary += f"Languages: {', '.join(service.languages)}\n"
        summary += f"Description: {service.description}\n\n"
        
        summary += "**Contact Methods:**\n"
        for contact in service.contact_methods:
            summary += f"• {contact.type.title()}: {contact.value}"
            if contact.availability:
                summary += f" ({contact.availability})"
            summary += f" - {contact.description}\n"
        
        if service.specializations:
            summary += f"\n**Specializations:** {', '.join(spec.replace('_', ' ').title() for spec in service.specializations)}\n"
        
        if service.target_audience:
            summary += f"**Target Audience:** {', '.join(aud.replace('_', ' ').title() for aud in service.target_audience)}\n"
        
        if service.website:
            summary += f"**Website:** {service.website}\n"
        
        if service.notes:
            summary += f"**Notes:** {service.notes}\n"
        
        return summary

# Singleton instance for easy import
malaysian_support_resources = MalaysianSupportResources()
