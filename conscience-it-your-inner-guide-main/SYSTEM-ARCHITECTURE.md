# 🏗️ CONSCIENCE System Architecture Overview

## 🎯 Architecture Summary

**Frontend**: Vite + React + WebXR VR Support
**Backend**: FastAPI with WebSocket + JWT Verification  
**Authentication**: Supabase Auth (Identity Provider Only)
**Databases**: PostgreSQL (Structured) + Weaviate (Vector)


## 🔄 Data Flow Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend    │    │   FastAPI     │    │  PostgreSQL    │
│   (React)     │◄──►│   (Backend)    │◄──►│ (Structured)   │
│               │    │               │    │               │
│   WebXR       │    │   WebSocket    │    │   Mood Logs    │
│   VR Client    │◄──►│   Real-time    │◄──►│   Users         │
│               │    │   Communication│    │   Goals         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ▲                        ▲
    │                        │
    ▼                        ▼
┌─────────────────┐    ┌─────────────────┐
│  Supabase     │    │   Weaviate     │
│  Auth Only     │◄──►│   Vector DB     │
│                │    │   Semantic      │
│  OAuth + JWT   │    │   Search       │
│                │    │   Embeddings    │
└─────────────────┘    └─────────────────┘
```

---

## 🔐 Authentication Architecture

### Supabase (Identity Provider)
- **OAuth Providers**: Google, Apple, GitHub, X (Twitter)
- **JWT Management**: Token signing, verification, refresh
- **Session Handling**: Persistent sessions, automatic cleanup
- **Security**: No passwords stored, OAuth tokens never reach backend

### Backend JWT Verification
```python
def verify_supabase_token(credentials):
    token = credentials.credentials
    payload = jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=["HS256"])
    
    if payload.get("exp") < datetime.now().timestamp():
        raise HTTPException(status_code=401, detail="Token expired")
    
    return payload  # Contains user_id, email, etc.
```

### Frontend Authentication Flow
```typescript
// OAuth Login
const { data, error } = await supabase.auth.signInWithOAuth({
  provider: 'google',
  options: { redirectTo: 'http://localhost:8081/auth/callback' }
})

// Get JWT for API
const { session } = await supabase.auth.getSession()
const token = session.access_token
```

---

## 📊 Database Separation

### PostgreSQL (Structured Data)
**Purpose**: ACID-compliant transactional storage
**Tables**:
- `users` - User profiles, preferences
- `mood_logs` - Emotional tracking with scores
- `goals` - Therapy milestones, progress
- `vr_sessions` - Immersive session tracking
- `audit_logs` - Security, compliance events

**Why PostgreSQL**:
- **Reliability**: 30+ years production stability
- **Consistency**: ACID guarantees prevent data corruption
- **Complex Queries**: Joins, transactions, constraints
- **Compliance**: Audit trails, GDPR requirements

### Weaviate (Vector Data)
**Purpose**: Semantic similarity search and AI memory
**Schema**:
```json
{
  "class": "EmotionalMemory",
  "properties": {
    "user_id": "string",
    "emotion": "string", 
    "message": "text",
    "context": "text",
    "timestamp": "date",
    "intensity": "number",
    "memory_type": "string"
  },
  "vectorIndexType": "hnsw"
}
```

**Why Weaviate**:
- **Semantic Search**: Find similar emotional states
- **AI-Native**: Built for machine learning workflows
- **Performance**: Optimized for vector operations
- **RAG Support**: Perfect for conversational context

---

## 🥽 VR Integration

### WebXR Support
**Devices**: Meta Quest 2/3, HTC Vive, Valve Index
**Features**:
- **Immersive VR**: Full 360° environments
- **Hand Tracking**: Natural gesture control
- **Spatial Audio**: 3D therapeutic audio
- **Session Management**: Persistent VR connections

### WebSocket Real-time Communication
```typescript
// VR Client Connection
const vrClient = new VRClient(userId)
await vrClient.connect()

// Send emotional state
vrClient.sendEmotionalState('calm', 0.3)

// Complete breathing exercise
vrClient.completeBreathingExercise('box_breathing', 0.8)
```

### Backend WebSocket Handler
```python
@app.websocket("/ws/vr/{user_id}")
async def vr_websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    
    while True:
        data = await websocket.receive_text()
        message = json.loads(data)
        
        if message.get("type") == "emotional_state_update":
            # Process emotional state
            ai_response = await ai_processor.process_message(...)
            
            await manager.send_personal_message(user_id, {
                "type": "ai_response",
                "response": ai_response.response
            })
```

---

## 🤖 AI Processing Layer

### Modular Architecture
```python
class AIProcessor:
    def __init__(self):
        self.mock_mode = os.getenv("MOCK_AI", "true").lower() == "true"
    
    async def process_message(self, user_id, message, emotion=None):
        if self.mock_mode:
            # Development mode with canned responses
            return AIResponse(
                response="I understand you're feeling anxious. Let's try breathing.",
                therapeutic_approach="supportive_listening",
                confidence=0.85,
                suggestions=["Deep breathing", "Grounding technique"]
            )
        else:
            # TODO: Integrate Llama model
            return await llama_model.generate_response(...)
```

### Integration Points
- **Frontend → Backend**: REST API with JWT auth
- **Backend → Weaviate**: Store conversation embeddings
- **Backend → Frontend**: WebSocket real-time updates
- **VR → Backend**: Emotional state, breathing completion

---

## 🚀 Infrastructure

### Docker Compose Services
```yaml
services:
  fastapi:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql://...
      - WEAVIATE_URL=http://weaviate:8080
      - SUPABASE_JWT_SECRET=...
    ports: ["8000:8000"]
    depends_on: [postgres, weaviate]
  
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: conscience_db
      POSTGRES_USER: conscience_user
    volumes: [postgres_data:/var/lib/postgresql/data]
    ports: ["5432:5432"]
  
  weaviate:
    image: semitechnologies/weaviate:1.24.4
    environment:
      AUTHENTICATION_APIKEY_ENABLED: 'true'
      PERSISTENCE_DATA_PATH: /var/lib/weaviate
    ports: ["8080:8080", "50051:50051"]
    depends_on: [text2vec-transformers]
```

### Kubernetes Ready Structure
- **Separate Services**: Each container independently scalable
- **Persistent Volumes**: Data persistence across deployments
- **Internal Networking**: Service isolation and security
- **Health Checks**: Service monitoring and auto-restart
- **Environment Variables**: Secret management via Kubernetes secrets

---

## 🛡️ Security Model

### Authentication Security
1. **Supabase**: Handles all credential security
2. **JWT Verification**: Cryptographic token validation
3. **HTTPS Required**: Production SSL/TLS termination
4. **Rate Limiting**: API abuse prevention
5. **Input Validation**: Pydantic model validation
6. **CORS Configuration**: Proper cross-origin setup

### Data Security
- **Encryption**: PostgreSQL connections, Weaviate API
- **No Password Storage**: Supabase handles credential security
- **Audit Logging**: All authentication events tracked
- **Session Isolation**: User data properly separated

---

## 📱 User Experience Flow

### 1. Authentication
1. User visits app
2. Clicks "Continue with Google"
3. Redirects to Supabase OAuth
4. Google authentication
5. Supabase creates JWT token
6. Redirect back to app with token
7. Frontend stores token, creates user in PostgreSQL

### 2. VR Experience
1. User puts on VR headset
2. WebXR session starts
3. WebSocket connects to backend
4. Real-time emotional state updates
5. AI provides therapeutic guidance
6. Breathing exercises with visual feedback

### 3. Data Flow
1. **Mood Entry**: PostgreSQL + Weaviate embedding
2. **Conversation**: Weaviate semantic search + PostgreSQL metadata
3. **VR Session**: PostgreSQL logs + WebSocket real-time
4. **AI Processing**: Mock responses → Llama integration

---

## 🔧 Development vs Production

### Development
```bash
# Frontend
VITE_SUPABASE_URL=https://dev.supabase.co
VITE_API_BASE_URL=http://localhost:8000
MOCK_AI=true

# Backend
DEBUG=true
DATABASE_URL=postgresql://localhost:5432/conscience_db
```

### Production
```bash
# Frontend
VITE_SUPABASE_URL=https://prod.supabase.co
VITE_API_BASE_URL=https://api.conscience.app
MOCK_AI=false

# Backend
DEBUG=false
DATABASE_URL=postgresql://prod-host:5432/conscience_db
SUPABASE_JWT_SECRET=${KUBERNETES_SECRET}
```

---

## 🎯 Key Benefits

1. **Clear Separation**: Each service has single responsibility
2. **Scalability**: Independent scaling of components
3. **Security**: Professional-grade authentication and data protection
4. **VR-Ready**: Full WebXR support with real-time communication
5. **AI-Ready**: Modular AI service with easy model swapping
6. **Production-Ready**: Kubernetes-ready infrastructure
7. **Compliance**: GDPR, HIPAA considerations built-in

This architecture provides enterprise-grade mental health infrastructure with clear separation of concerns and modern VR capabilities.
