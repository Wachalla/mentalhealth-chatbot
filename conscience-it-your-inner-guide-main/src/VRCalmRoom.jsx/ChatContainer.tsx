import { useEffect, useRef, useState } from "react";
import { useChat, type AIPersonality } from "@/hooks/useChat";
import ChatMessage from "./ChatMessage";
import ChatInput from "./ChatInput";
import TypingIndicator from "./TypingIndicator";
import WelcomeMessage from "./WelcomeMessage";
import Header from "./Header";
import SupportInterface from "@/components/SupportInterface";
import { ScrollArea } from "@/VRCalmRoom.jsx/ui/scroll-area";
import { Brain, User, Sparkles, Heart, AlertTriangle } from "lucide-react";
import { useNotifications } from "@/contexts/NotificationContext";

const ChatContainer = () => {
  const [selectedPersonality, setSelectedPersonality] = useState("empathetic");
  const { messages, isLoading, sendMessage, currentPersonality, availablePersonalities, changePersonality } = useChat(selectedPersonality);
  const scrollRef = useRef<HTMLDivElement>(null);
  const endOfMessagesRef = useRef<HTMLDivElement>(null);
  const [showCrisisSupport, setShowCrisisSupport] = useState(false);
  const [isCrisisDetected, setIsCrisisDetected] = useState(false);
  const { addNotification } = useNotifications();

  // Suicide/self-harm detection
  const detectCrisisContent = (text: string) => {
    const crisisKeywords = [
      'suicide', 'kill myself', 'end it', 'end my life', 'want to die',
      'harm myself', 'self harm', 'cut myself', 'overdose', 'jump off',
      'hang myself', 'shoot myself', 'take my life', 'no point living',
      'better off dead', 'want to disappear', 'end the pain'
    ];
    
    const lowerText = text.toLowerCase();
    return crisisKeywords.some(keyword => lowerText.includes(keyword));
  };

  // Check for crisis content in messages
  useEffect(() => {
    const lastMessage = messages[messages.length - 1];
    if (lastMessage && lastMessage.role === 'user') {
      if (detectCrisisContent(lastMessage.content)) {
        setIsCrisisDetected(true);
        setShowCrisisSupport(true);
        
        // Only show notification once per session
        if (!sessionStorage.getItem('crisisNotificationShown')) {
          addNotification({
            type: 'support',
            title: 'Support Available',
            message: 'Help is available 24/7. Check the support options above.',
            duration: 5000
          });
          sessionStorage.setItem('crisisNotificationShown', 'true');
        }
      }
    }
  }, [messages, addNotification]);

  // Smooth auto-scroll to bottom on new messages
  useEffect(() => {
    if (endOfMessagesRef.current) {
      endOfMessagesRef.current.scrollIntoView({ 
        behavior: "smooth", 
        block: "end" 
      });
    }
  }, [messages, isLoading]);

  const handlePersonalityChange = (personalityId: string) => {
    setSelectedPersonality(personalityId);
    changePersonality(personalityId);
  };

  const getPersonalityIcon = (personality: AIPersonality) => {
    switch (personality.id) {
      case "empathetic":
        return <Heart className="w-4 h-4" />;
      case "professional":
        return <User className="w-4 h-4" />;
      case "mindfulness":
        return <Sparkles className="w-4 h-4" />;
      default:
        return <Brain className="w-4 h-4" />;
    }
  };

  return (
    <div className="flex flex-col h-full">
      <Header />

      {/* Support Banner */}
      <div className={`border-b transition-all duration-300 ${
        isCrisisDetected 
          ? 'border-red-500 bg-red-50' 
          : 'border-border/30 bg-card/30'
      }`}>
        {isCrisisDetected ? (
          <div className="p-4">
            <div className="flex items-center gap-3 mb-3">
              <AlertTriangle className="w-5 h-5 text-red-600" />
              <div className="flex-1">
                <h3 className="font-semibold text-red-900">Support Available</h3>
                <p className="text-sm text-red-800">Help is available 24/7. You don't have to go through this alone.</p>
              </div>
            </div>
            <div className="flex gap-3 flex-wrap">
              <button
                onClick={() => window.open('tel:1-800-18-0066', '_self')}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors flex items-center gap-2"
              >
                <AlertTriangle className="w-4 h-4" />
                Call MIASA (24/7)
              </button>
              <button
                onClick={() => window.open('tel:15999', '_self')}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Call Talian Kasih
              </button>
              <button
                onClick={() => window.open('/vr', '_self')}
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
              >
                Breathing Exercise
              </button>
            </div>
          </div>
        ) : (
          <SupportInterface compact={true} />
        )}
      </div>

      {/* AI Personality Selector */}
      <div className="border-b border-border/30 bg-card/20 px-4 py-3">
        <div className="max-w-3xl mx-auto">
          <div className="flex items-center gap-2 text-sm text-muted-foreground mb-2">
            <Brain className="w-4 h-4" />
            <span>AI Companion Style:</span>
          </div>
          <div className="flex gap-2 flex-wrap">
            {availablePersonalities.map((personality) => (
              <button
                key={personality.id}
                onClick={() => handlePersonalityChange(personality.id)}
                className={`px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                  currentPersonality.id === personality.id
                    ? "bg-primary text-primary-foreground shadow-md"
                    : "bg-card/60 text-muted-foreground hover:bg-card hover:text-foreground border border-border/50"
                }`}
              >
                <div className="flex items-center gap-2">
                  {getPersonalityIcon(personality)}
                  <span>{personality.name}</span>
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Messages */}
      <ScrollArea className="flex-1 p-4 lg:p-6" ref={scrollRef}>
        {messages.length === 0 ? (
          <WelcomeMessage />
        ) : (
          <div className="space-y-6 max-w-3xl mx-auto">
            {messages.map((message) => (
              <ChatMessage
                key={message.id}
                content={message.content}
                role={message.role}
                timestamp={message.timestamp}
              />
            ))}
            {isLoading && messages[messages.length - 1]?.content === "" && (
              <TypingIndicator />
            )}
            <div ref={endOfMessagesRef} />
          </div>
        )}
      </ScrollArea>

      {/* Floating Crisis Help Button */}
      {isCrisisDetected && (
        <div className="fixed bottom-8 right-8 z-50">
          <button
            onClick={() => window.open('tel:1-800-18-0066', '_self')}
            className="bg-red-600 hover:bg-red-700 text-white p-3 rounded-full shadow-lg transition-all duration-200 flex items-center gap-2"
          >
            <AlertTriangle className="w-5 h-5" />
            <span className="font-medium text-sm">Help</span>
          </button>
        </div>
      )}

      {/* Input */}
      <div className="p-4 lg:p-6">
        <div className="max-w-3xl mx-auto">
          <ChatInput onSend={sendMessage} disabled={isLoading} />
        </div>
      </div>
    </div>
  );
};

export default ChatContainer;