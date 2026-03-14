# Extended Recommendation Engine with Activity History
# This file contains the additional methods for activity history tracking

from typing import Dict, List, Optional
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

class RecommendationEngineExtended:
    """Extended recommendation engine with activity history tracking"""
    
    def __init__(self):
        # Activity history storage (in production, this would be in a database)
        self.activity_history: Dict[str, List[ActivityHistory]] = {}
        
        # History-based scoring weights
        self.history_weights = {
            'improvement_boost': 0.3,      # Boost for activities that improved mood
            'recent_activity_penalty': 0.1, # Penalty for activities done recently
            'history_decay_days': 30,      # History older than this gets less weight
            'min_history_samples': 3       # Minimum samples for reliable scoring
        }
    
    def record_activity_completion(
        self, 
        user_id: str, 
        activity_id: str, 
        activity_type: str,
        mood_before: float, 
        mood_after: float,
        timestamp: Optional[datetime] = None
    ) -> bool:
        """
        Record activity completion with mood tracking
        
        Args:
            user_id: User identifier
            activity_id: Activity identifier
            activity_type: Type of activity (breathing, meditation, etc.)
            mood_before: Mood valence before activity (-1 to 1)
            mood_after: Mood valence after activity (-1 to 1)
            timestamp: When the activity was completed (defaults to now)
            
        Returns:
            True if recorded successfully
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        improvement_score = mood_after - mood_before
        
        history_record = ActivityHistory(
            activity_id=activity_id,
            activity_type=activity_type,
            mood_before=mood_before,
            mood_after=mood_after,
            timestamp=timestamp,
            user_id=user_id,
            improvement_score=improvement_score
        )
        
        if user_id not in self.activity_history:
            self.activity_history[user_id] = []
        
        self.activity_history[user_id].append(history_record)
        
        # Keep only recent history (last 100 records per user)
        if len(self.activity_history[user_id]) > 100:
            self.activity_history[user_id] = self.activity_history[user_id][-100:]
        
        return True
    
    def get_user_activity_history(self, user_id: str) -> List[ActivityHistory]:
        """
        Get activity history for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            List of activity history records
        """
        return self.activity_history.get(user_id, [])
    
    def get_activity_effectiveness(self, user_id: str, activity_id: str) -> Dict:
        """
        Calculate effectiveness metrics for a specific activity
        
        Args:
            user_id: User identifier
            activity_id: Activity identifier
            
        Returns:
            Dictionary with effectiveness metrics
        """
        user_history = self.get_user_activity_history(user_id)
        activity_records = [record for record in user_history if record.activity_id == activity_id]
        
        if not activity_records:
            return {
                'sample_size': 0,
                'average_improvement': 0.0,
                'success_rate': 0.0,
                'confidence': 0.0
            }
        
        improvements = [record.improvement_score for record in activity_records]
        successful_activities = [imp for imp in improvements if imp > 0]
        
        average_improvement = sum(improvements) / len(improvements)
        success_rate = len(successful_activities) / len(activity_records)
        
        # Confidence based on sample size
        sample_size = len(activity_records)
        confidence = min(sample_size / self.history_weights['min_history_samples'], 1.0)
        
        return {
            'sample_size': sample_size,
            'average_improvement': average_improvement,
            'success_rate': success_rate,
            'confidence': confidence,
            'recent_performance': self._get_recent_performance(activity_records)
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
        Get activity recommendations based on emotional state and history
        
        Args:
            emotional_category: Current emotional category
            valence: Emotional valence (-1 to 1)
            arousal: Emotional arousal (-1 to 1)
            user_preferences: User's activity preferences
            recent_activities: Recently completed activities to avoid repetition
            time_of_day: Current time of day ('morning', 'afternoon', 'evening', 'night')
            user_id: User ID for history-based recommendations
            
        Returns:
            Dictionary with personalized recommendations
        """
        
        # Import base recommendation engine for activity mappings
        from services.recommendation_engine import RecommendationEngine
        base_engine = RecommendationEngine()
        
        # Get base recommendations for emotional category
        base_recommendations = base_engine.activity_mappings.get(emotional_category, [])
        
        # Get user's activity history for personalized scoring
        user_history = self.get_user_activity_history(user_id) if user_id else []
        
        # Score recommendations based on history
        scored_recommendations = []
        for rec in base_recommendations:
            history_score = self._calculate_history_score(rec, user_history)
            rec_with_score = rec.copy()
            rec_with_score['history_score'] = history_score
            scored_recommendations.append((history_score, rec_with_score))
        
        # Sort by history score (highest first)
        scored_recommendations.sort(key=lambda x: x[0], reverse=True)
        
        # Select primary recommendation
        primary_recommendation = scored_recommendations[0][1] if scored_recommendations else None
        
        # Select secondary recommendations (top 3 excluding primary)
        secondary_recommendations = [rec for _, rec in scored_recommendations[1:4]]
        
        # Calculate confidence based on history
        if user_history and primary_recommendation:
            effectiveness = self.get_activity_effectiveness(user_id, primary_recommendation['activity_id'])
            confidence = effectiveness['confidence']
        else:
            confidence = 0.5  # Default confidence without history
        
        # Get VR mode suggestion (simplified)
        vr_mode = None
        if emotional_category == 'anxious' and arousal > 0.5:
            vr_mode = 'calm'
        elif emotional_category == 'calm' and arousal > 0.5:
            vr_mode = 'mindful'
        
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
            'history_insights': self._get_history_insights(user_history, emotional_category),
            'personalization_score': self._calculate_personalization_score(
                primary_recommendation, user_history
            ) if primary_recommendation else 0.0
        }
    
    def _calculate_history_score(self, activity: Dict, user_history: List[ActivityHistory]) -> float:
        if not user_history:
            return 0.0
        
        activity_id = activity['activity_id']
        activity_type = activity.get('activity_type', '')
        
        # Get records for this specific activity and activity type
        specific_records = [record for record in user_history if record.activity_id == activity_id]
        type_records = [record for record in user_history if record.activity_type == activity_type]
        
        score = 0.0
        
        # Score based on specific activity performance
        if specific_records:
            recent_specific = self._get_recent_records(specific_records)
            if len(recent_specific) >= self.history_weights['min_history_samples']:
                avg_improvement = sum(record.improvement_score for record in recent_specific) / len(recent_specific)
                score += avg_improvement * self.history_weights['improvement_boost']
        
        # Score based on activity type performance (fallback)
        elif type_records:
            recent_type = self._get_recent_records(type_records)
            if len(recent_type) >= self.history_weights['min_history_samples']:
                avg_improvement = sum(record.improvement_score for record in recent_type) / len(recent_type)
                score += avg_improvement * self.history_weights['improvement_boost'] * 0.5  # Lower weight for type-level
        
        # Penalty for very recent activity (avoid repetition)
        if specific_records:
            most_recent = max(specific_records, key=lambda r: r.timestamp)
            days_since = (datetime.now() - most_recent.timestamp).days
            if days_since < 1:  # Completed today
                score -= self.history_weights['recent_activity_penalty']
            elif days_since < 7:  # Completed this week
                score -= self.history_weights['recent_activity_penalty'] * 0.5
        
        return score
    
    def _get_recent_records(self, records: List[ActivityHistory], days: int = 30) -> List[ActivityHistory]:
        """Get records from the last N days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        return [record for record in records if record.timestamp >= cutoff_date]
    
    def _get_recent_performance(self, records: List[ActivityHistory]) -> Dict:
        """Get recent performance metrics"""
        recent_records = self._get_recent_records(records, days=7)  # Last week
        
        if not recent_records:
            return {'trend': 'insufficient_data', 'last_improvement': 0.0}
        
        # Calculate trend
        improvements = [record.improvement_score for record in recent_records]
        last_improvement = improvements[-1] if improvements else 0.0
        
        if len(improvements) >= 3:
            recent_avg = sum(improvements[-3:]) / 3
            older_avg = sum(improvements[:-3]) / len(improvements[:-3]) if len(improvements) > 3 else recent_avg
            
            if recent_avg > older_avg + 0.1:
                trend = 'improving'
            elif recent_avg < older_avg - 0.1:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'insufficient_data'
        
        return {
            'trend': trend,
            'last_improvement': last_improvement,
            'recent_average': sum(improvements) / len(improvements)
        }
    
    def _get_history_insights(self, user_history: List[ActivityHistory], emotional_category: str) -> Dict:
        """Generate insights from user's activity history"""
        if not user_history:
            return {
                'total_activities': 0,
                'favorite_types': [],
                'most_effective': [],
                'recommendation_confidence': 'low'
            }
        
        # Analyze activity types
        type_counts = {}
        type_improvements = {}
        
        for record in user_history:
            activity_type = record.activity_type
            if activity_type not in type_counts:
                type_counts[activity_type] = 0
                type_improvements[activity_type] = []
            
            type_counts[activity_type] += 1
            type_improvements[activity_type].append(record.improvement_score)
        
        # Calculate average improvements by type
        type_avg_improvement = {}
        for activity_type, improvements in type_improvements.items():
            type_avg_improvement[activity_type] = sum(improvements) / len(improvements)
        
        # Get favorite types (most used)
        favorite_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        favorite_types = [{'type': t[0], 'count': t[1]} for t in favorite_types]
        
        # Get most effective types
        most_effective = sorted(type_avg_improvement.items(), key=lambda x: x[1], reverse=True)[:3]
        most_effective = [{'type': t[0], 'avg_improvement': t[1]} for t in most_effective]
        
        # Determine recommendation confidence
        total_activities = len(user_history)
        if total_activities >= 20:
            confidence = 'high'
        elif total_activities >= 10:
            confidence = 'medium'
        else:
            confidence = 'low'
        
        return {
            'total_activities': total_activities,
            'favorite_types': favorite_types,
            'most_effective': most_effective,
            'recommendation_confidence': confidence
        }
    
    def _calculate_personalization_score(self, activity: Dict, user_history: List[ActivityHistory]) -> float:
        """Calculate how personalized this recommendation is for the user"""
        if not user_history:
            return 0.0
        
        activity_id = activity['activity_id']
        activity_type = activity.get('activity_type', '')
        
        # Check if user has done this specific activity before
        specific_count = sum(1 for record in user_history if record.activity_id == activity_id)
        
        # Check if user has done this activity type before
        type_count = sum(1 for record in user_history if record.activity_type == activity_type)
        
        # Calculate personalization score based on familiarity
        if specific_count > 0:
            return min(specific_count * 0.2, 1.0)  # Max 1.0 for specific activity
        elif type_count > 0:
            return min(type_count * 0.1, 0.5)  # Max 0.5 for activity type
        else:
            return 0.0  # No personalization data

# Extended singleton instance
recommendation_engine_extended = RecommendationEngineExtended()
