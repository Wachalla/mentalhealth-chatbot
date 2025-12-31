import AppLayout from "@/components/AppLayout";
import { Heart, Zap, Calendar, Clock, Brain } from "lucide-react";
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from "recharts";

const moodData = [
  { date: "Dec 4", moodAfter: 8, moodBefore: 5 },
  { date: "Dec 5", moodAfter: 7, moodBefore: 3 },
  { date: "Dec 6", moodAfter: 7, moodBefore: 6 },
  { date: "Dec 7", moodAfter: 8, moodBefore: 5 },
  { date: "Dec 8", moodAfter: 7, moodBefore: 3 },
  { date: "Dec 9", moodAfter: 7, moodBefore: 7 },
  { date: "Dec 10", moodAfter: 6, moodBefore: 5 },
  { date: "Dec 11", moodAfter: 7, moodBefore: 5 },
];

const activityData = [
  { name: "Breathing Exercise", timesCompleted: 20, moodImprovement: 3 },
  { name: "Journaling", timesCompleted: 10, moodImprovement: 3 },
];

const topicsData = [
  { name: "anxiety", value: 60, color: "#60a5fa" },
  { name: "stress", value: 40, color: "#f59e0b" },
];

const insights = [
  { icon: "✓", text: "Your mood consistently improves after therapy sessions. Keep up the great work!", color: "text-calm-sage" },
  { icon: "💡", text: '"Breathing Exercise" seems to be most effective for you. Consider doing it more frequently.', color: "text-accent" },
  { icon: "📊", text: "You've completed 30 sessions in this period. Consistency is key to progress!", color: "text-primary" },
];

const Progress = () => {
  return (
    <AppLayout>
      <div className="p-4 lg:p-6 space-y-6 overflow-auto">
        <div>
          <h2 className="font-display text-2xl font-bold text-foreground">Progress & Analytics</h2>
          <p className="text-muted-foreground text-sm">Track your mental wellness journey</p>
        </div>

        {/* Time Filter */}
        <div className="flex gap-2">
          <button className="px-4 py-2 rounded-full bg-primary text-primary-foreground text-sm font-medium">
            Last 7 Days
          </button>
          <button className="px-4 py-2 rounded-full bg-card/80 text-foreground text-sm font-medium hover:bg-card transition-colors">
            Last 30 Days
          </button>
          <button className="px-4 py-2 rounded-full bg-card/80 text-foreground text-sm font-medium hover:bg-card transition-colors">
            All Time
          </button>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="glass-card p-4">
            <div className="flex items-center gap-2 text-muted-foreground text-sm mb-1">
              <Heart className="w-4 h-4" />
              Avg Mood Improvement
            </div>
            <p className="text-2xl font-bold text-foreground">+2.1</p>
          </div>
          <div className="glass-card p-4">
            <div className="flex items-center gap-2 text-muted-foreground text-sm mb-1">
              <Zap className="w-4 h-4" />
              Activities Done
            </div>
            <p className="text-2xl font-bold text-foreground">5</p>
          </div>
          <div className="glass-card p-4">
            <div className="flex items-center gap-2 text-muted-foreground text-sm mb-1">
              <Calendar className="w-4 h-4" />
              Total Sessions
            </div>
            <p className="text-2xl font-bold text-foreground">8</p>
          </div>
          <div className="glass-card p-4">
            <div className="flex items-center gap-2 text-muted-foreground text-sm mb-1">
              <Clock className="w-4 h-4" />
              Avg Duration
            </div>
            <p className="text-2xl font-bold text-foreground">20m</p>
          </div>
        </div>

        {/* Mood Trend Chart */}
        <div className="glass-card p-4 lg:p-6">
          <h3 className="font-display font-semibold text-lg text-foreground mb-4">Mood Trend</h3>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={moodData}>
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
        </div>

        {/* Activity Effectiveness */}
        <div className="glass-card p-4 lg:p-6">
          <h3 className="font-display font-semibold text-lg text-foreground mb-4">Activity Effectiveness</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={activityData}>
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
        </div>

        {/* Topics Discussed */}
        <div className="glass-card p-4 lg:p-6">
          <h3 className="font-display font-semibold text-lg text-foreground mb-4">Topics Discussed</h3>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie
                data={topicsData}
                cx="50%"
                cy="50%"
                innerRadius={50}
                outerRadius={80}
                dataKey="value"
                label={({ name }) => name}
              >
                {topicsData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Insights & Recommendations */}
        <div className="glass-card p-4 lg:p-6">
          <div className="flex items-center gap-2 mb-4">
            <Brain className="w-5 h-5 text-primary" />
            <h3 className="font-display font-semibold text-lg text-foreground">Insights & Recommendations</h3>
          </div>
          <div className="space-y-3">
            {insights.map((insight, index) => (
              <div
                key={index}
                className={`p-3 rounded-lg bg-card/50 border border-border/30 ${insight.color}`}
              >
                <span className="mr-2">{insight.icon}</span>
                {insight.text}
              </div>
            ))}
          </div>
        </div>
      </div>
    </AppLayout>
  );
};

export default Progress;