# Emotional State Engine
# Implements Russell's Circumplex emotional model for tracking user emotional states

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import json

class EmotionalCategory(Enum):
    """Emotional categories based on Russell's Circumplex model"""
    DISTRESSED = "distressed"
    ANXIOUS = "anxious"
    LOW = "low"
    CALM = "calm"
    ENERGIZED = "energized"
    NEUTRAL = "neutral"

class EmotionalState:
    """Represents a user's emotional state at a point in time"""
    
    def __init__(
        self,
        valence: float,
        arousal: float,
        category: EmotionalCategory,
        confidence: float,
        timestamp: datetime,
        source: str = "unknown",
        user_id: str = None
    ):
        self.valence = valence  # -1 (negative) to 1 (positive)
        self.arousal = arousal  # -1 (calm) to 1 (excited)
        self.category = category
        self.confidence = confidence  # 0 to 1
        self.timestamp = timestamp
        self.source = source  # "chat", "checkin", "activity"
        self.user_id = user_id
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage"""
        return {
            'valence': self.valence,
            'arousal': self.arousal,
            'category': self.category.value,
            'confidence': self.confidence,
            'timestamp': self.timestamp.isoformat(),
            'source': self.source,
            'user_id': self.user_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'EmotionalState':
        """Create from dictionary"""
        return cls(
            valence=data['valence'],
            arousal=data['arousal'],
            category=EmotionalCategory(data['category']),
            confidence=data['confidence'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            source=data.get('source', 'unknown'),
            user_id=data.get('user_id')
        )

class EmotionalStateEngine:
    """Engine for tracking and analyzing user emotional states"""
    
    def __init__(self):
        # In-memory cache for recent states (user_id -> list of states)
        self.state_cache = {}
        self.cache_ttl = 300  # 5 minutes cache TTL
        
        # Sentiment analysis weights
        self.positive_keywords = [
            'happy', 'good', 'great', 'excellent', 'wonderful', 'amazing',
            'fantastic', 'love', 'joy', 'excited', 'pleased', 'satisfied',
            'grateful', 'thankful', 'relieved', 'calm', 'peaceful',
            'content', 'proud', 'confident', 'optimistic', 'hopeful'
        ]
        
        self.negative_keywords = [
            'sad', 'bad', 'terrible', 'awful', 'horrible', 'hate',
            'angry', 'frustrated', 'annoyed', 'upset', 'disappointed',
            'worried', 'anxious', 'scared', 'afraid', 'fear', 'panic',
            'depressed', 'hopeless', 'helpless', 'worthless', 'ashamed',
            'guilty', 'embarrassed', 'lonely', 'isolated', 'empty'
        ]
        
        self.high_arousal_keywords = [
            'excited', 'energetic', 'enthusiastic', 'passionate', 'intense',
            'urgent', 'desperate', 'panicked', 'terrified', 'furious',
            'overwhelmed', 'agitated', 'restless', 'hyper', 'racing'
        ]
        
        self.low_arousal_keywords = [
            'calm', 'relaxed', 'peaceful', 'serene', 'tranquil',
            'tired', 'exhausted', 'fatigued', 'drained', 'lethargic',
            'numb', 'apathetic', 'bored', 'uninterested', 'flat'
        ]
    
    def categorize_state(self, valence: float, arousal: float) -> EmotionalCategory:
        """
        Categorize emotional state based on valence and arousal
        Using Russell's Circumplex model
        """
        if valence < -0.5 and arousal > 0.5:
            return EmotionalCategory.DISTRESSED
        elif valence < 0.3 and arousal > 0.5:
            return EmotionalCategory.ANXIOUS
        elif valence < -0.5 and arousal <= 0.5:
            return EmotionalCategory.LOW
        elif valence > 0.3 and arousal < -0.3:
            return EmotionalCategory.CALM
        elif valence > 0.5 and arousal > 0.3:
            return EmotionalCategory.ENERGIZED
        else:
            return EmotionalCategory.NEUTRAL
    
    def analyze_sentiment(self, message: str) -> Tuple[float, float]:
        """
        Analyze sentiment from text message
        Returns (valence, arousal) scores
        """
        lower_message = message.lower()
        
        # Initialize scores
        valence = 0.0
        arousal = 0.0
        
        # Count keyword occurrences
        positive_count = sum(1 for word in self.positive_keywords if word in lower_message)
        negative_count = sum(1 for word in self.negative_keywords if word in lower_message)
        high_arousal_count = sum(1 for word in self.high_arousal_keywords if word in lower_message)
        low_arousal_count = sum(1 for word in self.low_arousal_keywords if word in lower_message)
        
        # Calculate valence (-1 to 1) with normalization
        if positive_count > 0 or negative_count > 0:
            total_sentiment = positive_count + negative_count
            valence = (positive_count - negative_count) / total_sentiment
            valence = max(-1.0, min(1.0, valence))
        
        # Calculate arousal (-1 to 1) with normalization
        if high_arousal_count > 0 or low_arousal_count > 0:
            total_arousal = high_arousal_count + low_arousal_count
            arousal = (high_arousal_count - low_arousal_count) / total_arousal
            arousal = max(-1.0, min(1.0, arousal))
        
        return valence, arousal
    
    def get_current_state(self, user_id: str) -> Optional[EmotionalState]:
        """
        Get the current emotional state for a user
        Checks cache first, then database
        """
        # Check cache first
        if user_id in self.state_cache:
            cached_states = self.state_cache[user_id]
            if cached_states:
                latest_state = cached_states[-1]
                # Check if cache is still valid
                if (datetime.now() - latest_state.timestamp).seconds < self.cache_ttl:
                    return latest_state
        
        # Load from database
        try:
            from main import get_db_connection
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                SELECT valence, arousal, category, confidence, updated_at, source
                FROM emotional_states
                WHERE user_id = %s
                ORDER BY updated_at DESC
                LIMIT 1
                """,
                (user_id,)
            )
            
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if row:
                state = EmotionalState(
                    valence=float(row[0]),
                    arousal=float(row[1]),
                    category=EmotionalCategory(row[2]),
                    confidence=float(row[3]),
                    timestamp=row[4],
                    source=row[5] or "unknown",
                    user_id=user_id
                )
                
                # Update cache
                self._update_cache(user_id, state)
                return state
            
        except Exception as e:
            print(f"Error loading emotional state: {e}")
        
        # No state found, return neutral baseline
        baseline_state = EmotionalState(
            valence=0.0,
            arousal=0.0,
            category=EmotionalCategory.NEUTRAL,
            confidence=0.5,
            timestamp=datetime.now(),
            source="baseline",
            user_id=user_id
        )
        
        return baseline_state
    
    def update_from_chat(self, user_id: str, message: str) -> EmotionalState:
        """
        Update emotional state based on chat message sentiment
        """
        # Get current state
        current_state = self.get_current_state(user_id)
        
        # Analyze message sentiment
        message_valence, message_arousal = self.analyze_sentiment(message)
        
        # Blend with existing state (40% new, 60% existing)
        new_valence = (message_valence * 0.4) + (current_state.valence * 0.6)
        new_arousal = (message_arousal * 0.4) + (current_state.arousal * 0.6)
        
        # Determine category
        new_category = self.categorize_state(new_valence, new_arousal)
        
        # Calculate confidence (chat-based has moderate confidence)
        confidence = 0.7
        
        # Create new state
        new_state = EmotionalState(
            valence=new_valence,
            arousal=new_arousal,
            category=new_category,
            confidence=confidence,
            timestamp=datetime.now(),
            source="chat",
            user_id=user_id
        )
        
        # Persist to database
        self._persist_state(new_state)
        
        # Update cache
        self._update_cache(user_id, new_state)
        
        return new_state
    
    def update_from_checkin(self, user_id: str, mood_score: int, notes: str = None) -> EmotionalState:
        """
        Update emotional state from mood check-in (1-5 scale)
        """
        # Convert mood score to valence (-1 to 1)
        valence = self._mood_score_to_valence(mood_score)
        
        # Infer arousal from notes if provided
        arousal = 0.0
        if notes:
            _, arousal = self.analyze_sentiment(notes)
        
        # Get current state for blending
        current_state = self.get_current_state(user_id)
        
        # Blend with existing state (50% check-in, 50% existing)
        new_valence = (valence * 0.5) + (current_state.valence * 0.5)
        new_arousal = (arousal * 0.5) + (current_state.arousal * 0.5)
        
        # Determine category
        new_category = self.categorize_state(new_valence, new_arousal)
        
        # High confidence for check-ins
        confidence = 0.9
        
        # Create new state
        new_state = EmotionalState(
            valence=new_valence,
            arousal=new_arousal,
            category=new_category,
            confidence=confidence,
            timestamp=datetime.now(),
            source="checkin",
            user_id=user_id
        )
        
        # Persist to database
        self._persist_state(new_state)
        
        # Update cache
        self._update_cache(user_id, new_state)
        
        return new_state
    
    def update_from_activity(self, user_id: str, activity_id: str, completed: bool, 
                           pre_mood: Optional[int] = None, post_mood: Optional[int] = None) -> EmotionalState:
        """
        Update emotional state based on activity completion
        """
        current_state = self.get_current_state(user_id)
        
        if completed and pre_mood is not None and post_mood is not None:
            # Calculate mood improvement
            mood_change = post_mood - pre_mood
            
            # Convert to valence change
            valence_change = mood_change / 2.0  # Scale -1 to 1 range
            
            # Apply mood improvement with diminishing returns
            if valence_change > 0:
                valence_change = min(valence_change * 0.3, 0.2)  # Max +0.2 improvement
            else:
                valence_change = max(valence_change * 0.3, -0.1)  # Max -0.1 decline
            
            # Successful activity often reduces arousal (calming effect)
            arousal_change = -0.1 if valence_change > 0 else 0.0
            
            # Update state
            new_valence = max(-1.0, min(1.0, current_state.valence + valence_change))
            new_arousal = max(-1.0, min(1.0, current_state.arousal + arousal_change))
            
        else:
            # Activity not completed or no mood data - minimal change
            new_valence = current_state.valence
            new_arousal = current_state.arousal
        
        # Determine category
        new_category = self.categorize_state(new_valence, new_arousal)
        
        # Activity-based updates have moderate confidence
        confidence = 0.6
        
        # Create new state
        new_state = EmotionalState(
            valence=new_valence,
            arousal=new_arousal,
            category=new_category,
            confidence=confidence,
            timestamp=datetime.now(),
            source="activity",
            user_id=user_id
        )
        
        # Persist to database
        self._persist_state(new_state)
        
        # Update cache
        self._update_cache(user_id, new_state)
        
        return new_state
    
    def get_state_history(self, user_id: str, days: int = 7) -> List[EmotionalState]:
        """
        Get emotional state history for a user over specified days
        """
        try:
            from main import get_db_connection
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                SELECT valence, arousal, category, confidence, updated_at, source
                FROM emotional_states
                WHERE user_id = %s 
                  AND updated_at >= %s
                ORDER BY updated_at ASC
                """,
                (user_id, datetime.now() - timedelta(days=days))
            )
            
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            
            states = []
            for row in rows:
                state = EmotionalState(
                    valence=float(row[0]),
                    arousal=float(row[1]),
                    category=EmotionalCategory(row[2]),
                    confidence=float(row[3]),
                    timestamp=row[4],
                    source=row[5] or "unknown",
                    user_id=user_id
                )
                states.append(state)
            
            return states
            
        except Exception as e:
            print(f"Error loading state history: {e}")
            return []
    
    def get_state_trends(self, user_id: str, days: int = 7) -> Dict:
        """
        Analyze emotional state trends over time
        """
        states = self.get_state_history(user_id, days)
        
        if not states:
            return {
                'trend': 'insufficient_data',
                'avg_valence': 0.0,
                'avg_arousal': 0.0,
                'most_common_category': 'neutral',
                'stability': 0.0
            }
        
        # Calculate averages
        avg_valence = sum(s.valence for s in states) / len(states)
        avg_arousal = sum(s.arousal for s in states) / len(states)
        
        # Most common category
        category_counts = {}
        for state in states:
            category = state.category.value
            category_counts[category] = category_counts.get(category, 0) + 1
        
        most_common_category = max(category_counts, key=category_counts.get)
        
        # Calculate stability (lower = more stable)
        if len(states) > 1:
            valence_variance = sum((s.valence - avg_valence) ** 2 for s in states) / len(states)
            arousal_variance = sum((s.arousal - avg_arousal) ** 2 for s in states) / len(states)
            stability = (valence_variance + arousal_variance) / 2
        else:
            stability = 0.0
        
        # Determine trend direction
        if len(states) >= 3:
            recent_avg_valence = sum(s.valence for s in states[-3:]) / 3
            early_avg_valence = sum(s.valence for s in states[:3]) / 3
            
            if recent_avg_valence > early_avg_valence + 0.1:
                trend = 'improving'
            elif recent_avg_valence < early_avg_valence - 0.1:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'insufficient_data'
        
        return {
            'trend': trend,
            'avg_valence': avg_valence,
            'avg_arousal': avg_arousal,
            'most_common_category': most_common_category,
            'stability': stability,
            'state_count': len(states)
        }
    
    def _mood_score_to_valence(self, score: int) -> float:
        """Convert 1-5 mood score to -1 to 1 valence"""
        # 1 → -1, 2 → -0.5, 3 → 0, 4 → 0.5, 5 → 1
        return (score - 3) / 2.0
    
    def _update_cache(self, user_id: str, state: EmotionalState):
        """Update in-memory cache with new state"""
        if user_id not in self.state_cache:
            self.state_cache[user_id] = []
        
        # Add new state and keep only recent ones
        self.state_cache[user_id].append(state)
        
        # Keep only last 10 states per user
        if len(self.state_cache[user_id]) > 10:
            self.state_cache[user_id] = self.state_cache[user_id][-10:]
    
    def _persist_state(self, state: EmotionalState):
        """Save emotional state to database"""
        try:
            from main import get_db_connection
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                INSERT INTO emotional_states 
                (user_id, valence, arousal, category, confidence, updated_at, source)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    state.user_id,
                    state.valence,
                    state.arousal,
                    state.category.value,
                    state.confidence,
                    state.timestamp,
                    state.source
                )
            )
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"Error persisting emotional state: {e}")

# Singleton instance for easy import
emotional_state_engine = EmotionalStateEngine()
