import { useState } from "react";
import { Heart, Phone, MessageCircle, Book, Headphones, AlertTriangle, Clock, Globe, Users } from "lucide-react";
import { Button } from "@/VRCalmRoom.jsx/ui/button";
import { Card } from "@/VRCalmRoom.jsx/ui/card";
import { useNotifications } from "@/contexts/NotificationContext";
import { cn } from "@/lib/utils";
import { malaysianHelplines, getHelplineByType, getAvailableHelplines, emergencyServices } from "@/config/malaysianHelplines";

const SupportOptions = [
  {
    icon: Phone,
    title: "Crisis Support",
    description: "24/7 Malaysian crisis helplines",
    action: "#crisis",
    color: "text-red-500",
    bgColor: "bg-red-50",
    borderColor: "border-red-200"
  },
  {
    icon: MessageCircle,
    title: "Chat Support",
    description: "Talk with trained listeners",
    action: "/chat",
    color: "text-blue-500",
    bgColor: "bg-blue-50",
    borderColor: "border-blue-200"
  },
  {
    icon: Book,
    title: "Self-Help Resources",
    description: "Guided exercises and articles",
    action: "/resources",
    color: "text-emerald-500",
    bgColor: "bg-emerald-50",
    borderColor: "border-emerald-200"
  },
  {
    icon: Headphones,
    title: "VR Therapy",
    description: "Immersive calming environments",
    action: "/vr",
    color: "text-purple-500",
    bgColor: "bg-purple-50",
    borderColor: "border-purple-200"
  }
];

const EmotionalRiskResponses = [
  {
    keywords: ['suicide', 'kill myself', 'end it', 'harm'],
    response: {
      title: "We're Here for You",
      message: "It sounds like you're going through a difficult time. Please reach out to someone who can help.",
      action: {
        label: "Call MIASA Helpline (24/7)",
        onClick: () => window.open('tel:1-800-18-0066', '_self')
      }
    }
  },
  {
    keywords: ['anxious', 'panic', 'overwhelmed'],
    response: {
      title: "Take a Deep Breath",
      message: "Let's try a grounding exercise together. You're safe and this feeling will pass.",
      action: {
        label: "Start Breathing Exercise",
        onClick: () => window.open('/vr', '_self')
      }
    }
  },
  {
    keywords: ['sad', 'depressed', 'hopeless'],
    response: {
      title: "You're Not Alone",
      message: "Many people feel this way. Talking about it can help lighten the burden.",
      action: {
        label: "Call Talian Kasih (15999)",
        onClick: () => window.open('tel:15999', '_self')
      }
    }
  }
];

interface SupportInterfaceProps {
  className?: string;
  compact?: boolean;
}

const SupportInterface = ({ className, compact = false }: SupportInterfaceProps) => {
  const [showDetails, setShowDetails] = useState(false);
  const [showHelplines, setShowHelplines] = useState(false);
  const { addNotification } = useNotifications();

  const handleSupportAction = (option: typeof SupportOptions[0]) => {
    if (option.action === '#crisis') {
      setShowHelplines(true);
      return;
    }
    
    if (option.action.startsWith('tel:')) {
      window.open(option.action, '_self');
    } else {
      window.location.href = option.action;
    }
    
    addNotification({
      type: 'support',
      title: 'Support Accessed',
      message: `Opening ${option.title}...`,
      duration: 3000
    });
  };

  const handleHelplineCall = (helpline: typeof malaysianHelplines[0], method: 'phone' | 'whatsapp') => {
    const number = method === 'phone' ? helpline.phone : helpline.whatsapp;
    const prefix = method === 'phone' ? 'tel:' : 'https://wa.me/';
    window.open(`${prefix}${number}`, '_self');
    
    addNotification({
      type: 'support',
      title: 'Connecting to Support',
      message: `Calling ${helpline.name}...`,
      duration: 3000
    });
  };

  const detectEmotionalRisk = (text: string) => {
    const lowerText = text.toLowerCase();
    for (const risk of EmotionalRiskResponses) {
      if (risk.keywords.some(keyword => lowerText.includes(keyword))) {
        return risk.response;
      }
    }
    return null;
  };

  if (compact) {
    return (
      <div className={cn("flex items-center gap-2", className)}>
        <Button
          variant="outline"
          size="sm"
          onClick={() => setShowDetails(!showDetails)}
          className="border-red-200 text-red-600 hover:bg-red-50"
        >
          <AlertTriangle className="w-4 h-4 mr-2" />
          Need Help?
        </Button>
        {showDetails && (
          <div className="flex gap-2">
            {SupportOptions.slice(0, 2).map((option) => (
              <Button
                key={option.title}
                variant="ghost"
                size="sm"
                onClick={() => handleSupportAction(option)}
                className={option.color}
              >
                <option.icon className="w-4 h-4" />
              </Button>
            ))}
          </div>
        )}
      </div>
    );
  }

  return (
    <div className={cn("space-y-4", className)}>
      <div className="text-center">
        <h3 className="text-lg font-semibold text-gray-900">Support & Resources</h3>
        <p className="text-sm text-gray-600 mt-1">We're here to help you through difficult moments</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {SupportOptions.map((option) => (
          <Card
            key={option.title}
            className={cn(
              "p-4 cursor-pointer transition-all hover:shadow-md border-2",
              option.bgColor,
              option.borderColor
            )}
            onClick={() => handleSupportAction(option)}
          >
            <div className="flex items-start gap-3">
              <div className={cn("p-2 rounded-lg bg-white", option.color)}>
                <option.icon className="w-5 h-5" />
              </div>
              <div className="flex-1">
                <h4 className="font-medium text-gray-900">{option.title}</h4>
                <p className="text-sm text-gray-600 mt-1">{option.description}</p>
              </div>
            </div>
          </Card>
        ))}
      </div>

      <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-amber-600 mt-0.5" />
          <div>
            <h4 className="font-medium text-amber-900">Emergency Support</h4>
            <p className="text-sm text-amber-800 mt-1">
              If you're in immediate crisis, please call 988 or go to your nearest emergency room.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SupportInterface;
