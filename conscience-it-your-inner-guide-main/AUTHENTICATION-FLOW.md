# 🔐 CONSCIENCE Authentication Flow

## 🏗️ Architecture Overview

**Clear Separation of Responsibilities:**
- **Supabase** → Identity provider + session management ONLY
- **PostgreSQL** → Structured data (mood logs, goals, preferences)
- **Weaviate** → Emotional memory embeddings
- **FastAPI** → Backend API with JWT verification

## 🔄 Authentication Flow

### 1. User Login (Frontend)
```
User clicks "Continue with Google" 
→ Supabase OAuth flow 
→ Google authentication 
→ Supabase creates session 
→ Frontend receives JWT token
→ Redirect back to app
```

### 2. Token Verification (Backend)
```
Frontend sends request with Authorization: Bearer <JWT>
→ FastAPI middleware extracts token
→ Verify JWT with Supabase JWT Secret
→ Extract user_id and email from payload
→ Check token expiration
→ Allow access to protected routes
```

### 3. User Creation (Database)
```
First-time user login
→ Backend extracts Supabase user_id
→ Check PostgreSQL for existing user
→ If not found, create user record:
  - id: UUID (self-hosted)
  - supabase_user_id: from JWT
  - email: from JWT
  - created_at: timestamp
→ Return user data to frontend
```

## 🔒 Security Model

### Why Backend Trusts Supabase

1. **Cryptographic Verification**: JWT tokens signed with Supabase's secret key
2. **Expiration Checks**: Tokens expire automatically
3. **Audience Validation**: Tokens must be for "authenticated" audience
4. **No Password Storage**: Supabase handles all credential security
5. **OAuth Security**: Supabase manages OAuth token security

### Token Structure
```json
{
  "aud": "authenticated",
  "exp": 1640995200,
  "sub": "supabase-user-uuid",
  "email": "user@example.com",
  "role": "authenticated",
  "iat": 1640991600
}
```

## 🚀 Implementation Details

### Frontend (React + Vite)
```typescript
// Supabase Client Setup
import { createClient } from '@supabase/supabase-js'
export const supabase = createClient(url, key, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    flowType: 'pkce'
  }
})

// OAuth Login
const { data, error } = await supabase.auth.signInWithOAuth({
  provider: 'google',
  options: {
    redirectTo: 'http://localhost:8081/auth/callback'
  }
})

// Get JWT for Backend
const { session } = await supabase.auth.getSession()
const token = session.access_token
```

### Backend (FastAPI)
```python
# JWT Verification Middleware
def verify_supabase_token(credentials: HTTPAuthorizationCredentials):
    token = credentials.credentials
    payload = jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=["HS256"])
    
    if payload.get("exp") < datetime.now().timestamp():
        raise HTTPException(status_code=401, detail="Token expired")
    
    return payload

# Protected Route
@app.get("/me")
async def get_current_user(payload: Dict = Depends(verify_supabase_token)):
    supabase_user_id = payload.get("sub")
    email = payload.get("email")
    user = get_or_create_user(supabase_user_id, email)
    return user
```

## 📊 Database Schema

### PostgreSQL Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    supabase_user_id UUID UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**Important:**
- ✅ Store `supabase_user_id` for reference
- ❌ NEVER store passwords
- ❌ NEVER store OAuth tokens
- ✅ Use Supabase for all auth operations

## 🔄 Session Management

### Frontend Session
```typescript
// Auto-refresh tokens
supabase.auth.onAuthStateChange((event, session) => {
  if (event === 'SIGNED_IN') {
    // User logged in
    const token = session.access_token
    // Store for API calls
  }
  if (event === 'SIGNED_OUT') {
    // User logged out
    // Clear local state
  }
})
```

### Backend Session
```python
# Stateless verification
# Each request includes JWT token
# Backend verifies token on each request
# No session storage needed on backend
```

## 🛡️ Security Benefits

1. **Credential Isolation**: Supabase handles all credential security
2. **Token Security**: JWT tokens are cryptographically signed
3. **Automatic Expiration**: Tokens expire automatically
4. **OAuth Security**: OAuth tokens never reach your backend
5. **Audit Trail**: All authentication events logged by Supabase
6. **Compliance**: GDPR, CCPA compliant with Supabase

## 🚀 Quick Start

### 1. Setup Supabase
```bash
# Create Supabase project
# Enable OAuth providers (Google, Apple, GitHub, X)
# Get JWT Secret from Settings > API
# Configure redirect URLs
```

### 2. Configure Environment
```bash
# Frontend .env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_PUBLISHABLE_KEY=your-publishable-key

# Backend .env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_JWT_SECRET=your-jwt-secret
DATABASE_URL=postgresql://...
```

### 3. Start Services
```bash
# Frontend
npm run dev

# Backend
pip install -r requirements.txt
uvicorn main:app --reload

# PostgreSQL + Weaviate
docker-compose up -d
```

## 📱 User Experience

1. **Login**: Click OAuth button → Redirect to provider → Back to app
2. **Session**: Auto-refresh tokens, persistent login
3. **Logout**: Clear Supabase session, clear local state
4. **Security**: Invalid tokens automatically rejected

## 🔧 Troubleshooting

### Common Issues
1. **JWT Secret**: Get from Supabase dashboard > Settings > API
2. **CORS**: Add frontend URL to Supabase allowed origins
3. **Redirect URLs**: Configure in Supabase auth settings
4. **Token Expiration**: Frontend handles auto-refresh

### Debug Mode
```typescript
// Enable Supabase debug
export const supabase = createClient(url, key, {
  auth: { debug: true }
})
```

This architecture provides maximum security while maintaining clear separation of concerns between authentication and data storage.
