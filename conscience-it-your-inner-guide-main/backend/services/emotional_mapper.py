# Emotional Mapper Service
# Maps valence and arousal values to emotional categories with confidence scoring

from typing import Dict, Tuple, Optional
from enum import Enum
import math

class EmotionalCategory(Enum):
    """Emotional categories based on valence-arousal mapping"""
    DISTRESSED = "distressed"
    ANXIOUS = "anxious"
    LOW = "low"
    CALM = "calm"
    ENERGIZED = "energized"
    NEUTRAL = "neutral"

class EmotionalMapper:
    """Maps valence and arousal values to emotional categories"""
    
    def __init__(self):
        # Define quadrant boundaries
        self.valence_threshold = 0.0  # Positive vs negative
        self.arousal_threshold = 0.0  # High vs low arousal
        
        # Define intensity thresholds for confidence calculation
        self.high_intensity = 0.7
        self.medium_intensity = 0.3
        self.low_intensity = 0.1
    
    def map_to_category(self, valence: float, arousal: float) -> Tuple[EmotionalCategory, float]:
        """
        Map valence and arousal to emotional category with confidence
        
        Args:
            valence: -1.0 (very negative) to 1.0 (very positive)
            arousal: -1.0 (very calm) to 1.0 (very excited)
            
        Returns:
            Tuple of (category, confidence_score)
        """
        # Normalize inputs to ensure they're within bounds
        valence = max(-1.0, min(1.0, valence))
        arousal = max(-1.0, min(1.0, arousal))
        
        # Calculate distance from center (0,0) - affects confidence
        distance_from_center = math.sqrt(valence**2 + arousal**2)
        
        # Determine category based on quadrant
        if valence <= -0.5 and arousal >= 0.5:
            category = EmotionalCategory.DISTRESSED
        elif valence < 0.3 and arousal > 0.5:
            category = EmotionalCategory.ANXIOUS
        elif valence < -0.5 and arousal <= 0.5:
            category = EmotionalCategory.LOW
        elif valence > 0.3 and arousal < -0.3:
            category = EmotionalCategory.CALM
        elif valence > 0.5 and arousal > 0.3:
            category = EmotionalCategory.ENERGIZED
        else:
            category = EmotionalCategory.NEUTRAL
        
        # Calculate confidence based on distance from center and intensity
        confidence = self._calculate_confidence(valence, arousal, distance_from_center)
        
        return category, confidence
    
    def _calculate_confidence(self, valence: float, arousal: float, distance: float) -> float:
        """
        Calculate confidence score based on how clearly the point falls into a category
        
        Args:
            valence: Valence value (-1 to 1)
            arousal: Arousal value (-1 to 1)
            distance: Distance from center (0 to sqrt(2))
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        # Base confidence from distance from center
        # Points farther from center are more clearly categorized
        distance_confidence = min(distance / 1.4, 1.0)  # Normalize by max possible distance
        
        # Additional confidence from intensity
        intensity = max(abs(valence), abs(arousal))
        
        if intensity >= self.high_intensity:
            intensity_confidence = 0.9
        elif intensity >= self.medium_intensity:
            intensity_confidence = 0.7
        elif intensity >= self.low_intensity:
            intensity_confidence = 0.5
        else:
            intensity_confidence = 0.3
        
        # Combine distance and intensity confidence
        combined_confidence = (distance_confidence * 0.6) + (intensity_confidence * 0.4)
        
        # Boost confidence for clear quadrant placement
        quadrant_boost = self._get_quadrant_boost(valence, arousal)
        final_confidence = min(combined_confidence + quadrant_boost, 1.0)
        
        return max(0.0, final_confidence)
    
    def _get_quadrant_boost(self, valence: float, arousal: float) -> float:
        """
        Get additional confidence boost based on clear quadrant placement
        """
        boost = 0.0
        
        # Strong negative valence
        if valence <= -0.7:
            boost += 0.1
        # Strong positive valence
        elif valence >= 0.7:
            boost += 0.1
        
        # High arousal
        if arousal >= 0.7:
            boost += 0.1
        # Low arousal
        elif arousal <= -0.7:
            boost += 0.1
        
        # Clear diagonal placement (strong in both dimensions)
        if (abs(valence) >= 0.6 and abs(arousal) >= 0.6):
            boost += 0.05
        
        return boost
    
    def get_category_description(self, category: EmotionalCategory) -> Dict:
        """
        Get detailed description of an emotional category
        
        Args:
            category: EmotionalCategory enum
            
        Returns:
            Dictionary with category information
        """
        descriptions = {
            EmotionalCategory.DISTRESSED: {
                "name": "Distressed",
                "description": "Negative emotional state with high arousal",
                "characteristics": ["feeling overwhelmed", "high stress", "emotional intensity"],
                "typical_valence_range": (-1.0, -0.5),
                "typical_arousal_range": (0.5, 1.0),
                "color": "#E74C3C",  # Red
                "recommendations": ["breathing exercises", "grounding techniques", "crisis support"]
            },
            EmotionalCategory.ANXIOUS: {
                "name": "Anxious",
                "description": "Mildly negative emotional state with high arousal",
                "characteristics": ["worry", "nervousness", "anticipatory fear"],
                "typical_valence_range": (-0.3, 0.3),
                "typical_arousal_range": (0.5, 1.0),
                "color": "#F39C12",  # Orange
                "recommendations": ["mindfulness", "breathing exercises", "cognitive techniques"]
            },
            EmotionalCategory.LOW: {
                "name": "Low",
                "description": "Negative emotional state with low arousal",
                "characteristics": ["sadness", "low energy", "withdrawal"],
                "typical_valence_range": (-1.0, -0.5),
                "typical_arousal_range": (-1.0, 0.5),
                "color": "#95A5A6",  # Gray
                "recommendations": ["gentle activity", "self-compassion", "social connection"]
            },
            EmotionalCategory.CALM: {
                "name": "Calm",
                "description": "Positive emotional state with low arousal",
                "characteristics": ["peacefulness", "contentment", "relaxation"],
                "typical_valence_range": (0.3, 1.0),
                "typical_arousal_range": (-1.0, -0.3),
                "color": "#27AE60",  # Green
                "recommendations": ["meditation", "reflection", "gratitude practice"]
            },
            EmotionalCategory.ENERGIZED: {
                "name": "Energized",
                "description": "Positive emotional state with high arousal",
                "characteristics": ["excitement", "motivation", "enthusiasm"],
                "typical_valence_range": (0.5, 1.0),
                "typical_arousal_range": (0.3, 1.0),
                "color": "#3498DB",  # Blue
                "recommendations": ["creative activities", "goal setting", "social engagement"]
            },
            EmotionalCategory.NEUTRAL: {
                "name": "Neutral",
                "description": "Balanced emotional state near center",
                "characteristics": ["calm neutrality", "emotional balance"],
                "typical_valence_range": (-0.3, 0.3),
                "typical_arousal_range": (-0.3, 0.3),
                "color": "#7F8C8D",  # Light gray
                "recommendations": ["mindfulness", "self-awareness", "emotional check-in"]
            }
        }
        
        return descriptions.get(category, descriptions[EmotionalCategory.NEUTRAL])
    
    def get_transition_probability(self, from_category: EmotionalCategory, 
                                 to_category: EmotionalCategory) -> float:
        """
        Calculate probability of transitioning from one emotional category to another
        
        Args:
            from_category: Current emotional category
            to_category: Target emotional category
            
        Returns:
            Transition probability (0.0 to 1.0)
        """
        # Define transition matrix (simplified model)
        transition_matrix = {
            EmotionalCategory.DISTRESSED: {
                EmotionalCategory.DISTRESSED: 0.4,
                EmotionalCategory.ANXIOUS: 0.3,
                EmotionalCategory.LOW: 0.2,
                EmotionalCategory.CALM: 0.05,
                EmotionalCategory.ENERGIZED: 0.03,
                EmotionalCategory.NEUTRAL: 0.02
            },
            EmotionalCategory.ANXIOUS: {
                EmotionalCategory.DISTRESSED: 0.1,
                EmotionalCategory.ANXIOUS: 0.3,
                EmotionalCategory.LOW: 0.1,
                EmotionalCategory.CALM: 0.3,
                EmotionalCategory.ENERGIZED: 0.15,
                EmotionalCategory.NEUTRAL: 0.05
            },
            EmotionalCategory.LOW: {
                EmotionalCategory.DISTRESSED: 0.05,
                EmotionalCategory.ANXIOUS: 0.1,
                EmotionalCategory.LOW: 0.4,
                EmotionalCategory.CALM: 0.3,
                EmotionalCategory.ENERGIZED: 0.1,
                EmotionalCategory.NEUTRAL: 0.05
            },
            EmotionalCategory.CALM: {
                EmotionalCategory.DISTRESSED: 0.02,
                EmotionalCategory.ANXIOUS: 0.05,
                EmotionalCategory.LOW: 0.1,
                EmotionalCategory.CALM: 0.5,
                EmotionalCategory.ENERGIZED: 0.25,
                EmotionalCategory.NEUTRAL: 0.08
            },
            EmotionalCategory.ENERGIZED: {
                EmotionalCategory.DISTRESSED: 0.03,
                EmotionalCategory.ANXIOUS: 0.1,
                EmotionalCategory.LOW: 0.05,
                EmotionalCategory.CALM: 0.3,
                EmotionalCategory.ENERGIZED: 0.4,
                EmotionalCategory.NEUTRAL: 0.12
            },
            EmotionalCategory.NEUTRAL: {
                EmotionalCategory.DISTRESSED: 0.05,
                EmotionalCategory.ANXIOUS: 0.15,
                EmotionalCategory.LOW: 0.15,
                EmotionalCategory.CALM: 0.25,
                EmotionalCategory.ENERGIZED: 0.25,
                EmotionalCategory.NEUTRAL: 0.15
            }
        }
        
        return transition_matrix.get(from_category, {}).get(to_category, 0.1)
    
    def get_emotional_distance(self, valence1: float, arousal1: float, 
                              valence2: float, arousal2: float) -> float:
        """
        Calculate Euclidean distance between two emotional states
        
        Args:
            valence1, arousal1: First emotional state
            valence2, arousal2: Second emotional state
            
        Returns:
            Distance (0.0 to ~2.828)
        """
        return math.sqrt((valence2 - valence1)**2 + (arousal2 - arousal1)**2)
    
    def is_similar_state(self, valence1: float, arousal1: float,
                         valence2: float, arousal2: float, 
                         threshold: float = 0.3) -> bool:
        """
        Check if two emotional states are similar
        
        Args:
            valence1, arousal1: First emotional state
            valence2, arousal2: Second emotional state
            threshold: Distance threshold for similarity
            
        Returns:
            True if states are similar
        """
        distance = self.get_emotional_distance(valence1, arousal1, valence2, arousal2)
        return distance <= threshold

# Singleton instance for easy import
emotional_mapper = EmotionalMapper()
