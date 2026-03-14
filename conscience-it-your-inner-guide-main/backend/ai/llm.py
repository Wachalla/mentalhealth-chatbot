#!/usr/bin/env python3
"""
LLM Integration Module
Handles OpenAI API calls for language generation
"""

import os
from openai import OpenAI
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Initialize OpenAI client lazily
_client = None

def get_openai_client():
    """Get OpenAI client, initializing if needed"""
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        _client = OpenAI(api_key=api_key)
    return _client

async def generate_response(messages: List[Dict[str, str]], system_prompt: str) -> str:
    """
    Generate AI response using OpenAI GPT-4o-mini
    
    Args:
        messages: List of conversation messages in OpenAI format
        system_prompt: System prompt defining the AI behavior
        
    Returns:
        Generated AI response as string
    """
    try:
        client = get_openai_client()
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                *messages
            ],
            temperature=0.7,
            max_tokens=500,  # Keep responses concise
            presence_penalty=0.1,
            frequency_penalty=0.1
        )
        
        ai_response = response.choices[0].message.content
        
        # Log for monitoring
        logger.info(f"LLM response generated: {len(ai_response)} characters")
        
        return ai_response.strip()
        
    except Exception as e:
        logger.error(f"LLM API error: {str(e)}")
        
        # Fallback response if API fails
        fallback_responses = [
            "I'm here to support you. Could you tell me more about how you're feeling?",
            "Thank you for sharing that with me. I'm here to listen and help.",
            "That sounds challenging. Let's explore this together.",
            "I appreciate you opening up. What would be most helpful right now?"
        ]
        
        import random
        return random.choice(fallback_responses)

async def generate_empathetic_response(user_message: str, emotional_state: str, crisis_level: str) -> str:
    """
    Generate context-aware response based on emotional state and crisis level
    
    Args:
        user_message: The user's current message
        emotional_state: Detected emotional state
        crisis_level: Current crisis level
        
    Returns:
        Context-appropriate AI response
    """
    
    # Adjust system prompt based on crisis level
    if crisis_level == "high":
        system_prompt = """
You are Conscience, an emotionally intelligent mental health companion responding to someone in crisis.

CRISIS PROTOCOL:
- Prioritize safety and immediate support
- Provide crisis resources
- Express genuine concern and empathy
- Keep responses calm and reassuring
- Never give medical advice or diagnoses
- Encourage professional help immediately

Response guidelines:
- Be warm and supportive
- Acknowledge their pain
- Suggest specific crisis resources
- Keep responses concise (2-3 sentences)
"""
    elif crisis_level == "medium":
        system_prompt = f"""
You are Conscience, an emotionally intelligent mental health companion.

User emotional state: {emotional_state}

Guidelines:
- Be empathetic and supportive
- Validate their feelings
- Suggest healthy coping strategies
- Encourage professional help if appropriate
- Keep responses 2-4 sentences
- Never diagnose or prescribe medication
"""
    else:
        system_prompt = f"""
You are Conscience, an emotionally intelligent mental health companion.

User emotional state: {emotional_state}

Guidelines:
- Be warm and supportive
- Provide thoughtful reflection
- Suggest helpful activities or perspectives
- Keep responses conversational (2-3 sentences)
- Focus on emotional wellness
"""

    # Format messages for OpenAI
    messages = [{"role": "user", "content": user_message}]
    
    return await generate_response(messages, system_prompt)

def validate_response_safety(response: str) -> tuple[bool, str]:
    """
    Validate AI response for safety and appropriateness
    
    Args:
        response: Generated AI response
        
    Returns:
        Tuple of (is_safe, safe_response_or_original)
    """
    
    # Check for harmful content patterns
    harmful_patterns = [
        "kill yourself",
        "harm yourself", 
        "end your life",
        "suicide",
        "self-harm",
        "diagnose",
        "prescribe",
        "medication",
        "cure"
    ]
    
    response_lower = response.lower()
    
    for pattern in harmful_patterns:
        if pattern in response_lower:
            # Replace with safe response
            safe_response = "I'm here to support you. If you're having thoughts of harming yourself, please reach out to a crisis helpline immediately. You don't have to go through this alone."
            return False, safe_response
    
    return True, response
