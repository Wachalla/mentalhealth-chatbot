-- PostgreSQL Schema for CONSCIENCE AI Mental Health System
-- This file creates the structured relational database

-- Users table for authentication and profile management
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true,
    email_verified BOOLEAN DEFAULT false,
    preferences JSONB DEFAULT '{}'
);

-- User preferences structure
-- preferences field will contain JSON like:
-- {
--   "theme": "dark",
--   "notifications": true,
--   "vr_mode": "desktop",
--   "breathing_preference": "box",
--   "language": "en"
-- }

-- Mood logs for emotional tracking
CREATE TABLE IF NOT EXISTS mood_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    mood_score INTEGER NOT NULL CHECK (mood_score >= 1 AND mood_score <= 10),
    emotion VARCHAR(50) NOT NULL,
    notes TEXT,
    triggers TEXT[],
    activities TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Emotion categories for structured tracking
CREATE TABLE IF NOT EXISTS emotion_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    color VARCHAR(7) DEFAULT '#888888',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Goals and progress tracking
CREATE TABLE IF NOT EXISTS goals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL,
    target_date DATE,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'completed', 'paused', 'cancelled')),
    progress INTEGER DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- VR session logs for immersive therapy tracking
CREATE TABLE IF NOT EXISTS vr_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    environment VARCHAR(50) NOT NULL,
    breathing_technique VARCHAR(50),
    duration_minutes INTEGER,
    completion_rate DECIMAL(5,2),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- System audit logs for compliance and debugging
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource VARCHAR(255),
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- System metadata for configuration
CREATE TABLE IF NOT EXISTS system_metadata (
    key VARCHAR(100) PRIMARY KEY,
    value TEXT,
    description TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Performance indexes for optimal query performance
CREATE INDEX IF NOT EXISTS idx_mood_logs_user_created ON mood_logs(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_goals_user_status ON goals(user_id, status);
CREATE INDEX IF NOT EXISTS idx_vr_sessions_user_created ON vr_sessions(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created ON audit_logs(created_at DESC);

-- Insert default emotion categories
INSERT INTO emotion_categories (name, description, color) VALUES
('happy', 'Feeling joyful and positive', '#FFD700'),
('sad', 'Feeling down or melancholic', '#4169E1'),
('anxious', 'Feeling worried or tense', '#FF6B6B'),
('angry', 'Feeling frustrated or irritable', '#DC143C'),
('calm', 'Feeling peaceful and relaxed', '#90EE90'),
('confused', 'Feeling uncertain or unclear', '#FFA500'),
('motivated', 'Feeling driven and focused', '#32CD32')
ON CONFLICT (name) DO NOTHING;

-- Insert system metadata
INSERT INTO system_metadata (key, value, description) VALUES
('database_version', '1.0.0', 'Current database schema version'),
('maintenance_mode', 'false', 'System maintenance status'),
('max_sessions_per_day', '10', 'Maximum VR sessions allowed per day')
ON CONFLICT (key) DO NOTHING;
