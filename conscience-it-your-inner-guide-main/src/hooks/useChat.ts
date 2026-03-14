import { v4 as uuidv4 } from "uuid";
import { useState, useCallback, useEffect } from "react";
import { toast } from "sonner";
import { supabase } from "@/integrations/supabase/client";
import { apiFetch } from "@/lib/api";

export interface Message {
  id: string;
  content: string;
  role: "user" | "assistant";
  timestamp: Date;
}

export interface AIPersonality {
  id: string;
  name: string;
  systemPrompt: string;
  model: string;
  temperature: number;
}

const AI_PERSONALITIES: AIPersonality[] = [
  {
    id: "empathetic",
    name: "Empathetic Companion",
    systemPrompt: "You are a warm, empathetic AI companion focused on mental wellness. Provide supportive, validating responses with practical coping strategies. Use gentle language and always prioritize the user's wellbeing. Include specific techniques like breathing exercises, grounding methods, or self-care suggestions when relevant.",
    model: "gpt-3.5-turbo",
    temperature: 0.8
  },
  {
    id: "professional",
    name: "Professional Therapist",
    systemPrompt: "You are a professional mental health counselor. Provide evidence-based therapeutic responses using CBT, mindfulness, and other proven techniques. Maintain a professional yet caring tone. Ask thoughtful questions that encourage self-reflection and offer structured guidance.",
    model: "gpt-4",
    temperature: 0.7
  },
  {
    id: "mindfulness",
    name: "Mindfulness Guide",
    systemPrompt: "You are a mindfulness and meditation guide. Focus on present-moment awareness, acceptance, and non-judgmental observation. Include specific mindfulness exercises, breathing techniques, and meditation practices in your responses. Use calming, centered language.",
    model: "gpt-3.5-turbo",
    temperature: 0.6
  }
];

interface ChatHistoryResponse {
  session_id: string | null;
  messages: {
    id: string;
    session_id: string;
    role: "user" | "assistant";
    content: string;
    created_at: string;
  }[];
}

interface AIChatResponse {
  response: string;
  therapeutic_approach: string;
  confidence: number;
  suggestions: string[];
  topics: string[];
  recommended_activities: string[];
  suggested_vr_mode: string | null;
  risk_level: string;
  session_id: string | null;
}

export interface ChatGuidance {
  suggestions: string[];
  topics: string[];
  recommendedActivities: string[];
  suggestedVrMode: string | null;
  riskLevel: string;
  therapeuticApproach: string;
}

export const useChat = (personalityId: string = "empathetic") => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [userId, setUserId] = useState<string | null>(null);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [latestGuidance, setLatestGuidance] = useState<ChatGuidance | null>(null);
  const [currentPersonality, setCurrentPersonality] = useState<AIPersonality>(
    AI_PERSONALITIES.find(p => p.id === personalityId) || AI_PERSONALITIES[0]
  );

  // Get user and load history
  useEffect(() => {
    const loadUser = async () => {
      try {
        const { data: { user } } = await supabase.auth.getUser();
        if (user) {
          setUserId(user.id);
          loadChatHistory();
        }
      } catch (error) {
        toast.error("Unable to load your chat history right now.");
      }
    };
    loadUser();
  }, []);

  useEffect(() => {
    const personality = AI_PERSONALITIES.find(p => p.id === personalityId) || AI_PERSONALITIES[0];
    setCurrentPersonality(personality);
  }, [personalityId]);

  const loadChatHistory = async () => {
    try {
      const data = await apiFetch<ChatHistoryResponse>("/chat/history?limit=50");
      setCurrentSessionId(data.session_id);
      setMessages(
        data.messages.map((msg) => ({
          id: msg.id,
          content: msg.content,
          role: msg.role,
          timestamp: new Date(msg.created_at),
        }))
      );
    } catch (error) {
      setMessages([]);
    }
  };

  const sendMessage = useCallback(async (content: string) => {
    if (!userId) {
      toast.error("You need to be signed in to chat.");
      return;
    }

    const userMessage: Message = {
      id: uuidv4(),
      content,
      role: "user",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const result = await apiFetch<AIChatResponse>("/ai/chat", {
        method: "POST",
        body: JSON.stringify({
          message: content,
          personality: currentPersonality.id,
          session_id: currentSessionId,
        }),
      });

      setCurrentSessionId(result.session_id);
      setLatestGuidance({
        suggestions: result.suggestions,
        topics: result.topics,
        recommendedActivities: result.recommended_activities,
        suggestedVrMode: result.suggested_vr_mode,
        riskLevel: result.risk_level,
        therapeuticApproach: result.therapeutic_approach,
      });

      const assistantMessage: Message = {
        id: uuidv4(),
        content: result.response,
        role: "assistant",
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Unable to send your message.");

      const assistantMessage: Message = {
        id: uuidv4(),
        content: "I couldn't complete that request right now. Please try again in a moment.",
        role: "assistant",
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [currentPersonality, currentSessionId, userId]);

  const clearChat = useCallback(async () => {
    if (!userId) return;

    try {
      await apiFetch<{ cleared: boolean }>("/chat/history", { method: "DELETE" });
      setMessages([]);
      setCurrentSessionId(null);
      setLatestGuidance(null);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Failed to clear chat history.");
    }
  }, [userId]);

  const changePersonality = useCallback((personalityId: string) => {
    const personality = AI_PERSONALITIES.find(p => p.id === personalityId) || AI_PERSONALITIES[0];
    setCurrentPersonality(personality);
  }, []);

  return {
    messages,
    isLoading,
    sendMessage,
    clearChat,
    currentPersonality,
    latestGuidance,
    availablePersonalities: AI_PERSONALITIES,
    changePersonality,
  };
};
