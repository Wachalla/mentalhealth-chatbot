import { useState, useCallback, useEffect } from "react";
import { toast } from "sonner";
import { supabase } from "@/integrations/supabase/client";

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

const OPENAI_API_URL = "https://api.openai.com/v1/chat/completions";

export const useChat = (personalityId: string = "empathetic") => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [userId, setUserId] = useState<string | null>(null);
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
          loadChatHistory(user.id);
        } else {
          // Use a fallback user ID for development
          setUserId("dev-user");
          loadChatHistory("dev-user");
        }
      } catch (error) {
        // Use fallback user ID if auth fails
        setUserId("dev-user");
        loadChatHistory("dev-user");
      }
    };
    loadUser();
  }, []);

  useEffect(() => {
    const personality = AI_PERSONALITIES.find(p => p.id === personalityId) || AI_PERSONALITIES[0];
    setCurrentPersonality(personality);
  }, [personalityId]);

  const loadChatHistory = async (uid: string) => {
    try {
      const { data } = await supabase
        .from("chat_messages")
        .select("*")
        .eq("user_id", uid)
        .order("created_at", { ascending: true })
        .limit(50);

      if (data) {
        setMessages(
          data.map((msg) => ({
            id: msg.id,
            content: msg.content,
            role: msg.role as "user" | "assistant",
            timestamp: new Date(msg.created_at),
          }))
        );
      }
    } catch (error) {
      console.log("Chat history not available, checking localStorage");
      // Fallback to localStorage for development
      const savedMessages = JSON.parse(localStorage.getItem(`chat_messages_${uid}`) || '[]');
      if (savedMessages.length > 0) {
        setMessages(
          savedMessages.map((msg: any) => ({
            id: msg.id,
            content: msg.content,
            role: msg.role as "user" | "assistant",
            timestamp: new Date(msg.created_at),
          }))
        );
      }
    }
  };

  const saveMessage = async (content: string, role: "user" | "assistant") => {
    if (!userId) return;
    try {
      await supabase.from("chat_messages").insert({
        user_id: userId,
        content,
        role,
      });
    } catch (error) {
      // Save to localStorage as fallback for development
      const savedMessages = JSON.parse(localStorage.getItem(`chat_messages_${userId}`) || '[]');
      savedMessages.push({
        id: crypto.randomUUID(),
        user_id: userId,
        content,
        role,
        created_at: new Date().toISOString()
      });
      localStorage.setItem(`chat_messages_${userId}`, JSON.stringify(savedMessages));
    }
  };

  const callOpenAI = async (messages: Message[], personality: AIPersonality): Promise<string> => {
    const apiKey = import.meta.env.VITE_OPENAI_API_KEY;
    
    if (!apiKey) {
      throw new Error("OpenAI API key not configured");
    }

    const systemMessage = {
      role: "system" as const,
      content: personality.systemPrompt
    };

    const apiMessages = [
      systemMessage,
      ...messages.map(msg => ({
        role: msg.role,
        content: msg.content
      }))
    ];

    const response = await fetch(OPENAI_API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${apiKey}`
      },
      body: JSON.stringify({
        model: personality.model,
        messages: apiMessages,
        temperature: personality.temperature,
        max_tokens: 500,
        stream: false
      })
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error?.message || `API Error: ${response.status}`);
    }

    const data = await response.json();
    return data.choices[0]?.message?.content || "I apologize, but I couldn't generate a response.";
  };

  const getFallbackResponse = (userMessage: string): string => {
    const responses = [
      "I understand how you're feeling. It takes courage to share your thoughts.",
      "Thank you for opening up. I'm here to support you through this.",
      "That sounds challenging. You're not alone in experiencing this.",
      "I appreciate you sharing this with me. Let's explore this together.",
      "Your feelings are valid. It's okay to feel this way.",
      "I'm here to listen. Tell me more about what's on your mind.",
      "That takes self-awareness to recognize. How can I help you with this?",
      "I hear you. Let's work through this step by step together.",
    ];
    
    // Simple keyword-based responses
    const lowerMessage = userMessage.toLowerCase();
    if (lowerMessage.includes("anxious") || lowerMessage.includes("anxiety")) {
      return "I understand anxiety can be overwhelming. Deep breathing exercises can help in the moment. Try taking 4 deep breaths, counting to 4 as you inhale and 6 as you exhale. Would you like to try some grounding techniques together?";
    }
    if (lowerMessage.includes("sad") || lowerMessage.includes("depressed")) {
      return "I'm sorry you're feeling this way. Remember that it's okay to not be okay. Sometimes small acts of self-care, like a short walk or listening to calming music, can provide some relief. You're taking a positive step by reaching out.";
    }
    if (lowerMessage.includes("stress") || lowerMessage.includes("stressed")) {
      return "Stress can feel really heavy. Let's try a quick stress-relief technique: tense your shoulders for 5 seconds, then release them completely. Notice the difference. What's one small thing you could do to make today a bit easier?";
    }
    
    return responses[Math.floor(Math.random() * responses.length)];
  };

  const sendMessage = useCallback(async (content: string) => {
    const userMessage: Message = {
      id: crypto.randomUUID(),
      content,
      role: "user",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    // Save user message
    saveMessage(content, "user");

    let assistantContent = "";

    try {
      // Try OpenAI API first
      if (import.meta.env.VITE_OPENAI_API_KEY) {
        assistantContent = await callOpenAI([...messages, userMessage], currentPersonality);
      } else {
        // Fallback to local responses
        await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 1000));
        assistantContent = getFallbackResponse(content);
      }

      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        content: assistantContent,
        role: "assistant",
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
      
      if (assistantContent) {
        saveMessage(assistantContent, "assistant");
      }
    } catch (error) {
      console.error("Chat error:", error);
      
      // Fallback to local response
      await new Promise(resolve => setTimeout(resolve, 500));
      assistantContent = getFallbackResponse(content);
      
      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        content: assistantContent,
        role: "assistant",
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
      
      if (assistantContent) {
        saveMessage(assistantContent, "assistant");
      }
    } finally {
      setIsLoading(false);
    }
  }, [messages, userId, currentPersonality]);

  const clearChat = useCallback(async () => {
    if (userId) {
      try {
        await supabase.from("chat_messages").delete().eq("user_id", userId);
      } catch (error) {
        console.log("Failed to clear chat history");
      }
      // Also clear localStorage
      localStorage.removeItem(`chat_messages_${userId}`);
    }
    setMessages([]);
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
    availablePersonalities: AI_PERSONALITIES,
    changePersonality,
  };
};