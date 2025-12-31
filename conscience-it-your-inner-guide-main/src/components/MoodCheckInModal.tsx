import React, { useState } from 'react';
import { X, Heart, Brain, Frown, Meh, Smile } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { MoodEntry } from '@/types/activities';

interface MoodCheckInModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (mood: MoodEntry) => void;
  title?: string;
  description?: string;
}

const MoodCheckInModal: React.FC<MoodCheckInModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  title = "How are you feeling?",
  description = "Select your current emotional state"
}) => {
  const [valence, setValence] = useState(0); // -1 to 1 (negative to positive)
  const [arousal, setArousal] = useState(0); // -1 to 1 (calm to excited)
  const [notes, setNotes] = useState('');

  if (!isOpen) return null;

  const handleSubmit = () => {
    const mood: MoodEntry = {
      id: Date.now().toString(),
      user_id: 'current-user', // This would come from auth context
      valence,
      arousal,
      timestamp: new Date(),
      notes: notes.trim() || undefined
    };
    onSubmit(mood);
    onClose();
    // Reset form
    setValence(0);
    setArousal(0);
    setNotes('');
  };

  const getMoodEmoji = (valence: number, arousal: number) => {
    if (valence < -0.5 && arousal < -0.5) return <Frown className="w-8 h-8" />;
    if (valence < -0.5 && arousal > 0.5) return <Heart className="w-8 h-8" />;
    if (Math.abs(valence) < 0.3 && Math.abs(arousal) < 0.3) return <Meh className="w-8 h-8" />;
    if (valence > 0.5) return <Smile className="w-8 h-8" />;
    return <Brain className="w-8 h-8" />;
  };

  const getMoodLabel = (valence: number, arousal: number) => {
    if (valence < -0.5 && arousal < -0.5) return "Sad & Tired";
    if (valence < -0.5 && arousal > 0.5) return "Anxious & Worried";
    if (valence < -0.5) return "Feeling Down";
    if (valence > 0.5 && arousal > 0.5) return "Excited & Happy";
    if (valence > 0.5 && arousal < -0.5) return "Calm & Content";
    if (valence > 0.5) return "Feeling Good";
    if (arousal > 0.5) return "High Energy";
    if (arousal < -0.5) return "Low Energy";
    return "Neutral";
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-md backdrop-blur-md bg-white/10 border border-white/20">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
          <div>
            <CardTitle className="text-foreground">{title}</CardTitle>
            <p className="text-sm text-muted-foreground mt-1">{description}</p>
          </div>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="w-4 h-4" />
          </Button>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Mood Preview */}
          <div className="text-center">
            <div className="flex justify-center mb-2">
              {getMoodEmoji(valence, arousal)}
            </div>
            <p className="text-lg font-medium text-foreground">
              {getMoodLabel(valence, arousal)}
            </p>
          </div>

          {/* Valence Slider (Negative to Positive) */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm text-muted-foreground">
              <span>Negative</span>
              <span>Positive</span>
            </div>
            <input
              type="range"
              min="-1"
              max="1"
              step="0.1"
              value={valence}
              onChange={(e) => setValence(parseFloat(e.target.value))}
              className="w-full h-2 bg-muted rounded-lg appearance-none cursor-pointer"
            />
          </div>

          {/* Arousal Slider (Calm to Excited) */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm text-muted-foreground">
              <span>Calm</span>
              <span>Excited</span>
            </div>
            <input
              type="range"
              min="-1"
              max="1"
              step="0.1"
              value={arousal}
              onChange={(e) => setArousal(parseFloat(e.target.value))}
              className="w-full h-2 bg-muted rounded-lg appearance-none cursor-pointer"
            />
          </div>

          {/* Notes */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-foreground">
              Notes (optional)
            </label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="What's on your mind?"
              className="w-full p-3 bg-background/50 border border-border/50 rounded-lg text-foreground placeholder-muted-foreground resize-none"
              rows={3}
            />
          </div>

          {/* Submit Button */}
          <Button onClick={handleSubmit} className="w-full">
            Save Mood Check-in
          </Button>
        </CardContent>
      </Card>
    </div>
  );
};

export default MoodCheckInModal;
