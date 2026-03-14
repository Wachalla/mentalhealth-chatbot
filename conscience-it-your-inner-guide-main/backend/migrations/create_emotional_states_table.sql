-- Create emotional_states table for Russell's Circumplex emotional model
-- Stores derived emotional signals only (no raw message content)

CREATE TABLE IF NOT EXISTS emotional_states (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    valence DECIMAL(3,2) NOT NULL CHECK (valence >= -1 AND valence <= 1),
    arousal DECIMAL(3,2) NOT NULL CHECK (arousal >= -1 AND arousal <= 1),
    category VARCHAR(50) NOT NULL CHECK (category IN ('distressed', 'anxious', 'low', 'calm', 'energized', 'neutral')),
    confidence DECIMAL(3,2) NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    source VARCHAR(20) NOT NULL CHECK (source IN ('chat', 'checkin', 'activity', 'baseline')),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_emotional_states_user_updated 
ON emotional_states(user_id, updated_at DESC);

CREATE INDEX IF NOT EXISTS idx_emotional_states_category 
ON emotional_states(category, updated_at DESC);

CREATE INDEX IF NOT EXISTS idx_emotional_states_source 
ON emotional_states(source, updated_at DESC);

-- Comment for documentation
COMMENT ON TABLE emotional_states IS 'Stores derived emotional states using Russell''s Circumplex model for privacy-preserving emotional tracking';
COMMENT ON COLUMN emotional_states.valence IS 'Emotional valence: -1 (negative) to 1 (positive)';
COMMENT ON COLUMN emotional_states.arousal IS 'Emotional arousal: -1 (calm) to 1 (excited)';
COMMENT ON COLUMN emotional_states.category IS 'Emotional category based on valence/arousal quadrant';
COMMENT ON COLUMN emotional_states.confidence IS 'Confidence in state detection: 0 (low) to 1 (high)';
COMMENT ON COLUMN emotional_states.source IS 'Source of emotional state: chat, checkin, activity, or baseline';
