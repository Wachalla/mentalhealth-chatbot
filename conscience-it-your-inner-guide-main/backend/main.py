from fastapi import FastAPI, HTTPException, Depends, status, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import jwt
import psycopg2
from psycopg2.extras import execute_values
import os
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import uuid
import json
import asyncio
from urllib import request as urllib_request, error as urllib_error

# Import new AI API routes
from api.ai import router as ai_router

# Load environment variables
load_dotenv()

# Configuration
app = FastAPI(title="CONSCIENCE Backend", version="1.0.0")

# Include AI API routes
app.include_router(ai_router)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost:8081", "https://localhost:8081", "http://192.168.0.138:8080", "http://192.168.0.138:8081", "http://192.168.100.72:8080", "http://192.168.100.72:8081"],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")
DATABASE_URL = os.getenv("DATABASE_URL")
WEAVIATE_URL = os.getenv("WEAVIATE_URL")
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.user_connections[user_id] = websocket
        logger.info(f"User {user_id} connected via WebSocket")

    def disconnect(self, websocket: WebSocket, user_id: str):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if user_id in self.user_connections:
            del self.user_connections[user_id]
        logger.info(f"User {user_id} disconnected from WebSocket")

    async def send_personal_message(self, user_id: str, message: dict):
        if user_id in self.user_connections:
            await self.user_connections[user_id].send_text(json.dumps(message))

    async def broadcast_to_all(self, message: dict):
        for connection in self.active_connections:
            await connection.send_text(json.dumps(message))

manager = ConnectionManager()

# Database Models
class UserCreate(BaseModel):
    supabase_user_id: str
    email: str

class UserResponse(BaseModel):
    id: str
    supabase_user_id: str
    email: str
    created_at: datetime

class MoodLogCreate(BaseModel):
    mood_score: int
    emotion: str
    notes: Optional[str] = None
    triggers: Optional[list] = None
    activities: Optional[list] = None

class VRSessionCreate(BaseModel):
    environment: str
    breathing_technique: Optional[str] = None
    emotional_state: Optional[str] = None

class AIRequest(BaseModel):
    message: str
    context: Optional[str] = None
    emotion: Optional[str] = None
    personality: Optional[str] = None
    session_id: Optional[str] = None

class AIResponse(BaseModel):
    response: str
    therapeutic_approach: str
    confidence: float
    suggestions: List[str]
    topics: List[str] = []
    recommended_activities: List[str] = []
    suggested_vr_mode: Optional[str] = None
    risk_level: str = "low"
    session_id: Optional[str] = None
    emotional_state: Optional[Dict] = None  # Add emotional state field
    
    # Structured output fields for frontend compatibility
    message: Optional[str] = None  # Will be set to response
    recommendedActivity: Optional[str] = None  # Will be set to first recommended activity
    mode: Optional[str] = None  # Will be set to suggested_vr_mode
    emotional_category: Optional[str] = None  # Will be extracted from emotional_state
    
    def __init__(self, **data):
        super().__init__(**data)
        # Automatically populate structured fields
        self.message = self.response
        if self.recommended_activities:
            self.recommendedActivity = self.recommended_activities[0]
        self.mode = self.suggested_vr_mode
        if self.emotional_state and 'category' in self.emotional_state:
            self.emotional_category = self.emotional_state['category']

class ActivitySessionStart(BaseModel):
    activity_id: str
    title: str
    category: str
    duration_minutes: Optional[int] = None
    recommended_source: Optional[str] = None

class ActivitySessionComplete(BaseModel):
    session_id: Optional[str] = None
    activity_id: str
    title: str
    category: str
    duration_minutes: Optional[int] = None
    recommended_source: Optional[str] = None
    pre_mood_score: Optional[int] = None
    post_mood_score: Optional[int] = None
    notes: Optional[str] = None

class VRSessionComplete(BaseModel):
    duration_minutes: Optional[int] = None
    completion_rate: Optional[float] = None
    pre_mood_score: Optional[int] = None
    post_mood_score: Optional[int] = None
    notes: Optional[str] = None

# Database Connection
def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

def ensure_backend_schema():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                supabase_user_id VARCHAR(255) UNIQUE,
                email VARCHAR(255) UNIQUE NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
            """
        )
        cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS supabase_user_id VARCHAR(255)")
        cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS email VARCHAR(255)")
        cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()")
        cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()")
        cursor.execute(
            """
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1
                    FROM information_schema.columns
                    WHERE table_schema = 'public' AND table_name = 'users' AND column_name = 'password_hash'
                ) THEN
                    EXECUTE 'ALTER TABLE users ALTER COLUMN password_hash SET DEFAULT ''''';
                    EXECUTE 'UPDATE users SET password_hash = '''' WHERE password_hash IS NULL';
                    EXECUTE 'ALTER TABLE users ALTER COLUMN password_hash DROP NOT NULL';
                END IF;
            END $$;
            """
        )
        cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_supabase_user_id ON users(supabase_user_id)")

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS conversation_sessions (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                summary TEXT,
                primary_topic VARCHAR(100),
                safety_level VARCHAR(20) DEFAULT 'low',
                therapeutic_approach VARCHAR(100),
                techniques_used TEXT[] DEFAULT ARRAY[]::TEXT[],
                started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_messages (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                session_id UUID NOT NULL REFERENCES conversation_sessions(id) ON DELETE CASCADE,
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
            """
        )
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chat_messages_user_created ON chat_messages(user_id, created_at DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chat_messages_session_created ON chat_messages(session_id, created_at ASC)")

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS activity_sessions (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                activity_id VARCHAR(120) NOT NULL,
                title VARCHAR(255) NOT NULL,
                category VARCHAR(100) NOT NULL,
                recommended_source VARCHAR(50),
                pre_mood_score INTEGER,
                post_mood_score INTEGER,
                duration_minutes INTEGER,
                status VARCHAR(20) NOT NULL DEFAULT 'started',
                notes TEXT,
                started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                completed_at TIMESTAMP WITH TIME ZONE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
            """
        )
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_activity_sessions_user_created ON activity_sessions(user_id, created_at DESC)")

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ai_memories (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                category VARCHAR(100) NOT NULL,
                information TEXT NOT NULL,
                importance VARCHAR(20) DEFAULT 'Medium',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
            """
        )
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ai_memories_user_created ON ai_memories(user_id, created_at DESC)")

        cursor.execute("ALTER TABLE vr_sessions ADD COLUMN IF NOT EXISTS breathing_technique VARCHAR(50)")
        cursor.execute("ALTER TABLE vr_sessions ADD COLUMN IF NOT EXISTS emotional_state VARCHAR(50)")
        cursor.execute("ALTER TABLE vr_sessions ADD COLUMN IF NOT EXISTS duration_minutes INTEGER")
        cursor.execute("ALTER TABLE vr_sessions ADD COLUMN IF NOT EXISTS completion_rate DECIMAL(5,2)")
        cursor.execute("ALTER TABLE vr_sessions ADD COLUMN IF NOT EXISTS notes TEXT")
        cursor.execute("ALTER TABLE vr_sessions ADD COLUMN IF NOT EXISTS prompt_source VARCHAR(50)")
        cursor.execute("ALTER TABLE vr_sessions ADD COLUMN IF NOT EXISTS pre_mood_score INTEGER")
        cursor.execute("ALTER TABLE vr_sessions ADD COLUMN IF NOT EXISTS post_mood_score INTEGER")
        cursor.execute("ALTER TABLE vr_sessions ADD COLUMN IF NOT EXISTS started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()")
        cursor.execute("ALTER TABLE vr_sessions ADD COLUMN IF NOT EXISTS completed_at TIMESTAMP WITH TIME ZONE")
        cursor.execute("ALTER TABLE vr_sessions ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()")

        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Schema setup failed: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

def build_time_filter(column_name: str, range_key: str):
    if range_key == "7d":
        return f" AND {column_name} >= %s", [datetime.now() - timedelta(days=7)]
    if range_key == "30d":
        return f" AND {column_name} >= %s", [datetime.now() - timedelta(days=30)]
    return "", []

def detect_crisis_level(message: str, emotional_valence: Optional[float] = None, emotional_arousal: Optional[float] = None) -> str:
    """
    Enhanced crisis detection with multiple signal sources and scoring logic
    
    Args:
        message: User message to analyze
        emotional_valence: Optional emotional valence (-1 to 1)
        emotional_arousal: Optional emotional arousal (-1 to 1)
        
    Returns:
        Risk level: "high", "medium", or "low"
    """
    import re
    
    lower_message = message.lower()
    score = 0.0
    
    # 1. HIGH RISK KEYWORDS (weight: 0.8)
    high_risk_keywords = [
        "suicide", "kill myself", "end my life", "want to die", "self harm",
        "overdose", "better off dead", "hang myself", "take my life",
        "want to disappear", "end it all", "no reason to live", "can't go on",
        "shouldn't exist", "wish i was dead", "cut myself", "hurt myself",
        "disappear", "vanish", "wish i could disappear"
    ]
    
    # 2. MEDIUM RISK KEYWORDS (weight: 0.4)
    medium_risk_keywords = [
        "hopeless", "can't go on", "panic attack", "overwhelmed", "unsafe",
        "desperate", "giving up", "can't take it anymore", "at breaking point"
    ]
    
    # LOW RISK KEYWORDS (weight: 0.2) - only count if no other signals
    low_risk_keywords = [
        "anxious", "stressed", "worried", "nervous", "afraid"
    ]
    
    # 3. HIGH RISK PHRASES (weight: 0.9)
    high_risk_phrases = [
        r"i\s+want\s+to\s+(?:kill|end|take)\s+my\s+life",
        r"i'm\s+going\s+to\s+(?:kill|end|take)\s+my\s+life",
        r"i\s+should\s+(?:kill|end|take)\s+my\s+life",
        r"i\s+want\s+to\s+(?:die|disappear|vanish)",
        r"i'm\s+going\s+to\s+hurt\s+myself",
        r"i\s+want\s+to\s+hurt\s+myself",
        r"i'm\s+going\s+to\s+overdose",
        r"i\s+want\s+to\s+overdose"
    ]
    
    # 4. SEVERE DISTRESS PHRASES (weight: 0.6)
    severe_distress_phrases = [
        r"hearing\s+voices",
        r"voices\s+(?:are\s+)?telling\s+me",
        r"nothing\s+feels\s+real",
        r"detached\s+from\s+reality",
        r"out\s+of\s+my\s+body",
        r"losing\s+my\s+mind",
        r"going\s+crazy",
        r"can't\s+control\s+myself"
    ]
    
    # Calculate keyword scores
    keyword_score = 0.0
    for keyword in high_risk_keywords:
        if keyword in lower_message:
            keyword_score += 0.8
            break  # One high-risk keyword is enough
    
    for keyword in medium_risk_keywords:
        if keyword in lower_message:
            keyword_score += 0.4
            break  # Only count once per category
    
    # Calculate phrase pattern scores
    phrase_score = 0.0
    for pattern in high_risk_phrases:
        if re.search(pattern, lower_message):
            phrase_score += 0.9
            break  # One high-risk phrase is enough
    
    for pattern in severe_distress_phrases:
        if re.search(pattern, lower_message):
            phrase_score += 0.6
            break  # Only count once per category
    
    # Only count low-risk keywords if no other signals detected
    if keyword_score == 0 and phrase_score == 0:
        for keyword in low_risk_keywords:
            if keyword in lower_message:
                keyword_score += 0.2
                break
    
    # Calculate emotional state scores
    emotional_score = 0.0
    if emotional_valence is not None:
        # Very negative valence indicates distress
        if emotional_valence < -0.8:
            emotional_score += 0.6  # Increased weight
        elif emotional_valence < -0.6:
            emotional_score += 0.4
    
    if emotional_arousal is not None:
        # High arousal with negative valence indicates distress
        if emotional_arousal > 0.8:
            emotional_score += 0.5  # Increased weight
        elif emotional_arousal > 0.6 and emotional_valence is not None and emotional_valence < -0.3:
            emotional_score += 0.4
    
    # Combine scores with weights
    total_score = (
        keyword_score * 1.0 +      # Keywords are most reliable
        phrase_score * 0.9 +       # Phrases are very reliable
        emotional_score * 0.8     # Increased emotional weight
    )
    
    # Determine risk level based on total score
    if total_score >= 0.8:  # Strong signals
        return "high"
    elif total_score >= 0.3:  # Moderate signals (lowered threshold)
        return "medium"
    else:  # Weak or no signals
        return "low"

def infer_topics(message: str) -> List[Dict]:
    """
    Enhanced topic detection for adolescent mental health themes
    Returns topics with confidence scores
    """
    import re
    
    lower_message = message.lower()
    
    # Topic definitions with keywords and phrase patterns
    topic_definitions = {
        "school": {
            "keywords": [
                "school", "class", "homework", "assignment", "exam", "test",
                "study", "teacher", "student", "grade", "academic", "education",
                "university", "college", "classroom", "lecture", "deadline",
                "project", "presentation", "semester", "course", "subject"
            ],
            "phrases": [
                r"can't\s+focus\s+in\s+class",
                r"falling\s+behind\s+in\s+school",
                r"school\s+stress",
                r"exam\s+anxiety",
                r"bad\s+grades",
                r"failing\s+class",
                r"school\s+pressure"
            ],
            "weight": 1.0
        },
        "relationships": {
            "keywords": [
                "relationship", "friend", "friends", "boyfriend", "girlfriend",
                "partner", "dating", "breakup", "broken up", "cheating", "trust",
                "social", "popular", "bully", "bullying", "peer", "peers",
                r"fit\s+in", r"left\s+out", "rejected", "acceptance"
            ],
            "phrases": [
                r"break\s+up",
                r"broke\s+up",
                r"friend\s+zone",
                r"social\s+anxiety",
                r"can't\s+make\s+friends",
                r"no\s+friends",
                r"feeling\s+lonely",
                r"peer\s+pressure"
            ],
            "weight": 1.0
        },
        "family": {
            "keywords": [
                "family", "parents", "mom", "dad", "mother", "father",
                "sister", "brother", "sibling", "home", "household",
                "argue", "fight", "conflict", "divorce", "separated",
                "strict", "overprotective", "understanding", "support"
            ],
            "phrases": [
                r"family\s+fight",
                r"parents\s+don't\s+understand",
                r"family\s+pressure",
                r"home\s+life",
                r"family\s+issues",
                r"argue\s+with\s+parents",
                r"divorce",
                r"broken\s+family"
            ],
            "weight": 1.0
        },
        "sleep": {
            "keywords": [
                "sleep", "insomnia", "tired", "fatigue", "exhausted", "rest",
                "awake", "night", "bedtime", "sleepless", "oversleeping",
                "nightmare", "dreams", "circadian", "schedule", "routine"
            ],
            "phrases": [
                r"can't\s+sleep",
                r"trouble\s+sleeping",
                r"sleep\s+problems",
                r"staying\s+up\s+late",
                r"all\s+night",
                r"sleep\s+deprivation",
                r"poor\s+sleep",
                r"sleep\s+anxiety"
            ],
            "weight": 0.9
        },
        "stress": {
            "keywords": [
                "stress", "stressed", "pressure", "overwhelmed", "burnout",
                "tense", "anxious", "worried", "nervous", "panic", "coping",
                r"manage", r"handle", r"deal\s+with", "struggling", "struggle"
            ],
            "phrases": [
                r"too\s+much\s+stress",
                r"can't\s+cope",
                r"overwhelmed",
                r"stressed\s+out",
                r"burning\s+out",
                r"under\s+pressure",
                r"can't\s+handle",
                r"at\s+breaking\s+point"
            ],
            "weight": 0.9
        },
        "anxiety": {
            "keywords": [
                "anxiety", "anxious", "panic", "worry", "worried", "nervous",
                "fear", "scared", "afraid", "phobia", r"social\s+anxiety",
                r"generalized\s+anxiety", "gad", r"panic\s+attack", "attack"
            ],
            "phrases": [
                r"anxiety\s+attack",
                r"panic\s+attack",
                r"social\s+anxiety",
                r"feeling\s+anxious",
                r"can't\s+breathe",
                r"heart\s+racing",
                r"racing\s+thoughts",
                r"anxious\s+about"
            ],
            "weight": 1.0
        },
        "self_esteem": {
            "keywords": [
                r"self\s+esteem", "confidence", r"self\s+worth", r"self\s+image",
                "insecure", "insecurity", "doubt", r"self\s+doubt", "worthless",
                "failure", "fail", "failure", r"not\s+good\s+enough", "inadequate",
                "compare", "comparison", "judgment", "criticism", r"self\s+criticism"
            ],
            "phrases": [
                r"low\s+self\s+esteem",
                r"no\s+confidence",
                r"feel\s+worthless",
                r"not\s+good\s+enough",
                r"self\s+doubt",
                r"compare\s+myself",
                r"imposter\s+syndrome",
                r"self\s+conscious"
            ],
            "weight": 1.0
        },
        "loneliness": {
            "keywords": [
                "lonely", "loneliness", "alone", "isolated", "solitude",
                r"no\s+friends", "friendless", "rejection", r"left\s+out",
                "excluded", "invisible", "unseen", "disconnected", "withdrawn"
            ],
            "phrases": [
                r"feel\s+lonely",
                r"all\s+alone",
                r"no\s+one\s+understands",
                r"feel\s+isolated",
                r"can't\s+connect",
                r"socially\s+isolated",
                r"emotional\s+loneliness",
                r"feeling\s+empty"
            ],
            "weight": 1.0
        },
        "productivity": {
            "keywords": [
                "productivity", "productive", "procrastination", "motivation",
                "motivated", "unmotivated", "focus", "concentrate", "distracted",
                "lazy", "unfocused", "goals", "achievement", "accomplish",
                "task", "tasks", "deadline", r"time\s+management", "schedule"
            ],
            "phrases": [
                r"can't\s+focus",
                r"procrastinating",
                r"no\s+motivation",
                r"unmotivated",
                r"can't\s+concentrate",
                r"easily\s+distracted",
                r"time\s+management",
                r"falling\s+behind",
                r"too\s+much\s+to\s+do"
            ],
            "weight": 0.8
        }
    }
    
    detected_topics = []
    
    for topic_name, topic_data in topic_definitions.items():
        score = 0.0
        matches = []
        
        # Check keyword matches
        keyword_matches = 0
        for keyword in topic_data["keywords"]:
            # Handle regex keywords differently
            if isinstance(keyword, str) and keyword.startswith("r\"") or keyword.startswith("r'"):
                # This is a regex pattern, skip for keyword matching (handled in phrases)
                continue
            if keyword in lower_message:
                keyword_matches += 1
                matches.append(f"keyword:{keyword}")
        
        # Calculate keyword score (more matches = higher confidence)
        if keyword_matches > 0:
            keyword_score = min(keyword_matches * 0.3, 0.8)  # Cap at 0.8
            score += keyword_score
        
        # Check phrase matches (including regex keywords)
        phrase_matches = 0
        all_patterns = topic_data["phrases"].copy()
        
        # Add regex keywords to phrase patterns
        for keyword in topic_data["keywords"]:
            if isinstance(keyword, str) and (keyword.startswith("r\"") or keyword.startswith("r'")):
                # Convert raw string notation to actual regex
                pattern = keyword[2:-1] if keyword.startswith("r\"") else keyword[2:-1]
                all_patterns.append(pattern)
        
        for pattern in all_patterns:
            if re.search(pattern, lower_message):
                phrase_matches += 1
                matches.append(f"phrase:{pattern}")
        
        # Calculate phrase score (phrase matches are stronger)
        if phrase_matches > 0:
            phrase_score = min(phrase_matches * 0.5, 0.9)  # Cap at 0.9
            score += phrase_score
        
        # Apply topic weight
        final_score = score * topic_data["weight"]
        
        # Only include topics with meaningful confidence
        if final_score >= 0.3:
            detected_topics.append({
                "topic": topic_name,
                "confidence": min(final_score, 1.0),
                "matches": matches
            })
    
    # Sort by confidence score
    detected_topics.sort(key=lambda x: x["confidence"], reverse=True)
    
    # Return topic names for backward compatibility, or general_support if none found
    if detected_topics:
        return detected_topics
    else:
        return [{"topic": "general_support", "confidence": 1.0, "matches": []}]

def infer_recommendations(message: str, topics: List[str]):
    lower_message = message.lower()
    recommendations = {
        "suggestions": [
            "Pause and take one slow breath before deciding your next step.",
            "Name what you are feeling in one sentence to reduce overwhelm.",
            "Choose one small supportive action you can complete in the next 10 minutes."
        ],
        "recommended_activities": ["mindfulness-body-scan"],
        "suggested_vr_mode": None,
        "therapeutic_approach": "supportive_reflection"
    }

    if "anxiety" in topics or "stress" in topics:
        recommendations = {
            "suggestions": [
                "Try 4-7-8 breathing for five cycles.",
                "Use the 5-4-3-2-1 grounding exercise to reconnect with the present.",
                "Reduce the problem to the next one manageable action."
            ],
            "recommended_activities": ["breathing-4-7-8", "grounding-5-4-3-2-1"],
            "suggested_vr_mode": "box",
            "therapeutic_approach": "cbt_grounding"
        }
    elif "low_mood" in topics:
        recommendations = {
            "suggestions": [
                "Try a gentle body scan to reconnect with your body.",
                "Write down one compassionate response you would give a friend feeling this way.",
                "Choose one tiny activity that gives structure for the next hour."
            ],
            "recommended_activities": ["mindfulness-body-scan"],
            "suggested_vr_mode": "mindful",
            "therapeutic_approach": "act_self_compassion"
        }
    elif "sleep" in topics:
        recommendations = {
            "suggestions": [
                "Dim stimulation and avoid problem-solving in bed.",
                "Do a slow breathing exercise with a longer exhale.",
                "Try a short body scan instead of forcing sleep."
            ],
            "recommended_activities": ["breathing-4-7-8", "mindfulness-body-scan"],
            "suggested_vr_mode": "deep",
            "therapeutic_approach": "sleep_hygiene_support"
        }

    if detect_crisis_level(message) == "high":
        recommendations["suggestions"] = [
            "Contact a crisis helpline or emergency service right now.",
            "Move closer to another person or safer environment if possible.",
            "Put distance between yourself and anything you could use to hurt yourself."
        ]
        recommendations["recommended_activities"] = ["grounding-5-4-3-2-1"]
        recommendations["suggested_vr_mode"] = None
        recommendations["therapeutic_approach"] = "crisis_support"

    if "relationships" in topics and "relationships" not in lower_message:
        recommendations["recommended_activities"] = recommendations["recommended_activities"] + ["mindfulness-body-scan"]

    return recommendations

def build_supportive_response(message: str, topics: List[str], risk_level: str, approach: str) -> str:
    if risk_level == "high":
        return (
            "I'm really glad you told me this. I may not be enough support for this level of danger, "
            "so I want to be direct: please contact a crisis service, emergency support, or a trusted person with you right now. "
            "If you can, do not stay alone while you get immediate help."
        )

    if "anxiety" in topics or "stress" in topics:
        return (
            "It sounds like your system is carrying a lot right now. Let's slow things down and work with what is happening in this moment. "
            "Notice your feet, relax your shoulders, and try one steady breath in and a longer breath out. "
            "From there, we can focus on one manageable next step instead of the whole problem at once."
        )

    if "low_mood" in topics:
        return (
            "Thank you for being honest about how heavy things feel. I want to respond with care, not pressure. "
            "When mood is low, very small actions often work better than big goals. "
            "Let's focus on one grounding action, one kind thought, and one realistic task for today."
        )

    if "sleep" in topics:
        return (
            "Sleep struggles can make everything feel louder. Instead of forcing sleep, it can help to create the conditions for rest: "
            "lower stimulation, slow the breath, and return attention to the body whenever your mind starts racing."
        )

    if approach == "act_self_compassion":
        return (
            "What you're feeling deserves space and kindness. Rather than fighting the feeling, let's notice it, make room for it, "
            "and choose one small action that still moves you toward what matters to you."
        )

    return (
        "Thank you for sharing that. I'm here to help you slow this down, understand what is most present for you, "
        "and find one evidence-based step that feels realistic right now."
    )

def get_or_create_conversation_session(user_id: str, request_session_id: Optional[str] = None) -> str:
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if request_session_id:
            cursor.execute(
                "SELECT id FROM conversation_sessions WHERE id = %s AND user_id = %s",
                (request_session_id, user_id)
            )
            existing_session = cursor.fetchone()
            if existing_session:
                return str(existing_session[0])

        cursor.execute(
            """
            SELECT id
            FROM conversation_sessions
            WHERE user_id = %s AND updated_at >= %s
            ORDER BY updated_at DESC
            LIMIT 1
            """,
            (user_id, datetime.now() - timedelta(hours=6))
        )
        recent_session = cursor.fetchone()
        if recent_session:
            return str(recent_session[0])

        session_id = str(uuid.uuid4())
        cursor.execute(
            """
            INSERT INTO conversation_sessions (id, user_id, started_at, updated_at)
            VALUES (%s, %s, %s, %s)
            """,
            (session_id, user_id, datetime.now(), datetime.now())
        )
        conn.commit()
        return session_id
    except Exception as e:
        conn.rollback()
        logger.error(f"Conversation session error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create conversation session"
        )
    finally:
        cursor.close()
        conn.close()

def update_conversation_session(session_id: str, response: AIResponse, user_message: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            UPDATE conversation_sessions
            SET summary = %s,
                primary_topic = %s,
                safety_level = %s,
                therapeutic_approach = %s,
                techniques_used = %s,
                updated_at = %s
            WHERE id = %s
            """,
            (
                user_message[:180],
                response.topics[0] if response.topics else "general_support",
                response.risk_level,
                response.therapeutic_approach,
                response.suggestions,
                datetime.now(),
                session_id,
            )
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to update conversation session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update conversation session"
        )
    finally:
        cursor.close()
        conn.close()

@app.on_event("startup")
async def startup_event():
    ensure_backend_schema()

# JWT Verification
def verify_supabase_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token, 
            SUPABASE_JWT_SECRET, 
            algorithms=["HS256"],
            audience="authenticated"
        )
        
        if payload.get("exp") < datetime.now().timestamp():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired"
            )
        
        return payload
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )

# Get or Create User
def get_or_create_user(supabase_user_id: str, email: str) -> UserResponse:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "SELECT id, supabase_user_id, email, created_at FROM users WHERE supabase_user_id = %s",
            (supabase_user_id,)
        )
        user = cursor.fetchone()
        
        if user:
            return UserResponse(
                id=user[0],
                supabase_user_id=user[1],
                email=user[2],
                created_at=user[3]
            )
        
        user_id = str(uuid.uuid4())
        cursor.execute(
            """
            INSERT INTO users (id, supabase_user_id, email, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, supabase_user_id, email, created_at
            """,
            (user_id, supabase_user_id, email, datetime.now(), datetime.now())
        )
        
        user = cursor.fetchone()
        conn.commit()
        
        return UserResponse(
            id=user[0],
            supabase_user_id=user[1],
            email=user[2],
            created_at=user[3]
        )
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database operation failed"
        )
    finally:
        cursor.close()
        conn.close()

# AI Processing Layer
from services.crisis_detection import crisis_detector, RiskLevel

class AIProcessor:
    def __init__(self):
        self.mock_mode = os.getenv("MOCK_AI", "false").lower() == "true"
        self.provider = "rule_based"
    
    async def process_message(self, user_id: str, message: str, emotion: str = None, personality: Optional[str] = None, session_id: Optional[str] = None) -> AIResponse:
        await asyncio.sleep(0.2 if self.mock_mode else 0.1)

        # Save user message to conversation history
        self.save_conversation_message(user_id, message, "user", session_id)

        # STEP 1: Crisis Detection - analyze message first
        crisis_analysis = crisis_detector.analyze_message(message)
        
        # STEP 2: Handle HIGH risk - bypass normal AI flow
        if crisis_analysis['risk_level'] == RiskLevel.HIGH:
            crisis_response = self._build_crisis_response(crisis_analysis)
            # Save crisis response to conversation history
            self.save_conversation_message(user_id, crisis_response.response, "assistant", session_id, {
                'therapeutic_approach': crisis_response.therapeutic_approach,
                'risk_level': crisis_response.risk_level,
                'suggestions': crisis_response.suggestions
            })
            return crisis_response
        
        # STEP 3: Update emotional state based on message content
        from services.emotional_state_engine import emotional_state_engine
        emotional_state_obj = emotional_state_engine.update_from_chat(user_id, message)
        emotional_state = emotional_state_obj.to_dict() if emotional_state_obj else None
        
        # STEP 4: Detect topics
        topics = infer_topics(message)
        # Extract topic names for backward compatibility
        if topics and isinstance(topics[0], dict):
            topic_names = [t["topic"] for t in topics]
        else:
            topic_names = topics if topics else []
        
        # STEP 5: Build prompt with emotional context
        from services.prompt_builder import prompt_builder, PromptComponents
        from services.recommendation_engine_extended import recommendation_engine_extended
        from services.conversation_history import get_conversation_history, format_history_for_prompt
        
        # Get conversation history (last 5 messages)
        conversation_history_raw = get_conversation_history(user_id, limit=5)
        conversation_history = format_history_for_prompt(conversation_history_raw)
        
        # Build prompt with emotional state context
        prompt_components = PromptComponents(
            ai_identity="",
            behavioral_guidelines="",
            safety_rules="",
            emotional_state=emotional_state,
            conversation_history=conversation_history,
            user_message=message,
            user_context={'user_id': user_id}
        )
        
        # STEP 6: Generate response using prompt builder
        # For now, use existing response generation as fallback
        # In production, this would use the built prompt with LLM
        legacy_risk_level = detect_crisis_level(message)  # Keep existing for backward compat
        recommendation_bundle = infer_recommendations(message, topic_names)
        response_text = build_supportive_response(
            message,
            topic_names,
            legacy_risk_level,
            recommendation_bundle["therapeutic_approach"],
        )

        # STEP 7: Retrieve personalized recommendations based on emotional state
        if emotional_state:
            emotional_category = emotional_state.get('category', 'neutral')
            valence = emotional_state.get('valence', 0.0)
            arousal = emotional_state.get('arousal', 0.0)
            
            # Get user history for personalization
            user_history = recommendation_engine_extended.get_user_activity_history(user_id)
            
            # Get personalized recommendations
            recommendations = recommendation_engine_extended.get_recommendations(
                emotional_category=emotional_category,
                valence=valence,
                arousal=arousal,
                user_id=user_id
            )
            
            # Update recommendation bundle with personalized results
            if recommendations['primary_activity']:
                recommendation_bundle["recommended_activities"] = [recommendations['primary_activity']['activity_id']]
            if recommendations['vr_mode']:
                recommendation_bundle["suggested_vr_mode"] = recommendations['vr_mode']
        
        # STEP 8: Append MODERATE risk gentle encouragement
        if crisis_analysis['risk_level'] == RiskLevel.MODERATE:
            response_text += self._build_moderate_risk_encouragement()

        # STEP 9: Personality modifiers (existing)
        if personality == "mindfulness" and legacy_risk_level == "low":
            response_text += " Focus gently on what you can notice in your breathing, your body, and your surroundings right now."
        if personality == "professional" and legacy_risk_level == "low":
            response_text += " If it helps, we can next identify the thought, emotion, and action urge involved here."

        confidence = 0.95 if legacy_risk_level == "high" else 0.82

        final_response = AIResponse(
            response=response_text,
            therapeutic_approach=recommendation_bundle["therapeutic_approach"],
            confidence=confidence,
            suggestions=recommendation_bundle["suggestions"],
            topics=topic_names,  # Use topic_names instead of topics
            recommended_activities=recommendation_bundle["recommended_activities"],
            suggested_vr_mode=recommendation_bundle["suggested_vr_mode"],
            risk_level=legacy_risk_level,
            emotional_state=emotional_state  # Add emotional state to response
        )
        
        # Save assistant response to conversation history
        self.save_conversation_message(user_id, response_text, "assistant", session_id, {
            'therapeutic_approach': final_response.therapeutic_approach,
            'confidence': final_response.confidence,
            'topics': final_response.topics,
            'recommended_activities': final_response.recommended_activities,
            'suggested_vr_mode': final_response.suggested_vr_mode,
            'risk_level': final_response.risk_level,
            'emotional_state': final_response.emotional_state
        })
        
        return final_response
    
    def save_conversation_message(self, user_id: str, message: str, role: str, session_id: Optional[str] = None, metadata: Optional[Dict] = None) -> bool:
        """
        Save conversation message to history
        
        Args:
            user_id: User identifier
            message: Message content
            role: Message role ("user" or "assistant")
            session_id: Optional session identifier
            metadata: Optional metadata (for assistant messages)
            
        Returns:
            True if successfully saved
        """
        try:
            from services.conversation_history import add_user_message, add_assistant_message
            
            if role == "user":
                return add_user_message(user_id, message, session_id)
            elif role == "assistant":
                return add_assistant_message(user_id, message, session_id, metadata)
            else:
                return False
        except Exception as e:
            print(f"Error saving conversation message: {e}")
            return False
    
    def _build_crisis_response(self, crisis_analysis: Dict) -> AIResponse:
        """Build immediate crisis escalation response with Malaysian resources"""
        
        # Import support resources for structured Malaysian resources
        from services.support_resources import malaysian_support_resources
        
        # Supportive escalation message with structured resources
        escalation_text = (
            "I'm really glad you shared this with me, and I want to respond with care. "
            "What you're describing sounds like you might need support beyond what I can provide right now. "
            "\n\n"
            "It's important to speak with someone who can help you directly. "
            "Please reach out to one of these crisis support services:\n\n"
        )
        
        # Add structured Malaysian resources
        escalation_text += malaysian_support_resources.format_for_crisis_response()
        
        escalation_text += (
            "\n"
            "You don't have to go through this alone. These services are confidential, "
            "free where specified, and staffed by trained professionals who want to help you. "
            "Reaching out is a sign of strength, and you deserve support right now."
        )
        
        # Get specific crisis suggestions from resources
        crisis_services = malaysian_support_resources.get_crisis_services()
        suggestions = []
        
        for service in crisis_services[:3]:  # Top 3 crisis services
            phone_contacts = [cm for cm in service.contact_methods if cm.type == "phone"]
            if phone_contacts:
                phone = phone_contacts[0]
                suggestions.append(f"Contact {service.name} immediately: {phone.value}")
        
        # Add general crisis suggestions
        suggestions.extend([
            "Reach out to a trusted person right now",
            "Go to emergency services if in immediate danger: 999"
        ])
        
        return AIResponse(
            response=escalation_text,
            therapeutic_approach="crisis_escalation",
            confidence=crisis_analysis['confidence'],
            suggestions=suggestions,
            topics=["crisis", "emergency_support"],
            recommended_activities=[],  # No activities for HIGH risk - focus on immediate help
            suggested_vr_mode=None,
            risk_level="high",
            emotional_state=None  # No emotional state analysis for crisis - focus on safety
        )
    
    def _build_moderate_risk_encouragement(self) -> str:
        """Build gentle encouragement for moderate risk"""
        return (
            "\n\nI hear that things feel really intense right now. "
            "While I'm here to support you, it might also help to speak with "
            "a mental health professional who can provide more specialized support.\n\n"
            "**Professional Support Options:**\n"
            "• **Talian HEAL**: 15555 (8am-12am daily, tele-counseling)\n"
            "• **Life Line Malaysia**: 03-4265-7995 (12pm-10pm daily)\n"
            "\n"
            "In the meantime, let's work through this together."
        )

# Initialize AI processor
ai_processor = AIProcessor()

# Protected Routes
@app.get("/me", response_model=UserResponse)
async def get_current_user(payload: Dict[str, Any] = Depends(verify_supabase_token)):
    supabase_user_id = payload.get("sub")
    email = payload.get("email")
    
    if not supabase_user_id or not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token payload"
        )
    
    user = get_or_create_user(supabase_user_id, email)
    return user

@app.post("/mood/log")
async def create_mood_log(
    mood_data: MoodLogCreate,
    payload: Dict[str, Any] = Depends(verify_supabase_token)
):
    supabase_user_id = payload.get("sub")
    user = get_or_create_user(supabase_user_id, payload.get("email"))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            """
            INSERT INTO mood_logs (user_id, mood_score, emotion, notes, triggers, activities, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, mood_score, emotion, notes, triggers, activities, created_at
            """,
            (
                user.id,
                mood_data.mood_score,
                mood_data.emotion,
                mood_data.notes,
                mood_data.triggers,
                mood_data.activities,
                datetime.now(),
                datetime.now()
            )
        )
        
        mood_log = cursor.fetchone()
        conn.commit()
        
        await store_emotional_memory(user.id, mood_data.emotion, mood_data.notes, mood_data.mood_score)
        
        return {
            "id": mood_log[0],
            "mood_score": mood_log[1],
            "emotion": mood_log[2],
            "notes": mood_log[3],
            "triggers": mood_log[4],
            "activities": mood_log[5],
            "created_at": mood_log[6]
        }
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Mood log creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create mood log"
        )
    finally:
        cursor.close()
        conn.close()

@app.post("/vr/session")
async def create_vr_session(
    session_data: VRSessionCreate,
    payload: Dict[str, Any] = Depends(verify_supabase_token)
):
    supabase_user_id = payload.get("sub")
    user = get_or_create_user(supabase_user_id, payload.get("email"))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            """
            INSERT INTO vr_sessions (user_id, environment, breathing_technique, emotional_state, created_at)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, environment, breathing_technique, emotional_state, created_at
            """,
            (user.id, session_data.environment, session_data.breathing_technique, session_data.emotional_state, datetime.now())
        )
        
        session = cursor.fetchone()
        conn.commit()
        
        return {
            "id": session[0],
            "environment": session[1],
            "breathing_technique": session[2],
            "emotional_state": session[3],
            "created_at": session[4]
        }
        
    except Exception as e:
        conn.rollback()
        logger.error(f"VR session creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create VR session"
        )
    finally:
        cursor.close()
        conn.close()

@app.post("/vr/session/{session_id}/complete")
async def complete_vr_session(
    session_id: str,
    session_data: VRSessionComplete,
    payload: Dict[str, Any] = Depends(verify_supabase_token)
):
    supabase_user_id = payload.get("sub")
    user = get_or_create_user(supabase_user_id, payload.get("email"))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            """
            UPDATE vr_sessions
            SET duration_minutes = COALESCE(%s, duration_minutes),
                completion_rate = COALESCE(%s, completion_rate),
                pre_mood_score = COALESCE(%s, pre_mood_score),
                post_mood_score = COALESCE(%s, post_mood_score),
                notes = COALESCE(%s, notes),
                completed_at = %s
            WHERE id = %s AND user_id = %s
            RETURNING id, duration_minutes, completion_rate, pre_mood_score, post_mood_score, completed_at
            """,
            (
                session_data.duration_minutes,
                session_data.completion_rate,
                session_data.pre_mood_score,
                session_data.post_mood_score,
                session_data.notes,
                datetime.now(),
                session_id,
                user.id,
            )
        )
        session = cursor.fetchone()
        conn.commit()

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="VR session not found"
            )

        return {
            "id": session[0],
            "duration_minutes": session[1],
            "completion_rate": float(session[2]) if session[2] is not None else None,
            "pre_mood_score": session[3],
            "post_mood_score": session[4],
            "completed_at": session[5]
        }
    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        logger.error(f"VR session completion error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete VR session"
        )
    finally:
        cursor.close()
        conn.close()

@app.post("/activities/start")
async def start_activity_session(
    activity_data: ActivitySessionStart,
    payload: Dict[str, Any] = Depends(verify_supabase_token)
):
    user = get_or_create_user(payload.get("sub"), payload.get("email"))
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO activity_sessions (
                user_id, activity_id, title, category, recommended_source, duration_minutes, status, started_at, created_at, updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, 'started', %s, %s, %s)
            RETURNING id, status, started_at
            """,
            (
                user.id,
                activity_data.activity_id,
                activity_data.title,
                activity_data.category,
                activity_data.recommended_source,
                activity_data.duration_minutes,
                datetime.now(),
                datetime.now(),
                datetime.now(),
            )
        )
        session = cursor.fetchone()
        conn.commit()

        return {
            "id": session[0],
            "status": session[1],
            "started_at": session[2]
        }
    except Exception as e:
        conn.rollback()
        logger.error(f"Activity start error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start activity"
        )
    finally:
        cursor.close()
        conn.close()

@app.post("/activities/complete")
async def complete_activity_session(
    activity_data: ActivitySessionComplete,
    payload: Dict[str, Any] = Depends(verify_supabase_token)
):
    user = get_or_create_user(payload.get("sub"), payload.get("email"))
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if activity_data.session_id:
            cursor.execute(
                """
                UPDATE activity_sessions
                SET duration_minutes = COALESCE(%s, duration_minutes),
                    recommended_source = COALESCE(%s, recommended_source),
                    pre_mood_score = COALESCE(%s, pre_mood_score),
                    post_mood_score = COALESCE(%s, post_mood_score),
                    notes = COALESCE(%s, notes),
                    status = 'completed',
                    completed_at = %s,
                    updated_at = %s
                WHERE id = %s AND user_id = %s
                RETURNING id, status, completed_at
                """,
                (
                    activity_data.duration_minutes,
                    activity_data.recommended_source,
                    activity_data.pre_mood_score,
                    activity_data.post_mood_score,
                    activity_data.notes,
                    datetime.now(),
                    datetime.now(),
                    activity_data.session_id,
                    user.id,
                )
            )
            session = cursor.fetchone()
        else:
            cursor.execute(
                """
                INSERT INTO activity_sessions (
                    user_id, activity_id, title, category, recommended_source, duration_minutes,
                    pre_mood_score, post_mood_score, notes, status, started_at, completed_at, created_at, updated_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'completed', %s, %s, %s, %s)
                RETURNING id, status, completed_at
                """,
                (
                    user.id,
                    activity_data.activity_id,
                    activity_data.title,
                    activity_data.category,
                    activity_data.recommended_source,
                    activity_data.duration_minutes,
                    activity_data.pre_mood_score,
                    activity_data.post_mood_score,
                    activity_data.notes,
                    datetime.now(),
                    datetime.now(),
                    datetime.now(),
                    datetime.now(),
                )
            )
            session = cursor.fetchone()

        conn.commit()

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activity session not found"
            )

        return {
            "id": session[0],
            "status": session[1],
            "completed_at": session[2]
        }
    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        logger.error(f"Activity completion error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete activity"
        )
    finally:
        cursor.close()
        conn.close()

@app.get("/activities/summary")
async def get_activity_summary(
    payload: Dict[str, Any] = Depends(verify_supabase_token)
):
    user = get_or_create_user(payload.get("sub"), payload.get("email"))
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM activity_sessions
            WHERE user_id = %s AND status = 'completed'
            """,
            (user.id,)
        )
        total_completed = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM activity_sessions
            WHERE user_id = %s AND status = 'completed' AND completed_at >= %s
            """,
            (user.id, datetime.now().replace(hour=0, minute=0, second=0, microsecond=0))
        )
        today_completed = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT activity_id, title, COUNT(*) AS completion_count, MAX(completed_at) AS last_completed_at
            FROM activity_sessions
            WHERE user_id = %s AND status = 'completed'
            GROUP BY activity_id, title
            ORDER BY completion_count DESC, MAX(completed_at) DESC
            """,
            (user.id,)
        )
        rows = cursor.fetchall()

        return {
            "today_completed": today_completed,
            "total_completed": total_completed,
            "activity_stats": [
                {
                    "activity_id": row[0],
                    "title": row[1],
                    "completion_count": row[2],
                    "last_completed_at": row[3]
                }
                for row in rows
            ]
        }
    except Exception as e:
        logger.error(f"Activity summary error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load activity summary"
        )
    finally:
        cursor.close()
        conn.close()

@app.get("/chat/history")
async def get_chat_history(
    limit: int = 50,
    payload: Dict[str, Any] = Depends(verify_supabase_token)
):
    user = get_or_create_user(payload.get("sub"), payload.get("email"))
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT id, session_id, role, content, created_at
            FROM (
                SELECT id, session_id, role, content, created_at
                FROM chat_messages
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT %s
            ) recent_messages
            ORDER BY created_at ASC
            """,
            (user.id, limit)
        )
        messages = cursor.fetchall()

        cursor.execute(
            """
            SELECT id
            FROM conversation_sessions
            WHERE user_id = %s
            ORDER BY updated_at DESC
            LIMIT 1
            """,
            (user.id,)
        )
        latest_session = cursor.fetchone()

        return {
            "session_id": str(latest_session[0]) if latest_session else None,
            "messages": [
                {
                    "id": row[0],
                    "session_id": row[1],
                    "role": row[2],
                    "content": row[3],
                    "created_at": row[4]
                }
                for row in messages
            ]
        }
    except Exception as e:
        logger.error(f"Chat history error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load chat history"
        )
    finally:
        cursor.close()
        conn.close()

@app.delete("/chat/history")
async def clear_chat_history(
    payload: Dict[str, Any] = Depends(verify_supabase_token)
):
    user = get_or_create_user(payload.get("sub"), payload.get("email"))
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM chat_messages WHERE user_id = %s", (user.id,))
        cursor.execute("DELETE FROM conversation_sessions WHERE user_id = %s", (user.id,))
        conn.commit()
        return {"cleared": True}
    except Exception as e:
        conn.rollback()
        logger.error(f"Clear chat history error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear chat history"
        )
    finally:
        cursor.close()
        conn.close()

@app.get("/history/sessions")
async def get_history_sessions(
    limit: int = 20,
    payload: Dict[str, Any] = Depends(verify_supabase_token)
):
    user = get_or_create_user(payload.get("sub"), payload.get("email"))
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            SELECT id, summary, primary_topic, safety_level, therapeutic_approach, techniques_used, started_at, updated_at
            FROM conversation_sessions
            WHERE user_id = %s
            ORDER BY updated_at DESC
            LIMIT %s
            """,
            (user.id, limit)
        )
        sessions = cursor.fetchall()
        response_sessions = []

        for session in sessions:
            cursor.execute(
                """
                SELECT id, role, content, created_at
                FROM chat_messages
                WHERE session_id = %s
                ORDER BY created_at ASC
                """,
                (session[0],)
            )
            messages = cursor.fetchall()
            response_sessions.append(
                {
                    "id": str(session[0]),
                    "summary": session[1] or "Conversation session",
                    "primary_topic": session[2] or "general_support",
                    "safety_level": session[3] or "low",
                    "therapeutic_approach": session[4] or "supportive_reflection",
                    "techniques_used": session[5] or [],
                    "started_at": session[6],
                    "updated_at": session[7],
                    "message_count": len(messages),
                    "preview": [
                        {
                            "id": row[0],
                            "role": row[1],
                            "content": row[2],
                            "created_at": row[3]
                        }
                        for row in messages[:4]
                    ]
                }
            )

        return {"sessions": response_sessions}
    except Exception as e:
        logger.error(f"History sessions error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load conversation history"
        )
    finally:
        cursor.close()
        conn.close()

@app.get("/progress/summary")
async def get_progress_summary(
    range_key: str = "30d",
    payload: Dict[str, Any] = Depends(verify_supabase_token)
):
    user = get_or_create_user(payload.get("sub"), payload.get("email"))
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        session_filter, session_params = build_time_filter("started_at", range_key)
        activity_filter, activity_params = build_time_filter("completed_at", range_key)
        vr_filter, vr_params = build_time_filter("created_at", range_key)

        cursor.execute(
            f"""
            SELECT COUNT(*)
            FROM conversation_sessions
            WHERE user_id = %s {session_filter}
            """,
            [user.id] + session_params
        )
        total_sessions = cursor.fetchone()[0]

        cursor.execute(
            f"""
            SELECT COUNT(*)
            FROM activity_sessions
            WHERE user_id = %s AND status = 'completed' {activity_filter}
            """,
            [user.id] + activity_params
        )
        activities_done = cursor.fetchone()[0]

        cursor.execute(
            f"""
            SELECT COUNT(*)
            FROM vr_sessions
            WHERE user_id = %s {vr_filter}
            """,
            [user.id] + vr_params
        )
        vr_sessions_count = cursor.fetchone()[0]

        cursor.execute(
            f"""
            SELECT AVG(duration_minutes)
            FROM (
                SELECT duration_minutes FROM activity_sessions WHERE user_id = %s AND duration_minutes IS NOT NULL {activity_filter}
                UNION ALL
                SELECT duration_minutes FROM vr_sessions WHERE user_id = %s AND duration_minutes IS NOT NULL {vr_filter}
            ) durations
            """,
            [user.id] + activity_params + [user.id] + vr_params
        )
        avg_duration = cursor.fetchone()[0]

        cursor.execute(
            f"""
            SELECT AVG(improvement)
            FROM (
                SELECT (post_mood_score - pre_mood_score)::DECIMAL AS improvement
                FROM activity_sessions
                WHERE user_id = %s AND post_mood_score IS NOT NULL AND pre_mood_score IS NOT NULL {activity_filter}
                UNION ALL
                SELECT (post_mood_score - pre_mood_score)::DECIMAL AS improvement
                FROM vr_sessions
                WHERE user_id = %s AND post_mood_score IS NOT NULL AND pre_mood_score IS NOT NULL {vr_filter}
            ) improvements
            """,
            [user.id] + activity_params + [user.id] + vr_params
        )
        avg_mood_improvement = cursor.fetchone()[0]

        cursor.execute(
            f"""
            SELECT DATE(created_at) AS day,
                   AVG(pre_mood_score) AS mood_before,
                   AVG(post_mood_score) AS mood_after
            FROM (
                SELECT created_at, pre_mood_score, post_mood_score
                FROM activity_sessions
                WHERE user_id = %s AND pre_mood_score IS NOT NULL AND post_mood_score IS NOT NULL {activity_filter.replace('completed_at', 'created_at')}
                UNION ALL
                SELECT created_at, pre_mood_score, post_mood_score
                FROM vr_sessions
                WHERE user_id = %s AND pre_mood_score IS NOT NULL AND post_mood_score IS NOT NULL {vr_filter}
            ) mood_events
            GROUP BY DATE(created_at)
            ORDER BY DATE(created_at) ASC
            """,
            [user.id] + activity_params + [user.id] + vr_params
        )
        mood_rows = cursor.fetchall()

        cursor.execute(
            f"""
            SELECT title,
                   COUNT(*) AS times_completed,
                   AVG(COALESCE(post_mood_score - pre_mood_score, 0)) AS mood_improvement
            FROM activity_sessions
            WHERE user_id = %s AND status = 'completed' {activity_filter}
            GROUP BY title
            ORDER BY COUNT(*) DESC, title ASC
            """,
            [user.id] + activity_params
        )
        activity_rows = cursor.fetchall()

        cursor.execute(
            f"""
            SELECT COALESCE(primary_topic, 'general_support') AS topic, COUNT(*) AS topic_count
            FROM conversation_sessions
            WHERE user_id = %s {session_filter}
            GROUP BY COALESCE(primary_topic, 'general_support')
            ORDER BY COUNT(*) DESC
            LIMIT 5
            """,
            [user.id] + session_params
        )
        topic_rows = cursor.fetchall()

        insights = []
        if activities_done > 0:
            insights.append({
                "icon": "✓",
                "text": f"You've completed {activities_done} activity sessions in this period.",
                "color": "text-calm-sage"
            })
        if activity_rows:
            insights.append({
                "icon": "💡",
                "text": f"{activity_rows[0][0]} has been your most-used activity so far.",
                "color": "text-accent"
            })
        if vr_sessions_count > 0:
            insights.append({
                "icon": "🌿",
                "text": f"You've completed {vr_sessions_count} VR support sessions recently.",
                "color": "text-primary"
            })

        return {
            "stats": {
                "avg_mood_improvement": round(float(avg_mood_improvement), 1) if avg_mood_improvement is not None else 0,
                "activities_done": activities_done,
                "total_sessions": total_sessions,
                "avg_duration_minutes": round(float(avg_duration), 1) if avg_duration is not None else 0,
            },
            "mood_trend": [
                {
                    "date": row[0].strftime("%b %d"),
                    "moodBefore": round(float(row[1]), 1) if row[1] is not None else 0,
                    "moodAfter": round(float(row[2]), 1) if row[2] is not None else 0,
                }
                for row in mood_rows
            ],
            "activity_effectiveness": [
                {
                    "name": row[0],
                    "timesCompleted": row[1],
                    "moodImprovement": round(float(row[2]), 1) if row[2] is not None else 0,
                }
                for row in activity_rows
            ],
            "topics": [
                {
                    "name": row[0],
                    "value": row[1],
                }
                for row in topic_rows
            ],
            "insights": insights,
        }
    except Exception as e:
        logger.error(f"Progress summary error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load progress summary"
        )
    finally:
        cursor.close()
        conn.close()

@app.post("/ai/chat")
async def ai_chat(
    request: AIRequest,
    payload: Dict[str, Any] = Depends(verify_supabase_token)
):
    supabase_user_id = payload.get("sub")
    user = get_or_create_user(supabase_user_id, payload.get("email"))
    
    try:
        session_id = get_or_create_conversation_session(user.id, request.session_id)
        ai_response = await ai_processor.process_message(
            user_id=user.id,
            message=request.message,
            emotion=request.emotion,
            personality=request.personality
        )
        ai_response.session_id = session_id
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO chat_messages (session_id, user_id, role, content, created_at)
            VALUES (%s, %s, 'user', %s, %s)
            """,
            (session_id, user.id, request.message, datetime.now())
        )
        cursor.execute(
            """
            INSERT INTO chat_messages (session_id, user_id, role, content, created_at)
            VALUES (%s, %s, 'assistant', %s, %s)
            """,
            (session_id, user.id, ai_response.response, datetime.now())
        )
        conn.commit()
        cursor.close()
        conn.close()

        update_conversation_session(session_id, ai_response, request.message)
        
        await store_emotional_memory(user.id, "conversation", request.message, 0.8)
        
        return ai_response
        
    except Exception as e:
        logger.error(f"AI chat error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI processing failed"
        )

@app.get("/ai/similar-memories")
async def get_similar_memories(
    query: str,
    limit: int = 5,
    payload: Dict[str, Any] = Depends(verify_supabase_token)
):
    supabase_user_id = payload.get("sub")
    user = get_or_create_user(supabase_user_id, payload.get("email"))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT category, information, created_at
            FROM ai_memories
            WHERE user_id = %s AND information ILIKE %s
            ORDER BY created_at DESC
            LIMIT %s
            """,
            (user.id, f"%{query}%", limit)
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        return {
            "query": query,
            "similar_memories": [
                {
                    "emotion": row[0],
                    "message": row[1],
                    "similarity": 0.7
                }
                for row in rows
            ],
            "user_id": user.id
        }
        
    except Exception as e:
        logger.error(f"Similar memories error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve similar memories"
        )

# WebSocket endpoint for VR real-time communication
@app.websocket("/ws/vr/{user_id}")
async def vr_websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "emotional_state_update":
                emotion = message.get("emotion")
                intensity = message.get("intensity")
                
                ai_response = await ai_processor.process_message(
                    user_id=user_id,
                    message=f"User is feeling {emotion}",
                    emotion=emotion
                )
                
                await manager.send_personal_message(user_id, {
                    "type": "ai_response",
                    "response": ai_response.response,
                    "therapeutic_approach": ai_response.therapeutic_approach,
                    "suggestions": ai_response.suggestions
                })
                
            elif message.get("type") == "breathing_complete":
                logger.info(f"User {user_id} completed breathing exercise")
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, user_id)

# Weaviate integration placeholder
async def store_emotional_memory(user_id: str, emotion: str, message: str, intensity: float):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO ai_memories (user_id, category, information, importance, created_at)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                user_id,
                emotion,
                message[:500],
                "High" if intensity >= 0.8 else "Medium",
                datetime.now(),
            )
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to store emotional memory: {e}")
    finally:
        cursor.close()
        conn.close()

def get_weaviate_status() -> str:
    if not WEAVIATE_URL:
        return "not_configured"
    try:
        ready_url = WEAVIATE_URL.rstrip("/") + "/v1/.well-known/ready"
        with urllib_request.urlopen(ready_url, timeout=2) as response:
            if response.status == 200:
                return "healthy"
    except urllib_error.URLError:
        return "unavailable"
    except Exception:
        return "unavailable"
    return "unavailable"

@app.get("/health")
async def health_check():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "database": "healthy",
                "authentication": "healthy",
                "ai_processor": "mock" if ai_processor.mock_mode else ai_processor.provider,
                "websocket": "available",
                "weaviate": get_weaviate_status()
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# VR-compatible endpoint
@app.get("/vr/config")
async def get_vr_config():
    return {
        "webxr_support": True,
        "supported_devices": [
            "Meta Quest 2",
            "Meta Quest 3", 
            "HTC Vive",
            "Valve Index"
        ],
        "websocket_endpoint": "ws://localhost:8000/ws/vr/{user_id}",
        "authentication_required": True,
        "https_required": True
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
