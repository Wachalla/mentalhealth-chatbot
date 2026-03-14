"""
Activity Effectiveness Tracking Service
Tracks mood before and after activities to improve future recommendations
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
import sqlite3
import os
from statistics import mean, median

@dataclass
class ActivityEffectivenessRecord:
    """Record of activity effectiveness for mood improvement"""
    id: Optional[int] = None
    user_id: str = ""
    activity_id: str = ""
    activity_type: str = ""
    mood_before: float = 0.0  # -1 to 1 scale
    mood_after: float = 0.0   # -1 to 1 scale
    timestamp: datetime = None
    session_duration: Optional[int] = None  # minutes
    user_rating: Optional[int] = None  # 1-5 scale
    notes: Optional[str] = None
    completion_status: str = "completed"  # "completed", "partial", "abandoned"
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    @property
    def mood_improvement(self) -> float:
        """Calculate mood improvement (after - before)"""
        return self.mood_after - self.mood_before
    
    @property
    def effectiveness_score(self) -> float:
        """Calculate overall effectiveness score"""
        # Base score from mood improvement
        base_score = max(0, self.mood_improvement)  # Only positive improvements count
        
        # Bonus for completion
        completion_bonus = 1.0 if self.completion_status == "completed" else 0.5
        
        # Bonus for user rating if available
        rating_bonus = (self.user_rating or 3) / 5.0  # Normalize to 0-1 scale
        
        # Duration bonus (optimal duration is 10-30 minutes)
        duration_bonus = 1.0
        if self.session_duration:
            if 10 <= self.session_duration <= 30:
                duration_bonus = 1.2
            elif self.session_duration > 30:
                duration_bonus = 1.1
            elif self.session_duration < 5:
                duration_bonus = 0.8
        
        return base_score * completion_bonus * rating_bonus * duration_bonus

class ActivityEffectivenessTracker:
    """Tracks and analyzes activity effectiveness for mood improvement"""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            # Default to database directory
            db_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
            os.makedirs(db_dir, exist_ok=True)
            db_path = os.path.join(db_dir, 'activity_effectiveness.db')
        
        self.db_path = db_path
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize SQLite database for activity effectiveness tracking"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS activity_effectiveness (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        activity_id TEXT NOT NULL,
                        activity_type TEXT NOT NULL,
                        mood_before REAL NOT NULL,
                        mood_after REAL NOT NULL,
                        timestamp DATETIME NOT NULL,
                        session_duration INTEGER,
                        user_rating INTEGER,
                        notes TEXT,
                        completion_status TEXT DEFAULT 'completed',
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create indexes for better performance
                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_user_id ON activity_effectiveness(user_id)
                ''')
                
                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_activity_id ON activity_effectiveness(activity_id)
                ''')
                
                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_timestamp ON activity_effectiveness(timestamp)
                ''')
                
                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_user_activity ON activity_effectiveness(user_id, activity_id)
                ''')
                
                conn.commit()
        except Exception as e:
            print(f"Warning: Could not initialize activity effectiveness database: {e}")
    
    def record_activity_completion(self, record: ActivityEffectivenessRecord) -> bool:
        """
        Record completion of an activity with mood measurements
        
        Args:
            record: ActivityEffectivenessRecord with all activity data
            
        Returns:
            True if successfully recorded
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO activity_effectiveness 
                    (user_id, activity_id, activity_type, mood_before, mood_after, 
                     timestamp, session_duration, user_rating, notes, completion_status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    record.user_id,
                    record.activity_id,
                    record.activity_type,
                    record.mood_before,
                    record.mood_after,
                    record.timestamp.isoformat(),
                    record.session_duration,
                    record.user_rating,
                    record.notes,
                    record.completion_status
                ))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Error recording activity effectiveness: {e}")
            return False
    
    def get_activity_effectiveness(self, user_id: str, activity_id: str, days: int = 30) -> Dict:
        """
        Get effectiveness statistics for a specific activity
        
        Args:
            user_id: User identifier
            activity_id: Activity identifier
            days: Number of days to look back
            
        Returns:
            Dictionary with effectiveness statistics
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                cursor = conn.execute('''
                    SELECT 
                        mood_before,
                        mood_after,
                        user_rating,
                        session_duration,
                        completion_status,
                        timestamp
                    FROM activity_effectiveness
                    WHERE user_id = ? AND activity_id = ?
                    AND timestamp >= datetime('now', '-{} days')
                    ORDER BY timestamp DESC
                '''.format(days), (user_id, activity_id))
                
                records = cursor.fetchall()
                
                if not records:
                    return {
                        'sample_size': 0,
                        'average_improvement': 0.0,
                        'success_rate': 0.0,
                        'confidence': 0.0,
                        'recent_performance': [],
                        'recommendation_score': 0.0
                    }
                
                # Calculate statistics
                mood_improvements = []
                user_ratings = []
                completion_rates = []
                recent_performance = []
                
                for record in records:
                    improvement = record['mood_after'] - record['mood_before']
                    mood_improvements.append(improvement)
                    
                    if record['user_rating']:
                        user_ratings.append(record['user_rating'])
                    
                    completion_rates.append(1 if record['completion_status'] == 'completed' else 0)
                    
                    # Recent performance (last 5 records)
                    if len(recent_performance) < 5:
                        recent_performance.append({
                            'timestamp': record['timestamp'],
                            'improvement': improvement,
                            'rating': record['user_rating'],
                            'completed': record['completion_status'] == 'completed'
                        })
                
                avg_improvement = mean(mood_improvements) if mood_improvements else 0.0
                success_rate = mean(completion_rates) if completion_rates else 0.0
                avg_rating = mean(user_ratings) if user_ratings else 3.0
                
                # Confidence based on sample size
                sample_size = len(records)
                confidence = min(sample_size / 10.0, 1.0)  # Max confidence at 10 samples
                
                # Recommendation score (0-1 scale)
                recommendation_score = max(0, avg_improvement) * success_rate * (avg_rating / 5.0)
                
                return {
                    'sample_size': sample_size,
                    'average_improvement': avg_improvement,
                    'success_rate': success_rate,
                    'average_rating': avg_rating,
                    'confidence': confidence,
                    'recent_performance': recent_performance,
                    'recommendation_score': recommendation_score,
                    'total_completions': len([r for r in records if r['completion_status'] == 'completed']),
                    'average_duration': mean([r['session_duration'] for r in records if r['session_duration']]) if any(r['session_duration'] for r in records) else None
                }
                
        except Exception as e:
            print(f"Error getting activity effectiveness: {e}")
            return {
                'sample_size': 0,
                'average_improvement': 0.0,
                'success_rate': 0.0,
                'confidence': 0.0,
                'recent_performance': [],
                'recommendation_score': 0.0
            }
    
    def get_user_activity_history(self, user_id: str, days: int = 30, limit: int = 50) -> List[ActivityEffectivenessRecord]:
        """
        Get user's activity history with effectiveness data
        
        Args:
            user_id: User identifier
            days: Number of days to look back
            limit: Maximum number of records to return
            
        Returns:
            List of ActivityEffectivenessRecord objects
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                cursor = conn.execute('''
                    SELECT *
                    FROM activity_effectiveness
                    WHERE user_id = ?
                    AND timestamp >= datetime('now', '-{} days')
                    ORDER BY timestamp DESC
                    LIMIT ?
                '''.format(days), (user_id, limit))
                
                records = []
                for row in cursor.fetchall():
                    record = ActivityEffectivenessRecord(
                        id=row['id'],
                        user_id=row['user_id'],
                        activity_id=row['activity_id'],
                        activity_type=row['activity_type'],
                        mood_before=row['mood_before'],
                        mood_after=row['mood_after'],
                        timestamp=datetime.fromisoformat(row['timestamp']),
                        session_duration=row['session_duration'],
                        user_rating=row['user_rating'],
                        notes=row['notes'],
                        completion_status=row['completion_status']
                    )
                    records.append(record)
                
                return records
                
        except Exception as e:
            print(f"Error getting user activity history: {e}")
            return []
    
    def get_activity_type_effectiveness(self, user_id: str, activity_type: str, days: int = 30) -> Dict:
        """
        Get effectiveness statistics for an activity type
        
        Args:
            user_id: User identifier
            activity_type: Type of activity (e.g., "breathing", "meditation")
            days: Number of days to look back
            
        Returns:
            Dictionary with effectiveness statistics for the activity type
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                cursor = conn.execute('''
                    SELECT 
                        activity_id,
                        mood_before,
                        mood_after,
                        user_rating,
                        completion_status,
                        timestamp
                    FROM activity_effectiveness
                    WHERE user_id = ? AND activity_type = ?
                    AND timestamp >= datetime('now', '-{} days')
                    ORDER BY timestamp DESC
                '''.format(days), (user_id, activity_type))
                
                records = cursor.fetchall()
                
                if not records:
                    return {
                        'sample_size': 0,
                        'average_improvement': 0.0,
                        'success_rate': 0.0,
                        'confidence': 0.0,
                        'best_activities': [],
                        'recommendation_score': 0.0
                    }
                
                # Group by activity ID
                activity_stats = {}
                mood_improvements = []
                completion_rates = []
                user_ratings = []
                
                for record in records:
                    activity_id = record['activity_id']
                    improvement = record['mood_after'] - record['mood_before']
                    
                    if activity_id not in activity_stats:
                        activity_stats[activity_id] = {
                            'improvements': [],
                            'ratings': [],
                            'completions': []
                        }
                    
                    activity_stats[activity_id]['improvements'].append(improvement)
                    mood_improvements.append(improvement)
                    
                    if record['user_rating']:
                        activity_stats[activity_id]['ratings'].append(record['user_rating'])
                        user_ratings.append(record['user_rating'])
                    
                    completion = record['completion_status'] == 'completed'
                    activity_stats[activity_id]['completions'].append(completion)
                    completion_rates.append(1 if completion else 0)
                
                # Calculate overall statistics
                avg_improvement = mean(mood_improvements) if mood_improvements else 0.0
                success_rate = mean(completion_rates) if completion_rates else 0.0
                avg_rating = mean(user_ratings) if user_ratings else 3.0
                
                # Find best activities
                best_activities = []
                for activity_id, stats in activity_stats.items():
                    if stats['improvements']:
                        activity_avg_improvement = mean(stats['improvements'])
                        activity_success_rate = mean(stats['completions'])
                        activity_avg_rating = mean(stats['ratings']) if stats['ratings'] else 3.0
                        
                        score = max(0, activity_avg_improvement) * activity_success_rate * (activity_avg_rating / 5.0)
                        
                        best_activities.append({
                            'activity_id': activity_id,
                            'score': score,
                            'average_improvement': activity_avg_improvement,
                            'success_rate': activity_success_rate,
                            'sample_size': len(stats['improvements'])
                        })
                
                # Sort by score
                best_activities.sort(key=lambda x: x['score'], reverse=True)
                
                # Confidence based on sample size
                sample_size = len(records)
                confidence = min(sample_size / 10.0, 1.0)
                
                # Recommendation score
                recommendation_score = max(0, avg_improvement) * success_rate * (avg_rating / 5.0)
                
                return {
                    'sample_size': sample_size,
                    'average_improvement': avg_improvement,
                    'success_rate': success_rate,
                    'average_rating': avg_rating,
                    'confidence': confidence,
                    'best_activities': best_activities[:5],  # Top 5 activities
                    'recommendation_score': recommendation_score,
                    'total_activities': len(activity_stats)
                }
                
        except Exception as e:
            print(f"Error getting activity type effectiveness: {e}")
            return {
                'sample_size': 0,
                'average_improvement': 0.0,
                'success_rate': 0.0,
                'confidence': 0.0,
                'best_activities': [],
                'recommendation_score': 0.0
            }
    
    def get_user_effectiveness_summary(self, user_id: str, days: int = 30) -> Dict:
        """
        Get overall effectiveness summary for a user
        
        Args:
            user_id: User identifier
            days: Number of days to look back
            
        Returns:
            Dictionary with overall effectiveness summary
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                cursor = conn.execute('''
                    SELECT 
                        activity_type,
                        mood_before,
                        mood_after,
                        user_rating,
                        completion_status,
                        timestamp,
                        session_duration
                    FROM activity_effectiveness
                    WHERE user_id = ?
                    AND timestamp >= datetime('now', '-{} days')
                    ORDER BY timestamp DESC
                '''.format(days), (user_id,))
                
                records = cursor.fetchall()
                
                if not records:
                    return {
                        'total_activities': 0,
                        'average_improvement': 0.0,
                        'success_rate': 0.0,
                        'most_effective_types': [],
                        'recommendation_insights': []
                    }
                
                # Analyze by activity type
                type_stats = {}
                all_improvements = []
                all_completions = []
                all_ratings = []
                
                for record in records:
                    activity_type = record['activity_type']
                    improvement = record['mood_after'] - record['mood_before']
                    
                    if activity_type not in type_stats:
                        type_stats[activity_type] = {
                            'improvements': [],
                            'ratings': [],
                            'completions': [],
                            'durations': []
                        }
                    
                    type_stats[activity_type]['improvements'].append(improvement)
                    all_improvements.append(improvement)
                    
                    if record['user_rating']:
                        type_stats[activity_type]['ratings'].append(record['user_rating'])
                        all_ratings.append(record['user_rating'])
                    
                    completion = record['completion_status'] == 'completed'
                    type_stats[activity_type]['completions'].append(completion)
                    all_completions.append(1 if completion else 0)
                    
                    if record['session_duration']:
                        type_stats[activity_type]['durations'].append(record['session_duration'])
                
                # Calculate overall statistics
                avg_improvement = mean(all_improvements) if all_improvements else 0.0
                success_rate = mean(all_completions) if all_completions else 0.0
                avg_rating = mean(all_ratings) if all_ratings else 3.0
                
                # Find most effective activity types
                most_effective_types = []
                for activity_type, stats in type_stats.items():
                    if stats['improvements']:
                        type_avg_improvement = mean(stats['improvements'])
                        type_success_rate = mean(stats['completions'])
                        type_avg_rating = mean(stats['ratings']) if stats['ratings'] else 3.0
                        
                        score = max(0, type_avg_improvement) * type_success_rate * (type_avg_rating / 5.0)
                        
                        most_effective_types.append({
                            'activity_type': activity_type,
                            'score': score,
                            'average_improvement': type_avg_improvement,
                            'success_rate': type_success_rate,
                            'sample_size': len(stats['improvements']),
                            'average_duration': mean(stats['durations']) if stats['durations'] else None
                        })
                
                # Sort by effectiveness score
                most_effective_types.sort(key=lambda x: x['score'], reverse=True)
                
                # Generate recommendation insights
                insights = []
                
                if avg_improvement > 0.2:
                    insights.append("Activities are generally improving your mood effectively")
                elif avg_improvement < -0.1:
                    insights.append("Activities may need adjustment as mood is declining")
                else:
                    insights.append("Activities have neutral effect on mood overall")
                
                if success_rate > 0.8:
                    insights.append("You have excellent completion rates")
                elif success_rate < 0.5:
                    insights.append("Consider shorter activities to improve completion rates")
                
                if most_effective_types:
                    best_type = most_effective_types[0]['activity_type']
                    insights.append(f"Your most effective activity type is {best_type}")
                
                return {
                    'total_activities': len(records),
                    'average_improvement': avg_improvement,
                    'success_rate': success_rate,
                    'average_rating': avg_rating,
                    'most_effective_types': most_effective_types[:3],
                    'recommendation_insights': insights,
                    'activity_types_tried': len(type_stats),
                    'period_days': days
                }
                
        except Exception as e:
            print(f"Error getting user effectiveness summary: {e}")
            return {
                'total_activities': 0,
                'average_improvement': 0.0,
                'success_rate': 0.0,
                'most_effective_types': [],
                'recommendation_insights': []
            }
    
    def clear_old_records(self, days: int = 90) -> int:
        """
        Clear old effectiveness records
        
        Args:
            days: Number of days to keep records
            
        Returns:
            Number of records deleted
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    DELETE FROM activity_effectiveness
                    WHERE timestamp < datetime('now', '-{} days')
                '''.format(days))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                return deleted_count
                
        except Exception as e:
            print(f"Error clearing old records: {e}")
            return 0

# Singleton instance for easy import
activity_effectiveness_tracker = ActivityEffectivenessTracker()

# Helper functions for integration with AIProcessor
def record_activity_completion(user_id: str, activity_id: str, activity_type: str, 
                             mood_before: float, mood_after: float, 
                             session_duration: Optional[int] = None,
                             user_rating: Optional[int] = None,
                             notes: Optional[str] = None,
                             completion_status: str = "completed") -> bool:
    """Record activity completion with mood tracking"""
    record = ActivityEffectivenessRecord(
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
    return activity_effectiveness_tracker.record_activity_completion(record)

def get_activity_recommendation_score(user_id: str, activity_id: str) -> float:
    """Get recommendation score for an activity based on user's historical effectiveness"""
    effectiveness = activity_effectiveness_tracker.get_activity_effectiveness(user_id, activity_id)
    return effectiveness.get('recommendation_score', 0.0)

def get_personalized_activity_insights(user_id: str) -> Dict:
    """Get personalized insights for activity recommendations"""
    return activity_effectiveness_tracker.get_user_effectiveness_summary(user_id)
