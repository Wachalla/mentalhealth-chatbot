import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { supabase } from "@/integrations/supabase/client";
import { useAuth } from "./AuthContext";

interface ThemeContextType {
  colorScheme: string;
  backgroundTheme: string;
  setColorScheme: (scheme: string) => void;
  setBackgroundTheme: (theme: string) => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error("useTheme must be used within a ThemeProvider");
  }
  return context;
};

export const ThemeProvider = ({ children }: { children: ReactNode }) => {
  const [colorScheme, setColorSchemeState] = useState("midnight");
  const [backgroundTheme, setBackgroundThemeState] = useState("dark");
  const { user } = useAuth();

  // Load theme from database on mount
  useEffect(() => {
    if (user) {
      loadTheme();
    }
  }, [user]);

  // Apply theme changes to document
  useEffect(() => {
    document.documentElement.setAttribute("data-color-scheme", colorScheme);
    document.documentElement.setAttribute("data-background", backgroundTheme);
  }, [colorScheme, backgroundTheme]);

  const loadTheme = async () => {
    if (!user) return;
    
    try {
      const { data } = await supabase
        .from("user_settings")
        .select("color_scheme, background_theme")
        .eq("id", user?.id)
        .single();

      if (data) {
        setColorSchemeState(data.color_scheme);
        setBackgroundThemeState(data.background_theme);
      }
    } catch (error) {
      // Ignore errors for theme loading (table might not exist yet)
      console.log("Theme settings not found, using defaults");
    }
  };

  const setColorScheme = (scheme: string) => {
    setColorSchemeState(scheme);
  };

  const setBackgroundTheme = (theme: string) => {
    setBackgroundThemeState(theme);
  };

  return (
    <ThemeContext.Provider
      value={{
        colorScheme,
        backgroundTheme,
        setColorScheme,
        setBackgroundTheme,
      }}
    >
      {children}
    </ThemeContext.Provider>
  );
};
