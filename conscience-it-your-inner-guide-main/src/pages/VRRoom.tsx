import React, { useState, useEffect, useRef } from "react";
import AppLayout from "@/components/AppLayout";
import QuickNav from "@/components/QuickNav";
import { X, Monitor, Headphones } from "lucide-react";
import { useLocation } from "react-router-dom";
import { apiFetch } from "@/lib/api";
import { SAMPLE_ACTIVITIES } from "@/types/activities";

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
  const locationState = (location.state || {}) as {
    mode?: 'box' | 'deep' | 'mindful';
    activityId?: string;
    activitySessionId?: string;
    recommendedSource?: string;
  };
  const mode = locationState.mode || 'box';
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
  const [vrDevices, setVrDevices] = useState<any[]>([]);
  const [selectedDevice, setSelectedDevice] = useState<string>('');
  const [showDeviceSelector, setShowDeviceSelector] = useState(false);
  const [vrSessionId, setVrSessionId] = useState<string | null>(null);
  const sceneRef = useRef<any>(null);
  const vrSessionIdRef = useRef<string | null>(null);
  const currentSpaceRef = useRef<SpaceType>("beach");
  const sessionStartedAtRef = useRef<number | null>(null);
  const completionSubmittedRef = useRef(false);

  useEffect(() => {
    vrSessionIdRef.current = vrSessionId;
  }, [vrSessionId]);

  useEffect(() => {
    currentSpaceRef.current = currentSpace;
  }, [currentSpace]);

  useEffect(() => {
    let isMounted = true;

    const createVREntry = async () => {
      try {
        const session = await apiFetch<{ id: string }>("/vr/session", {
          method: "POST",
          body: JSON.stringify({
            environment: currentSpace,
            breathing_technique: mode,
            emotional_state: mode,
          }),
        });

        if (!isMounted) return;

        setVrSessionId(session.id);
        sessionStartedAtRef.current = Date.now();
      } catch (error) {
        console.error("Failed to create VR session entry", error);
      }
    };

    createVREntry();

    return () => {
      isMounted = false;
    };
  }, []);

  useEffect(() => {
    return () => {
      void finalizeSession();
    };
  }, []);

  useEffect(() => {
    // Check if A-Frame is already loaded (either by npm package or previous load)
    if ((window as any).AFRAME) {
      console.log('A-Frame already loaded, using existing instance');
      setAframeReady(true);
      // Add delay to ensure A-Frame systems are fully initialized
      setTimeout(() => {
        setSceneReady(true);
      }, 1000);
    } else {
      // Load A-Frame script dynamically
      const script = document.createElement('script');
      script.src = 'https://aframe.io/releases/1.5.0/aframe.min.js';
      script.async = true;
      
      script.onload = () => {
        console.log('A-Frame loaded successfully');
        setAframeReady(true);
        // Additional delay for A-Frame systems to initialize
        setTimeout(() => {
          setSceneReady(true);
        }, 1000);
      };
      
      script.onerror = () => {
        console.error('Failed to load A-Frame');
      };
      
      document.head.appendChild(script);
    }
  }, []);

  useEffect(() => {
    const detectVRDevices = async () => {
      const devices = [];
      
      // Check for WebXR support
      if ('xr' in navigator) {
        try {
          const isVRSupported = await (navigator as any).xr.isSessionSupported('immersive-vr');
          if (isVRSupported) {
            devices.push({ name: 'WebXR VR Device', type: 'webxr' });
            if (!selectedDevice) {
              setSelectedDevice('WebXR VR Device');
            }
          }
        } catch (error) {
          console.log('WebXR detection failed:', error);
        }
      }
      
      // Add desktop option
      devices.push({ name: 'Desktop Mode', type: 'desktop' });
      if (!selectedDevice) {
        setSelectedDevice('Desktop Mode');
      }
      
      setVrDevices(devices);
    };

    if (aframeReady) {
      detectVRDevices();
    }
  }, [aframeReady, selectedDevice]);

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

  const finalizeSession = async () => {
    if (completionSubmittedRef.current || !vrSessionIdRef.current || !sessionStartedAtRef.current) {
      return;
    }

    completionSubmittedRef.current = true;
    const durationMinutes = Math.max(1, Math.round((Date.now() - sessionStartedAtRef.current) / 60000));

    try {
      await apiFetch(`/vr/session/${vrSessionIdRef.current}/complete`, {
        method: "POST",
        body: JSON.stringify({
          duration_minutes: durationMinutes,
          completion_rate: 100,
          notes: `${mode} breathing session in ${currentSpaceRef.current}`,
        }),
      });
    } catch (error) {
      console.error("Failed to complete VR session", error);
    }

    if (locationState.activitySessionId && locationState.activityId) {
      const linkedActivity = SAMPLE_ACTIVITIES.find((activity) => activity.id === locationState.activityId);

      if (linkedActivity) {
        try {
          await apiFetch("/activities/complete", {
            method: "POST",
            body: JSON.stringify({
              session_id: locationState.activitySessionId,
              activity_id: linkedActivity.id,
              title: linkedActivity.title,
              category: linkedActivity.category,
              duration_minutes: linkedActivity.duration,
              recommended_source: locationState.recommendedSource || "vr_room",
            }),
          });
        } catch (error) {
          console.error("Failed to complete linked activity session", error);
        }
      }
    }
  };

  const enterVR = async () => {
    try {
      if (!("xr" in navigator)) {
        const scene = sceneRef.current;
        if (scene && scene.enterVR) {
          scene.enterVR();
          return;
        }
        return;
      }

      const session = await (navigator as any).xr.requestSession("immersive-vr", {
        optionalFeatures: ["local-floor", "bounded-floor"],
      });

      console.log("VR session started:", session);
      setIsVRMode(true);

      session.addEventListener("end", () => {
        console.log("VR session ended");
        setIsVRMode(false);
        void finalizeSession();
      });
    } catch (error) {
      console.error("Failed to start VR session:", error);
      const scene = sceneRef.current;
      if (scene && scene.enterVR) {
        scene.enterVR();
      }
    }
  };

  const exitVR = async () => {
    try {
      const session = await (navigator as any).xr?.getSession();
      if (session) {
        await session.end();
      }
      setIsVRMode(false);
      await finalizeSession();
    } catch (error) {
      console.error('Failed to exit VR:', error);
    }
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

      {/* VR Device Selector */}
      {aframeReady && (
        <div className="absolute top-16 right-4 z-40">
          <button
            onClick={() => setShowDeviceSelector(!showDeviceSelector)}
            className="bg-gray-800 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors flex items-center gap-2"
          >
            <Monitor className="w-4 h-4" />
            <span className="text-sm">
              {selectedDevice || 'Select Device'}
            </span>
          </button>
          
          {showDeviceSelector && (
            <div className="absolute top-full right-0 mt-2 w-64 bg-gray-800 border border-gray-600 rounded-lg shadow-xl">
              <div className="p-2">
                <h3 className="text-white font-semibold mb-2 text-sm">VR Devices</h3>
                <button
                  onClick={() => {
                    setSelectedDevice('Desktop Mode');
                    setShowDeviceSelector(false);
                  }}
                  className={`w-full text-left px-3 py-2 rounded text-sm transition-colors flex items-center gap-2 ${
                    selectedDevice === 'Desktop Mode'
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                  }`}
                >
                  <Monitor className="w-4 h-4" />
                  <span>Desktop Mode</span>
                </button>
                <button
                  onClick={() => {
                    setSelectedDevice('VR Headset');
                    setShowDeviceSelector(false);
                  }}
                  className={`w-full text-left px-3 py-2 rounded text-sm transition-colors flex items-center gap-2 ${
                    selectedDevice === 'VR Headset'
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                  }`}
                >
                  <Headphones className="w-4 h-4" />
                  <span>VR Headset</span>
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* VR Entry Button */}
      {aframeReady && !isVRMode && (
        <div className="absolute top-32 right-4 z-40">
          <button
            onClick={enterVR}
            className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-lg transition-colors flex items-center gap-2 shadow-lg"
            disabled={!('xr' in navigator)}
          >
            <Headphones className="w-5 h-5" />
            <span className="font-medium">Enter VR Mode</span>
          </button>
        </div>
      )}

      {/* VR Exit Button */}
      {isVRMode && (
        <div className="absolute top-32 right-4 z-40">
          <button
            onClick={exitVR}
            className="bg-red-600 hover:bg-red-700 text-white px-6 py-3 rounded-lg transition-colors flex items-center gap-2 shadow-lg"
          >
            <X className="w-5 h-5" />
            <span className="font-medium">Exit VR</span>
          </button>
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
