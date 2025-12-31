import { Link, useLocation } from "react-router-dom";
import { MessageCircle, Headset, TrendingUp, Home, ArrowLeft, Phone } from "lucide-react";
import { Button } from "@/VRCalmRoom.jsx/ui/button";
import { cn } from "@/lib/utils";

interface QuickNavProps {
  className?: string;
  showBackButton?: boolean;
  backPath?: string;
}

const QuickNav = ({ className, showBackButton = false, backPath = "/" }: QuickNavProps) => {
  const location = useLocation();
  
  const quickActions = [
    { icon: MessageCircle, label: "Chat", path: "/" },
    { icon: Headset, label: "VR", path: "/vr" },
    { icon: Phone, label: "Support", path: "/support" },
    { icon: TrendingUp, label: "Progress", path: "/progress" },
    { icon: Home, label: "Home", path: "/" },
  ];

  return (
    <div className={cn("flex items-center gap-2", className)}>
      {showBackButton && (
        <Link to={backPath}>
          <Button variant="secondary" size="sm" className="bg-black/50 hover:bg-black/70 text-white border-white/20">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
        </Link>
      )}
      
      {quickActions.map((action) => (
        <Link key={action.path} to={action.path}>
          <Button 
            variant={location.pathname === action.path ? "default" : "ghost"} 
            size="sm" 
            className={cn(
              "bg-black/50 hover:bg-black/70 text-white border-white/20",
              location.pathname === action.path && "bg-primary hover:bg-primary"
            )}
            title={action.label}
          >
            <action.icon className="w-4 h-4" />
          </Button>
        </Link>
      ))}
    </div>
  );
};

export default QuickNav;
