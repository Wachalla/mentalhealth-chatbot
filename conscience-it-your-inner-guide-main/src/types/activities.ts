// Activity Types and Strategy Pattern Implementation

export interface MoodEntry {
  id: string;
  user_id: string;
  valence: number; // -1 to 1 (negative to positive)
  arousal: number; // -1 to 1 (calm to excited)
  timestamp: Date;
  notes?: string;
}

export interface ActivityCategory {
  id: string;
  name: string;
  description: string;
  icon: string;
  color: string;
  targetMoods: {
    valenceRange: [number, number];
    arousalRange: [number, number];
  };
  priority: number;
}

export interface Activity {
  id: string;
  title: string;
  description: string;
  category: ActivityCategory['id'];
  duration: number; // in minutes
  difficulty: 'easy' | 'medium' | 'hard';
  vrEnabled?: boolean;
  resources?: string[];
  therapeuticGoals: string[];
  featured?: boolean;
}

export interface ActivityStrategy {
  shouldShow: (activity: Activity, userMood: MoodEntry | null) => boolean;
  getPriority: (activity: Activity, userMood: MoodEntry | null) => number;
}

// Activity Categories
export const ACTIVITY_CATEGORIES: ActivityCategory[] = [
  {
    id: 'breathing',
    name: 'Breathing Exercises',
    description: 'Calm your nervous system',
    icon: 'Wind',
    color: 'blue',
    targetMoods: {
      valenceRange: [-0.5, 0.5],
      arousalRange: [0.5, 1]
    },
    priority: 1
  },
  {
    id: 'grounding',
    name: 'Grounding Techniques',
    description: 'Stay present and centered',
    icon: 'Zap',
    color: 'green',
    targetMoods: {
      valenceRange: [-1, -0.3],
      arousalRange: [-0.5, 0.5]
    },
    priority: 2
  },
  {
    id: 'mindfulness',
    name: 'Mindfulness',
    description: 'Present moment awareness',
    icon: 'Brain',
    color: 'purple',
    targetMoods: {
      valenceRange: [-0.5, 0.5],
      arousalRange: [-0.5, 0.5]
    },
    priority: 3
  }
];

// Strategy Implementations
export class AnxietyStrategy implements ActivityStrategy {
  shouldShow(activity: Activity, userMood: MoodEntry | null): boolean {
    if (!userMood) return true;
    
    if (userMood.arousal > 0.6) {
      return ['breathing', 'grounding'].includes(activity.category);
    }
    
    return true;
  }

  getPriority(activity: Activity, userMood: MoodEntry | null): number {
    if (!userMood) return activity.featured ? 10 : 5;
    
    if (userMood.arousal > 0.6 && ['breathing', 'grounding'].includes(activity.category)) {
      return 20;
    }
    
    return activity.featured ? 10 : 5;
  }
}

export class DepressionStrategy implements ActivityStrategy {
  shouldShow(activity: Activity, userMood: MoodEntry | null): boolean {
    if (!userMood) return true;
    
    if (userMood.valence < -0.5) {
      return ['grounding', 'movement', 'creative'].includes(activity.category);
    }
    
    return true;
  }

  getPriority(activity: Activity, userMood: MoodEntry | null): number {
    if (!userMood) return activity.featured ? 10 : 5;
    
    if (userMood.valence < -0.5) {
      const boostMap = {
        'grounding': 15,
        'movement': 12,
        'creative': 10
      };
      return boostMap[activity.category as keyof typeof boostMap] || 5;
    }
    
    return activity.featured ? 10 : 5;
  }
}

export class NeutralStrategy implements ActivityStrategy {
  shouldShow(activity: Activity, userMood: MoodEntry | null): boolean {
    return true;
  }

  getPriority(activity: Activity, userMood: MoodEntry | null): number {
    return activity.featured ? 10 : 5;
  }
}

// Strategy Factory
export class ActivityStrategyFactory {
  static createStrategy(userMood: MoodEntry | null): ActivityStrategy {
    if (!userMood) return new NeutralStrategy();
    
    if (userMood.arousal > 0.6) {
      return new AnxietyStrategy();
    } else if (userMood.valence < -0.5) {
      return new DepressionStrategy();
    }
    
    return new NeutralStrategy();
  }
}

// Sample Activities Data
export const SAMPLE_ACTIVITIES: Activity[] = [
  {
    id: 'breathing-4-7-8',
    title: '4-7-8 Breathing',
    description: 'Calming breathing technique to reduce anxiety',
    category: 'breathing',
    duration: 5,
    difficulty: 'easy',
    vrEnabled: true,
    therapeuticGoals: ['anxiety-reduction', 'nervous-system-regulation'],
    featured: true
  },
  {
    id: 'grounding-5-4-3-2-1',
    title: '5-4-3-2-1 Grounding',
    description: 'Use your senses to ground yourself in the present',
    category: 'grounding',
    duration: 10,
    difficulty: 'easy',
    therapeuticGoals: ['mindfulness', 'anxiety-reduction']
  },
  {
    id: 'mindfulness-body-scan',
    title: 'Body Scan Meditation',
    description: 'Progressive relaxation through body awareness',
    category: 'mindfulness',
    duration: 15,
    difficulty: 'medium',
    vrEnabled: true,
    therapeuticGoals: ['stress-reduction', 'body-awareness']
  }
];
