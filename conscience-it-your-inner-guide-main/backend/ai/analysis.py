#!/usr/bin/env python3
"""
AI Analysis Module
Handles emotion detection, crisis detection, and topic inference
"""

import re
from typing import Dict, List, Tuple, Any
import logging

logger = logging.getLogger(__name__)

# Crisis keywords indicating immediate danger
CRISIS_KEYWORDS = [
    "kill myself", "end my life", "suicide", "suicidal",
    "harm myself", "self-harm", "hurt myself",
    "don't want to live", "want to die", "better off dead",
    "no reason to live", "end it all", "take my own life"
]

# High distress indicators
DISTRESS_KEYWORDS = [
    "overwhelmed", "can't cope", "breaking point", "falling apart",
    "losing control", "can't take it anymore", "at my limit",
    "desperate", "hopeless", "helpless", "trapped"
]

# Emotion keywords
EMOTION_KEYWORDS = {
    "anxious": ["anxious", "anxiety", "worried", "panic", "nervous", "fear", "scared", "terrified"],
    "depressed": ["depressed", "sad", "depression", "down", "blue", "hopeless", "empty", "numb"],
    "angry": ["angry", "mad", "furious", "rage", "irritated", "frustrated", "annoyed"],
    "stressed": ["stressed", "stress", "overwhelmed", "pressure", "burned out", "exhausted"],
    "lonely": ["lonely", "alone", "isolated", "loneliness", "no one", "nobody"],
    "confused": ["confused", "uncertain", "unsure", "lost", "don't know", "unclear"],
    "calm": ["calm", "peaceful", "relaxed", "okay", "fine", "better"],
    "happy": ["happy", "good", "great", "excited", "joyful", "pleased"]
}

# Topic keywords
TOPIC_KEYWORDS = {
    "relationships": ["relationship", "partner", "boyfriend", "girlfriend", "husband", "wife", "friend", "family"],
    "work": ["work", "job", "career", "boss", "coworker", "unemployment", "fired"],
    "health": ["health", "doctor", "medical", "illness", "pain", "symptoms"],
    "school": ["school", "college", "university", "study", "exam", "grades"],
    "grief": ["death", "died", "grief", "loss", "funeral", "miss"],
    "trauma": ["trauma", "abuse", "assault", "violence", "attack"],
    "addiction": ["addiction", "addicted", "alcohol", "drugs", "substance"],
    "self-esteem": ["self-esteem", "confidence", "worth", "insecure", "failure"]
}

def detect_crisis_level(message: str) -> str:
    """
    Detect crisis level from user message
    
    Args:
        message: User's message
        
    Returns:
        Crisis level: "high", "medium", or "low"
    """
    message_lower = message.lower()
    
    # Check for immediate crisis indicators
    for keyword in CRISIS_KEYWORDS:
        if keyword in message_lower:
            logger.warning(f"High crisis detected: {keyword}")
            return "high"
    
    # Check for high distress
    distress_count = sum(1 for keyword in DISTRESS_KEYWORDS if keyword in message_lower)
    if distress_count >= 2:
        return "medium"
    
    # Check for intense emotional language
    intense_words = ["!!!", "desperate", "emergency", "urgent", "please help"]
    intense_count = sum(1 for word in intense_words if word in message_lower)
    if intense_count >= 1:
        return "medium"
    
    return "low"

def detect_emotion(message: str) -> str:
    """
    Detect primary emotion from message
    
    Args:
        message: User's message
        
    Returns:
        Primary emotion category
    """
    message_lower = message.lower()
    emotion_scores = {}
    
    # Score each emotion based on keyword matches
    for emotion, keywords in EMOTION_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in message_lower)
        emotion_scores[emotion] = score
    
    # Return emotion with highest score
    if emotion_scores:
        primary_emotion = max(emotion_scores, key=emotion_scores.get)
        if emotion_scores[primary_emotion] > 0:
            return primary_emotion
    
    return "neutral"

def infer_topics(message: str) -> List[str]:
    """
    Infer topics from user message
    
    Args:
        message: User's message
        
    Returns:
        List of detected topics
    """
    message_lower = message.lower()
    detected_topics = []
    
    for topic, keywords in TOPIC_KEYWORDS.items():
        if any(keyword in message_lower for keyword in keywords):
            detected_topics.append(topic)
    
    return detected_topics

def choose_behavior_mode(emotion: str, crisis_level: str, topics: List[str]) -> str:
    """
    Choose appropriate behavior mode based on context
    
    Args:
        emotion: Detected emotion
        crisis_level: Current crisis level
        topics: Detected topics
        
    Returns:
        Behavior mode for AI response
    """
    if crisis_level == "high":
        return "crisis_intervention"
    elif crisis_level == "medium":
        return "supportive_care"
    elif emotion in ["anxious", "depressed", "angry"]:
        return "emotional_support"
    elif emotion in ["calm", "happy"]:
        return "wellness_maintenance"
    elif "trauma" in topics:
        return "trauma_informed"
    elif "grief" in topics:
        return "grief_support"
    else:
        return "general_support"

def analyze_user_message(message: str) -> Dict[str, Any]:
    """
    Complete analysis of user message
    
    Args:
        message: User's message
        
    Returns:
        Dictionary with all analysis results
    """
    crisis_level = detect_crisis_level(message)
    emotion = detect_emotion(message)
    topics = infer_topics(message)
    behavior_mode = choose_behavior_mode(emotion, crisis_level, topics)
    
    analysis = {
        "crisis_level": crisis_level,
        "emotion": emotion,
        "topics": topics,
        "behavior_mode": behavior_mode,
        "message_length": len(message),
        "contains_crisis_keywords": crisis_level == "high"
    }
    
    logger.info(f"Message analysis: {analysis}")
    return analysis
