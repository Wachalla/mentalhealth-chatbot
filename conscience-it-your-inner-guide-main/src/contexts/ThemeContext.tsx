import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { supabase } from "@/integrations/supabase/client";
import { useAuth } from "./AuthContext";

const OVERLAY_EFFECT_STORAGE_KEY = "conscience.overlay_effect";
const DARK_COLOR_SCHEMES = new Set(["dark-blue", "dark-purple", "midnight", "dark-forest"]);

interface ThemeContextType {
  colorScheme: string;
  backgroundTheme: string;
  fontFamily: string;
  overlayEffect: string;
  setColorScheme: (scheme: string) => void;
  setBackgroundTheme: (theme: string) => void;
  setFontFamily: (font: string) => void;
  setOverlayEffect: (effect: string) => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const isDarkColorScheme = (scheme: string) => DARK_COLOR_SCHEMES.has(scheme);

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
  const [fontFamily, setFontFamilyState] = useState("quicksand");
  const [overlayEffect, setOverlayEffectState] = useState(() => localStorage.getItem(OVERLAY_EFFECT_STORAGE_KEY) || "off");
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
    document.documentElement.setAttribute("data-font", fontFamily);
    document.documentElement.setAttribute("data-overlay-effect", overlayEffect);
    
    // Apply font family to body
    const fontMap: Record<string, string> = {
      quicksand: "'Quicksand', sans-serif",
      nunito: "'Nunito', sans-serif",
      system: "system-ui, -apple-system, sans-serif"
    };
    document.body.style.fontFamily = fontMap[fontFamily] || fontMap.quicksand;
    localStorage.setItem(OVERLAY_EFFECT_STORAGE_KEY, overlayEffect);
  }, [colorScheme, backgroundTheme, fontFamily, overlayEffect]);

  const loadTheme = async () => {
    if (!user) return;
    
    try {
      const { data } = await supabase
        .from("user_settings")
        .select("*")
        .eq("id", user?.id)
        .single();

      if (data) {
        setColorSchemeState(data.color_scheme);
        setBackgroundThemeState(data.background_theme);
        setFontFamilyState(data.font_style || "quicksand");
        if (typeof data.overlay_effect === "string") {
          setOverlayEffectState(data.overlay_effect);
        }
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

  const setFontFamily = (font: string) => {
    setFontFamilyState(font);
  };

  const setOverlayEffect = (effect: string) => {
    setOverlayEffectState(effect);
  };

  return (
    <ThemeContext.Provider
      value={{
        colorScheme,
        backgroundTheme,
        fontFamily,
        overlayEffect,
        setColorScheme,
        setBackgroundTheme,
        setFontFamily,
        setOverlayEffect,
      }}
    >
      {children}
    </ThemeContext.Provider>
  );
};
