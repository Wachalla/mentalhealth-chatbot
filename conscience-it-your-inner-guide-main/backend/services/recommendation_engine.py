# Recommendation Engine Service
# Maps emotional categories to appropriate activities and interventions

from typing import Dict, List, Optional, Tuple
from enum import Enum
import random
from datetime import datetime, timedelta
from dataclasses import dataclass

@dataclass
class ActivityHistory:
    """Activity history record for tracking effectiveness"""
    activity_id: str
    activity_type: str
    mood_before: float  # -1 to 1 valence before activity
    mood_after: float   # -1 to 1 valence after activity
    timestamp: datetime
    user_id: str
    improvement_score: float  # mood_after - mood_before

class EmotionalCategory(Enum):
    """Emotional categories for activity recommendations"""
    DISTRESSED = "distressed"
    ANXIOUS = "anxious"
    LOW = "low"
    CALM = "calm"
    ENERGIZED = "energized"
    NEUTRAL = "neutral"

class RecommendationEngine:
    """Maps emotional states to appropriate activities and interventions"""
    
    def __init__(self):
        # Activity mappings based on existing activity system IDs
        self.activity_mappings = self._get_activity_mappings()
        
        # VR mode suggestions for different emotional states
        self.vr_recommendations = self._get_vr_recommendations()
        
        # Intensity levels for activity selection
        self.intensity_levels = {
            'high': ['grounding-5-4-3-2-1', 'breathing-4-7-8'],  # Immediate interventions
            'medium': ['mindfulness-body-scan', 'journaling'],      # Reflective activities
            'low': ['reflection-prompts', 'gratitude-practice']     # Gentle activities
        }
        
        # Time-based recommendations
        self.time_based_mappings = self._get_time_based_mappings()
        
        # Activity history storage (in production, this would be in a database)
        self.activity_history: Dict[str, List[ActivityHistory]] = {}
        
        # History-based scoring weights
        self.history_weights = {
            'improvement_boost': 0.3,      # Boost for activities that improved mood
            'recent_activity_penalty': 0.1, # Penalty for activities done recently
            'history_decay_days': 30,      # History older than this gets less weight
            'min_history_samples': 3       # Minimum samples for reliable scoring
        }
    
    def get_recommendations(
        self, 
        emotional_category: str,
        valence: float = 0.0,
        arousal: float = 0.0,
        user_preferences: Optional[Dict] = None,
        recent_activities: Optional[List[str]] = None,
        time_of_day: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict:
        """
        Get activity recommendations based on emotional state
        
        Args:
            emotional_category: Current emotional category
            valence: Emotional valence (-1 to 1)
            arousal: Emotional arousal (-1 to 1)
            user_preferences: User's activity preferences
            recent_activities: Recently completed activities to avoid repetition
            time_of_day: Current time of day ('morning', 'afternoon', 'evening', 'night')
            user_id: User ID for history-based recommendations
            
        Returns:
            Dictionary with recommendations and metadata
        """
        
        # Get base recommendations for emotional category
        base_recommendations = self.activity_mappings.get(emotional_category, [])
        
        # Filter out recently completed activities
        if recent_activities:
            available_recommendations = [
                rec for rec in base_recommendations 
                if rec['activity_id'] not in recent_activities
            ]
        else:
            available_recommendations = base_recommendations
        
        # If no activities available after filtering, use all recommendations
        if not available_recommendations:
            available_recommendations = base_recommendations
        
        # Get user's activity history for personalized scoring
        user_history = self.get_user_activity_history(user_id) if user_id else []
        
        # Select primary recommendation with history-based scoring
        primary_recommendation = self._select_primary_recommendation(
            available_recommendations, 
            valence, 
            arousal,
            user_preferences,
            user_history
        )
        
        # Select secondary recommendations
        secondary_recommendations = self._select_secondary_recommendations(
            available_recommendations,
            primary_recommendation,
            valence,
            arousal,
            user_history
        )
        
        # Get VR mode suggestion
        vr_mode = self._get_vr_mode_suggestion(emotional_category, arousal)
        
        # Get time-based adjustments
        time_adjustments = self._get_time_adjustments(time_of_day)
        
        # Calculate confidence
        confidence = self._calculate_confidence(
            emotional_category, 
            valence, 
            arousal, 
            len(available_recommendations)
        )
        
        # Get history-based insights
        history_insights = self._get_history_insights(user_history, emotional_category)
        
        return {
            'primary_activity': primary_recommendation,
            'secondary_activities': secondary_recommendations,
            'vr_mode': vr_mode,
            'confidence': confidence,
            'emotional_context': {
                'category': emotional_category,
                'valence': valence,
                'arousal': arousal
            },
            'time_adjustments': time_adjustments,
            'recommendation_rationale': self._get_recommendation_rationale(
                emotional_category, 
                primary_recommendation
            ),
            'history_insights': history_insights,
            'personalization_score': self._calculate_personalization_score(
                primary_recommendation, user_history
            )
        }
    
    def _select_primary_recommendation(
        self, 
        recommendations: List[Dict], 
        valence: float, 
        arousal: float,
        user_preferences: Optional[Dict] = None,
        user_history: Optional[List[ActivityHistory]] = None
    ) -> Dict:
        """Select the best primary recommendation based on emotional state and history"""
        
        if not recommendations:
            # Fallback recommendation
            return {
                'activity_id': 'breathing-4-7-8',
                'activity_name': '4-7-8 Breathing Exercise',
                'description': 'Simple breathing technique for immediate relief',
                'priority': 'high',
                'estimated_duration': 5,
                'difficulty': 'beginner'
            }
        
        # Score recommendations based on emotional fit and history
        scored_recommendations = []
        
        for rec in recommendations:
            score = 0.0
            
            # Base score from priority
            priority_scores = {'high': 3, 'medium': 2, 'low': 1}
            score += priority_scores.get(rec.get('priority', 'medium'), 2)
            
            # Adjust score based on emotional intensity
            if abs(arousal) > 0.7:  # High arousal
                if rec.get('calming_effect', False):
                    score += 2
                if rec.get('grounding_technique', False):
                    score += 1
            
            if valence < -0.5:  # Negative valence
                if rec.get('uplifting', False):
                    score += 1
                if rec.get('grounding_technique', False):
                    score += 2
            
            # User preference adjustments
            if user_preferences:
                preferred_types = user_preferences.get('preferred_types', [])
                if rec.get('activity_type') in preferred_types:
                    score += 1
                
                preferred_difficulty = user_preferences.get('preferred_difficulty', 'beginner')
                if rec.get('difficulty') == preferred_difficulty:
                    score += 1
            
            # History-based scoring
            if user_history:
                history_score = self._calculate_history_score(rec, user_history)
                score += history_score
            
            scored_recommendations.append((score, rec))
        
        # Sort by score and select top recommendation
        scored_recommendations.sort(key=lambda x: x[0], reverse=True)
        
        # Add some randomness to top 3 recommendations for variety
        top_three = scored_recommendations[:3]
        if top_three:
            selected = random.choice(top_three)[1]
        else:
            selected = scored_recommendations[0][1] if scored_recommendations else recommendations[0]
        
        return selected
    
    def _select_secondary_recommendations(
        self, 
        all_recommendations: List[Dict],
        primary: Dict,
        valence: float,
        arousal: float,
        user_history: Optional[List[ActivityHistory]] = None
    ) -> List[Dict]:
        """Select secondary recommendations as alternatives with history consideration"""
        
        # Filter out primary recommendation
        secondary = [rec for rec in all_recommendations if rec['activity_id'] != primary['activity_id']]
        
        # Score secondary recommendations with history
        if user_history:
            scored_secondary = []
            for rec in secondary:
                history_score = self._calculate_history_score(rec, user_history)
                scored_secondary.append((history_score, rec))
            
            # Sort by history score (highest first)
            scored_secondary.sort(key=lambda x: x[0], reverse=True)
            secondary = [rec for _, rec in scored_secondary]
        
        # Limit to 2-3 secondary recommendations
        secondary = secondary[:3]
        
        return secondary
    
    def _get_vr_mode_suggestion(self, emotional_category: str, arousal: float) -> Optional[str]:
        """Get VR mode suggestion based on emotional state"""
        
        # High arousal states may benefit from immersive VR
        if abs(arousal) > 0.6:
            return self.vr_recommendations.get(emotional_category, {}).get('high_arousal')
        
        # Moderate arousal states
        elif abs(arousal) > 0.3:
            return self.vr_recommendations.get(emotional_category, {}).get('medium_arousal')
        
        # Low arousal states
        else:
            return self.vr_recommendations.get(emotional_category, {}).get('low_arousal')
    
    def _get_time_adjustments(self, time_of_day: Optional[str]) -> Dict:
        """Get time-based adjustments for recommendations"""
        
        if not time_of_day:
            return {}
        
        return self.time_based_mappings.get(time_of_day, {})
    
    def _calculate_confidence(
        self, 
        emotional_category: str, 
        valence: float, 
        arousal: float, 
        available_count: int
    ) -> float:
        """Calculate confidence in recommendations"""
        
        base_confidence = 0.7  # Base confidence
        
        # Adjust based on available recommendations
        if available_count >= 3:
            base_confidence += 0.2
        elif available_count >= 2:
            base_confidence += 0.1
        elif available_count == 1:
            base_confidence -= 0.1
        
        # Adjust based on emotional clarity
        emotional_intensity = max(abs(valence), abs(arousal))
        if emotional_intensity > 0.7:
            base_confidence += 0.1  # Clear emotional state
        elif emotional_intensity < 0.3:
            base_confidence -= 0.1  # Unclear emotional state
        
        return min(max(base_confidence, 0.0), 1.0)
    
    def _get_recommendation_rationale(self, emotional_category: str, recommendation: Dict) -> str:
        """Get rationale for why this activity was recommended"""
        
        rationales = {
            'distressed': "This grounding exercise can help you feel more present and stable when you're feeling overwhelmed.",
            'anxious': "This breathing technique can help calm your nervous system and reduce anxiety symptoms.",
            'low': "This gentle activity can provide comfort and support when you're feeling low energy.",
            'calm': "This reflective activity can help you build on your current sense of peace.",
            'energized': "This focused activity can help channel your energy productively.",
            'neutral': "This activity can help you explore your current feelings and gain clarity."
        }
        
        base_rationale = rationales.get(emotional_category, "This activity may help with your current emotional state.")
        
        # Add activity-specific rationale
        activity_specific = recommendation.get('rationale', '')
        
        if activity_specific:
            return f"{base_rationale} {activity_specific}"
        
        return base_rationale
    
    def _get_activity_mappings(self) -> Dict[str, List[Dict]]:
        """Get activity mappings for each emotional category"""
        
        return {
            'distressed': [
                {
                    'activity_id': 'grounding-5-4-3-2-1',
                    'activity_name': '5-4-3-2-1 Grounding',
                    'description': 'Sensory grounding technique to return to present moment',
                    'priority': 'high',
                    'estimated_duration': 10,
                    'difficulty': 'beginner',
                    'calming_effect': True,
                    'grounding_technique': True,
                    'activity_type': 'grounding'
                },
                {
                    'activity_id': 'breathing-4-7-8',
                    'activity_name': '4-7-8 Breathing',
                    'description': 'Breathing exercise to regulate nervous system',
                    'priority': 'high',
                    'estimated_duration': 5,
                    'difficulty': 'beginner',
                    'calming_effect': True,
                    'activity_type': 'breathing'
                },
                {
                    'activity_id': 'mindfulness-body-scan',
                    'activity_name': 'Body Scan Meditation',
                    'description': 'Progressive relaxation to reconnect with body',
                    'priority': 'medium',
                    'estimated_duration': 15,
                    'difficulty': 'intermediate',
                    'calming_effect': True,
                    'grounding_technique': True,
                    'activity_type': 'meditation'
                }
            ],
            'anxious': [
                {
                    'activity_id': 'breathing-4-7-8',
                    'activity_name': '4-7-8 Breathing',
                    'description': 'Calming breathing pattern for anxiety relief',
                    'priority': 'high',
                    'estimated_duration': 5,
                    'difficulty': 'beginner',
                    'calming_effect': True,
                    'activity_type': 'breathing'
                },
                {
                    'activity_id': 'grounding-5-4-3-2-1',
                    'activity_name': '5-4-3-2-1 Grounding',
                    'description': 'Grounding technique for anxious thoughts',
                    'priority': 'high',
                    'estimated_duration': 10,
                    'difficulty': 'beginner',
                    'calming_effect': True,
                    'grounding_technique': True,
                    'activity_type': 'grounding'
                },
                {
                    'activity_id': 'mindfulness-body-scan',
                    'activity_name': 'Body Scan Meditation',
                    'description': 'Body awareness to reduce anxiety',
                    'priority': 'medium',
                    'estimated_duration': 15,
                    'difficulty': 'intermediate',
                    'calming_effect': True,
                    'activity_type': 'meditation'
                }
            ],
            'low': [
                {
                    'activity_id': 'mindfulness-body-scan',
                    'activity_name': 'Body Scan Meditation',
                    'description': 'Gentle body awareness for low energy states',
                    'priority': 'high',
                    'estimated_duration': 15,
                    'difficulty': 'beginner',
                    'uplifting': True,
                    'activity_type': 'meditation'
                },
                {
                    'activity_id': 'gratitude-practice',
                    'activity_name': 'Gratitude Practice',
                    'description': 'Reflection exercise to lift mood',
                    'priority': 'medium',
                    'estimated_duration': 10,
                    'difficulty': 'beginner',
                    'uplifting': True,
                    'activity_type': 'reflection'
                },
                {
                    'activity_id': 'journaling',
                    'activity_name': 'Guided Journaling',
                    'description': 'Expressive writing for emotional processing',
                    'priority': 'medium',
                    'estimated_duration': 15,
                    'difficulty': 'beginner',
                    'uplifting': True,
                    'activity_type': 'writing'
                }
            ],
            'calm': [
                {
                    'activity_id': 'reflection-prompts',
                    'activity_name': 'Reflection Prompts',
                    'description': 'Guided self-reflection to build on calm state',
                    'priority': 'high',
                    'estimated_duration': 10,
                    'difficulty': 'beginner',
                    'activity_type': 'reflection'
                },
                {
                    'activity_id': 'gratitude-practice',
                    'activity_name': 'Gratitude Practice',
                    'description': 'Cultivate appreciation in calm state',
                    'priority': 'medium',
                    'estimated_duration': 10,
                    'difficulty': 'beginner',
                    'activity_type': 'reflection'
                },
                {
                    'activity_id': 'mindfulness-body-scan',
                    'activity_name': 'Body Scan Meditation',
                    'description': 'Deepen awareness in calm state',
                    'priority': 'medium',
                    'estimated_duration': 15,
                    'difficulty': 'intermediate',
                    'activity_type': 'meditation'
                }
            ],
            'energized': [
                {
                    'activity_id': 'focus-activities',
                    'activity_name': 'Focus Activities',
                    'description': 'Channel energy into productive focus',
                    'priority': 'high',
                    'estimated_duration': 10,
                    'difficulty': 'intermediate',
                    'activity_type': 'cognitive'
                },
                {
                    'activity_id': 'reflection-prompts',
                    'activity_name': 'Reflection Prompts',
                    'description': 'Direct energy toward self-discovery',
                    'priority': 'medium',
                    'estimated_duration': 10,
                    'difficulty': 'beginner',
                    'activity_type': 'reflection'
                },
                {
                    'activity_id': 'goal-setting',
                    'activity_name': 'Goal Setting',
                    'description': 'Use energy to plan positive actions',
                    'priority': 'medium',
                    'estimated_duration': 15,
                    'difficulty': 'intermediate',
                    'activity_type': 'planning'
                }
            ],
            'neutral': [
                {
                    'activity_id': 'reflection-prompts',
                    'activity_name': 'Reflection Prompts',
                    'description': 'Explore current emotional state',
                    'priority': 'high',
                    'estimated_duration': 10,
                    'difficulty': 'beginner',
                    'activity_type': 'reflection'
                },
                {
                    'activity_id': 'breathing-4-7-8',
                    'activity_name': '4-7-8 Breathing',
                    'description': 'Check in with breath and body',
                    'priority': 'medium',
                    'estimated_duration': 5,
                    'difficulty': 'beginner',
                    'activity_type': 'breathing'
                },
                {
                    'activity_id': 'mindfulness-body-scan',
                    'activity_name': 'Body Scan Meditation',
                    'description': 'Connect with current physical state',
                    'priority': 'medium',
                    'estimated_duration': 15,
                    'difficulty': 'beginner',
                    'activity_type': 'meditation'
                }
            ]
        }
    
    def _get_vr_recommendations(self) -> Dict[str, Dict[str, Optional[str]]]:
        """Get VR mode recommendations for different emotional states"""
        
        return {
            'distressed': {
                'high_arousal': None,  # Not recommended for high distress
                'medium_arousal': None,  # Not recommended for distress
                'low_arousal': None      # Not recommended for distress
            },
            'anxious': {
                'high_arousal': 'calm',     # VR calm room for anxiety
                'medium_arousal': 'calm',   # VR calm room for moderate anxiety
                'low_arousal': None         # Standard mode preferred
            },
            'low': {
                'high_arousal': None,        # Not recommended
                'medium_arousal': None,      # Not recommended
                'low_arousal': None          # Not recommended
            },
            'calm': {
                'high_arousal': 'mindful',   # VR for deepening calm
                'medium_arousal': None,      # Standard mode preferred
                'low_arousal': None          # Standard mode preferred
            },
            'energized': {
                'high_arousal': None,        # Not recommended
                'medium_arousal': None,      # Not recommended
                'low_arousal': None          # Not recommended
            },
            'neutral': {
                'high_arousal': None,        # Standard mode preferred
                'medium_arousal': None,      # Standard mode preferred
                'low_arousal': None          # Standard mode preferred
            }
        }
    
    def _get_time_based_mappings(self) -> Dict[str, Dict]:
        """Get time-based adjustments for recommendations"""
        
        return {
            'morning': {
                'preferred_intensity': 'medium',
                'avoid_activities': ['intense-meditation'],
                'note': 'Morning is good for gentle, centering activities'
            },
            'afternoon': {
                'preferred_intensity': 'medium',
                'avoid_activities': [],
                'note': 'Afternoon supports most activity types'
            },
            'evening': {
                'preferred_intensity': 'low',
                'avoid_activities': ['high-energy-focus'],
                'note': 'Evening calls for calming, reflective activities'
            },
            'night': {
                'preferred_intensity': 'low',
                'avoid_activities': ['energizing-activities'],
                'note': 'Night should focus on relaxation and sleep preparation'
            }
        }
    
    def get_activity_by_id(self, activity_id: str) -> Optional[Dict]:
        """Get activity details by ID"""
        
        for category_activities in self.activity_mappings.values():
            for activity in category_activities:
                if activity['activity_id'] == activity_id:
                    return activity
        
        return None
    
    def get_all_activities(self) -> List[Dict]:
        """Get all available activities"""
        
        all_activities = []
        for category_activities in self.activity_mappings.values():
            all_activities.extend(category_activities)
        
        return all_activities
    
    def update_user_preferences(self, user_id: str, preferences: Dict) -> bool:
        """Update user preferences for recommendations (placeholder for future implementation)"""
        
        # This would typically involve database storage
        # For now, return True to indicate success
        return True
    
    def get_user_preferences(self, user_id: str) -> Dict:
        """Get user preferences for recommendations (placeholder for future implementation)"""
        
        # This would typically involve database retrieval
        # For now, return default preferences
        return {
            'preferred_types': ['breathing', 'grounding'],
            'preferred_difficulty': 'beginner',
            'preferred_duration': 'short',
            'vr_preference': 'standard'
        }

# Singleton instance for easy import
recommendation_engine = RecommendationEngine()
