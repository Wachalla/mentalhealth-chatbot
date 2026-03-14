// WebXR VR Client for CONSCIENCE
export class VRClient {
  private ws: WebSocket | null = null
  private user_id: string
  private isVRAvailable: boolean = false
  private emotionalState: string = 'neutral'
  private reconnectAttempts: number = 0
  private maxReconnectAttempts: number = 5

  constructor(user_id: string) {
    this.user_id = user_id
    this.checkWebXRAvailability()
  }

  private checkWebXRAvailability(): void {
    if ('xr' in navigator) {
      (navigator as any).xr?.isSessionSupported('immersive-vr')
        .then((supported: boolean) => {
          this.isVRAvailable = supported
          console.log('VR Support:', supported)
        })
        .catch((error: any) => {
          console.error('VR Support check failed:', error)
          this.isVRAvailable = false
        })
    } else {
      console.log('WebXR not supported in this browser')
      this.isVRAvailable = false
    }
  }

  async connect(): Promise<boolean> {
    if (!this.isVRAvailable) {
      console.error('VR not available')
      return false
    }

    try {
      // Get WebSocket URL from environment
      const wsUrl = `${(import.meta as any).env.VITE_API_BASE_URL?.replace('http', 'ws') || 'ws://localhost:8000'}/ws/vr/${this.user_id}`
      
      console.log('Connecting to VR WebSocket:', wsUrl)
      
      this.ws = new WebSocket(wsUrl)
      
      return new Promise((resolve, reject) => {
        this.ws!.onopen = () => {
          console.log('VR WebSocket connected')
          this.reconnectAttempts = 0
          
          // Send initial connection message
          this.sendMessage({
            type: 'vr_client_connected',
            device: this.getVRDeviceInfo(),
            capabilities: this.getVRCapabilities()
          })
          
          resolve(true)
        }

        this.ws!.onmessage = (event: MessageEvent) => {
          try {
            const message = JSON.parse(event.data)
            this.handleMessage(message)
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error)
          }
        }

        this.ws!.onclose = () => {
          console.log('VR WebSocket disconnected')
          this.attemptReconnect()
          reject(new Error('WebSocket disconnected'))
        }

        this.ws!.onerror = (error: Event) => {
          console.error('VR WebSocket error:', error)
          reject(error)
        }

        // Connection timeout
        setTimeout(() => {
          if (this.ws?.readyState === WebSocket.CONNECTING) {
            reject(new Error('Connection timeout'))
          }
        }, 10000)
      })
    } catch (error) {
      console.error('VR connection failed:', error)
      return false
    }
  }

  private async attemptReconnect(): Promise<void> {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached')
      return
    }

    this.reconnectAttempts++
    console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})`)
    
    // Exponential backoff
    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000)
    await new Promise(resolve => setTimeout(resolve, delay))
    
    await this.connect()
  }

  private handleMessage(message: any): void {
    switch (message.type) {
      case 'ai_response':
        this.handleAIResponse(message)
        break
      case 'breathing_guidance':
        this.handleBreathingGuidance(message)
        break
      case 'environment_change':
        this.handleEnvironmentChange(message)
        break
      case 'therapeutic_prompt':
        this.handleTherapeuticPrompt(message)
        break
      default:
        console.log('Unknown message type:', message.type)
    }
  }

  private handleAIResponse(message: any): void {
    console.log('AI Response:', message.response)
    
    // Display AI response in VR environment
    this.displayMessageInVR(message.response, 'ai', {
      approach: message.therapeutic_approach,
      confidence: message.confidence,
      suggestions: message.suggestions
    })
  }

  private handleBreathingGuidance(message: any): void {
    console.log('Breathing guidance:', message)
    
    // Update breathing exercise in VR
    this.updateBreathingExercise(message.technique, message.duration)
  }

  private handleEnvironmentChange(message: any): void {
    console.log('Environment change:', message.environment)
    
    // Change VR environment
    this.changeVREnvironment(message.environment)
  }

  private handleTherapeuticPrompt(message: any): void {
    console.log('Therapeutic prompt:', message.prompt)
    
    // Display therapeutic prompt in VR
    this.displayMessageInVR(message.prompt, 'therapist', {
      urgency: message.urgency || 'normal'
    })
  }

  private displayMessageInVR(text: string, type: string, metadata: any = {}): void {
    // This would integrate with your VR framework (A-Frame, Three.js, etc.)
    console.log(`VR Display [${type}]:`, text, metadata)
    
    // Example: Update UI elements in VR space
    this.updateVRUI({
      text,
      type,
      timestamp: new Date().toISOString(),
      metadata
    })
  }

  private updateBreathingExercise(technique: string, duration: number): void {
    console.log(`Starting breathing exercise: ${technique} for ${duration}s`)
    
    // Update VR breathing visualization
    this.updateBreathingVisualization(technique, duration)
  }

  private changeVREnvironment(environment: string): void {
    console.log(`Changing VR environment to: ${environment}`)
    
    // Update VR scene/environment
    this.updateVRScene(environment)
  }

  private updateVRUI(message: any): void {
    // This would update UI elements in your VR scene
    // Implementation depends on your VR framework
    console.log('VR UI Update:', message)
  }

  private updateBreathingVisualization(technique: string, duration: number): void {
    // Update breathing circle animation in VR
    console.log(`Breathing visualization: ${technique} - ${duration}s`)
    
    // Emit event to VR scene
    this.emitVREvent('breathing_start', { technique, duration })
  }

  private updateVRScene(environment: string): void {
    // Change VR scene (beach, forest, etc.)
    console.log(`VR Scene change: ${environment}`)
    
    // Emit event to VR scene
    this.emitVREvent('scene_change', { environment })
  }

  private emitVREvent(eventType: string, data: any): void {
    // Emit custom event to VR scene
    const event = new CustomEvent(eventType, { detail: data })
    document.dispatchEvent(event)
  }

  private getVRDeviceInfo(): any {
    return {
      userAgent: navigator.userAgent,
      platform: navigator.platform,
      vrSupport: this.isVRAvailable,
      webXRSupported: 'xr' in navigator
    }
  }

  private getVRCapabilities(): any {
    return {
      immersiveVR: this.isVRAvailable,
      handTracking: this.checkHandTrackingSupport(),
      eyeTracking: this.checkEyeTrackingSupport(),
      spatialAudio: this.checkSpatialAudioSupport()
    }
  }

  private checkHandTrackingSupport(): boolean {
    // Check for hand tracking capabilities
    return 'xr' in navigator && 
           (navigator as any).xr?.requestSession?.call?.toString().includes('hand-tracking')
  }

  private checkEyeTrackingSupport(): boolean {
    // Check for eye tracking capabilities
    return 'xr' in navigator && 
           (navigator as any).xr?.requestSession?.call?.toString().includes('eye-tracking')
  }

  private checkSpatialAudioSupport(): boolean {
    // Check for spatial audio capabilities
    return 'xr' in navigator && 
           (navigator as any).xr?.requestSession?.call?.toString().includes('spatial-audio')
  }

  // Public methods for VR interaction
  public sendEmotionalState(emotion: string, intensity: number): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.error('WebSocket not connected')
      return
    }

    this.emotionalState = emotion
    
    this.sendMessage({
      type: 'emotional_state_update',
      emotion,
      intensity,
      timestamp: new Date().toISOString()
    })
  }

  public completeBreathingExercise(technique: string, effectiveness: number): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.error('WebSocket not connected')
      return
    }

    this.sendMessage({
      type: 'breathing_complete',
      technique,
      effectiveness,
      timestamp: new Date().toISOString()
    })
  }

  public requestAIGuidance(message: string, emotion: string): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.error('WebSocket not connected')
      return
    }

    this.sendMessage({
      type: 'ai_request',
      message,
      emotion,
      timestamp: new Date().toISOString()
    })
  }

  private sendMessage(message: any): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message))
    }
  }

  public disconnect(): void {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  public isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN
  }
}

// VR Device Detection
export const detectVRDevice = (): string => {
  const userAgent = navigator.userAgent
  
  if (userAgent.includes('Oculus')) {
    if (userAgent.includes('Quest 3')) return 'Meta Quest 3'
    if (userAgent.includes('Quest 2')) return 'Meta Quest 2'
    if (userAgent.includes('Quest')) return 'Meta Quest'
  }
  
  if (userAgent.includes('HTC Vive')) return 'HTC Vive'
  if (userAgent.includes('Valve Index')) return 'Valve Index'
  
  return 'Desktop'
}

// VR Session Management
export const startVRSession = async (user_id: string): Promise<VRClient> => {
  const client = new VRClient(user_id)
  
  // Request VR session if available
  if ('xr' in navigator) {
    try {
      const session = await (navigator as any).xr.requestSession('immersive-vr', {
        optionalFeatures: ['local-floor', 'bounded-floor']
      })
      
      console.log('VR Session started:', session)
      
      // Connect WebSocket after VR session is established
      await client.connect()
      
      return client
    } catch (error) {
      console.error('VR Session failed:', error)
      return client
    }
  } else {
    console.log('WebXR not available, using desktop mode')
    await client.connect()
    return client
  }
}
