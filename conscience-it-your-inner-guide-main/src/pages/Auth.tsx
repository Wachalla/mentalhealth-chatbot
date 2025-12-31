import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { User, Mail, Lock, X } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const Auth = () => {
  const [isSignUp, setIsSignUp] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [showWelcome, setShowWelcome] = useState(false);
  const { signIn, signUp, user, devBypass } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();

  // Redirect if already logged in
  if (user) {
    navigate("/");
    return null;
  }

  // Handle welcome animation timer
  useEffect(() => {
    if (showWelcome) {
      const timer = setTimeout(() => {
        setShowWelcome(false);
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [showWelcome]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    // Hardcoded bypass for development
    if (email === "joeyentsie2004@gmail.com" && password === "kofi123") {
      const bypassSuccess = await devBypass(email, password);
      if (bypassSuccess) {
        toast({
          title: "Development Bypass",
          description: "Welcome Back, Boss! Authentication bypassed for development.",
        });
        setShowWelcome(true);
        setTimeout(() => navigate("/"), 500);
        setLoading(false);
        return;
      }
    }

    try {
      if (isSignUp) {
        const { error } = await signUp(email, password);
        if (error) {
          if (error.message.includes("already registered")) {
            toast({
              title: "Account exists",
              description: "This email is already registered. Please sign in instead.",
              variant: "destructive",
            });
          } else {
            toast({
              title: "Sign up failed",
              description: error.message,
              variant: "destructive",
            });
          }
        } else {
          toast({
            title: "Account created!",
            description: "Welcome to Conscience. You're now signed in.",
          });
          setShowWelcome(true);
          setTimeout(() => navigate("/"), 500);
        }
      } else {
        const { error } = await signIn(email, password);
        if (error) {
          toast({
            title: "Sign in failed",
            description: error.message,
            variant: "destructive",
          });
        } else {
          setShowWelcome(true);
          setTimeout(() => navigate("/"), 500);
        }
      }
    } catch (err) {
      toast({
        title: "Error",
        description: "Something went wrong. Please try again.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      {/* Welcome Animation */}
      {showWelcome && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
          <div className="text-center space-y-4">
            <h1 className="font-display text-6xl font-bold text-white animate-pulse">
              Welcome to
            </h1>
            <h2 className="font-display text-7xl font-bold text-primary animate-bounce">
              Conscience
            </h2>
            <p className="text-white/80 animate-fade-in">
              Your mental health companion
            </p>
          </div>
        </div>
      )}
      
      <div className="w-full max-w-md">
        {/* Modal Card */}
        <div className="glass-card p-6 space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <h1 className="font-display text-xl font-bold text-foreground">
              {isSignUp ? "Create Account" : "Sign In"}
            </h1>
            <button className="w-8 h-8 rounded-full bg-card border border-border/50 flex items-center justify-center text-muted-foreground">
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Social Login Buttons */}
          <div className="space-y-3">
            {/* Google */}
            <button className="w-full flex items-center justify-center gap-3 px-4 py-3 rounded-lg bg-card border border-border/50 text-foreground hover:bg-muted/50 transition-colors">
              <img 
                src="https://authjs.dev/img/providers/google.svg" 
                alt="Google" 
                className="w-5 h-5" 
              />
              <span className="text-sm font-medium">Continue with Google</span>
            </button>

            {/* Apple */}
            <button className="w-full flex items-center justify-center gap-3 px-4 py-3 rounded-lg bg-card border border-border/50 text-foreground hover:bg-muted/50 transition-colors">
              <img 
                src="https://authjs.dev/img/providers/apple.svg" 
                alt="Apple" 
                className="w-5 h-5 dark:invert" 
              />
              <span className="text-sm font-medium">Continue with Apple</span>
            </button>

            {/* X(formely twitter) */}
            <button className="w-full flex items-center justify-center gap-3 px-4 py-3 rounded-lg bg-card border border-border/50 text-foreground hover:bg-muted/50 transition-colors">
              <img 
                src="https://authjs.dev/img/providers/twitter.svg" 
                alt="Twitter" 
                className="w-5 h-5" 
              />
              <span className="text-sm font-medium">Continue with X</span>
            </button>

            {/* Facebook */}
            <button className="w-full flex items-center justify-center gap-3 px-4 py-3 rounded-lg bg-card border border-border/50 text-foreground hover:bg-muted/50 transition-colors">
              <img 
                src="https://authjs.dev/img/providers/facebook.svg" 
                alt="Facebook" 
                className="w-5 h-5" 
              />
              <span className="text-sm font-medium">Continue with Facebook</span>
            </button>
          </div>
  


          {/* Divider */}
          <div className="flex items-center gap-4">
            <div className="flex-1 h-px bg-border" />
            <span className="text-muted-foreground text-sm">or</span>
            <div className="flex-1 h-px bg-border" />
          </div>

          {/* Email/Password Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm text-primary mb-2">
                Email <span className="text-accent">*</span>
              </label>
              <div className="relative">
                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Enter your email"
                  required
                  className="w-full pl-12 pr-4 py-3 rounded-lg bg-input border border-border text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-primary"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm text-primary mb-2">
                Password <span className="text-accent">*</span>
              </label>
              <div className="relative">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  required
                  minLength={6}
                  className="w-full pl-12 pr-4 py-3 rounded-lg bg-input border border-border text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-primary"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 rounded-lg bg-primary text-primary-foreground font-medium hover:bg-primary/90 transition-colors disabled:opacity-50"
            >
              {loading ? "Please wait..." : isSignUp ? "Create Account" : "Sign In"}
            </button>
          </form>

          {/* Toggle Sign In/Up */}
          <p className="text-center text-sm">
            <button
              type="button"
              onClick={() => setIsSignUp(!isSignUp)}
              className="text-primary hover:underline"
            >
              {isSignUp ? "Already have an account? Sign in" : "Don't have an account? Sign up"}
            </button>
          </p>

          {/* Disclaimer */}
          <div className="p-3 rounded-lg bg-accent/10 border border-accent/20">
            <p className="text-xs text-muted-foreground">
              This is a prototype. In production, all authentication would be secure and encrypted.
            </p>
          </div>
        </div>

        {/* Welcome Text */}
        <div className="text-center mt-6">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-primary/20 border border-primary/30 flex items-center justify-center">
            <User className="w-8 h-8 text-primary" />
          </div>
          <h2 className="font-display text-2xl font-bold text-foreground mb-2">
            Welcome to Conscience
          </h2>
          <p className="text-muted-foreground text-sm">
            Sign in to save your progress and access your account across devices
          </p>
        </div>
      </div>
    </div>
  );
};

export default Auth;