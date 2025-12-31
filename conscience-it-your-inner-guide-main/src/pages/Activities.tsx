import { useState } from "react";
import Layout from "@/VRCalmRoom.jsx/Layout";
import { Wind, Heart, Footprints, Moon, Sun, Target, Calendar, Lightbulb, Brain } from "lucide-react";
import { useNavigate } from "react-router-dom";

const activities = [
  {
    id: 1,
    title: "5-Minute Breathing Exercise",
    description: "Practice deep breathing to reduce anxiety and promote calmness",
    duration: "5 min",
    icon: Wind,
    tags: ["Reduces stress", "Improves focus"],
    completed: false,
  },
  {
    id: 2,
    title: "Gratitude Journaling",
    description: "Write down three things you're grateful for today",
    duration: "10 min",
    icon: Heart,
    tags: ["Positive mindset", "Self-awareness"],
    completed: false,
  },
  {
    id: 3,
    title: "Mindful Walk",
    description: "Take a walk while focusing on your surroundings and sensations",
    duration: "15 min",
    icon: Footprints,
    tags: ["Physical health", "Mental clarity"],
    completed: false,
  },
  {
    id: 4,
    title: "Evening Reflection",
    description: "Reflect on your day and identify moments of growth",
    duration: "10 min",
    icon: Moon,
    tags: ["Self-awareness", "Growth mindset"],
    completed: false,
  },
  {
    id: 5,
    title: "Morning Affirmations",
    description: "Start your day with positive self-talk and intentions",
    duration: "5 min",
    icon: Sun,
    tags: ["Confidence", "Positive outlook"],
    completed: false,
  },
  {
    id: 6,
    title: "Body Scan Meditation",
    description: "Progressive relaxation technique to release tension",
    duration: "15 min",
    icon: Target,
    tags: ["Relaxation", "Body awareness"],
    completed: false,
  },
];

const Activities = () => {
  const [activeTab, setActiveTab] = useState<"activities" | "schedule">("activities");
  const [completedActivities, setCompletedActivities] = useState<number[]>([]);
  const navigate = useNavigate();

  const handleComplete = (id: number) => {
    if (completedActivities.includes(id)) {
      setCompletedActivities(completedActivities.filter((actId) => actId !== id));
    } else {
      setCompletedActivities([...completedActivities, id]);
    }
  };

  return (
    <Layout>
      <div className="p-4 lg:p-6 space-y-6 overflow-auto">
        <div>
          <h2 className="font-display text-2xl font-bold text-foreground">Therapy Activities</h2>
          <p className="text-muted-foreground text-sm">AI-curated activities and schedules for your wellness journey</p>
        </div>

        {/* Breathing Exercises Section */}
        <div className="glass-card p-4 lg:p-6">
          <div className="flex items-center gap-2 mb-4">
            <Wind className="w-5 h-5 text-primary" />
            <h3 className="font-display font-semibold text-lg text-foreground">Breathing Exercises</h3>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Deep Diaphragmatic */}
            <div className="bg-gradient-to-br from-green-50/20 to-emerald-50/20 border border-green-200/30 rounded-xl p-6 hover:shadow-lg transition-all duration-300">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center">
                  <Wind className="w-6 h-6 text-green-600" />
                </div>
                <div>
                  <h4 className="font-display font-semibold text-foreground">Deep Diaphragmatic</h4>
                  <p className="text-sm text-muted-foreground">Relaxing</p>
                </div>
              </div>
              
              <p className="text-sm text-muted-foreground mb-4">
                Sit comfortably. Breathe deeply through nose, belly expands. Pause. Exhale slowly.
              </p>
              
              <button
                onClick={() => navigate('/vr', { state: { mode: 'deep' } })}
                className="w-full bg-green-600 hover:bg-green-700 text-white font-medium py-3 px-4 rounded-lg transition-colors duration-200 flex items-center justify-center gap-2"
              >
                <Wind className="w-4 h-4" />
                Start Session
              </button>
            </div>

            {/* Box Breathing */}
            <div className="bg-gradient-to-br from-blue-50/20 to-cyan-50/20 border border-blue-200/30 rounded-xl p-6 hover:shadow-lg transition-all duration-300">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center">
                  <Target className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <h4 className="font-display font-semibold text-foreground">Box Breathing</h4>
                  <p className="text-sm text-muted-foreground">Focusing</p>
                </div>
              </div>
              
              <p className="text-sm text-muted-foreground mb-4">
                Inhale 4s, Hold 4s, Exhale 4s, Hold 4s. Centers your focus.
              </p>
              
              <button
                onClick={() => navigate('/vr', { state: { mode: 'box' } })}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4 rounded-lg transition-colors duration-200 flex items-center justify-center gap-2"
              >
                <Target className="w-4 h-4" />
                Start Session
              </button>
            </div>

            {/* Mindful Breathing */}
            <div className="bg-gradient-to-br from-purple-50/20 to-pink-50/20 border border-purple-200/30 rounded-xl p-6 hover:shadow-lg transition-all duration-300">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 rounded-full bg-purple-100 flex items-center justify-center">
                  <Brain className="w-6 h-6 text-purple-600" />
                </div>
                <div>
                  <h4 className="font-display font-semibold text-foreground">Mindful Breathing</h4>
                  <p className="text-sm text-muted-foreground">Observing</p>
                </div>
              </div>
              
              <p className="text-sm text-muted-foreground mb-4">
                Find a comfortable seat. Observe natural breath. If mind wanders, gently guide focus back.
              </p>
              
              <button
                onClick={() => navigate('/vr', { state: { mode: 'mindful' } })}
                className="w-full bg-purple-600 hover:bg-purple-700 text-white font-medium py-3 px-4 rounded-lg transition-colors duration-200 flex items-center justify-center gap-2"
              >
                <Brain className="w-4 h-4" />
                Start Session
              </button>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-2">
          <button
            onClick={() => setActiveTab("activities")}
            className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-colors ${
              activeTab === "activities"
                ? "bg-primary text-primary-foreground"
                : "bg-card/80 text-foreground hover:bg-card"
            }`}
          >
            <Lightbulb className="w-4 h-4" />
            Activities
          </button>
          <button
            onClick={() => setActiveTab("schedule")}
            className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-colors ${
              activeTab === "schedule"
                ? "bg-primary text-primary-foreground"
                : "bg-card/80 text-foreground hover:bg-card"
            }`}
          >
            <Calendar className="w-4 h-4" />
            Daily Schedule
          </button>
        </div>

        {/* Progress */}
        <div className="glass-card p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-foreground font-medium">Today's Progress</span>
            <span className="text-muted-foreground text-sm">
              {completedActivities.length} / {activities.length} completed
            </span>
          </div>
          <div className="w-full bg-muted rounded-full h-2">
            <div
              className="bg-primary h-2 rounded-full transition-all duration-300"
              style={{ width: `${(completedActivities.length / activities.length) * 100}%` }}
            />
          </div>
        </div>

        {/* Activities Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {activities.map((activity) => {
            const Icon = activity.icon;
            const isCompleted = completedActivities.includes(activity.id);

            return (
              <div key={activity.id} className="glass-card p-4">
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 rounded-xl bg-primary/20 border border-primary/30 flex items-center justify-center flex-shrink-0">
                    <Icon className="w-6 h-6 text-primary" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <h3 className="font-semibold text-foreground">{activity.title}</h3>
                      <span className="text-xs text-muted-foreground bg-muted/50 px-2 py-1 rounded-full">
                        {activity.duration}
                      </span>
                    </div>
                    <p className="text-sm text-muted-foreground mb-3">{activity.description}</p>
                    <div className="flex flex-wrap gap-2 mb-3">
                      {activity.tags.map((tag) => (
                        <span
                          key={tag}
                          className="text-xs px-2 py-1 rounded-full bg-card border border-border/50 text-muted-foreground"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                    <button
                      onClick={() => handleComplete(activity.id)}
                      className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                        isCompleted
                          ? "bg-calm-sage/20 text-calm-sage"
                          : "bg-primary text-primary-foreground hover:bg-primary/90"
                      }`}
                    >
                      {isCompleted ? "✓ Completed" : "Mark as Complete"}
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </Layout>
  );
};

export default Activities;