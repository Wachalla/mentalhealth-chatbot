# Crisis Detection Service
# Analyzes user messages for crisis signals and determines appropriate risk level

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import re

class RiskLevel(Enum):
    NONE = "NONE"
    MODERATE = "MODERATE"
    HIGH = "HIGH"

class CrisisDetectionService:
    """Detects crisis signals and determines appropriate risk level"""
    
    def __init__(self):
        # Crisis keywords (HIGH risk) - self-harm and suicide
        self.crisis_keywords = [
            # Direct suicide references
            "suicide", "suicidal", "kill myself", "end my life", "want to die",
            "take my life", "overdose", "better off dead", "hang myself",
            "end it all", "no reason to live", "can't go on", "shouldn't exist",
            # Self-harm
            "self harm", "self-harm", "cut myself", "hurt myself", "cutting",
            "self injury", "self-injury", "want to hurt myself",
            # Disappearance/death wishes
            "want to disappear", "wish I was dead", "shouldn't be here",
            "disappear forever", "vanish", "end everything"
        ]
        
        # Severe distress keywords (MODERATE risk)
        self.severe_distress_keywords = [
            # Psychotic symptoms
            "hearing voices", "voices telling me", "voices in my head",
            "people watching me", "being followed", "they're after me",
            "someone is watching", "paranoid", "conspiracy",
            # Dissociation/depersonalization
            "nothing feels real", "detached from reality", "out of body",
            "not in my body", "world isn't real", "dream state",
            "derealization", "depersonalization", "unreal",
            # Extreme instability
            "losing my mind", "going crazy", "can't control myself",
            "completely unstable", "falling apart", "breaking down",
            "losing control", "can't take it anymore", "at breaking point"
        ]
        
        # Crisis phrases (more complex patterns)
        self.crisis_phrases = [
            r"i\s+want\s+to\s+(?:kill|end|take)\s+my\s+life",
            r"i\s+want\s+to\s+(?:die|disappear|vanish)",
            r"i'm\s+going\s+to\s+(?:kill|end|take)\s+my\s+life",
            r"i\s+should\s+(?:kill|end|take)\s+my\s+life",
            r"i\s+wish\s+i\s+was\s+dead",
            r"i\s+want\s+to\s+hurt\s+myself",
            r"i'm\s+going\s+to\s+hurt\s+myself",
            r"i\s+want\s+to\s+cut\s+myself",
            r"i'm\s+going\s+to\s+overdose",
            r"i\s+want\s+to\s+overdose"
        ]
        
        # Severe distress phrases
        self.severe_distress_phrases = [
            r"i\s+hear\s+(?:voices|someone)",
            r"voices\s+(?:are\s+)?telling\s+me",
            r"nothing\s+feels\s+real",
            r"detached\s+from\s+reality",
            r"out\s+of\s+my\s+body",
            r"losing\s+my\s+mind",
            r"going\s+crazy",
            r"can't\s+control\s+myself"
        ]
        
        # Compile regex patterns for efficiency
        self.crisis_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.crisis_phrases]
        self.severe_distress_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.severe_distress_phrases]
    
    def analyze_message(
        self, 
        message: str,
        emotional_valence: Optional[float] = None,
        emotional_arousal: Optional[float] = None
    ) -> Dict:
        """
        Analyze message for crisis signals
        
        Args:
            message: User message to analyze
            emotional_valence: Optional valence score (-1 to 1)
            emotional_arousal: Optional arousal score (-1 to 1)
            
        Returns:
            {
                'risk_level': RiskLevel,
                'triggers': List[str],
                'confidence': float
            }
        """
        
        lower_message = message.lower()
        
        # Check for HIGH risk crisis signals
        crisis_triggers = []
        
        # Check crisis keywords
        for keyword in self.crisis_keywords:
            if keyword in lower_message:
                crisis_triggers.append(f"keyword: {keyword}")
        
        # Check crisis phrases
        for pattern in self.crisis_patterns:
            if pattern.search(message):
                crisis_triggers.append(f"phrase: {pattern.pattern}")
        
        # If crisis signals found, return HIGH risk
        if crisis_triggers:
            return {
                'risk_level': RiskLevel.HIGH,
                'triggers': crisis_triggers,
                'confidence': 0.95
            }
        
        # Check for MODERATE risk severe distress signals
        distress_triggers = []
        
        # Check severe distress keywords
        for keyword in self.severe_distress_keywords:
            if keyword in lower_message:
                distress_triggers.append(f"keyword: {keyword}")
        
        # Check severe distress phrases
        for pattern in self.severe_distress_patterns:
            if pattern.search(message):
                distress_triggers.append(f"phrase: {pattern.pattern}")
        
        # Check for severe emotional state signals
        emotional_triggers = self._analyze_emotional_signals(
            emotional_valence, 
            emotional_arousal
        )
        distress_triggers.extend(emotional_triggers)
        
        # If severe distress signals found, return MODERATE risk
        if distress_triggers:
            return {
                'risk_level': RiskLevel.MODERATE,
                'triggers': distress_triggers,
                'confidence': 0.75
            }
        
        # No risk detected
        return {
            'risk_level': RiskLevel.NONE,
            'triggers': [],
            'confidence': 1.0
        }
    
    def _analyze_emotional_signals(
        self, 
        valence: Optional[float], 
        arousal: Optional[float]
    ) -> List[str]:
        """
        Analyze emotional state for distress signals
        
        Args:
            valence: Emotional valence (-1 to 1)
            arousal: Emotional arousal (-1 to 1)
            
        Returns:
            List of detected emotional triggers
        """
        
        triggers = []
        
        if valence is not None:
            # Very negative valence indicates distress
            if valence < -0.7:
                triggers.append(f"severe_negative_valence: {valence:.2f}")
            elif valence < -0.5:
                triggers.append(f"negative_valence: {valence:.2f}")
        
        if arousal is not None:
            # High arousal combined with negative valence indicates distress
            if arousal > 0.7:
                triggers.append(f"high_arousal: {arousal:.2f}")
            elif arousal > 0.5 and valence is not None and valence < -0.3:
                triggers.append(f"moderate_arousal_negative_valence: {arousal:.2f}")
        
        return triggers
    
    def detect_persistent_distress(
        self, 
        user_id: str,
        days_back: int = 14,
        min_sessions: int = 5
    ) -> Dict:
        """
        Detect persistent distress patterns across multiple sessions
        
        Args:
            user_id: User identifier
            days_back: Number of days to look back
            min_sessions: Minimum number of sessions required for analysis
            
        Returns:
            {
                'detected': bool,
                'triggers': List[str],
                'confidence': float
            }
        """
        
        try:
            # Try to import database functions (may not be available)
            from main import get_db_connection
        except ImportError:
            # Database not available, skip persistent detection
            return {
                'detected': False,
                'triggers': ['database_unavailable'],
                'confidence': 0.0
            }
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Check last N days of emotional states
            cursor.execute(
                """
                SELECT valence, arousal, category, updated_at
                FROM emotional_states
                WHERE user_id = %s 
                  AND updated_at >= %s
                ORDER BY updated_at DESC
                LIMIT 50
                """,
                (user_id, datetime.now() - timedelta(days=days_back))
            )
            
            states = cursor.fetchall()
            
            if len(states) < min_sessions:
                return {
                    'detected': False,
                    'triggers': ['insufficient_data'],
                    'confidence': 0.0
                }
            
            triggers = []
            
            # Count distressed states
            distressed_count = sum(1 for s in states if s[2] == 'distressed')
            if distressed_count >= 5:
                triggers.append(f'distressed_states: {distressed_count}')
            
            # Count very negative valence
            very_negative_count = sum(1 for s in states if s[0] < -0.6)
            if very_negative_count >= len(states) * 0.7:
                triggers.append(f'very_negative_valence_ratio: {very_negative_count}/{len(states)}')
            
            # Count high arousal with negative valence
            high_arousal_negative_count = sum(
                1 for s in states 
                if s[0] < -0.3 and s[1] > 0.6
            )
            if high_arousal_negative_count >= len(states) * 0.5:
                triggers.append(f'high_arousal_negative_ratio: {high_arousal_negative_count}/{len(states)}')
            
            # Determine if persistent distress detected
            detected = len(triggers) > 0
            confidence = 0.8 if detected else 0.0
            
            return {
                'detected': detected,
                'triggers': triggers,
                'confidence': confidence
            }
            
        except Exception as e:
            # Error during analysis
            return {
                'detected': False,
                'triggers': [f'analysis_error: {str(e)}'],
                'confidence': 0.0
            }
        finally:
            cursor.close()
            conn.close()
    
    def get_risk_level_description(self, risk_level: RiskLevel) -> str:
        """Get human-readable description of risk level"""
        descriptions = {
            RiskLevel.NONE: "No crisis signals detected",
            RiskLevel.MODERATE: "Severe distress signals detected",
            RiskLevel.HIGH: "Crisis signals detected"
        }
        return descriptions.get(risk_level, "Unknown risk level")
    
    def is_crisis_keyword(self, message: str) -> bool:
        """Quick check if message contains any crisis keywords"""
        lower_message = message.lower()
        return any(keyword in lower_message for keyword in self.crisis_keywords)
    
    def is_severe_distress_keyword(self, message: str) -> bool:
        """Quick check if message contains any severe distress keywords"""
        lower_message = message.lower()
        return any(keyword in lower_message for keyword in self.severe_distress_keywords)


# Singleton instance for easy import
crisis_detector = CrisisDetectionService()
