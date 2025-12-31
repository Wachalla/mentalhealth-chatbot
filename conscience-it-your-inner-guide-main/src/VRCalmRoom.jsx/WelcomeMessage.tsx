import { Heart, Shield, Sparkles, MessageCircle } from "lucide-react";

const WelcomeMessage = () => {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center px-6 animate-fade-in">
      <div className="w-24 h-24 rounded-full bg-primary/20 border border-primary/30 flex items-center justify-center mb-6 animate-float">
        <MessageCircle className="w-12 h-12 text-primary" />
      </div>
      
      <h2 className="font-display text-2xl lg:text-3xl font-bold text-foreground mb-3">
        Welcome to Conscience
      </h2>
      
      <p className="text-muted-foreground max-w-md mb-8 leading-relaxed">
        I'm here to listen, support, and walk alongside you on your mental wellness journey. 
        Feel free to share whatever is on your mind.
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 max-w-xl w-full">
        <div className="glass-card p-4">
          <Sparkles className="w-6 h-6 text-primary mb-3 mx-auto" />
          <h3 className="font-medium text-sm text-foreground mb-1">Empathetic</h3>
          <p className="text-xs text-muted-foreground">Understanding & caring responses</p>
        </div>
        
        <div className="glass-card p-4">
          <Shield className="w-6 h-6 text-calm-lavender mb-3 mx-auto" />
          <h3 className="font-medium text-sm text-foreground mb-1">Safe Space</h3>
          <p className="text-xs text-muted-foreground">No judgment, just support</p>
        </div>
        
        <div className="glass-card p-4">
          <Heart className="w-6 h-6 text-accent mb-3 mx-auto" />
          <h3 className="font-medium text-sm text-foreground mb-1">Always Here</h3>
          <p className="text-xs text-muted-foreground">Available whenever you need</p>
        </div>
      </div>

      <p className="text-xs text-muted-foreground mt-8 max-w-sm">
        Remember: I'm here to support you, but I'm not a replacement for professional mental health care.
      </p>
    </div>
  );
};

export default WelcomeMessage;