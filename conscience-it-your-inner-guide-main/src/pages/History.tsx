import { useEffect, useMemo, useState } from "react";
import AppLayout from "@/components/AppLayout";
import { MessageCircle, Calendar, Clock, ChevronDown, ShieldAlert } from "lucide-react";
import { apiFetch } from "@/lib/api";

interface HistorySession {
  id: string;
  summary: string;
  primary_topic: string;
  safety_level: string;
  therapeutic_approach: string;
  techniques_used: string[];
  started_at: string;
  updated_at: string;
  message_count: number;
  preview: { id: string; content: string; role: string; created_at: string }[];
}

interface HistoryResponse {
  sessions: HistorySession[];
}

const History = () => {
  const [sessions, setSessions] = useState<HistorySession[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedSessionId, setExpandedSessionId] = useState<string | null>(null);

  const groupedCountLabel = useMemo(() => {
    if (!sessions.length) return "No saved sessions yet";
    return `${sessions.length} tracked conversation session${sessions.length === 1 ? "" : "s"}`;
  }, [sessions]);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      const data = await apiFetch<HistoryResponse>("/history/sessions?limit=20");
      setSessions(data.sessions);
    } catch {
      setSessions([]);
    }
    setLoading(false);
  };

  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center h-full">
          <p className="text-muted-foreground">Loading history...</p>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="p-4 lg:p-6 space-y-6 overflow-auto">
        <div>
          <h2 className="font-display text-2xl font-bold text-foreground">Chat History</h2>
          <p className="text-muted-foreground text-sm">{groupedCountLabel}</p>
        </div>

        <div className="space-y-4">
          {sessions.map((session) => {
            const isExpanded = expandedSessionId === session.id;

            return (
            <div key={session.id} className="glass-card p-4 transition-all duration-300 hover:shadow-lg hover:shadow-primary/10">
              <button
                type="button"
                onClick={() => setExpandedSessionId(isExpanded ? null : session.id)}
                className="w-full text-left"
              >
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 rounded-full bg-primary/20 border border-primary/30 flex items-center justify-center flex-shrink-0">
                  <MessageCircle className="w-5 h-5 text-primary" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex flex-wrap items-center gap-3 mb-2">
                    <div className="flex items-center gap-1 text-sm text-muted-foreground">
                      <Calendar className="w-4 h-4" />
                      {new Date(session.updated_at).toLocaleDateString("en-US", {
                        year: "numeric",
                        month: "long",
                        day: "numeric",
                      })}
                    </div>
                    <div className="flex items-center gap-1 text-sm text-muted-foreground">
                      <Clock className="w-4 h-4" />
                      {session.message_count} messages
                    </div>
                    <span className="rounded-full bg-card/80 px-2.5 py-1 text-xs text-muted-foreground border border-border/50">
                      {session.primary_topic.replace(/_/g, " ")}
                    </span>
                    {session.safety_level !== "low" && (
                      <span className="inline-flex items-center gap-1 rounded-full bg-red-500/10 px-2.5 py-1 text-xs text-red-300 border border-red-400/20">
                        <ShieldAlert className="w-3.5 h-3.5" />
                        {session.safety_level} support
                      </span>
                    )}
                  </div>
                  <h3 className="font-medium text-foreground mb-2 line-clamp-2">{session.summary}</h3>
                  <div className="space-y-2">
                    {session.preview.slice(0, isExpanded ? session.preview.length : 3).map((msg) => (
                      <p key={msg.id} className="text-sm text-foreground/80 line-clamp-1">
                        <span className="text-primary font-medium">
                          {msg.role === "user" ? "You: " : "AI: "}
                        </span>
                        {msg.content}
                      </p>
                    ))}
                    {!isExpanded && session.preview.length > 3 && (
                      <p className="text-xs text-muted-foreground">
                        +{session.preview.length - 3} more preview messages
                      </p>
                    )}
                  </div>
                  <div className="mt-4 flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
                    <span className="rounded-full bg-primary/10 px-2 py-1 text-primary">
                      {session.therapeutic_approach.replace(/_/g, " ")}
                    </span>
                    {session.techniques_used.slice(0, 3).map((technique) => (
                      <span key={technique} className="rounded-full bg-muted px-2 py-1">
                        {technique}
                      </span>
                    ))}
                  </div>
                </div>
                <ChevronDown className={`w-5 h-5 text-muted-foreground transition-transform duration-300 ${isExpanded ? "rotate-180" : "rotate-0"}`} />
              </div>
              </button>
            </div>
          )})}
        </div>

        {sessions.length === 0 && (
          <div className="glass-card p-8 text-center">
            <MessageCircle className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <p className="text-muted-foreground">No chat history yet</p>
            <p className="text-sm text-muted-foreground">Start a conversation to see your history here</p>
          </div>
        )}
      </div>
    </AppLayout>
  );
};

export default History;