# CONSCIENCE AI Mental Health Infrastructure

## 🏗️ Architecture Overview

CONSCIENCE uses a dual-database architecture optimized for both structured transactional data and semantic vector search:

### 📊 PostgreSQL (Structured Relational Database)
**Purpose**: ACID-compliant transactional data storage
**Responsibilities**:
- User authentication and accounts
- Mood logs with structured metadata
- Goals and progress tracking
- VR session logs
- Audit trails and compliance
- System configuration

**Why PostgreSQL**:
- **ACID Compliance**: Ensures data consistency for user accounts and mood logs
- **Complex Relationships**: Handles user-goals, mood-emotions relationships
- **Transaction Integrity**: Critical for financial/health data
- **Mature Tooling**: Extensive monitoring and backup solutions
- **JSON Support**: Native JSONB for user preferences and flexible data

### 🔍 Weaviate (Vector Database)
**Purpose**: Semantic similarity search and AI memory augmentation
**Responsibilities**:
- Conversation embeddings for context retrieval
- Emotional context embeddings
- Semantic memory search across sessions
- RAG-style retrieval for AI responses
- Similarity matching for emotional patterns

**Why Weaviate**:
- **Native Vector Search**: Optimized for similarity queries
- **AI-Native**: Built for machine learning workflows
- **Semantic Understanding**: Goes beyond keyword matching
- **Scalable**: Handles millions of embeddings efficiently
- **GraphQL API**: Flexible querying capabilities

## 🐳 Docker Setup

### Services Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL   │    │   Weaviate    │    │  Text2Vec      │
│   (5432)     │    │   (8080/50051)│    │   (8080)       │
│   Structured  │    │   Vector Search  │    │  Embeddings     │
│   Data        │    │   Semantic      │    │  Service        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        └───────────────────────┴───────────────────┘
                        CONSCIENCE Network (172.20.0.0/16)
```

### Port Exposure
- **PostgreSQL**: `5432` - Structured data access
- **Weaviate REST**: `8080` - Vector search API
- **Weaviate gRPC**: `50051` - High-performance vector queries
- **Text2Vec**: `8080` - Embedding generation service

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Git

### Setup Commands
```bash
# Clone repository
git clone <repository-url>
cd conscience-it-your-inner-guide-main

# Start infrastructure
docker-compose up -d

# Initialize database schema
docker exec conscience-postgres psql -U conscience_user -d conscience_db -f database/init/01-create-database.sql

# Initialize Weaviate schema
curl -X POST http://localhost:8080/v1/schema \
  -H "Content-Type: application/json" \
  -d @weaviate/schema.json

# Verify services
docker-compose ps
curl http://localhost:5432  # PostgreSQL
curl http://localhost:8080/v1/.well-known/ready  # Weaviate
```

## 📡 Database Schemas

### PostgreSQL Schema Highlights
```sql
users          -- Authentication and profiles
mood_logs      -- Emotional tracking with scores
goals           -- Progress tracking
vr_sessions      -- Immersive therapy logs
audit_logs      -- Compliance and debugging
emotion_categories -- Structured emotion taxonomy
```

### Weaviate Schema Highlights
```json
EmotionalMemory  -- Vector embeddings for conversations
- user_id, emotion, message, context
- timestamp, intensity, conversation_id
- Semantic search capabilities
```

## 🔗 Service Communication

### Backend API Integration
```javascript
// PostgreSQL Connection
const pg = require('pg');
const pool = new pg.Pool({
  connectionString: process.env.DATABASE_URL
});

// Weaviate Connection
const weaviate = require('weaviate-client');
const client = weaviate.client({
  scheme: 'http',
  host: 'localhost',
  port: 8080,
  apiKey: process.env.WEAVIATE_API_KEY
});
```

### Data Flow Example
1. **User Conversation** → Store in PostgreSQL (mood_logs)
2. **Generate Embedding** → Send to Text2Vec → Store in Weaviate
3. **AI Query** → Search Weaviate for similar contexts
4. **Response Generation** → Use semantic context + structured data
5. **Storage** → Log everything in PostgreSQL for audit

## 🔐 Security Configuration

### Environment Variables
```bash
# Production Security
POSTGRES_PASSWORD=<strong-random-password>
WEAVIATE_API_KEY=<cryptographically-secure-key>
NODE_ENV=production

# Network Security
- Internal Docker network isolation
- No external port exposure except API gateway
- SSL/TLS termination at load balancer
```

## 📊 Monitoring & Health

### Health Checks
- **PostgreSQL**: `pg_isready` command
- **Weaviate**: `/v1/.well-known/ready` endpoint
- **Text2Vec**: Service availability check

### Logging Strategy
- JSON file logging with rotation
- Centralized log collection
- Error tracking and alerting

## 🚀 Production Deployment

### Scaling Considerations
- **PostgreSQL**: Read replicas, connection pooling
- **Weaviate**: Multi-node cluster, sharding
- **Load Balancer**: API gateway with SSL termination
- **Monitoring**: Prometheus + Grafana stack

### Backup Strategy
- **PostgreSQL**: WAL-E shipping, daily snapshots
- **Weaviate**: Backup vector collections
- **Recovery**: Point-in-time restoration capability

## 🔧 Development Workflow

### Local Development
```bash
# Start services
docker-compose up -d

# Reset data (development only)
docker-compose down -v
docker-compose up -d

# View logs
docker-compose logs -f postgres
docker-compose logs -f weaviate
```

### Database Migrations
```bash
# Create new migration
database/init/02-add-feature.sql

# Apply migration
docker exec conscience-postgres psql -U conscience_user -d conscience_db -f database/init/02-add-feature.sql
```

## 📋 Architecture Decisions Rationale

### Why This Dual-Database Approach?

**PostgreSQL for Structured Data**:
- **Reliability**: 30+ years of production proven stability
- **Consistency**: ACID guarantees prevent data corruption
- **Complexity**: Handles user relationships, transactions, constraints
- **Tooling**: Mature ecosystem, monitoring, backups
- **Compliance**: Audit trails, GDPR considerations

**Weaviate for Vector Data**:
- **Performance**: Purpose-built for similarity search
- **Semantics**: Understands meaning, not just keywords
- **AI Integration**: Native support for ML workflows
- **Scalability**: Horizontal scaling for vector operations
- **Flexibility**: GraphQL API, schema evolution

This architecture ensures:
- ✅ **Data Integrity**: Structured data never corrupted
- ✅ **Semantic Search**: AI can find relevant past contexts
- ✅ **Performance**: Optimized for each database's strengths
- ✅ **Scalability**: Each service can scale independently
- ✅ **Maintainability**: Clear separation of concerns
