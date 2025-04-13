-- Circuits Table
CREATE TABLE circuits (
    circuit_id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    country VARCHAR(50),
    location VARCHAR(100)
);

-- Events (Race Weekends) Table
CREATE TABLE events (
    event_id INTEGER PRIMARY KEY,
    circuit_id INTEGER NOT NULL,
    event_name VARCHAR(100) NOT NULL,
    event_date DATE NOT NULL,
    round INTEGER NOT NULL,
    FOREIGN KEY (circuit_id) REFERENCES circuits(circuit_id)
);

-- Session Types Table
CREATE TABLE session_types (
    session_type_id INTEGER PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    code VARCHAR(10) NOT NULL UNIQUE,
    description VARCHAR(255)
);

-- Sessions (Q, Sprint Quali, Sprint, R) Table
CREATE TABLE sessions (
    session_id INTEGER PRIMARY KEY,
    event_id INTEGER NOT NULL,
    session_type_id INTEGER NOT NULL,
    start_time DATETIME,
    end_time DATETIME,
    FOREIGN KEY (event_id) REFERENCES events(event_id),
    FOREIGN KEY (session_type_id) REFERENCES session_types(session_type_id)
);

-- Teams Table
CREATE TABLE teams (
    team_id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    nationality VARCHAR(50),
    constructor_ref VARCHAR(50) UNIQUE,
    team_color VARCHAR(7)
);

-- Drivers Table
CREATE TABLE drivers (
    driver_id INTEGER PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    abbreviation VARCHAR(3),
    number INTEGER,
    driver_ref VARCHAR(50) UNIQUE,
    nationality VARCHAR(50)
);

-- Seasons Table (needed for driver_teams reference)
CREATE TABLE seasons (
    season_id INTEGER PRIMARY KEY,
    year INTEGER NOT NULL UNIQUE
);

-- Driver-Team Relationships (for each season)
CREATE TABLE driver_teams (
    driver_team_id INTEGER PRIMARY KEY,
    driver_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    season_id INTEGER NOT NULL,
    FOREIGN KEY (driver_id) REFERENCES drivers(driver_id),
    FOREIGN KEY (team_id) REFERENCES teams(team_id),
    FOREIGN KEY (season_id) REFERENCES seasons(season_id),
    UNIQUE (driver_id, team_id, season_id)
);

-- Results Table
CREATE TABLE results (
    result_id INTEGER PRIMARY KEY,
    session_id INTEGER NOT NULL,
    driver_id INTEGER NOT NULL,
    finishing_position INTEGER,
    grid_position INTEGER,
    status VARCHAR(50),
    points FLOAT,
    fastest_lap_time FLOAT,
    fastest_lap_number INTEGER,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id),
    FOREIGN KEY (driver_id) REFERENCES drivers(driver_id)
);

-- Race Strategies Table
CREATE TABLE race_strategies (
    strategy_id INTEGER PRIMARY KEY,
    session_id INTEGER NOT NULL,
    driver_id INTEGER NOT NULL,
    stint_number INTEGER NOT NULL,
    compound VARCHAR(20),
    stint_start_lap INTEGER,
    stint_end_lap INTEGER,
    stint_length INTEGER,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id),
    FOREIGN KEY (driver_id) REFERENCES drivers(driver_id)
);

-- Qualifying or Sprint Shootout Times Table
CREATE TABLE qualifying_times (
    qualifying_time_id INTEGER PRIMARY KEY,
    session_id INTEGER NOT NULL,
    driver_id INTEGER NOT NULL,
    q1_time FLOAT,
    q2_time FLOAT,
    q3_time FLOAT,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id),
    FOREIGN KEY (driver_id) REFERENCES drivers(driver_id)
);

-- Insert session types
INSERT INTO session_types (session_type_id, name, code, description) VALUES
    (1, 'Qualifying', 'Q', 'Main qualifying session'),
    (2, 'Sprint Qualifying', 'SQ', 'Sprint qualifying session'),
    (3, 'Sprint Race', 'SR', 'Sprint race'),
    (4, 'Race', 'R', 'Main race');