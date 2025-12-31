import { MessageCircle, Phone, TrendingUp, History, Lightbulb, User, Settings, Headset } from "lucide-react";
import { cn } from "@/lib/utils";
import { Link, useLocation } from "react-router-dom";

interface SidebarProps {
  className?: string;
}

const navItems = [
  { icon: MessageCircle, label: "Chat", path: "/" },
  { icon: TrendingUp, label: "Progress", path: "/progress" },
  { icon: History, label: "History", path: "/history" },
  { icon: Lightbulb, label: "Activities", path: "/activities" },
  { icon: Phone, label: "Support", path: "/support" },
  { icon: Headset, label: "VR", path: "/vr" },
  { icon: User, label: "Account", path: "/account" },
  { icon: Settings, label: "Settings", path: "/settings" },
];

const Sidebar = ({ className }: SidebarProps) => {
  const location = useLocation();

  return (
    <aside className={cn("w-20 lg:w-64 bg-sidebar border-r border-sidebar-border flex flex-col", className)}>
      {/* Logo */}
      <div className="p-4 flex justify-center">
        <div className="w-10 h-10 rounded-full bg-primary/20 border border-primary/30 flex items-center justify-center">
          <MessageCircle className="w-5 h-5 text-primary" />
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-2">
        {navItems.map((item) => (
          <Link
            key={item.label}
            to={item.path}
            className={cn(
              "nav-item",
              location.pathname === item.path && "nav-item-active"
            )}
          >
            <item.icon className="w-5 h-5 lg:w-6 lg:h-6" />
            <span className="hidden lg:inline text-sm font-medium">{item.label}</span>
          </Link>
        ))}
      </nav>
    </aside>
  );
};

export default Sidebar;