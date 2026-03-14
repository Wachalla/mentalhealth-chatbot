import { useEffect, useMemo, useState } from "react";
import AppLayout from "@/components/AppLayout";
import { Brain, CheckCircle2, Clock3, Play, Sparkles } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { SAMPLE_ACTIVITIES, type Activity } from "@/types/activities";
import { apiFetch } from "@/lib/api";
import { cn } from "@/lib/utils";
import { useToast } from "@/hooks/use-toast";

interface ActivitySummaryResponse {
  today_completed: number;
  total_completed: number;
  activity_stats: {
    activity_id: string;
    title: string;
    completion_count: number;
    last_completed_at: string | null;
  }[];
}

interface ActivitySessionResponse {
  id: string;
  status: string;
}

const vrModeMap: Record<string, "box" | "deep" | "mindful"> = {
  "breathing-4-7-8": "box",
  "mindfulness-body-scan": "mindful",
};

const categoryLabelMap: Record<string, string> = {
  breathing: "Breathing",
  grounding: "Grounding",
  mindfulness: "Mindfulness",
};

const Activities = () => {
  const [summary, setSummary] = useState<ActivitySummaryResponse | null>(null);
  const [activeSessions, setActiveSessions] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [busyActivityId, setBusyActivityId] = useState<string | null>(null);
  const navigate = useNavigate();
  const { toast } = useToast();

  const activityCounts = useMemo(() => {
    return (summary?.activity_stats || []).reduce<Record<string, number>>((acc, stat) => {
      acc[stat.activity_id] = stat.completion_count;
      return acc;
    }, {});
  }, [summary]);

  const loadSummary = async () => {
    try {
      const data = await apiFetch<ActivitySummaryResponse>("/activities/summary");
      setSummary(data);
    } catch (error) {
      toast({
        title: "Unable to load activities",
        description: error instanceof Error ? error.message : "Please try again shortly.",
        variant: "destructive",
      });
      setSummary({ today_completed: 0, total_completed: 0, activity_stats: [] });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSummary();
  }, []);

  const handleStart = async (activity: Activity) => {
    setBusyActivityId(activity.id);

    try {
      const result = await apiFetch<ActivitySessionResponse>("/activities/start", {
        method: "POST",
        body: JSON.stringify({
          activity_id: activity.id,
          title: activity.title,
          category: activity.category,
          duration_minutes: activity.duration,
          recommended_source: "activities_page",
        }),
      });

      setActiveSessions((prev) => ({ ...prev, [activity.id]: result.id }));

      if (activity.vrEnabled) {
        navigate("/vr", {
          state: {
            mode: vrModeMap[activity.id] || "mindful",
            activityId: activity.id,
            activitySessionId: result.id,
            recommendedSource: "activities_page",
          },
        });
        return;
      }

      toast({
        title: "Activity started",
        description: `${activity.title} is ready when you are. Mark it complete when finished.`,
      });
    } catch (error) {
      toast({
        title: "Unable to start activity",
        description: error instanceof Error ? error.message : "Please try again.",
        variant: "destructive",
      });
    } finally {
      setBusyActivityId(null);
    }
  };

  const handleComplete = async (activity: Activity) => {
    setBusyActivityId(activity.id);

    try {
      await apiFetch<ActivitySessionResponse>("/activities/complete", {
        method: "POST",
        body: JSON.stringify({
          session_id: activeSessions[activity.id] || null,
          activity_id: activity.id,
          title: activity.title,
          category: activity.category,
          duration_minutes: activity.duration,
          recommended_source: "activities_page",
        }),
      });

      setActiveSessions((prev) => {
        const next = { ...prev };
        delete next[activity.id];
        return next;
      });
      await loadSummary();

      toast({
        title: "Activity completed",
        description: `Nice work finishing ${activity.title}.`,
      });
    } catch (error) {
      toast({
        title: "Unable to complete activity",
        description: error instanceof Error ? error.message : "Please try again.",
        variant: "destructive",
      });
    } finally {
      setBusyActivityId(null);
    }
  };

  return (
    <AppLayout>
      <div className="p-4 lg:p-6 space-y-6 overflow-auto">
        <div className="flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
          <div>
            <h2 className="font-display text-2xl font-bold text-foreground">Therapy Activities</h2>
            <p className="text-muted-foreground text-sm">Evidence-based exercises that connect directly to your progress tracking.</p>
          </div>
          <div className="inline-flex items-center gap-2 rounded-full bg-primary/10 px-3 py-2 text-sm text-primary">
            <Sparkles className="w-4 h-4" />
            Tracked in your analytics automatically
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="glass-card p-4 transition-all duration-300 hover:-translate-y-0.5 hover:shadow-lg">
            <p className="text-sm text-muted-foreground mb-1">Completed today</p>
            <p className="text-3xl font-bold text-foreground">{summary?.today_completed ?? 0}</p>
          </div>
          <div className="glass-card p-4 transition-all duration-300 hover:-translate-y-0.5 hover:shadow-lg">
            <p className="text-sm text-muted-foreground mb-1">Completed overall</p>
            <p className="text-3xl font-bold text-foreground">{summary?.total_completed ?? 0}</p>
          </div>
          <div className="glass-card p-4 transition-all duration-300 hover:-translate-y-0.5 hover:shadow-lg">
            <p className="text-sm text-muted-foreground mb-1">Most used</p>
            <p className="text-lg font-semibold text-foreground">
              {summary?.activity_stats?.[0]?.title || "No activity data yet"}
            </p>
          </div>
        </div>

        <div className="glass-card p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-foreground font-medium">Activity momentum</span>
            <span className="text-muted-foreground text-sm">
              {summary?.today_completed ?? 0} completed today
            </span>
          </div>
          <div className="w-full bg-muted rounded-full h-2 overflow-hidden">
            <div
              className="bg-primary h-2 rounded-full transition-all duration-500"
              style={{ width: `${Math.min(((summary?.today_completed ?? 0) / Math.max(SAMPLE_ACTIVITIES.length, 1)) * 100, 100)}%` }}
            />
          </div>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {Array.from({ length: 3 }).map((_, index) => (
              <div key={index} className="glass-card p-5 animate-pulse space-y-4">
                <div className="h-5 w-1/2 rounded bg-muted/50" />
                <div className="h-4 w-full rounded bg-muted/40" />
                <div className="h-4 w-3/4 rounded bg-muted/40" />
                <div className="h-10 w-full rounded-xl bg-muted/50" />
              </div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {SAMPLE_ACTIVITIES.map((activity) => {
              const isBusy = busyActivityId === activity.id;
              const hasActiveSession = Boolean(activeSessions[activity.id]);
              const completionCount = activityCounts[activity.id] || 0;

              return (
                <div
                  key={activity.id}
                  className="glass-card p-5 transition-all duration-300 hover:-translate-y-1 hover:shadow-xl hover:shadow-primary/10"
                >
                  <div className="flex items-start justify-between gap-4 mb-4">
                    <div>
                      <div className="inline-flex items-center gap-2 rounded-full bg-primary/10 px-3 py-1 text-xs text-primary mb-3">
                        <Brain className="w-3.5 h-3.5" />
                        {categoryLabelMap[activity.category] || activity.category}
                      </div>
                      <h3 className="font-display text-lg font-semibold text-foreground">{activity.title}</h3>
                    </div>
                    {activity.vrEnabled && (
                      <span className="rounded-full bg-purple-500/15 px-3 py-1 text-xs text-purple-300 border border-purple-400/20">
                        VR available
                      </span>
                    )}
                  </div>

                  <p className="text-sm text-muted-foreground leading-relaxed mb-4">{activity.description}</p>

                  <div className="flex flex-wrap gap-2 mb-4">
                    {activity.therapeuticGoals.map((goal) => (
                      <span key={goal} className="rounded-full bg-background/80 px-2.5 py-1 text-xs text-muted-foreground border border-border/50">
                        {goal.replace(/-/g, " ")}
                      </span>
                    ))}
                  </div>

                  <div className="flex items-center justify-between text-sm text-muted-foreground mb-4">
                    <div className="inline-flex items-center gap-2">
                      <Clock3 className="w-4 h-4" />
                      {activity.duration} minutes
                    </div>
                    <div className="inline-flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4" />
                      {completionCount} completions
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <button
                      type="button"
                      onClick={() => handleStart(activity)}
                      disabled={isBusy}
                      className={cn(
                        "inline-flex items-center justify-center gap-2 rounded-xl px-4 py-3 text-sm font-medium transition-all duration-300",
                        "bg-primary text-primary-foreground hover:scale-[1.01] hover:bg-primary/90 disabled:opacity-60"
                      )}
                    >
                      <Play className="w-4 h-4" />
                      {isBusy ? "Working..." : activity.vrEnabled ? "Start in VR" : "Start"}
                    </button>

                    <button
                      type="button"
                      onClick={() => handleComplete(activity)}
                      disabled={isBusy}
                      className={cn(
                        "inline-flex items-center justify-center gap-2 rounded-xl px-4 py-3 text-sm font-medium transition-all duration-300",
                        hasActiveSession
                          ? "bg-emerald-500/15 text-emerald-300 border border-emerald-400/20 hover:bg-emerald-500/25"
                          : "bg-card/80 text-foreground border border-border/50 hover:border-primary/30 hover:text-primary",
                        "disabled:opacity-60"
                      )}
                    >
                      <CheckCircle2 className="w-4 h-4" />
                      {hasActiveSession ? "Complete" : "Log complete"}
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </AppLayout>
  );
};

export default Activities;