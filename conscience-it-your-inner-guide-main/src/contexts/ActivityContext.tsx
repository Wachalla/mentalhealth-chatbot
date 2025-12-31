import React, { createContext, useContext, useState, ReactNode } from 'react';
import { useAuth } from './AuthContext';
import { 
  MoodEntry, 
  Activity, 
  ActivityStrategy, 
  ActivityStrategyFactory,
  SAMPLE_ACTIVITIES,
  ACTIVITY_CATEGORIES 
} from '@/types/activities';

interface ActivityContextType {
  activities: Activity[];
  currentMood: MoodEntry | null;
  filteredActivities: Activity[];
  featuredActivity: Activity | null;
  loading: boolean;
  setCurrentMood: (mood: MoodEntry | null) => void;
  startActivity: (activityId: string) => Promise<void>;
  completeActivity: (activityId: string, postMood: MoodEntry) => Promise<void>;
}

const ActivityContext = createContext<ActivityContextType | undefined>(undefined);

export const useActivities = () => {
  const context = useContext(ActivityContext);
  if (!context) {
    throw new Error('useActivities must be used within an ActivityProvider');
  }
  return context;
};

interface ActivityProviderProps {
  children: ReactNode;
}

export const ActivityProvider: React.FC<ActivityProviderProps> = ({ children }) => {
  const [activities, setActivities] = useState<Activity[]>(SAMPLE_ACTIVITIES);
  const [currentMood, setCurrentMood] = useState<MoodEntry | null>(null);
  const [filteredActivities, setFilteredActivities] = useState<Activity[]>([]);
  const [featuredActivity, setFeaturedActivity] = useState<Activity | null>(null);
  const [loading, setLoading] = useState(false);
  const { user } = useAuth();

  // Apply strategy pattern to filter activities
  const applyActivityStrategy = (mood: MoodEntry | null) => {
    const strategy = ActivityStrategyFactory.createStrategy(mood);
    
    const filtered = activities
      .filter(activity => strategy.shouldShow(activity, mood))
      .map(activity => ({
        ...activity,
        priority: strategy.getPriority(activity, mood)
      }))
      .sort((a, b) => (b as any).priority - (a as any).priority);

    setFilteredActivities(filtered);
    setFeaturedActivity(filtered[0] || null);
  };

  // Start activity tracking
  const startActivity = async (activityId: string) => {
    const activity = activities.find(a => a.id === activityId);
    if (!activity) return;

    console.log(`Starting activity: ${activity.title}`);
    
    // If VR enabled, redirect to VR room
    if (activity.vrEnabled) {
      window.location.href = '/vr';
    }
  };

  // Complete activity with post-mood tracking
  const completeActivity = async (activityId: string, postMood: MoodEntry) => {
    const activity = activities.find(a => a.id === activityId);
    if (!activity) return;

    console.log(`Completing activity: ${activity.title}`);
    
    // Update current mood
    setCurrentMood(postMood);
    applyActivityStrategy(postMood);
  };

  const handleSetCurrentMood = (mood: MoodEntry | null) => {
    setCurrentMood(mood);
    applyActivityStrategy(mood);
  };

  // Initialize with default activities
  useState(() => {
    applyActivityStrategy(currentMood);
  });

  const value: ActivityContextType = {
    activities,
    currentMood,
    filteredActivities,
    featuredActivity,
    loading,
    setCurrentMood: handleSetCurrentMood,
    startActivity,
    completeActivity
  };

  return (
    <ActivityContext.Provider value={value}>
      {children}
    </ActivityContext.Provider>
  );
};
