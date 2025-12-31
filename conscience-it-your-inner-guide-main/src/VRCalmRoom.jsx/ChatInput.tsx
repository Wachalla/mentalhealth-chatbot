import { useState, useRef, useEffect } from "react";
import { Send, Paperclip, Mic } from "lucide-react";
import { cn } from "@/lib/utils";

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

const ChatInput = ({ onSend, disabled, placeholder = "Share what's on your mind..." }: ChatInputProps) => {
  const [message, setMessage] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSend(message.trim());
      setMessage("");
      if (textareaRef.current) {
        textareaRef.current.style.height = "auto";
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [message]);

  return (
    <form onSubmit={handleSubmit} className="relative">
      <div className="flex items-end gap-3">
        {/* Attachment button */}
        <button
          type="button"
          className="w-12 h-12 rounded-full bg-card/80 backdrop-blur-sm border border-border/50 flex items-center justify-center text-muted-foreground hover:text-foreground hover:bg-card transition-colors"
        >
          <Paperclip className="w-5 h-5" />
        </button>

        {/* Input field */}
        <div className="flex-1 flex items-end bg-card/80 backdrop-blur-sm rounded-full border border-border/50 px-5 py-3">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled}
            rows={1}
            className={cn(
              "flex-1 resize-none bg-transparent text-foreground placeholder:text-muted-foreground focus:outline-none text-sm leading-relaxed",
              disabled && "opacity-50 cursor-not-allowed"
            )}
          />
        </div>

        {/* Mic button */}
        <button
          type="button"
          className="w-12 h-12 rounded-full bg-card/80 backdrop-blur-sm border border-border/50 flex items-center justify-center text-muted-foreground hover:text-foreground hover:bg-card transition-colors"
        >
          <Mic className="w-5 h-5" />
        </button>

        {/* Send button */}
        <button
          type="submit"
          disabled={!message.trim() || disabled}
          className={cn(
            "w-12 h-12 rounded-full flex items-center justify-center transition-all duration-200",
            message.trim() && !disabled
              ? "bg-primary text-primary-foreground hover:scale-105 shadow-lg"
              : "bg-card/80 text-muted-foreground cursor-not-allowed border border-border/50"
          )}
        >
          <Send className="w-5 h-5" />
        </button>
      </div>
    </form>
  );
};

export default ChatInput;