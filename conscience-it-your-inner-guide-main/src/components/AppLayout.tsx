import { ReactNode } from "react";
import Sidebar from "@/VRCalmRoom.jsx/Sidebar";
import { cn } from "@/lib/utils";
import ShootingStarsOverlay from "@/components/backgrounds/ShootingStarsOverlay";

interface AppLayoutProps {
  children: ReactNode;
  className?: string;
  showSidebar?: boolean;
}

const AppLayout = ({ children, className, showSidebar = true }: AppLayoutProps) => {
  return (
    <div className={cn("relative isolate flex h-screen overflow-hidden bg-background", className)}>
      <ShootingStarsOverlay />
      {showSidebar && (
        <div className="relative z-10">
          <Sidebar />
        </div>
      )}
      <main className={cn(
        "relative z-10 flex flex-1 flex-col overflow-hidden transition-all duration-300",
        showSidebar ? "ml-0" : "ml-0"
      )}>
        {children}
      </main>
    </div>
  );
};

export default AppLayout;
