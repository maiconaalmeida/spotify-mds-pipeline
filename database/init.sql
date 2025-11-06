-- Spotify Analytics Database Schema

CREATE DATABASE IF NOT EXISTS spotify_analytics;
USE spotify_analytics;

-- Bronze Layer (Raw Data)
CREATE TABLE IF NOT EXISTS bronze_plays (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255),
    track_id VARCHAR(255),
    track_name VARCHAR(500),
    artist_name VARCHAR(500),
    album_name VARCHAR(500),
    played_at TIMESTAMP,
    duration_ms INT,
    popularity INT,
    device_type VARCHAR(100),
    context_type VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_played_at (played_at),
    INDEX idx_user_id (user_id)
);

-- Silver Layer (Cleaned Data)
CREATE TABLE IF NOT EXISTS silver_plays (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255),
    track_id VARCHAR(255),
    track_name VARCHAR(500),
    artist_name VARCHAR(500),
    album_name VARCHAR(500),
    played_at TIMESTAMP,
    duration_minutes DECIMAL(5,2),
    popularity INT,
    device_type VARCHAR(100),
    is_premium BOOLEAN,
    hour_of_day INT,
    day_of_week INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_played_at (played_at),
    INDEX idx_user_id (user_id),
    INDEX idx_artist (artist_name)
);

-- Gold Layer (Business Metrics)
CREATE TABLE IF NOT EXISTS gold_user_metrics (
    user_id VARCHAR(255) PRIMARY KEY,
    total_plays INT DEFAULT 0,
    total_minutes_played DECIMAL(10,2) DEFAULT 0,
    favorite_artist VARCHAR(500),
    favorite_track VARCHAR(500),
    avg_daily_plays DECIMAL(5,2) DEFAULT 0,
    last_played TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS gold_artist_metrics (
    artist_name VARCHAR(500) PRIMARY KEY,
    total_plays INT DEFAULT 0,
    total_listeners INT DEFAULT 0,
    avg_popularity DECIMAL(5,2) DEFAULT 0,
    peak_popularity INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_total_plays (total_plays)
);

-- Insert sample data for testing
INSERT IGNORE INTO bronze_plays (
    id, user_id, track_id, track_name, artist_name, album_name, 
    played_at, duration_ms, popularity, device_type
) VALUES 
('demo_001', 'user_001', 'track_001', 'Evidências', 'Chitãozinho & Xororó', 'Evidências', 
 NOW() - INTERVAL 1 HOUR, 240000, 85, 'mobile'),
('demo_002', 'user_002', 'track_002', 'Cheia de Manias', 'Raça Negra', 'Raça Negra', 
 NOW() - INTERVAL 30 MINUTE, 210000, 80, 'web');

INSERT IGNORE INTO gold_user_metrics (user_id, total_plays, total_minutes_played, favorite_artist) 
VALUES ('user_001', 15, 45.5, 'Chitãozinho & Xororó');

INSERT IGNORE INTO gold_artist_metrics (artist_name, total_plays, total_listeners) 
VALUES ('Chitãozinho & Xororó', 25, 8);