"""
Enhanced Recommendation Engine with Activity Effectiveness Integration
Integrates mood tracking data to improve activity recommendations
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import random
from datetime import datetime, timedelta

from services.recommendation_engine_extended import RecommendationEngineExtended
from services.activity_effectiveness_tracker import (
    activity_effectiveness_tracker,
    get_activity_recommendation_score,
    get_personalized_activity_insights
)

@dataclass
class EffectivenessWeightedActivity:
    """Activity with effectiveness-based scoring"""
    activity_id: str
    activity_type: str
    title: str
    description: str
    base_score: float
    effectiveness_score: float
    combined_score: float
    confidence: float
    sample_size: int
    recent_improvement: float

class EffectivenessAwareRecommendationEngine(RecommendationEngineExtended):
    """Enhanced recommendation engine that incorporates activity effectiveness data"""
    
    def __init__(self):
        super().__init__()
        self.effectiveness_weight = 0.4  # Weight for effectiveness in scoring
        self.min_sample_size = 2  # Minimum samples for reliable effectiveness data
        self.recency_weight = 0.2  # Weight for recent performance
    
    def get_effectiveness_aware_recommendations(self, 
                                               emotional_category: str,
                                               valence: float,
                                               arousal: float,
                                               user_id: str,
                                               current_mood: Optional[float] = None) -> Dict:
        """
        Get recommendations that incorporate activity effectiveness data
        
        Args:
            emotional_category: Current emotional category
            valence: Emotional valence (-1 to 1)
            arousal: Emotional arousal (-1 to 1)
            user_id: User identifier
            current_mood: Current mood score for tracking
            
        Returns:
            Dictionary with effectiveness-aware recommendations
        """
        # Get base recommendations from extended engine
        base_recommendations = super().get_recommendations(
            emotional_category=emotional_category,
            valence=valence,
            arousal=arousal,
            user_id=user_id
        )
        
        # Handle different return formats from extended engine
        if 'primary_activity' in base_recommendations:
            # Extended engine format - convert to list format
            all_activities = []
            
            # Add primary activity
            if base_recommendations['primary_activity']:
                all_activities.append(base_recommendations['primary_activity'])
            
            # Add secondary activities
            if base_recommendations.get('secondary_activities'):
                all_activities.extend(base_recommendations['secondary_activities'])
        else:
            # Assume it's already in the expected format
            all_activities = base_recommendations.get('all_activities', [])
        
        # Get user's effectiveness insights
        user_insights = get_personalized_activity_insights(user_id)
        
        # Get effectiveness scores for recommended activities
        effectiveness_enhanced_activities = []
        
        for activity in all_activities:
            activity_id = activity['activity_id']
            
            # Get effectiveness data
            effectiveness = activity_effectiveness_tracker.get_activity_effectiveness(user_id, activity_id)
            
            # Calculate effectiveness score
            effectiveness_score = effectiveness['recommendation_score']
            confidence = effectiveness['confidence']
            sample_size = effectiveness['sample_size']
            
            # Get recent performance
            recent_improvement = 0.0
            if effectiveness['recent_performance']:
                recent_records = effectiveness['recent_performance'][:3]  # Last 3 records
                if recent_records:
                    recent_improvement = sum(r['improvement'] for r in recent_records) / len(recent_records)
            
            # Calculate combined score
            base_score = activity.get('score', activity.get('history_score', 0.5))
            
            # Weight effectiveness based on confidence and sample size
            if sample_size >= self.min_sample_size:
                effectiveness_weight = self.effectiveness_weight * confidence
            else:
                effectiveness_weight = self.effectiveness_weight * 0.3  # Lower weight for small samples
            
            # Add recency bonus for recent good performance
            recency_bonus = 0.0
            if recent_improvement > 0.1 and sample_size >= 2:
                recency_bonus = self.recency_weight * (recent_improvement / 1.0)  # Normalize
            
            combined_score = (
                base_score * (1 - effectiveness_weight - recency_bonus) +
                effectiveness_score * effectiveness_weight +
                recency_bonus
            )
            
            effectiveness_enhanced_activity = EffectivenessWeightedActivity(
                activity_id=activity_id,
                activity_type=activity.get('type', activity.get('activity_type', 'unknown')),
                title=activity.get('title', activity.get('name', 'Unknown Activity')),
                description=activity.get('description', ''),
                base_score=base_score,
                effectiveness_score=effectiveness_score,
                combined_score=combined_score,
                confidence=confidence,
                sample_size=sample_size,
                recent_improvement=recent_improvement
            )
            
            effectiveness_enhanced_activities.append(effectiveness_enhanced_activity)
        
        # Sort by combined score
        effectiveness_enhanced_activities.sort(key=lambda x: x.combined_score, reverse=True)
        
        # Select primary recommendation
        primary_activity = None
        if effectiveness_enhanced_activities:
            # Prefer activities with good effectiveness data
            candidates_with_data = [a for a in effectiveness_enhanced_activities 
                                   if a.sample_size >= self.min_sample_size]
            
            if candidates_with_data:
                primary_activity = candidates_with_data[0]
            else:
                primary_activity = effectiveness_enhanced_activities[0]
        
        # Select secondary recommendations
        secondary_activities = effectiveness_enhanced_activities[1:4]  # Next 3 activities
        
        # Generate effectiveness-aware explanations
        explanations = self._generate_effectiveness_explanations(
            primary_activity, secondary_activities, user_insights
        )
        
        # Determine VR mode based on effectiveness
        vr_mode = self._determine_effectiveness_aware_vr_mode(
            emotional_category, primary_activity, user_insights
        )
        
        return {
            'primary_activity': {
                'activity_id': primary_activity.activity_id if primary_activity else None,
                'title': primary_activity.title if primary_activity else None,
                'type': primary_activity.activity_type if primary_activity else None,
                'description': primary_activity.description if primary_activity else None,
                'effectiveness_score': primary_activity.effectiveness_score if primary_activity else 0.0,
                'confidence': primary_activity.confidence if primary_activity else 0.0,
                'sample_size': primary_activity.sample_size if primary_activity else 0
            },
            'secondary_activities': [
                {
                    'activity_id': activity.activity_id,
                    'title': activity.title,
                    'type': activity.activity_type,
                    'effectiveness_score': activity.effectiveness_score,
                    'confidence': activity.confidence,
                    'sample_size': activity.sample_size
                }
                for activity in secondary_activities
            ],
            'vr_mode': vr_mode,
            'explanations': explanations,
            'user_insights': user_insights,
            'effectiveness_summary': {
                'total_activities_analyzed': len(effectiveness_enhanced_activities),
                'activities_with_data': len([a for a in effectiveness_enhanced_activities if a.sample_size > 0]),
                'highest_effectiveness': max([a.effectiveness_score for a in effectiveness_enhanced_activities]) if effectiveness_enhanced_activities else 0.0,
                'average_confidence': sum([a.confidence for a in effectiveness_enhanced_activities]) / len(effectiveness_enhanced_activities) if effectiveness_enhanced_activities else 0.0
            }
        }
    
    def _generate_effectiveness_explanations(self, 
                                           primary_activity: Optional[EffectivenessWeightedActivity],
                                           secondary_activities: List[EffectivenessWeightedActivity],
                                           user_insights: Dict) -> List[str]:
        """Generate explanations based on effectiveness data"""
        explanations = []
        
        if primary_activity:
            if primary_activity.sample_size >= self.min_sample_size:
                if primary_activity.effectiveness_score > 0.5:
                    explanations.append(
                        f"This activity has worked well for you before (effectiveness: {primary_activity.effectiveness_score:.2f})"
                    )
                elif primary_activity.effectiveness_score > 0.2:
                    explanations.append(
                        f"This activity has shown some positive results for you (effectiveness: {primary_activity.effectiveness_score:.2f})"
                    )
                else:
                    explanations.append(
                        f"Recommended based on your current emotional state, though past results have been mixed"
                    )
            else:
                explanations.append(
                    "New recommendation based on your current emotional needs"
                )
            
            # Add recency explanation
            if primary_activity.recent_improvement > 0.2:
                explanations.append(
                    f"You've had good results with similar activities recently"
                )
        
        # Add insights-based explanations
        if user_insights.get('recommendation_insights'):
            insights = user_insights['recommendation_insights'][:2]  # Top 2 insights
            explanations.extend(insights)
        
        # Add activity type effectiveness
        if secondary_activities:
            effective_types = [a for a in secondary_activities if a.effectiveness_score > 0.3]
            if effective_types:
                explanations.append(
                    f"Also considering {len(effective_types)} other activities that have worked well for you"
                )
        
        return explanations
    
    def _determine_effectiveness_aware_vr_mode(self, 
                                              emotional_category: str,
                                              primary_activity: Optional[EffectivenessWeightedActivity],
                                              user_insights: Dict) -> Optional[str]:
        """Determine VR mode based on effectiveness and emotional state"""
        
        # Base VR mode from emotional category
        base_vr_modes = {
            'anxious': 'calm',
            'distressed': 'safe',
            'sad': 'uplift',
            'angry': 'peaceful',
            'overwhelmed': 'grounding',
            'neutral': 'mindful',
            'energetic': 'focused',
            'happy': 'creative'
        }
        
        base_mode = base_vr_modes.get(emotional_category, 'mindful')
        
        # Adjust based on effectiveness insights
        if primary_activity and primary_activity.sample_size >= self.min_sample_size:
            if primary_activity.effectiveness_score > 0.6:
                # High effectiveness - stick with what works
                return base_mode
            elif primary_activity.effectiveness_score < 0.2:
                # Low effectiveness - try something different
                alternative_modes = ['creative', 'grounding', 'focused']
                return random.choice(alternative_modes)
        
        # Consider user's most effective activity types
        most_effective_types = user_insights.get('most_effective_types', [])
        if most_effective_types:
            best_type = most_effective_types[0]['activity_type']
            
            # Map activity types to VR modes
            type_to_vr = {
                'breathing': 'calm',
                'meditation': 'mindful',
                'grounding': 'grounding',
                'movement': 'energetic',
                'creative': 'creative',
                'relaxation': 'peaceful'
            }
            
            return type_to_vr.get(best_type, base_mode)
        
        return base_mode
    
    def record_activity_start(self, user_id: str, activity_id: str, current_mood: float) -> bool:
        """
        Record the start of an activity with current mood
        
        Args:
            user_id: User identifier
            activity_id: Activity identifier
            current_mood: Current mood score (-1 to 1)
            
        Returns:
            True if successfully recorded
        """
        try:
            # Store activity start in temporary storage
            # In a real implementation, this would be stored in session or cache
            activity_start_key = f"{user_id}:{activity_id}:start"
            
            # For now, we'll use a simple in-memory approach
            # In production, this should use Redis or similar
            if not hasattr(self, '_activity_starts'):
                self._activity_starts = {}
            
            self._activity_starts[activity_start_key] = {
                'user_id': user_id,
                'activity_id': activity_id,
                'mood_before': current_mood,
                'start_time': datetime.now()
            }
            
            return True
        except Exception as e:
            print(f"Error recording activity start: {e}")
            return False
    
    def record_activity_completion(self, 
                                user_id: str, 
                                activity_id: str, 
                                activity_type: str,
                                mood_after: float,
                                session_duration: Optional[int] = None,
                                user_rating: Optional[int] = None,
                                notes: Optional[str] = None,
                                completion_status: str = "completed") -> bool:
        """
        Record activity completion with mood tracking
        
        Args:
            user_id: User identifier
            activity_id: Activity identifier
            activity_type: Type of activity
            mood_after: Mood after activity (-1 to 1)
            session_duration: Duration in minutes
            user_rating: User rating (1-5)
            notes: User notes
            completion_status: Completion status
            
        Returns:
            True if successfully recorded
        """
        try:
            # Get mood before from activity start
            activity_start_key = f"{user_id}:{activity_id}:start"
            mood_before = -0.1  # Default neutral mood
            
            if hasattr(self, '_activity_starts') and activity_start_key in self._activity_starts:
                start_data = self._activity_starts[activity_start_key]
                mood_before = start_data['mood_before']
                
                # Calculate session duration if not provided
                if session_duration is None:
                    start_time = start_data['start_time']
                    session_duration = int((datetime.now() - start_time).total_seconds() / 60)
                
                # Clean up start data
                del self._activity_starts[activity_start_key]
            
            # Record in effectiveness tracker
            from services.activity_effectiveness_tracker import record_activity_completion
            
            return record_activity_completion(
                user_id=user_id,
                activity_id=activity_id,
                activity_type=activity_type,
                mood_before=mood_before,
                mood_after=mood_after,
                session_duration=session_duration,
                user_rating=user_rating,
                notes=notes,
                completion_status=completion_status
            )
            
        except Exception as e:
            print(f"Error recording activity completion: {e}")
            return False
    
    def get_personalized_activity_insights(self, user_id: str) -> Dict:
        """
        Get comprehensive insights for personalized recommendations
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with personalized insights
        """
        try:
            # Get user effectiveness summary
            user_summary = get_personalized_activity_insights(user_id)
            
            # Get activity type preferences
            activity_type_preferences = {}
            
            # Analyze most effective types
            most_effective_types = user_summary.get('most_effective_types', [])
            for type_info in most_effective_types:
                activity_type = type_info['activity_type']
                score = type_info['score']
                activity_type_preferences[activity_type] = score
            
            # Generate recommendations based on insights
            recommendations = []
            
            if user_summary.get('average_improvement', 0) > 0.3:
                recommendations.append("Continue with activities that have shown good results")
            elif user_summary.get('average_improvement', 0) < -0.1:
                recommendations.append("Consider trying different types of activities")
            
            if user_summary.get('success_rate', 0) > 0.8:
                recommendations.append("You have excellent completion rates - try longer sessions")
            elif user_summary.get('success_rate', 0) < 0.5:
                recommendations.append("Focus on shorter activities to build consistency")
            
            return {
                'user_summary': user_summary,
                'activity_type_preferences': activity_type_preferences,
                'recommendations': recommendations,
                'confidence_level': min(user_summary.get('total_activities', 0) / 10.0, 1.0)
            }
            
        except Exception as e:
            print(f"Error getting personalized insights: {e}")
            return {
                'user_summary': {},
                'activity_type_preferences': {},
                'recommendations': [],
                'confidence_level': 0.0
            }

# Singleton instance for easy import
effectiveness_aware_engine = EffectivenessAwareRecommendationEngine()
