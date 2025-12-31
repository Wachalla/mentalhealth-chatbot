import { cn } from "@/lib/utils";

interface ChatMessageProps {
  content: string;
  role: "user" | "assistant";
  timestamp?: Date;
  isStreaming?: boolean;
}

const ChatMessage = ({ content, role, timestamp, isStreaming }: ChatMessageProps) => {
  const isUser = role === "user";

  return (
    <div
      className={cn(
        "flex gap-3 animate-fade-in transition-all duration-300",
        isUser ? "flex-row-reverse" : "flex-row"
      )}
    >
      {/* Avatar/Badge */}
      <div
        className={cn(
          "w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0 text-xs font-bold transition-colors duration-500",
          isUser 
            ? "bg-primary text-primary-foreground" 
            : "bg-primary/20 border border-primary/30 text-primary"
        )}
      >
        {isUser ? "You" : "AI"}
      </div>

      {/* Message Bubble */}
      <div className={cn("max-w-[75%] space-y-1", isUser ? "items-end" : "items-start")}>
        <div className={isUser ? "chat-bubble-user" : "chat-bubble-ai"}>
          <p className="text-sm leading-relaxed whitespace-pre-wrap">
            {content}
            {isStreaming && (
              <span className="inline-flex ml-1">
                <span className="w-1.5 h-1.5 bg-primary rounded-full animate-typing-1" />
                <span className="w-1.5 h-1.5 bg-primary rounded-full animate-typing-2 mx-0.5" />
                <span className="w-1.5 h-1.5 bg-primary rounded-full animate-typing-3" />
              </span>
            )}
          </p>
        </div>
        {timestamp && (
          <p
            className={cn(
              "text-xs text-muted-foreground px-1",
              isUser ? "text-right" : "text-left"
            )}
          >
            {timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
          </p>
        )}
      </div>
    </div>
  );
};

export default ChatMessage;