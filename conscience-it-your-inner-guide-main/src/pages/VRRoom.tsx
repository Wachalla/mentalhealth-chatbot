import React, { useState, useEffect, useRef } from "react";
import AppLayout from "@/components/AppLayout";
import QuickNav from "@/components/QuickNav";
import { X } from "lucide-react";
import { useLocation } from "react-router-dom";

type SpaceType = "forest" | "beach" | "sandy" | "mountain";

// Types for A-Frame elements (Required so TypeScript recognizes the 3D tags)
declare global {
  namespace JSX {
    interface IntrinsicElements {
      'a-scene': any;
      'a-sky': any;
      'a-light': any;
      'a-camera': any;
      'a-cursor': any;
      'a-circle': any;
      'a-text': any;
      'a-entity': any;
      'a-videosphere': any;
    }
  }
}

const VRRoom: React.FC = () => {
  const location = useLocation();
  const mode = (location.state?.mode as 'box' | 'deep' | 'mindful') || 'box';
  const [currentSpace, setCurrentSpace] = useState<SpaceType>("beach");
  const [isVRMode, setIsVRMode] = useState(false);
  const [fadeIn, setFadeIn] = useState(true);
  const [showInstructions, setShowInstructions] = useState(true);
  const [aframeReady, setAframeReady] = useState(false);
  const [sceneReady, setSceneReady] = useState(false);
  const [breathingPhase, setBreathingPhase] = useState<'Inhale' | 'Hold1' | 'Exhale' | 'Hold2'>('Inhale');
  const [currentText, setCurrentText] = useState(
    mode === 'deep' ? 'Deep Inhale' : 
    mode === 'mindful' ? 'Observe your breath...' : 
    'Breathe In'
  );
  const [currentScale, setCurrentScale] = useState(1);
  const sceneRef = useRef<any>(null);

  useEffect(() => {
    // Check if A-Frame is already loaded (either by npm package or previous load)
    if ((window as any).AFRAME) {
      console.log('A-Frame already loaded, using existing instance');
      setAframeReady(true);
      // Add delay to ensure A-Frame systems are fully initialized
      setTimeout(() => {
        setSceneReady(true);
      }, 500);
      return;
    }

    // Dynamically load A-Frame script with a unique ID to prevent conflicts
    const scriptId = 'aframe-dynamic-load';
    const existingScript = document.getElementById(scriptId);
    
    if (existingScript) {
      console.log('A-Frame script already exists, waiting for load');
      // If script exists but AFRAME not ready, wait for it
      const checkInterval = setInterval(() => {
        if ((window as any).AFRAME) {
          clearInterval(checkInterval);
          setAframeReady(true);
        }
      }, 100);
      
      // Safety timeout
      setTimeout(() => {
        clearInterval(checkInterval);
        setAframeReady(true);
      }, 3000);
      
      return;
    }

    // Create and append new script
    const script = document.createElement('script');
    script.id = scriptId;
    script.src = 'https://aframe.io/releases/1.6.0/aframe.min.js';
    script.async = true;
    script.crossOrigin = 'anonymous';
    
    script.onload = () => {
      console.log('A-Frame loaded successfully from CDN');
      setAframeReady(true);
      // Add delay to ensure A-Frame systems are fully initialized
      setTimeout(() => {
        setSceneReady(true);
      }, 500);
    };
    
    script.onerror = () => {
      console.error('Failed to load A-Frame from CDN');
      setAframeReady(true); // Force ready to prevent infinite loading
    };
    
    document.head.appendChild(script);

    // Safety timeout: force ready after 3 seconds
    const safetyTimeout = setTimeout(() => {
      if (!aframeReady) {
        console.warn('A-Frame loading timeout, forcing ready state');
        setAframeReady(true);
      }
    }, 3000);

    // Hide instructions after 8 seconds
    const timer = setTimeout(() => setShowInstructions(false), 8000);
    
    return () => {
      clearTimeout(timer);
      clearTimeout(safetyTimeout);
      // Don't remove the script as it might be needed by other components
    };
  }, [aframeReady]);

  useEffect(() => {
    const scene = sceneRef.current;
    if (!scene) return;

    const handleEnterVR = () => setIsVRMode(true);
    const handleExitVR = () => setIsVRMode(false);

    // A-Frame emits 'enter-vr' and 'exit-vr' events
    scene.addEventListener("enter-vr", handleEnterVR);
    scene.addEventListener("exit-vr", handleExitVR);

    return () => {
      scene.removeEventListener("enter-vr", handleEnterVR);
      scene.removeEventListener("exit-vr", handleExitVR);
    };
  }, []);

  // Breathing Logic for different modes
  useEffect(() => {
    let interval: NodeJS.Timeout;
    
    if (mode === 'box') {
      // Box Breathing: 4-4-4-4
      interval = setInterval(() => {
        setBreathingPhase((prevPhase) => {
          switch (prevPhase) {
            case 'Inhale':
              setCurrentText('Hold');
              setCurrentScale(2);
              return 'Hold1';
            case 'Hold1':
              setCurrentText('Breathe Out');
              setCurrentScale(1);
              return 'Exhale';
            case 'Exhale':
              setCurrentText('Hold');
              setCurrentScale(1);
              return 'Hold2';
            case 'Hold2':
              setCurrentText('Breathe In');
              setCurrentScale(2);
              return 'Inhale';
            default:
              return 'Inhale';
          }
        });
      }, 4000);
    } else if (mode === 'deep') {
      // Deep Diaphragmatic: 5-4-6
      interval = setInterval(() => {
        setBreathingPhase((prevPhase) => {
          switch (prevPhase) {
            case 'Inhale':
              setCurrentText('Pause');
              setCurrentScale(2.5); // Larger for belly expansion
              return 'Hold1';
            case 'Hold1':
              setCurrentText('Slow Exhale');
              setCurrentScale(1);
              return 'Exhale';
            case 'Exhale':
              setCurrentText('Deep Inhale');
              setCurrentScale(2.5);
              return 'Inhale';
            default:
              return 'Inhale';
          }
        });
      }, mode === 'deep' ? 
        (breathingPhase === 'Inhale' ? 5000 : breathingPhase === 'Hold1' ? 4000 : 6000) : 4000);
    } else if (mode === 'mindful') {
      // Mindful Breathing: Gentle pulsing, no strict timer
      setCurrentText('Observe your breath...');
      interval = setInterval(() => {
        setCurrentScale((prev) => prev === 1 ? 1.8 : 1); // Gentle pulse
      }, 6000);
    }

    return () => clearInterval(interval);
  }, [mode, breathingPhase]);

  const handleSpaceChange = (space: SpaceType) => {
    setFadeIn(false);
    setTimeout(() => {
      setCurrentSpace(space);
      setFadeIn(true);
    }, 300);
  };

  return (
    <AppLayout>
      <div className="relative w-full h-full bg-black">
        {/* Navigation Overlay */}
        <div className="absolute top-4 left-4 z-40">
          <QuickNav showBackButton backPath="/" />
        </div>

        {/* Loading overlay - fades out when A-Frame is ready */}
        <div 
          className={`absolute inset-0 z-50 flex items-center justify-center bg-black transition-opacity duration-500 ${
            aframeReady ? 'opacity-0 pointer-events-none' : 'opacity-100'
          }`}
        >
          <div className="text-white text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
            <p>Loading VR Environment...</p>
          </div>
        </div>
      
      {/* Scene always renders, hidden behind overlay until ready */}
      <a-scene
        ref={sceneRef}
        vr-mode-ui="enabled: true"
        style={{ width: "100%", height: "100%" }}
        className={fadeIn ? "opacity-100" : "opacity-0"}
      >
        {/* Sky and Lighting - Dynamic video backgrounds */}
        <a-videosphere 
          src={
            currentSpace === "forest" ? "/videos/forest-360.mp4" :
            currentSpace === "beach" ? "/videos/beach-360.mp4" :
            currentSpace === "sandy" ? "/videos/desert-360.mp4" :
            currentSpace === "mountain" ? "/videos/mountain-360.mp4" :
            "/videos/beach-360.mp4"
          } 
          autoplay="true"
          loop="true"
        />

        {/* Breathing Guide */}
        <a-entity position="0 1.6 -3">
          <a-entity
            scale={`${currentScale} ${currentScale} 1`}
            geometry="primitive: circle; radius: 0.5"
            material="color: #E0F7FA; transparent: true; opacity: 0.4"
          />
          <a-entity
            scale={`${currentScale} ${currentScale} 1`}
            geometry="primitive: circle; radius: 0.5"
            material="color: #E0F7FA; transparent: true; opacity: 0.2"
          />
          
          <a-text
            value={currentText}
            align="center"
            color="#FFF"
            width={10}
            position="0 0 0.1"
            scale="2 2 2"
            font="roboto"
            shader="msdf"
          />
        </a-entity>

        {/* Camera */}
        <a-camera>
          <a-cursor />
        </a-camera>
      </a-scene>

      {/* Instructions overlay */}
      {showInstructions && aframeReady && (
        <div className="absolute top-4 left-4 bg-black bg-opacity-50 text-white p-4 rounded-lg max-w-sm pointer-events-none">
          <h3 className="text-lg font-semibold mb-2">Welcome to Your Calm Space</h3>
          <p className="text-sm mb-2">Put on your VR headset and press the VR button to enter immersive mode.</p>
          <p className="text-sm">Use the buttons below to switch between different serene environments.</p>
        </div>
      )}

      {/* VR Mode Indicator */}
      {isVRMode && (
        <div className="absolute top-4 right-4 bg-green-500 text-white px-3 py-1 rounded-full text-sm">
          VR Mode Active
        </div>
      )}

      {/* Environment selector */}
      {aframeReady && (
        <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 flex gap-2 bg-black bg-opacity-50 p-2 rounded-lg">
          {(['forest', 'beach', 'sandy', 'mountain'] as SpaceType[]).map((space) => (
            <button
              key={space}
              onClick={() => handleSpaceChange(space)}
              className={`px-4 py-2 rounded transition-colors ${
                currentSpace === space
                  ? "bg-blue-500 text-white"
                  : "bg-gray-700 text-gray-300 hover:bg-gray-600"
              }`}
            >
              {space.charAt(0).toUpperCase() + space.slice(1)}
            </button>
          ))}
        </div>
      )}

      {/* Instructions toggle */}
      {aframeReady && (
        <button
          onClick={() => setShowInstructions(!showInstructions)}
          className="absolute top-4 right-4 bg-gray-700 text-white p-2 rounded hover:bg-gray-600"
        >
          {showInstructions ? "Hide" : "Show"} Instructions
        </button>
      )}
      </div>
    </AppLayout>
  );
};

export default VRRoom;
