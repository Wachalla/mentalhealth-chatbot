import { useEffect, useState } from "react";
import AppLayout from "@/components/AppLayout";
import { Heart, Zap, Calendar, Clock, Brain } from "lucide-react";
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { apiFetch } from "@/lib/api";
import { cn } from "@/lib/utils";

interface ProgressSummaryResponse {
  stats: {
    avg_mood_improvement: number;
    activities_done: number;
    total_sessions: number;
    avg_duration_minutes: number;
  };
  mood_trend: { date: string; moodBefore: number; moodAfter: number }[];
  activity_effectiveness: { name: string; timesCompleted: number; moodImprovement: number }[];
  topics: { name: string; value: number }[];
  insights: { icon: string; text: string; color: string }[];
}

const rangeOptions = [
  { id: "7d", label: "Last 7 Days" },
  { id: "30d", label: "Last 30 Days" },
  { id: "all", label: "All Time" },
] as const;

const chartColors = ["#60a5fa", "#f59e0b", "#a78bfa", "#10b981", "#f472b6"];

const Progress = () => {
  const [rangeKey, setRangeKey] = useState<(typeof rangeOptions)[number]["id"]>("30d");
  const [summary, setSummary] = useState<ProgressSummaryResponse | null>(null);
  const [loading, setLoading] = useState(true);

  const loadSummary = async (selectedRange: string) => {
    setLoading(true);
    try {
      const data = await apiFetch<ProgressSummaryResponse>(`/progress/summary?range_key=${selectedRange}`);
      setSummary(data);
    } catch {
      setSummary({
        stats: {
          avg_mood_improvement: 0,
          activities_done: 0,
          total_sessions: 0,
          avg_duration_minutes: 0,
        },
        mood_trend: [],
        activity_effectiveness: [],
        topics: [],
        insights: [],
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSummary(rangeKey);
  }, [rangeKey]);

  return (
    <AppLayout>
      <div className="p-4 lg:p-6 space-y-6 overflow-auto">
        <div>
          <h2 className="font-display text-2xl font-bold text-foreground">Progress & Analytics</h2>
          <p className="text-muted-foreground text-sm">Track your mental wellness journey with live session data.</p>
        </div>

        <div className="flex gap-2 flex-wrap">
          {rangeOptions.map((option) => (
            <button
              key={option.id}
              type="button"
              onClick={() => setRangeKey(option.id)}
              className={cn(
                "px-4 py-2 rounded-full text-sm font-medium transition-all duration-300",
                rangeKey === option.id
                  ? "bg-primary text-primary-foreground shadow-md"
                  : "bg-card/80 text-foreground hover:bg-card"
              )}
            >
              {option.label}
            </button>
          ))}
        </div>

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="glass-card p-4 transition-all duration-300 hover:-translate-y-0.5 hover:shadow-lg">
            <div className="flex items-center gap-2 text-muted-foreground text-sm mb-1">
              <Heart className="w-4 h-4" />
              Avg Mood Improvement
            </div>
            <p className="text-2xl font-bold text-foreground">+{summary?.stats.avg_mood_improvement ?? 0}</p>
          </div>
          <div className="glass-card p-4 transition-all duration-300 hover:-translate-y-0.5 hover:shadow-lg">
            <div className="flex items-center gap-2 text-muted-foreground text-sm mb-1">
              <Zap className="w-4 h-4" />
              Activities Done
            </div>
            <p className="text-2xl font-bold text-foreground">{summary?.stats.activities_done ?? 0}</p>
          </div>
          <div className="glass-card p-4 transition-all duration-300 hover:-translate-y-0.5 hover:shadow-lg">
            <div className="flex items-center gap-2 text-muted-foreground text-sm mb-1">
              <Calendar className="w-4 h-4" />
              Total Sessions
            </div>
            <p className="text-2xl font-bold text-foreground">{summary?.stats.total_sessions ?? 0}</p>
          </div>
          <div className="glass-card p-4 transition-all duration-300 hover:-translate-y-0.5 hover:shadow-lg">
            <div className="flex items-center gap-2 text-muted-foreground text-sm mb-1">
              <Clock className="w-4 h-4" />
              Avg Duration
            </div>
            <p className="text-2xl font-bold text-foreground">{summary?.stats.avg_duration_minutes ?? 0}m</p>
          </div>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
            {Array.from({ length: 4 }).map((_, index) => (
              <div key={index} className="glass-card p-6 animate-pulse space-y-4">
                <div className="h-5 w-40 rounded bg-muted/50" />
                <div className="h-64 rounded bg-muted/40" />
              </div>
            ))}
          </div>
        ) : (
          <>
            <div className="glass-card p-4 lg:p-6 transition-all duration-300 hover:shadow-lg">
              <h3 className="font-display font-semibold text-lg text-foreground mb-4">Mood Trend</h3>
              {summary?.mood_trend.length ? (
                <ResponsiveContainer width="100%" height={250}>
                  <LineChart data={summary.mood_trend}>
                    <XAxis dataKey="date" stroke="#6b7280" fontSize={12} />
                    <YAxis domain={[0, 10]} stroke="#6b7280" fontSize={12} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "hsl(210 40% 18%)",
                        border: "1px solid hsl(210 30% 25%)",
                        borderRadius: "8px",
                      }}
                    />
                    <Legend />
                    <Line type="monotone" dataKey="moodAfter" stroke="#60a5fa" strokeWidth={2} name="Mood After" dot={{ fill: "#60a5fa" }} />
                    <Line type="monotone" dataKey="moodBefore" stroke="#f59e0b" strokeWidth={2} name="Mood Before" dot={{ fill: "#f59e0b" }} />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-[250px] flex items-center justify-center text-sm text-muted-foreground">
                  Complete an activity or VR session to start building your mood trend.
                </div>
              )}
            </div>

            <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
              <div className="glass-card p-4 lg:p-6 transition-all duration-300 hover:shadow-lg">
                <h3 className="font-display font-semibold text-lg text-foreground mb-4">Activity Effectiveness</h3>
                {summary?.activity_effectiveness.length ? (
                  <ResponsiveContainer width="100%" height={250}>
                    <BarChart data={summary.activity_effectiveness}>
                      <XAxis dataKey="name" stroke="#6b7280" fontSize={12} />
                      <YAxis stroke="#6b7280" fontSize={12} />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: "hsl(210 40% 18%)",
                          border: "1px solid hsl(210 30% 25%)",
                          borderRadius: "8px",
                        }}
                      />
                      <Legend />
                      <Bar dataKey="moodImprovement" fill="#10b981" name="Avg Mood Improvement" />
                      <Bar dataKey="timesCompleted" fill="#60a5fa" name="Times Completed" />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-[250px] flex items-center justify-center text-sm text-muted-foreground">
                    Activity effectiveness appears after you log completed sessions.
                  </div>
                )}
              </div>

              <div className="glass-card p-4 lg:p-6 transition-all duration-300 hover:shadow-lg">
                <h3 className="font-display font-semibold text-lg text-foreground mb-4">Topics Discussed</h3>
                {summary?.topics.length ? (
                  <ResponsiveContainer width="100%" height={200}>
                    <PieChart>
                      <Pie
                        data={summary.topics}
                        cx="50%"
                        cy="50%"
                        innerRadius={50}
                        outerRadius={80}
                        dataKey="value"
                        label={({ name }) => name}
                      >
                        {summary.topics.map((entry, index) => (
                          <Cell key={`cell-${entry.name}`} fill={chartColors[index % chartColors.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="h-[200px] flex items-center justify-center text-sm text-muted-foreground">
                    Topic analytics will appear as you use the chat.
                  </div>
                )}
              </div>
            </div>

            <div className="glass-card p-4 lg:p-6 transition-all duration-300 hover:shadow-lg">
              <div className="flex items-center gap-2 mb-4">
                <Brain className="w-5 h-5 text-primary" />
                <h3 className="font-display font-semibold text-lg text-foreground">Insights & Recommendations</h3>
              </div>
              <div className="space-y-3">
                {summary?.insights.length ? (
                  summary.insights.map((insight, index) => (
                    <div
                      key={`${insight.text}-${index}`}
                      className={cn("p-3 rounded-lg bg-card/50 border border-border/30", insight.color)}
                    >
                      <span className="mr-2">{insight.icon}</span>
                      {insight.text}
                    </div>
                  ))
                ) : (
                  <div className="p-3 rounded-lg bg-card/50 border border-border/30 text-muted-foreground">
                    Your insights will become more useful after a few completed chats, activities, or VR sessions.
                  </div>
                )}
              </div>
            </div>
          </>
        )}
      </div>
    </AppLayout>
  );
};

export default Progress;