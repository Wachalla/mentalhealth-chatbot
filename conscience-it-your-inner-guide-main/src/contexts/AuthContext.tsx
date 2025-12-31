import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { User, Session } from "@supabase/supabase-js";
import { supabase } from "@/integrations/supabase/client";

interface AuthContextType {
  user: User | null;
  session: Session | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<{ error: Error | null }>;
  signUp: (email: string, password: string) => Promise<{ error: Error | null }>;
  signOut: () => Promise<void>;
  devBypass: (email: string, password: string) => Promise<boolean>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Skip Supabase auth for testing with placeholder credentials
    if (import.meta.env.VITE_SUPABASE_URL?.includes('demo')) {
      setLoading(false);
      return;
    }

    // Get initial session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      setUser(session?.user ?? null);
      setLoading(false);
    });

    // Listen for auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
      setUser(session?.user ?? null);
      setLoading(false);
    });

    return () => subscription.unsubscribe();
  }, []);

  const signIn = async (email: string, password: string) => {
    if (import.meta.env.VITE_SUPABASE_URL?.includes('demo')) {
      return { error: new Error('Auth disabled in demo mode') };
    }
    
    const { error } = await supabase.auth.signInWithPassword({ email, password });
    return { error };
  };

  const signUp = async (email: string, password: string) => {
    if (import.meta.env.VITE_SUPABASE_URL?.includes('demo')) {
      return { error: new Error('Auth disabled in demo mode') };
    }
    
    const { error } = await supabase.auth.signUp({ email, password });
    return { error };
  };

  const signOut = async () => {
    if (import.meta.env.VITE_SUPABASE_URL?.includes('demo')) {
      return;
    }
    
    await supabase.auth.signOut();
  };

  const devBypass = async (email: string, password: string): Promise<boolean> => {
    if (email === "joeyentsie2004@gmail.com" && password === "kofi123") {
      // Create a mock user object
      const mockUser = {
        id: 'dev-bypass-user',
        email: 'joeyentsie2004@gmail.com',
        aud: 'authenticated',
        role: 'authenticated',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      } as User;

      const mockSession = {
        user: mockUser,
        access_token: 'dev-bypass-token',
        refresh_token: 'dev-bypass-refresh',
        expires_in: 3600,
        token_type: 'bearer',
      } as Session;

      setUser(mockUser);
      setSession(mockSession);
      setLoading(false);
      return true;
    }
    return false;
  };

  const value = {
    user,
    session,
    loading,
    signIn,
    signUp,
    signOut,
    devBypass,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};