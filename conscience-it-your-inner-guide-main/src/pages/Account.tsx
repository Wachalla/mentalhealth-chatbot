import { useState, useEffect } from "react";
import Layout from "@/VRCalmRoom.jsx/Layout";
import { User, Brain, Tag, Calendar, LogOut, Trash2, Edit2 } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { supabase } from "@/integrations/supabase/client";
import { useToast } from "@/hooks/use-toast";
import { useNavigate } from "react-router-dom";

interface Profile {
  id: string;
  email: string | null;
  preferred_name: string | null;
  pronouns: string | null;
  created_at: string;
}

interface Memory {
  id: string;
  category: string;
  information: string;
  importance: string;
  created_at: string;
}

const Account = () => {
  const [activeTab, setActiveTab] = useState<"profile" | "memory">("profile");
  const [profile, setProfile] = useState<Profile | null>(null);
  const [memories, setMemories] = useState<Memory[]>([]);
  const [newMemory, setNewMemory] = useState({ category: "", info: "", importance: "Medium" });
  const [isEditing, setIsEditing] = useState(false);
  const [editForm, setEditForm] = useState({ preferred_name: "", pronouns: "" });
  const { user, signOut } = useAuth();
  const { toast } = useToast();
  const navigate = useNavigate();

  // Fetch profile
  useEffect(() => {
    if (user) {
      fetchProfile();
      fetchMemories();
    }
  }, [user]);

  const fetchProfile = async () => {
    const { data, error } = await supabase
      .from("profiles")
      .select("*")
      .eq("id", user?.id)
      .single();

    if (data) {
      setProfile(data);
      setEditForm({
        preferred_name: data.preferred_name || "",
        pronouns: data.pronouns || "",
      });
    }
  };

  const fetchMemories = async () => {
    const { data, error } = await supabase
      .from("ai_memories")
      .select("*")
      .eq("user_id", user?.id)
      .order("created_at", { ascending: false });

    if (data) {
      setMemories(data);
    }
  };

  const handleUpdateProfile = async () => {
    const { error } = await supabase
      .from("profiles")
      .update({
        preferred_name: editForm.preferred_name || null,
        pronouns: editForm.pronouns || null,
      })
      .eq("id", user?.id);

    if (error) {
      toast({ title: "Error", description: error.message, variant: "destructive" });
    } else {
      toast({ title: "Profile updated!" });
      setIsEditing(false);
      fetchProfile();
    }
  };

  const handleAddMemory = async () => {
    if (!newMemory.category || !newMemory.info) {
      toast({ title: "Please fill in all fields", variant: "destructive" });
      return;
    }

    const { error } = await supabase.from("ai_memories").insert({
      user_id: user?.id,
      category: newMemory.category,
      information: newMemory.info,
      importance: newMemory.importance,
    });

    if (error) {
      toast({ title: "Error", description: error.message, variant: "destructive" });
    } else {
      toast({ title: "Memory added!" });
      setNewMemory({ category: "", info: "", importance: "Medium" });
      fetchMemories();
    }
  };

  const handleDeleteMemory = async (id: string) => {
    const { error } = await supabase.from("ai_memories").delete().eq("id", id);
    if (!error) {
      fetchMemories();
      toast({ title: "Memory deleted" });
    }
  };

  const handleSignOut = async () => {
    await signOut();
    navigate("/auth");
  };

  return (
    <Layout>
      <div className="p-4 lg:p-6 space-y-6 overflow-auto max-w-3xl mx-auto">
        <div>
          <h2 className="font-display text-2xl font-bold text-foreground">Account</h2>
          <p className="text-muted-foreground text-sm">Manage your profile and AI memory</p>
        </div>

        {/* Tabs */}
        <div className="flex gap-2">
          <button
            onClick={() => setActiveTab("profile")}
            className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-colors ${
              activeTab === "profile"
                ? "bg-primary text-primary-foreground"
                : "bg-card/80 text-foreground hover:bg-card"
            }`}
          >
            <User className="w-4 h-4" />
            Profile
          </button>
          <button
            onClick={() => setActiveTab("memory")}
            className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-colors ${
              activeTab === "memory"
                ? "bg-primary text-primary-foreground"
                : "bg-card/80 text-foreground hover:bg-card"
            }`}
          >
            <Brain className="w-4 h-4" />
            AI Memory
          </button>
        </div>

        {activeTab === "profile" && (
          <div className="space-y-4">
            {/* Profile Card */}
            <div className="glass-card p-6">
              <div className="flex items-start justify-between mb-6">
                <div className="flex items-center gap-4">
                  <div className="w-16 h-16 rounded-full bg-primary/20 border border-primary/30 flex items-center justify-center">
                    <User className="w-8 h-8 text-primary" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-lg text-foreground">
                      {profile?.preferred_name || "User"}
                    </h3>
                    <p className="text-sm text-primary">{profile?.email || user?.email}</p>
                  </div>
                </div>
                <button
                  onClick={() => setIsEditing(!isEditing)}
                  className="w-10 h-10 rounded-full bg-card border border-border/50 flex items-center justify-center text-muted-foreground hover:text-foreground transition-colors"
                >
                  <Edit2 className="w-4 h-4" />
                </button>
              </div>

              {isEditing ? (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm text-primary mb-2">Preferred Name</label>
                    <input
                      type="text"
                      value={editForm.preferred_name}
                      onChange={(e) => setEditForm({ ...editForm, preferred_name: e.target.value })}
                      placeholder="Enter your preferred name"
                      className="w-full px-4 py-3 rounded-lg bg-input border border-border text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-primary"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-primary mb-2">Pronouns</label>
                    <input
                      type="text"
                      value={editForm.pronouns}
                      onChange={(e) => setEditForm({ ...editForm, pronouns: e.target.value })}
                      placeholder="e.g., they/them, she/her, he/him"
                      className="w-full px-4 py-3 rounded-lg bg-input border border-border text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-primary"
                    />
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={handleUpdateProfile}
                      className="px-4 py-2 rounded-lg bg-primary text-primary-foreground font-medium hover:bg-primary/90"
                    >
                      Save Changes
                    </button>
                    <button
                      onClick={() => setIsEditing(false)}
                      className="px-4 py-2 rounded-lg bg-card border border-border text-foreground hover:bg-muted/50"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              ) : (
                <div className="space-y-3">
                  <div className="flex items-center gap-3">
                    <Tag className="w-4 h-4 text-muted-foreground" />
                    <span className="text-muted-foreground">Preferred Name:</span>
                    <span className="text-foreground">{profile?.preferred_name || "Not set"}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <User className="w-4 h-4 text-muted-foreground" />
                    <span className="text-muted-foreground">Pronouns:</span>
                    <span className="text-foreground">{profile?.pronouns || "Not set"}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <Calendar className="w-4 h-4 text-muted-foreground" />
                    <span className="text-muted-foreground">Joined:</span>
                    <span className="text-foreground">
                      {profile?.created_at
                        ? new Date(profile.created_at).toLocaleDateString()
                        : "N/A"}
                    </span>
                  </div>
                </div>
              )}
            </div>

            {/* Account Actions */}
            <div className="glass-card p-6">
              <h3 className="font-semibold text-foreground mb-4">Account Actions</h3>
              <div className="space-y-3">
                <button
                  onClick={handleSignOut}
                  className="w-full flex items-center gap-3 px-4 py-3 rounded-lg bg-card border border-border/50 text-foreground hover:bg-muted/50 transition-colors"
                >
                  <LogOut className="w-4 h-4" />
                  Sign Out
                </button>
                <button className="w-full flex items-center gap-3 px-4 py-3 rounded-lg bg-accent/10 border border-accent/20 text-accent hover:bg-accent/20 transition-colors">
                  <Trash2 className="w-4 h-4" />
                  Delete Account
                </button>
              </div>
            </div>
          </div>
        )}

        {activeTab === "memory" && (
          <div className="space-y-4">
            <p className="text-muted-foreground text-sm">
              AI Memory helps the chatbot remember important details about you, making conversations more personalized and accurate.
            </p>

            {/* Add New Memory */}
            <div className="glass-card p-6">
              <h3 className="font-semibold text-foreground mb-4">Add New Memory</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-primary mb-2">Category</label>
                  <input
                    type="text"
                    value={newMemory.category}
                    onChange={(e) => setNewMemory({ ...newMemory, category: e.target.value })}
                    placeholder="e.g., Personal Goals, Preferences, Important Dates"
                    className="w-full px-4 py-3 rounded-lg bg-input border border-border text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-primary"
                  />
                </div>
                <div>
                  <label className="block text-sm text-primary mb-2">Information</label>
                  <textarea
                    value={newMemory.info}
                    onChange={(e) => setNewMemory({ ...newMemory, info: e.target.value })}
                    placeholder="e.g., I have a fear of public speaking that I'm working on"
                    rows={3}
                    className="w-full px-4 py-3 rounded-lg bg-input border border-border text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-primary resize-none"
                  />
                </div>
                <div>
                  <label className="block text-sm text-primary mb-2">Importance</label>
                  <select
                    value={newMemory.importance}
                    onChange={(e) => setNewMemory({ ...newMemory, importance: e.target.value })}
                    className="w-full px-4 py-3 rounded-lg bg-input border border-border text-foreground focus:outline-none focus:border-primary"
                  >
                    <option value="Low">Low</option>
                    <option value="Medium">Medium</option>
                    <option value="High">High</option>
                  </select>
                </div>
                <button
                  onClick={handleAddMemory}
                  className="w-full py-3 rounded-lg bg-primary text-primary-foreground font-medium hover:bg-primary/90 transition-colors"
                >
                  Add Memory
                </button>
              </div>
            </div>

            {/* Stored Memories */}
            <div>
              <h3 className="font-semibold text-foreground mb-4">Stored Memories ({memories.length})</h3>
              {memories.length === 0 ? (
                <div className="glass-card p-8 text-center">
                  <Brain className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
                  <p className="text-primary">No memories stored yet</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {memories.map((memory) => (
                    <div key={memory.id} className="glass-card p-4">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-primary">{memory.category}</span>
                        <div className="flex items-center gap-2">
                          <span className="text-xs px-2 py-1 rounded-full bg-muted text-muted-foreground">
                            {memory.importance}
                          </span>
                          <button
                            onClick={() => handleDeleteMemory(memory.id)}
                            className="text-accent hover:text-accent/80"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                      <p className="text-foreground text-sm">{memory.information}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default Account;