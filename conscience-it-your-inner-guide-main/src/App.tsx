import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "@/contexts/AuthContext";
import { ThemeProvider } from "@/contexts/ThemeContext";
import { NotificationProvider } from "@/contexts/NotificationContext";
import { ActivityProvider } from "@/contexts/ActivityContext";
import { Toaster } from "@/VRCalmRoom.jsx/ui/toaster";
import { Toaster as Sonner } from "@/VRCalmRoom.jsx/ui/sonner";
import { TooltipProvider } from "@/VRCalmRoom.jsx/ui/tooltip";
import ProtectedRoute from "@/VRCalmRoom.jsx/ProtectedRoute";
import Auth from "./pages/Auth";
import Index from "./pages/Index";
import Progress from "./pages/Progress";
import History from "./pages/History";
import Activities from "./pages/Activities";
import Account from "./pages/Account";
import Settings from "./pages/Settings";
import Support from "./pages/Support";
import VRRoom from "./pages/VRRoom";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <BrowserRouter>
      <NotificationProvider>
        <AuthProvider>
          <ThemeProvider>
            <ActivityProvider>
              <TooltipProvider>
                <Routes>
                  <Route path="/auth" element={<Auth />} />
                  <Route path="/" element={<ProtectedRoute><Index /></ProtectedRoute>} />
                  <Route path="/progress" element={<ProtectedRoute><Progress /></ProtectedRoute>} />
                  <Route path="/history" element={<ProtectedRoute><History /></ProtectedRoute>} />
                  <Route path="/activities" element={<ProtectedRoute><Activities /></ProtectedRoute>} />
                  <Route path="/support" element={<ProtectedRoute><Support /></ProtectedRoute>} />
                  <Route path="/account" element={<ProtectedRoute><Account /></ProtectedRoute>} />
                  <Route path="/settings" element={<ProtectedRoute><Settings /></ProtectedRoute>} />
                  <Route path="/vr" element={<ProtectedRoute><VRRoom /></ProtectedRoute>} />
                  <Route path="*" element={<NotFound />} />
                </Routes>
                <Toaster />
                <Sonner />
              </TooltipProvider>
            </ActivityProvider>
          </ThemeProvider>
        </AuthProvider>
      </NotificationProvider>
    </BrowserRouter>
  </QueryClientProvider>
);

export default App;
