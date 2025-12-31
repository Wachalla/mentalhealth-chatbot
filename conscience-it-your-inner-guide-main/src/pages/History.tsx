import { useEffect, useState } from "react";
import Layout from "@/VRCalmRoom.jsx/Layout";
import { MessageCircle, Calendar, Clock, Trash2 } from "lucide-react";
import { supabase } from "@/integrations/supabase/client";
import { useAuth } from "@/contexts/AuthContext";

interface ChatSession {
  date: string;
  messages: { id: string; content: string; role: string; created_at: string }[];
}

const History = () => {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();

  useEffect(() => {
    if (user) {
      loadHistory();
    }
  }, [user]);

  const loadHistory = async () => {
    const { data, error } = await supabase
      .from("chat_messages")
      .select("*")
      .eq("user_id", user?.id)
      .order("created_at", { ascending: false });

    if (data) {
      // Group messages by date
      const grouped: { [key: string]: any[] } = {};
      data.forEach((msg) => {
        const date = new Date(msg.created_at).toLocaleDateString("en-US", {
          year: "numeric",
          month: "long",
          day: "numeric",
        });
        if (!grouped[date]) grouped[date] = [];
        grouped[date].push(msg);
      });

      setSessions(
        Object.entries(grouped).map(([date, messages]) => ({ date, messages }))
      );
    }
    setLoading(false);
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-full">
          <p className="text-muted-foreground">Loading history...</p>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="p-4 lg:p-6 space-y-6 overflow-auto">
        <div>
          <h2 className="font-display text-2xl font-bold text-foreground">Chat History</h2>
          <p className="text-muted-foreground text-sm">Review your past conversations</p>
        </div>

        <div className="space-y-4">
          {sessions.map((session, idx) => (
            <div key={idx} className="glass-card p-4">
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 rounded-full bg-primary/20 border border-primary/30 flex items-center justify-center flex-shrink-0">
                  <MessageCircle className="w-5 h-5 text-primary" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-4 mb-2">
                    <div className="flex items-center gap-1 text-sm text-muted-foreground">
                      <Calendar className="w-4 h-4" />
                      {session.date}
                    </div>
                    <div className="flex items-center gap-1 text-sm text-muted-foreground">
                      <Clock className="w-4 h-4" />
                      {session.messages.length} messages
                    </div>
                  </div>
                  <div className="space-y-2">
                    {session.messages.slice(0, 3).map((msg) => (
                      <p key={msg.id} className="text-sm text-foreground/80 line-clamp-1">
                        <span className="text-primary font-medium">
                          {msg.role === "user" ? "You: " : "AI: "}
                        </span>
                        {msg.content}
                      </p>
                    ))}
                    {session.messages.length > 3 && (
                      <p className="text-xs text-muted-foreground">
                        +{session.messages.length - 3} more messages
                      </p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {sessions.length === 0 && (
          <div className="glass-card p-8 text-center">
            <MessageCircle className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <p className="text-muted-foreground">No chat history yet</p>
            <p className="text-sm text-muted-foreground">Start a conversation to see your history here</p>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default History;