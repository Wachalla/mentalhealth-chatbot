import { useState, useEffect } from "react";
import AppLayout from "@/components/AppLayout";
import { Palette, Image, Brain, Type, Lightbulb, Upload } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { useTheme } from "@/contexts/ThemeContext";
import { useNotifications } from "@/contexts/NotificationContext";
import { supabase } from "@/integrations/supabase/client";
import { useToast } from "@/hooks/use-toast";

const colorSchemes = [
  { id: "lavender", name: "Calm Lavender", description: "Peaceful and serene", color: "hsl(270, 50%, 60%)" },
  { id: "coral", name: "Warm Coral", description: "Comforting and gentle", color: "hsl(15, 75%, 55%)" },
  { id: "green", name: "Nature Green", description: "Fresh and grounding", color: "hsl(150, 55%, 42%)" },
  { id: "blue", name: "Ocean Blue", description: "Calm and focused", color: "hsl(200, 80%, 50%)" },
  { id: "rose", name: "Rose Pink", description: "Soft and nurturing", color: "hsl(350, 70%, 55%)" },
  { id: "sunset", name: "Warm Sunset", description: "Cozy and inviting", color: "hsl(25, 85%, 55%)" },
  { id: "dark-blue", name: "Dark Blue", description: "Deep and focused", color: "hsl(195, 80%, 55%)", isDark: true },
  { id: "dark-purple", name: "Dark Purple", description: "Mystical and calming", color: "hsl(280, 70%, 60%)", isDark: true },
  { id: "midnight", name: "Midnight", description: "Elegant and peaceful", color: "hsl(260, 60%, 55%)", isDark: true },
  { id: "dark-forest", name: "Dark Forest", description: "Natural and grounding", color: "hsl(160, 60%, 45%)", isDark: true },
];

const backgroundThemes = [
  { id: "dark", name: "Subtle Grid", preview: "linear-gradient(135deg, hsl(210, 35%, 12%) 0%, hsl(210, 40%, 18%) 100%)" },
  { id: "gradient", name: "Color Gradient", preview: "linear-gradient(135deg, hsl(270, 50%, 30%) 0%, hsl(200, 50%, 30%) 100%)" },
  { id: "nature", name: "Nature Blend", preview: "linear-gradient(180deg, hsl(150, 40%, 20%) 0%, hsl(200, 35%, 12%) 100%)" },
  { id: "ocean", name: "Ocean Depths", preview: "linear-gradient(180deg, hsl(200, 50%, 25%) 0%, hsl(220, 40%, 12%) 100%)" },
  { id: "sunset", name: "Sunset Sky", preview: "linear-gradient(180deg, hsl(30, 60%, 25%) 0%, hsl(280, 40%, 15%) 100%)" },
  { id: "stars", name: "Starry Night", preview: "radial-gradient(ellipse at 30% 30%, hsl(260, 50%, 20%) 0%, hsl(240, 30%, 8%) 100%)" },
  { id: "minimal", name: "Minimal", preview: "hsl(210, 35%, 12%)" },
];

const personalities = [
  { id: "empathetic", name: "Empathetic", description: "Warm, understanding, and emotionally supportive" },
  { id: "motivational", name: "Motivational", description: "Encouraging, positive, and action-oriented" },
  { id: "analytical", name: "Analytical", description: "Thoughtful, structured, and pattern-focused" },
  { id: "gentle", name: "Gentle", description: "Soft-spoken, patient, and calming" },
];

const fontStyles = [
  { id: "modern", name: "Modern Sans", description: "Clean and contemporary" },
  { id: "serif", name: "Classic Serif", description: "Traditional and elegant" },
  { id: "readable", name: "Highly Readable", description: "Clear and easy on the eyes" },
  { id: "friendly", name: "Friendly", description: "Warm and approachable" },
];

const Settings = () => {
  const [selectedColor, setSelectedColor] = useState("midnight");
  const [selectedBackground, setSelectedBackground] = useState("dark");
  const [selectedPersonality, setSelectedPersonality] = useState("empathetic");
  const [selectedFont, setSelectedFont] = useState("modern");
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();
  const { setColorScheme, setBackgroundTheme } = useTheme();
  const { addNotification } = useNotifications();
  const { toast } = useToast();

  // Load settings from database
  useEffect(() => {
    if (user) {
      loadSettings();
    }
  }, [user]);

  const loadSettings = async () => {
    if (!user) return;
    
    try {
      const { data, error } = await supabase
        .from("user_settings")
        .select("*")
        .eq("id", user?.id)
        .single();

      if (data) {
        setSelectedColor(data.color_scheme);
        setSelectedBackground(data.background_theme);
        setSelectedPersonality(data.ai_personality);
        setSelectedFont(data.font_style);
      }
      // If table doesn't exist or no settings found, use defaults
    } catch (error) {
      console.log("Settings table not found, using defaults");
    }
    setLoading(false);
  };

  const saveSettings = async (field: string, value: string) => {
    try {
      const { error } = await supabase
        .from("user_settings")
        .update({ [field]: value })
        .eq("id", user?.id);

      if (error) {
        // Try to insert if update fails (record doesn't exist)
        const { error: insertError } = await supabase
          .from("user_settings")
          .insert({ 
            id: user?.id, 
            [field]: value,
            color_scheme: selectedColor,
            background_theme: selectedBackground,
            ai_personality: selectedPersonality,
            font_style: selectedFont
          });

        if (insertError) {
          console.log("Settings not saved (table might not exist):", insertError.message);
          toast({ 
            title: "Settings Updated", 
            description: "Changes applied locally (database not available)" 
          });
        } else {
          toast({ title: "Settings saved!" });
        }
      } else {
        toast({ title: "Settings saved!" });
      }
    } catch (error) {
      console.log("Settings not saved:", error);
      toast({ 
        title: "Settings Updated", 
        description: "Changes applied locally" 
      });
    }
  };

  const handleColorChange = (colorId: string) => {
    setSelectedColor(colorId);
    setColorScheme(colorId);
    saveSettings("color_scheme", colorId);
  };

  const handleBackgroundChange = (bgId: string) => {
    setSelectedBackground(bgId);
    setBackgroundTheme(bgId);
    saveSettings("background_theme", bgId);
  };

  const handlePersonalityChange = (personalityId: string) => {
    setSelectedPersonality(personalityId);
    saveSettings("ai_personality", personalityId);
  };

  const handleFontChange = (fontId: string) => {
    setSelectedFont(fontId);
    saveSettings("font_style", fontId);
  };

  if (loading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center h-full">
          <p className="text-muted-foreground">Loading settings...</p>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="p-4 lg:p-6 space-y-8 overflow-auto max-w-3xl mx-auto">
        <div>
          <h2 className="font-display text-2xl font-bold text-foreground">Settings</h2>
          <p className="text-muted-foreground text-sm">Customize your therapy experience</p>
        </div>

        {/* Color Scheme */}
        <section className="space-y-4">
          <div className="flex items-center gap-2 text-foreground">
            <Palette className="w-5 h-5" />
            <h3 className="font-display font-semibold text-lg">Color Scheme</h3>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {colorSchemes.map((scheme) => (
              <button
                key={scheme.id}
                onClick={() => handleColorChange(scheme.id)}
                className={`flex items-center gap-3 p-4 rounded-xl border transition-all ${
                  selectedColor === scheme.id
                    ? "bg-primary/10 border-primary"
                    : "bg-card/60 border-border/50 hover:bg-card/80"
                }`}
              >
                <div 
                  className="w-8 h-8 rounded-full flex-shrink-0" 
                  style={{ backgroundColor: scheme.color }}
                />
                <div className="text-left">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-foreground">{scheme.name}</span>
                    {scheme.isDark && (
                      <span className="text-[10px] px-2 py-0.5 rounded-full bg-muted text-muted-foreground">
                        Dark
                      </span>
                    )}
                  </div>
                  <span className="text-xs text-muted-foreground">{scheme.description}</span>
                </div>
              </button>
            ))}
          </div>
        </section>

        {/* Background Theme */}
        <section className="space-y-4">
          <div className="flex items-center gap-2 text-foreground">
            <Image className="w-5 h-5" />
            <h3 className="font-display font-semibold text-lg">Background Theme</h3>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {backgroundThemes.map((theme) => (
              <button
                key={theme.id}
                onClick={() => handleBackgroundChange(theme.id)}
                className={`relative h-24 rounded-xl overflow-hidden border-2 transition-all ${
                  selectedBackground === theme.id
                    ? "border-primary ring-2 ring-primary/30"
                    : "border-transparent hover:border-border"
                }`}
              >
                <div 
                  className="absolute inset-0" 
                  style={{ background: theme.preview }}
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
                <span className="absolute bottom-2 left-2 text-xs text-white font-medium">{theme.name}</span>
              </button>
            ))}
          </div>
        </section>

        {/* AI Personality */}
        <section className="space-y-4">
          <div className="flex items-center gap-2 text-foreground">
            <Brain className="w-5 h-5" />
            <h3 className="font-display font-semibold text-lg">AI Personality</h3>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {personalities.map((personality) => (
              <button
                key={personality.id}
                onClick={() => handlePersonalityChange(personality.id)}
                className={`p-4 rounded-xl border text-left transition-all ${
                  selectedPersonality === personality.id
                    ? "bg-primary/10 border-primary"
                    : "bg-card/60 border-border/50 hover:bg-card/80"
                }`}
              >
                <span className="font-medium text-foreground">{personality.name}</span>
                <p className="text-xs text-muted-foreground mt-1">{personality.description}</p>
              </button>
            ))}
          </div>
        </section>

        {/* Font Style */}
        <section className="space-y-4">
          <div className="flex items-center gap-2 text-foreground">
            <Type className="w-5 h-5" />
            <h3 className="font-display font-semibold text-lg">Font Style</h3>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {fontStyles.map((font) => (
              <button
                key={font.id}
                onClick={() => handleFontChange(font.id)}
                className={`p-4 rounded-xl border text-left transition-all ${
                  selectedFont === font.id
                    ? "bg-primary/10 border-primary"
                    : "bg-card/60 border-border/50 hover:bg-card/80"
                }`}
              >
                <span className="font-medium text-foreground">{font.name}</span>
                <p className="text-xs text-muted-foreground mt-1">{font.description}</p>
              </button>
            ))}
          </div>
        </section>

        {/* Notification Test Section */}
        <section className="space-y-4">
          <div className="flex items-center gap-2 text-foreground">
            <Brain className="w-5 h-5" />
            <h3 className="font-display font-semibold text-lg">Test Notifications</h3>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <button
              onClick={() => addNotification({
                type: 'success',
                title: 'Settings Saved',
                message: 'Your preferences have been successfully saved.',
                duration: 3000
              })}
              className="p-3 rounded-xl border bg-emerald-50/80 border-emerald-200 text-emerald-900 hover:bg-emerald-100/80 transition-all"
            >
              <span className="font-medium">Success Notification</span>
            </button>
            <button
              onClick={() => addNotification({
                type: 'info',
                title: 'New Feature',
                message: 'Check out the new chat personalities!',
                duration: 4000
              })}
              className="p-3 rounded-xl border bg-blue-50/80 border-blue-200 text-blue-900 hover:bg-blue-100/80 transition-all"
            >
              <span className="font-medium">Info Notification</span>
            </button>
            <button
              onClick={() => addNotification({
                type: 'warning',
                title: 'Session Timeout',
                message: 'Your session will expire in 5 minutes.',
                duration: 5000
              })}
              className="p-3 rounded-xl border bg-amber-50/80 border-amber-200 text-amber-900 hover:bg-amber-100/80 transition-all"
            >
              <span className="font-medium">Warning Notification</span>
            </button>
            <button
              onClick={() => addNotification({
                type: 'support',
                title: 'Support Available',
                message: 'Need help? Our support team is here for you.',
                action: {
                  label: 'Get Help',
                  onClick: () => console.log('Support clicked')
                },
                duration: 6000
              })}
              className="p-3 rounded-xl border bg-rose-50/80 border-rose-200 text-rose-900 hover:bg-rose-100/80 transition-all"
            >
              <span className="font-medium">Support Notification</span>
            </button>
          </div>
        </section>

        {/* Note */}
        <div className="flex items-start gap-2 text-muted-foreground text-sm bg-card/50 p-4 rounded-xl border border-border/30">
          <Lightbulb className="w-4 h-4 mt-0.5 text-accent flex-shrink-0" />
          <p>
            Your settings are saved automatically and will persist across sessions. Feel free to experiment with different combinations to find what works best for you.
          </p>
        </div>
      </div>
    </AppLayout>
  );
};

export default Settings;