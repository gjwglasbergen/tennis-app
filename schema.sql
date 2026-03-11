-- ============================================
-- TennisTracker - Supabase SQL Schema
-- Voer dit uit in Supabase SQL Editor
-- ============================================

-- Wedstrijden tabel
CREATE TABLE matches (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    owner TEXT NOT NULL,
    player1 TEXT NOT NULL,
    player2 TEXT NOT NULL,
    surface TEXT DEFAULT 'Hard',
    best_of INTEGER DEFAULT 3,

    -- Actuele score
    sets_p1 INTEGER DEFAULT 0,
    sets_p2 INTEGER DEFAULT 0,
    games_p1 INTEGER DEFAULT 0,
    games_p2 INTEGER DEFAULT 0,
    points_p1 INTEGER DEFAULT 0,
    points_p2 INTEGER DEFAULT 0,

    status TEXT DEFAULT 'active', -- 'active' | 'finished'

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Punten tabel
CREATE TABLE points (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    match_id UUID REFERENCES matches(id) ON DELETE CASCADE,
    winner TEXT NOT NULL,       -- 'p1' of 'p2'
    point_type TEXT NOT NULL,   -- 'Ace', 'Smash', etc.
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes voor snelheid
CREATE INDEX idx_matches_owner ON matches(owner);
CREATE INDEX idx_matches_status ON matches(status);
CREATE INDEX idx_points_match_id ON points(match_id);

-- Row Level Security (publiek leesbaar, alleen owner mag schrijven)
ALTER TABLE matches ENABLE ROW LEVEL SECURITY;
ALTER TABLE points ENABLE ROW LEVEL SECURITY;

-- Iedereen mag wedstrijden bekijken (voor live follow links)
CREATE POLICY "Public read matches" ON matches FOR SELECT USING (true);
CREATE POLICY "Public read points" ON points FOR SELECT USING (true);

-- Schrijven alleen via service key (Streamlit backend)
CREATE POLICY "Service insert matches" ON matches FOR INSERT WITH CHECK (true);
CREATE POLICY "Service update matches" ON matches FOR UPDATE USING (true);
CREATE POLICY "Service insert points" ON points FOR INSERT WITH CHECK (true);
CREATE POLICY "Service delete points" ON points FOR DELETE USING (true);
