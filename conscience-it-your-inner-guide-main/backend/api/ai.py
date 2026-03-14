#!/usr/bin/env python3
"""
AI Chat API Routes
Handles chat interactions with proper architecture
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, List
import logging
import jwt
import os

from ai.llm import generate_empathetic_response, validate_response_safety
from ai.analysis import analyze_user_message
from services.crisis_detection import CrisisDetectionService
from services.emotional_state_engine import EmotionalStateEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["ai"])
security = HTTPBearer()
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")

# Initialize analysis engines
crisis_engine = CrisisDetectionService()
emotion_engine = EmotionalStateEngine()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify Supabase JWT token"""
    try:
        payload = jwt.decode(credentials.credentials, SUPABASE_JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/chat")
async def chat(
    request_data: Dict[str, Any],
    token_payload: Dict = Depends(verify_token)
) -> Dict[str, Any]:
    """
    Process chat message with proper AI architecture
    
    Flow:
    1. Analyze user message (crisis, emotion, topics)
    2. If high crisis -> immediate crisis response
    3. Generate AI response using OpenAI
    4. Validate response safety
    5. Return structured response
    """
    try:
        user_id = token_payload.get("sub", "unknown")
        user_message = request_data.get("message", "")
        conversation_history = request_data.get("history", [])
        
        if not user_message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        logger.info(f"Chat request from user {user_id}: {len(user_message)} characters")
        
        # Step 1: Analyze user message
        analysis = analyze_user_message(user_message)
        
        # Step 2: Enhanced crisis detection using existing engine
        crisis_result = crisis_engine.analyze_message(user_message)
        enhanced_crisis_level = crisis_result.get("risk_level", analysis["crisis_level"]).lower()
        
        # Step 3: Enhanced emotion detection using existing engine
        emotion_result = emotion_engine.analyze_sentiment(user_message)
        enhanced_emotion = analysis["emotion"]  # Use our analysis for now
        
        # Step 4: Handle high crisis immediately
        if enhanced_crisis_level == "high":
            crisis_response = {
                "message": "I'm really concerned about you right now. You don't have to go through this alone. Please consider reaching out to a crisis helpline immediately. In Malaysia, you can call Befrienders at 03-7627 2929 (available 24/7). Your safety is the most important thing.",
                "crisis_level": "high",
                "emotional_state": enhanced_emotion,
                "topics": analysis["topics"],
                "recommendedActivity": None,
                "mode": "crisis_intervention",
                "requires_immediate_help": True,
                "crisis_resources": [
                    {"name": "Befrienders Malaysia", "phone": "03-7627 2929", "available": "24/7"},
                    {"name": "Mental Health Psychosocial Support", "phone": "014-322 3386", "available": "24/7"}
                ]
            }
            logger.warning(f"High crisis response sent to user {user_id}")
            return crisis_response
        
        # Step 5: Generate empathetic AI response
        ai_response = await generate_empathetic_response(
            user_message, 
            enhanced_emotion, 
            enhanced_crisis_level
        )
        
        # Step 6: Validate response safety
        is_safe, safe_response = validate_response_safety(ai_response)
        if not is_safe:
            logger.warning(f"Unsafe response detected and replaced for user {user_id}")
            ai_response = safe_response
        
        # Step 7: Get activity recommendation based on emotional state
        recommended_activity = None
        if enhanced_crisis_level == "low":
            # Use existing recommendation engine
            from services.recommendation_engine_effectiveness import EffectivenessAwareRecommendationEngine
            rec_engine = EffectivenessAwareRecommendationEngine()
            
            # Map emotion to emotional category for recommendation engine
            emotion_mapping = {
                "anxious": "anxious",
                "depressed": "sad", 
                "angry": "angry",
                "stressed": "stressed",
                "lonely": "sad",
                "confused": "anxious",
                "calm": "calm",
                "happy": "calm",
                "neutral": "calm"
            }
            
            emotional_category = emotion_mapping.get(enhanced_emotion, "neutral")
            
            try:
                recommendations = rec_engine.get_effectiveness_aware_recommendations(
                    emotional_category=emotional_category,
                    valence=-0.3 if enhanced_emotion in ["depressed", "sad", "lonely"] else 0.0,
                    arousal=0.5 if enhanced_emotion in ["anxious", "stressed"] else 0.0,
                    user_id=user_id
                )
                
                if recommendations.get("primary_activity"):
                    recommended_activity = recommendations["primary_activity"]["title"]
                    
            except Exception as e:
                logger.error(f"Recommendation engine error: {e}")
                # Fallback simple recommendations
                fallback_activities = {
                    "anxious": "Deep breathing exercise",
                    "depressed": "Gentle walk outside", 
                    "stressed": "Progressive muscle relaxation",
                    "angry": "Mindful meditation",
                    "lonely": "Connect with a friend"
                }
                recommended_activity = fallback_activities.get(enhanced_emotion, "Self-care activity")
        
        # Step 8: Construct structured response
        response = {
            "message": ai_response,
            "crisis_level": enhanced_crisis_level,
            "emotional_state": enhanced_emotion,
            "topics": analysis["topics"],
            "recommendedActivity": recommended_activity,
            "mode": analysis["behavior_mode"],
            "requires_immediate_help": enhanced_crisis_level == "high",
            "emotional_analysis": {
                "confidence": 0.7,
                "valence": emotion_result[0] if emotion_result else 0.0,
                "arousal": emotion_result[1] if emotion_result else 0.0
            },
            "crisis_analysis": {
                "confidence": crisis_result.get("confidence", 0.7),
                "risk_factors": crisis_result.get("risk_factors", [])
            }
        }
        
        logger.info(f"Chat response sent to user {user_id}: {analysis['behavior_mode']} mode")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat processing error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/health")
async def health_check():
    """Health check for AI services"""
    return {
        "status": "healthy",
        "services": {
            "llm": "connected" if os.getenv("OPENAI_API_KEY") else "not_configured",
            "crisis_detection": "active",
            "emotion_analysis": "active",
            "recommendation_engine": "active"
        }
    }
