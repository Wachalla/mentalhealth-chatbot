import { Bot } from "lucide-react";

const TypingIndicator = () => {
  return (
    <div className="flex gap-3 animate-fade-in">
      <div className="w-9 h-9 rounded-full bg-calm-lavender flex items-center justify-center flex-shrink-0">
        <Bot className="w-4 h-4 text-secondary-foreground" />
      </div>
      <div className="chat-bubble-ai">
        <div className="flex items-center gap-1.5 py-1">
          <span className="w-2 h-2 bg-primary/60 rounded-full animate-typing-1" />
          <span className="w-2 h-2 bg-primary/60 rounded-full animate-typing-2" />
          <span className="w-2 h-2 bg-primary/60 rounded-full animate-typing-3" />
        </div>
      </div>
    </div>
  );
};

export default TypingIndicator;
