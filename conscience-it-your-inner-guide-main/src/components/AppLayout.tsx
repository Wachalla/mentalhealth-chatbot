import { ReactNode } from "react";
import Sidebar from "@/VRCalmRoom.jsx/Sidebar";
import { cn } from "@/lib/utils";

interface AppLayoutProps {
  children: ReactNode;
  className?: string;
  showSidebar?: boolean;
}

const AppLayout = ({ children, className, showSidebar = true }: AppLayoutProps) => {
  return (
    <div className={cn("flex h-screen bg-background", className)}>
      {showSidebar && <Sidebar />}
      <main className={cn(
        "flex-1 flex flex-col overflow-hidden transition-all duration-300",
        showSidebar ? "ml-0" : "ml-0"
      )}>
        {children}
      </main>
    </div>
  );
};

export default AppLayout;
