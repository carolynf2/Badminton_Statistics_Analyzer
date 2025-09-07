-- Badminton Statistics Database Schema
-- Comprehensive schema for tracking badminton matches, players, and statistics

-- Players table
CREATE TABLE players (
    player_id INTEGER PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    nationality VARCHAR(3), -- ISO country code
    birth_date DATE,
    gender VARCHAR(1) CHECK (gender IN ('M', 'F')),
    height_cm INTEGER,
    weight_kg INTEGER,
    dominant_hand VARCHAR(1) CHECK (dominant_hand IN ('L', 'R')),
    coach VARCHAR(100),
    world_ranking INTEGER,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tournaments table
CREATE TABLE tournaments (
    tournament_id INTEGER PRIMARY KEY,
    tournament_name VARCHAR(100) NOT NULL,
    location VARCHAR(100),
    country VARCHAR(3), -- ISO country code
    tournament_type VARCHAR(20) CHECK (tournament_type IN ('BWF_SUPER_1000', 'BWF_SUPER_750', 'BWF_SUPER_500', 'BWF_SUPER_300', 'BWF_WORLD_TOUR_FINALS', 'OLYMPICS', 'WORLD_CHAMPIONSHIPS', 'OTHER')),
    surface VARCHAR(20) CHECK (surface IN ('WOOD', 'SYNTHETIC', 'CONCRETE', 'OTHER')),
    prize_money INTEGER,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'SCHEDULED' CHECK (status IN ('SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED'))
);

-- Matches table - stores individual match information
CREATE TABLE matches (
    match_id INTEGER PRIMARY KEY,
    tournament_id INTEGER NOT NULL,
    match_date DATE NOT NULL,
    match_time TIME,
    round VARCHAR(20) CHECK (round IN ('QUALIFYING', 'R64', 'R32', 'R16', 'QF', 'SF', 'F')),
    court VARCHAR(10),
    match_type VARCHAR(2) CHECK (match_type IN ('MS', 'WS', 'MD', 'WD', 'XD')), -- Men's Singles, Women's Singles, Men's Doubles, Women's Doubles, Mixed Doubles
    best_of INTEGER DEFAULT 3 CHECK (best_of IN (3, 5)),
    duration_minutes INTEGER,
    winner_id INTEGER,
    status VARCHAR(20) DEFAULT 'SCHEDULED' CHECK (status IN ('SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'WALKOVER', 'RETIRED', 'DISQUALIFIED')),
    weather_condition VARCHAR(20),
    temperature_celsius INTEGER,
    humidity_percent INTEGER,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tournament_id) REFERENCES tournaments(tournament_id),
    FOREIGN KEY (winner_id) REFERENCES players(player_id)
);

-- Match participants - handles both singles and doubles
CREATE TABLE match_participants (
    participant_id INTEGER PRIMARY KEY,
    match_id INTEGER NOT NULL,
    player_id INTEGER NOT NULL,
    partner_id INTEGER, -- NULL for singles, partner ID for doubles
    team_position INTEGER CHECK (team_position IN (1, 2)), -- Team 1 or Team 2
    is_winner BOOLEAN DEFAULT FALSE,
    seeding INTEGER,
    FOREIGN KEY (match_id) REFERENCES matches(match_id),
    FOREIGN KEY (player_id) REFERENCES players(player_id),
    FOREIGN KEY (partner_id) REFERENCES players(player_id)
);

-- Game results - individual games within a match
CREATE TABLE games (
    game_id INTEGER PRIMARY KEY,
    match_id INTEGER NOT NULL,
    game_number INTEGER NOT NULL CHECK (game_number BETWEEN 1 AND 5),
    team1_score INTEGER NOT NULL DEFAULT 0,
    team2_score INTEGER NOT NULL DEFAULT 0,
    winner_team INTEGER CHECK (winner_team IN (1, 2)),
    duration_minutes INTEGER,
    max_rally_length INTEGER, -- longest rally in this game
    FOREIGN KEY (match_id) REFERENCES matches(match_id)
);

-- Point-by-point statistics
CREATE TABLE rally_stats (
    rally_id INTEGER PRIMARY KEY,
    game_id INTEGER NOT NULL,
    rally_number INTEGER NOT NULL,
    serving_player_id INTEGER NOT NULL,
    receiving_player_id INTEGER NOT NULL,
    rally_length INTEGER NOT NULL, -- number of shots
    winner_player_id INTEGER NOT NULL,
    winning_shot_type VARCHAR(30) CHECK (winning_shot_type IN ('SMASH', 'CLEAR', 'DROP', 'DRIVE', 'NET_SHOT', 'LOB', 'KILL', 'ERROR', 'FAULT')),
    duration_seconds INTEGER,
    FOREIGN KEY (game_id) REFERENCES games(game_id),
    FOREIGN KEY (serving_player_id) REFERENCES players(player_id),
    FOREIGN KEY (receiving_player_id) REFERENCES players(player_id),
    FOREIGN KEY (winner_player_id) REFERENCES players(player_id)
);

-- Detailed shot statistics per match
CREATE TABLE match_statistics (
    stat_id INTEGER PRIMARY KEY,
    match_id INTEGER NOT NULL,
    player_id INTEGER NOT NULL,
    
    -- Serving statistics
    total_serves INTEGER DEFAULT 0,
    service_aces INTEGER DEFAULT 0,
    service_faults INTEGER DEFAULT 0,
    short_serves INTEGER DEFAULT 0,
    long_serves INTEGER DEFAULT 0,
    flick_serves INTEGER DEFAULT 0,
    
    -- Shot statistics
    total_shots INTEGER DEFAULT 0,
    winners INTEGER DEFAULT 0,
    unforced_errors INTEGER DEFAULT 0,
    forced_errors INTEGER DEFAULT 0,
    
    -- Shot types
    smashes INTEGER DEFAULT 0,
    clears INTEGER DEFAULT 0,
    drops INTEGER DEFAULT 0,
    drives INTEGER DEFAULT 0,
    net_shots INTEGER DEFAULT 0,
    lobs INTEGER DEFAULT 0,
    kills INTEGER DEFAULT 0,
    
    -- Movement and positioning
    net_points_won INTEGER DEFAULT 0,
    net_points_played INTEGER DEFAULT 0,
    backcourt_points_won INTEGER DEFAULT 0,
    backcourt_points_played INTEGER DEFAULT 0,
    
    -- Rally statistics
    short_rallies_won INTEGER DEFAULT 0, -- 1-4 shots
    medium_rallies_won INTEGER DEFAULT 0, -- 5-9 shots
    long_rallies_won INTEGER DEFAULT 0, -- 10+ shots
    short_rallies_played INTEGER DEFAULT 0,
    medium_rallies_played INTEGER DEFAULT 0,
    long_rallies_played INTEGER DEFAULT 0,
    
    -- Other statistics
    points_won INTEGER DEFAULT 0,
    points_played INTEGER DEFAULT 0,
    break_points_saved INTEGER DEFAULT 0,
    break_points_faced INTEGER DEFAULT 0,
    
    FOREIGN KEY (match_id) REFERENCES matches(match_id),
    FOREIGN KEY (player_id) REFERENCES players(player_id)
);

-- Head-to-head records
CREATE TABLE head_to_head (
    h2h_id INTEGER PRIMARY KEY,
    player1_id INTEGER NOT NULL,
    player2_id INTEGER NOT NULL,
    matches_played INTEGER DEFAULT 0,
    player1_wins INTEGER DEFAULT 0,
    player2_wins INTEGER DEFAULT 0,
    last_match_date DATE,
    last_match_id INTEGER,
    FOREIGN KEY (player1_id) REFERENCES players(player_id),
    FOREIGN KEY (player2_id) REFERENCES players(player_id),
    FOREIGN KEY (last_match_id) REFERENCES matches(match_id),
    UNIQUE(player1_id, player2_id)
);

-- Player rankings history
CREATE TABLE rankings (
    ranking_id INTEGER PRIMARY KEY,
    player_id INTEGER NOT NULL,
    ranking_date DATE NOT NULL,
    world_ranking INTEGER,
    points INTEGER,
    tournaments_played INTEGER DEFAULT 0,
    FOREIGN KEY (player_id) REFERENCES players(player_id)
);

-- Create indexes for better query performance
CREATE INDEX idx_players_nationality ON players(nationality);
CREATE INDEX idx_players_gender ON players(gender);
CREATE INDEX idx_players_ranking ON players(world_ranking);
CREATE INDEX idx_tournaments_date ON tournaments(start_date, end_date);
CREATE INDEX idx_tournaments_type ON tournaments(tournament_type);
CREATE INDEX idx_matches_date ON matches(match_date);
CREATE INDEX idx_matches_tournament ON matches(tournament_id);
CREATE INDEX idx_matches_type ON matches(match_type);
CREATE INDEX idx_match_participants_player ON match_participants(player_id);
CREATE INDEX idx_match_participants_match ON match_participants(match_id);
CREATE INDEX idx_games_match ON games(match_id);
CREATE INDEX idx_rally_stats_game ON rally_stats(game_id);
CREATE INDEX idx_rally_stats_player ON rally_stats(serving_player_id, receiving_player_id);
CREATE INDEX idx_match_stats_player ON match_statistics(player_id);
CREATE INDEX idx_match_stats_match ON match_statistics(match_id);
CREATE INDEX idx_h2h_players ON head_to_head(player1_id, player2_id);
CREATE INDEX idx_rankings_player_date ON rankings(player_id, ranking_date);

-- Create views for common queries
CREATE VIEW player_performance AS
SELECT 
    p.player_id,
    p.first_name,
    p.last_name,
    p.nationality,
    COUNT(DISTINCT m.match_id) as matches_played,
    SUM(CASE WHEN mp.is_winner = 1 THEN 1 ELSE 0 END) as matches_won,
    ROUND(AVG(CASE WHEN mp.is_winner = 1 THEN 1.0 ELSE 0.0 END) * 100, 2) as win_percentage,
    AVG(ms.points_won * 1.0 / NULLIF(ms.points_played, 0)) * 100 as avg_points_won_pct
FROM players p
LEFT JOIN match_participants mp ON p.player_id = mp.player_id
LEFT JOIN matches m ON mp.match_id = m.match_id AND m.status = 'COMPLETED'
LEFT JOIN match_statistics ms ON p.player_id = ms.player_id AND m.match_id = ms.match_id
GROUP BY p.player_id, p.first_name, p.last_name, p.nationality;

CREATE VIEW tournament_summary AS
SELECT 
    t.tournament_id,
    t.tournament_name,
    t.location,
    t.tournament_type,
    COUNT(DISTINCT m.match_id) as total_matches,
    COUNT(DISTINCT mp.player_id) as total_players,
    AVG(m.duration_minutes) as avg_match_duration
FROM tournaments t
LEFT JOIN matches m ON t.tournament_id = m.tournament_id
LEFT JOIN match_participants mp ON m.match_id = mp.match_id
GROUP BY t.tournament_id, t.tournament_name, t.location, t.tournament_type;

-- Create triggers for automatic updates
CREATE TRIGGER update_head_to_head
AFTER INSERT ON matches
WHEN NEW.status = 'COMPLETED' AND NEW.winner_id IS NOT NULL
BEGIN
    -- Update head-to-head record
    INSERT OR REPLACE INTO head_to_head (
        player1_id, player2_id, matches_played, player1_wins, player2_wins, last_match_date, last_match_id
    )
    SELECT 
        CASE WHEN p1.player_id < p2.player_id THEN p1.player_id ELSE p2.player_id END,
        CASE WHEN p1.player_id < p2.player_id THEN p2.player_id ELSE p1.player_id END,
        COALESCE(h.matches_played, 0) + 1,
        COALESCE(h.player1_wins, 0) + CASE 
            WHEN (p1.player_id < p2.player_id AND NEW.winner_id = p1.player_id) OR 
                 (p1.player_id > p2.player_id AND NEW.winner_id = p2.player_id) THEN 1 ELSE 0 END,
        COALESCE(h.player2_wins, 0) + CASE 
            WHEN (p1.player_id < p2.player_id AND NEW.winner_id = p2.player_id) OR 
                 (p1.player_id > p2.player_id AND NEW.winner_id = p1.player_id) THEN 1 ELSE 0 END,
        NEW.match_date,
        NEW.match_id
    FROM match_participants mp1
    JOIN match_participants mp2 ON mp1.match_id = mp2.match_id AND mp1.team_position != mp2.team_position
    JOIN players p1 ON mp1.player_id = p1.player_id
    JOIN players p2 ON mp2.player_id = p2.player_id
    LEFT JOIN head_to_head h ON (
        (h.player1_id = CASE WHEN p1.player_id < p2.player_id THEN p1.player_id ELSE p2.player_id END) AND
        (h.player2_id = CASE WHEN p1.player_id < p2.player_id THEN p2.player_id ELSE p1.player_id END)
    )
    WHERE mp1.match_id = NEW.match_id AND mp2.match_id = NEW.match_id;
END;