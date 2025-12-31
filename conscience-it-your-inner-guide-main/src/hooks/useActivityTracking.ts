import { useState, useCallback } from 'react';
import { useActivities } from '@/contexts/ActivityContext';
import { MoodEntry } from '@/types/activities';

export const useActivityTracking = () => {
  const { currentMood, setCurrentMood, startActivity, completeActivity } = useActivities();
  const [showPreModal, setShowPreModal] = useState(false);
  const [showPostModal, setShowPostModal] = useState(false);
  const [currentActivityId, setCurrentActivityId] = useState<string | null>(null);

  const handleStartActivity = useCallback(async (activityId: string) => {
    // If no current mood, show pre-activity check-in
    if (!currentMood) {
      setCurrentActivityId(activityId);
      setShowPreModal(true);
      return;
    }

    // Start the activity
    await startActivity(activityId);
    setCurrentActivityId(activityId);
  }, [currentMood, startActivity]);

  const handlePreActivitySubmit = useCallback(async (mood: MoodEntry) => {
    // Set current mood and start activity
    setCurrentMood(mood);
    setShowPreModal(false);
    
    if (currentActivityId) {
      await startActivity(currentActivityId);
    }
  }, [currentActivityId, setCurrentMood, startActivity]);

  const handleCompleteActivity = useCallback(async () => {
    // Show post-activity check-in
    setShowPostModal(true);
  }, []);

  const handlePostActivitySubmit = useCallback(async (mood: MoodEntry) => {
    // Complete activity with post-mood
    if (currentActivityId) {
      await completeActivity(currentActivityId, mood);
    }
    setShowPostModal(false);
    setCurrentActivityId(null);
  }, [currentActivityId, completeActivity]);

  const cancelPreCheckIn = useCallback(() => {
    setShowPreModal(false);
    setCurrentActivityId(null);
  }, []);

  const cancelPostCheckIn = useCallback(() => {
    setShowPostModal(false);
    setCurrentActivityId(null);
  }, []);

  return {
    showPreModal,
    showPostModal,
    currentActivityId,
    handleStartActivity,
    handlePreActivitySubmit,
    handleCompleteActivity,
    handlePostActivitySubmit,
    cancelPreCheckIn,
    cancelPostCheckIn
  };
};
