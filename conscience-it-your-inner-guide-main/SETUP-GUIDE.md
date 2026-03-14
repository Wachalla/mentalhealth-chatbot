# 🚀 CONSCIENCE Setup Guide

## 📋 Prerequisites

Before starting, ensure you have:
- Node.js 18+ and npm installed
- Docker and Docker Compose installed
- Supabase account (free tier is fine)

## 🔧 Step 1: Create Supabase Project

1. **Visit** [supabase.com](https://supabase.com)
2. **Sign up** for a free account
3. **Create new project**:
   - Project name: `conscience-app`
   - Database password: Choose a strong password
   - Region: Choose closest to your users

4. **Get your credentials**:
   - Go to Project Settings → API
   - Copy **Project URL** and **anon public key**

5. **Configure OAuth providers**:
   - Go to Authentication → Providers
   - Enable **Google**, **Apple**, **GitHub**, **X (Twitter)**
   - Follow the setup instructions for each provider

## 🔧 Step 2: Configure Environment

1. **Copy the example**:
```bash
cp .env.example .env
```

2. **Update .env with your Supabase credentials**:
```bash
# Replace these with your actual Supabase project details
VITE_SUPABASE_URL=https://your-project-id.supabase.co
VITE_SUPABASE_PUBLISHABLE_KEY=your-actual-publishable-key
```

3. **Get JWT Secret**:
   - In Supabase dashboard → Settings → API
   - Copy the **JWT Secret** (not the public key)
   - Update: `SUPABASE_JWT_SECRET=your-actual-jwt-secret`

## 🔧 Step 3: Start Infrastructure

1. **Start all services**:
```bash
docker-compose up -d
```

2. **Initialize databases**:
```bash
# Create PostgreSQL tables
docker exec conscience-postgres psql -U conscience_user -d conscience_db -f database/init/01-create-database.sql

# Create Weaviate schema
curl -X POST http://localhost:8080/v1/schema \
  -H "Authorization: Bearer conscience-api-key-secure-123" \
  -H "Content-Type: application/json" \
  -d @weaviate/schema.json
```

3. **Verify services are running**:
```bash
# Check all containers
docker-compose ps

# Test backend health
curl http://localhost:8000/health

# Test Weaviate
curl http://localhost:8080/v1/.well-known/ready
```

## 🔧 Step 4: Start Frontend

1. **Install dependencies**:
```bash
npm install
```

2. **Start development server**:
```bash
npm run dev
```

3. **Open your browser**:
   - Navigate to: http://localhost:8081
   - You should see the Conscience login page

## 🔧 Step 5: Test Authentication

1. **Email/Password**:
   - Click "Sign in with Email"
   - Create a new account
   - Check email for confirmation (may be in spam)

2. **OAuth Providers**:
   - Click any OAuth button (Google, Apple, etc.)
   - Complete the OAuth flow
   - You should be redirected back to the app

3. **Verify user creation**:
   - Check PostgreSQL for new user:
```bash
docker exec conscience-postgres psql -U conscience_user -d conscience_db -c "SELECT * FROM users;"
```

## 🔧 Step 6: Test Full System

1. **Mood Logging**:
   - After login, try logging a mood
   - Check it appears in database

2. **VR Features**:
   - Navigate to VR room
   - Test WebXR compatibility (requires VR headset)

3. **AI Chat**:
   - Try the AI chat feature
   - Should get therapeutic responses

## 🚨 Troubleshooting

### ❌ "Please configure your Supabase project"
**Solution**: Update .env with real Supabase URL and key

### ❌ OAuth provider not working
**Solution**: 
- Ensure OAuth is enabled in Supabase dashboard
- Check redirect URLs match your setup
- Verify OAuth app credentials

### ❌ Database connection failed
**Solution**:
- Check PostgreSQL container is running
- Verify database credentials in .env
- Ensure database was initialized

### ❌ Weaviate not responding
**Solution**:
- Check Weaviate container is running
- Verify API key matches
- Ensure schema was created

### ❌ Frontend not loading
**Solution**:
- Check npm install completed successfully
- Verify environment variables are loaded
- Check browser console for errors

## 🔄 Production Deployment

### Environment Variables
For production, update these values:
```bash
DEBUG=false
MOCK_AI=false
VITE_API_BASE_URL=https://api.yourdomain.com
VITE_REDIRECT_URL=https://yourdomain.com/auth/callback
```

### Security
- Use strong passwords for database
- Enable SSL certificates
- Set up proper CORS origins
- Use environment-specific secrets

### Scaling
- Use Kubernetes for container orchestration
- Set up load balancers
- Configure database replication
- Monitor system performance

## 📚 Next Steps

1. **Customize AI**: Replace mock AI with real Llama integration
2. **Add Features**: Implement additional therapeutic exercises
3. **Deploy**: Set up production hosting
4. **Monitor**: Add logging and analytics
5. **Secure**: Implement additional security measures

## 🤝 Support

- **Documentation**: Check `SYSTEM-ARCHITECTURE.md`
- **Issues**: Report bugs in the project repository
- **Community**: Join our Discord for support

---

**🎉 Congratulations! Your CONSCIENCE mental health platform is now running!**
