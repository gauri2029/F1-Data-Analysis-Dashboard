from database.db_setup import get_db_connection
import pandas as pd

def get_all_seasons():
    """Get all seasons from the database"""
    conn = get_db_connection()
    seasons = pd.read_sql_query("SELECT * FROM seasons ORDER BY year", conn)
    conn.close()
    return seasons

def get_all_circuits():
    """Get all circuits from the database"""
    conn = get_db_connection()
    circuits = pd.read_sql_query("SELECT * FROM circuits", conn)
    conn.close()
    return circuits

def get_all_drivers():
    """Get all drivers from the database"""
    conn = get_db_connection()
    drivers = pd.read_sql_query("SELECT * FROM drivers", conn)
    conn.close()
    return drivers

def get_all_teams():
    """Get all teams from the database"""
    conn = get_db_connection()
    teams = pd.read_sql_query("SELECT * FROM teams", conn)
    conn.close()
    return teams

def get_driver_teams_by_season(season_id):
    """Get driver-team relationships for a specific season"""
    conn = get_db_connection()
    query = """
    SELECT dt.driver_team_id, d.full_name AS driver_name, d.abbreviation,
           t.name AS team_name, t.team_color, s.year
    FROM driver_teams dt
    JOIN drivers d ON dt.driver_id = d.driver_id
    JOIN teams t ON dt.team_id = t.team_id
    JOIN seasons s ON dt.season_id = s.season_id
    WHERE dt.season_id = ?
    """
    driver_teams = pd.read_sql_query(query, conn, params=(season_id,))
    conn.close()
    return driver_teams

def get_events_by_season(year):
    """Get all events for a specific season"""
    conn = get_db_connection()
    query = """
    SELECT e.event_id, e.event_name, e.event_date, e.round,
           c.name AS circuit_name, c.country, c.location
    FROM events e
    JOIN circuits c ON e.circuit_id = c.circuit_id
    WHERE strftime('%Y', e.event_date) = ?
    ORDER BY e.round
    """
    events = pd.read_sql_query(query, conn, params=(str(year),))
    conn.close()
    return events

def get_sessions_by_event(event_id):
    """Get all sessions for a specific event"""
    conn = get_db_connection()
    query = """
    SELECT s.session_id, s.start_time, s.end_time,
           st.name AS session_name, st.code AS session_code
    FROM sessions s
    JOIN session_types st ON s.session_type_id = st.session_type_id
    WHERE s.event_id = ?
    """
    sessions = pd.read_sql_query(query, conn, params=(event_id,))
    conn.close()
    return sessions

def get_results_by_session(session_id):
    """Get all results for a specific session"""
    conn = get_db_connection()
    query = """
    SELECT r.result_id, r.finishing_position, r.grid_position, r.status, r.points,
           r.fastest_lap_time, r.fastest_lap_number,
           d.full_name AS driver_name, d.abbreviation, d.number AS driver_number,
           t.name AS team_name, t.team_color
    FROM results r
    JOIN drivers d ON r.driver_id = d.driver_id
    JOIN sessions s ON r.session_id = s.session_id
    JOIN events e ON s.event_id = e.event_id
    JOIN seasons season ON strftime('%Y', e.event_date) = CAST(season.year AS TEXT)
    JOIN driver_teams dt ON r.driver_id = dt.driver_id AND dt.season_id = season.season_id
    JOIN teams t ON dt.team_id = t.team_id
    WHERE r.session_id = ?
    ORDER BY 
        CASE 
            WHEN r.finishing_position IS NULL THEN 999 
            ELSE r.finishing_position 
        END
    """
    results = pd.read_sql_query(query, conn, params=(session_id,))
    conn.close()
    return results

def get_qualifying_times_by_session(session_id):
    """Get qualifying times for a specific qualifying session"""
    conn = get_db_connection()
    query = """
    SELECT qt.qualifying_time_id, qt.q1_time, qt.q2_time, qt.q3_time,
           d.full_name AS driver_name, d.abbreviation, d.number AS driver_number,
           t.name AS team_name, t.team_color
    FROM qualifying_times qt
    JOIN drivers d ON qt.driver_id = d.driver_id
    JOIN sessions s ON qt.session_id = s.session_id
    JOIN events e ON s.event_id = e.event_id
    JOIN seasons season ON strftime('%Y', e.event_date) = CAST(season.year AS TEXT)
    JOIN driver_teams dt ON qt.driver_id = dt.driver_id AND dt.season_id = season.season_id
    JOIN teams t ON dt.team_id = t.team_id
    WHERE qt.session_id = ?
    """
    quali_times = pd.read_sql_query(query, conn, params=(session_id,))
    conn.close()
    return quali_times

def get_race_strategies_by_session(session_id):
    """Get race strategies for a specific race session"""
    conn = get_db_connection()
    query = """
    SELECT rs.strategy_id, rs.stint_number, rs.compound, 
           rs.stint_start_lap, rs.stint_end_lap, rs.stint_length,
           d.full_name AS driver_name, d.abbreviation, d.number AS driver_number,
           t.name AS team_name, t.team_color
    FROM race_strategies rs
    JOIN drivers d ON rs.driver_id = d.driver_id
    JOIN sessions s ON rs.session_id = s.session_id
    JOIN events e ON s.event_id = e.event_id
    JOIN seasons season ON strftime('%Y', e.event_date) = CAST(season.year AS TEXT)
    JOIN driver_teams dt ON rs.driver_id = dt.driver_id AND dt.season_id = season.season_id
    JOIN teams t ON dt.team_id = t.team_id
    WHERE rs.session_id = ?
    ORDER BY d.full_name, rs.stint_number
    """
    strategies = pd.read_sql_query(query, conn, params=(session_id,))
    conn.close()
    return strategies

def get_driver_performance_by_season(season_id):
    """Get driver performance statistics for a specific season"""
    conn = get_db_connection()
    query = """
    WITH RaceResults AS (
        SELECT 
            r.driver_id,
            r.finishing_position,
            r.points,
            st.code AS session_code
        FROM results r
        JOIN sessions s ON r.session_id = s.session_id
        JOIN session_types st ON s.session_type_id = st.session_type_id
        JOIN events e ON s.event_id = e.event_id
        JOIN seasons season ON strftime('%Y', e.event_date) = CAST(season.year AS TEXT)
        WHERE season.season_id = ? AND st.code IN ('R', 'SR')
    )
    SELECT 
        d.driver_id,
        d.full_name AS driver_name,
        d.abbreviation,
        d.number,
        t.name AS team_name,
        t.team_color,
        COUNT(CASE WHEN rr.finishing_position = 1 THEN 1 ELSE NULL END) AS wins,
        COUNT(CASE WHEN rr.finishing_position <= 3 THEN 1 ELSE NULL END) AS podiums,
        COUNT(CASE WHEN rr.finishing_position IS NOT NULL THEN 1 ELSE NULL END) AS race_finishes,
        ROUND(AVG(CASE WHEN rr.finishing_position IS NOT NULL THEN rr.finishing_position ELSE NULL END), 2) AS avg_finish_position,
        SUM(rr.points) AS total_points
    FROM drivers d
    JOIN driver_teams dt ON d.driver_id = dt.driver_id
    JOIN teams t ON dt.team_id = t.team_id
    LEFT JOIN RaceResults rr ON d.driver_id = rr.driver_id
    WHERE dt.season_id = ?
    GROUP BY d.driver_id, d.full_name, t.name
    ORDER BY total_points DESC
    """
    performance = pd.read_sql_query(query, conn, params=(season_id, season_id))
    conn.close()
    return performance

def get_team_performance_by_season(season_id):
    """Get team performance statistics for a specific season"""
    conn = get_db_connection()
    query = """
    WITH RaceResults AS (
        SELECT 
            dt.team_id,
            r.finishing_position,
            r.points,
            st.code AS session_code
        FROM results r
        JOIN drivers d ON r.driver_id = d.driver_id
        JOIN sessions s ON r.session_id = s.session_id
        JOIN session_types st ON s.session_type_id = st.session_type_id
        JOIN events e ON s.event_id = e.event_id
        JOIN seasons season ON strftime('%Y', e.event_date) = CAST(season.year AS TEXT)
        JOIN driver_teams dt ON r.driver_id = dt.driver_id AND dt.season_id = season.season_id
        WHERE season.season_id = ? AND st.code IN ('R', 'SR')
    )
    SELECT 
        t.team_id,
        t.name AS team_name,
        t.team_color,
        COUNT(CASE WHEN rr.finishing_position = 1 THEN 1 ELSE NULL END) AS wins,
        COUNT(CASE WHEN rr.finishing_position <= 3 THEN 1 ELSE NULL END) AS podiums,
        SUM(rr.points) AS total_points
    FROM teams t
    LEFT JOIN RaceResults rr ON t.team_id = rr.team_id
    WHERE t.team_id IN (SELECT DISTINCT team_id FROM driver_teams WHERE season_id = ?)
    GROUP BY t.team_id, t.name
    ORDER BY total_points DESC
    """
    performance = pd.read_sql_query(query, conn, params=(season_id, season_id))
    conn.close()
    return performance

# Custom query functions for the project requirements

def compare_lap_times_by_race(event_id):
    """
    Compare average lap times between different drivers for a specific race
    For project requirement: Draw a comparison between average lap times between different drivers for a specific race
    """
    conn = get_db_connection()
    query = """
    WITH LapData AS (
        SELECT 
            r.driver_id,
            rs.session_id,
            rs.stint_start_lap,
            rs.stint_end_lap,
            rs.compound
        FROM race_strategies rs
        JOIN results r ON rs.session_id = r.session_id AND rs.driver_id = r.driver_id
        JOIN sessions s ON rs.session_id = s.session_id
        WHERE s.event_id = ? AND s.session_type_id = 4  -- Race session
    ),
    DriverInfo AS (
        SELECT 
            d.driver_id,
            d.full_name AS driver_name,
            d.abbreviation,
            t.name AS team_name,
            t.team_color
        FROM drivers d
        JOIN sessions s ON 1=1
        JOIN events e ON s.event_id = e.event_id AND e.event_id = ?
        JOIN seasons season ON strftime('%Y', e.event_date) = CAST(season.year AS TEXT)
        JOIN driver_teams dt ON d.driver_id = dt.driver_id AND dt.season_id = season.season_id
        JOIN teams t ON dt.team_id = t.team_id
    )
    SELECT 
        di.driver_name,
        di.abbreviation,
        di.team_name,
        di.team_color,
        ld.compound,
        ROUND(AVG(CASE WHEN r.fastest_lap_time > 0 THEN r.fastest_lap_time ELSE NULL END), 3) AS avg_lap_time
    FROM LapData ld
    JOIN results r ON ld.driver_id = r.driver_id AND ld.session_id = r.session_id
    JOIN DriverInfo di ON ld.driver_id = di.driver_id
    GROUP BY di.driver_name, ld.compound
    ORDER BY avg_lap_time
    """
    lap_comparison = pd.read_sql_query(query, conn, params=(event_id, event_id))
    conn.close()
    return lap_comparison

def count_podium_finishes_by_team(season_id):
    """
    Find the number of podium finishes achieved by different teams over a season
    For project requirement: Find the number of podium finishes achieved by different teams over a season
    """
    conn = get_db_connection()
    query = """
    SELECT 
        t.name AS team_name,
        t.team_color,
        COUNT(CASE WHEN r.finishing_position <= 3 THEN 1 ELSE NULL END) AS podium_count
    FROM results r
    JOIN drivers d ON r.driver_id = d.driver_id
    JOIN sessions s ON r.session_id = s.session_id
    JOIN session_types st ON s.session_type_id = st.session_type_id
    JOIN events e ON s.event_id = e.event_id
    JOIN seasons season ON strftime('%Y', e.event_date) = CAST(season.year AS TEXT)
    JOIN driver_teams dt ON r.driver_id = dt.driver_id AND dt.season_id = season.season_id
    JOIN teams t ON dt.team_id = t.team_id
    WHERE season.season_id = ? AND st.code = 'R'  -- Main race only
    GROUP BY t.name
    ORDER BY podium_count DESC
    """
    podium_counts = pd.read_sql_query(query, conn, params=(season_id,))
    conn.close()
    return podium_counts

def analyze_lap_times_by_tire_age(event_id):
    """
    Analyze and compare lap times based on tire age for different teams
    For project requirement: Analyze and compare lap times based on tire age for different teams
    """
    conn = get_db_connection()
    query = """
    WITH TireData AS (
        SELECT 
            rs.driver_id,
            rs.stint_number,
            rs.compound,
            rs.stint_length,
            t.name AS team_name,
            t.team_color
        FROM race_strategies rs
        JOIN sessions s ON rs.session_id = s.session_id
        JOIN events e ON s.event_id = e.event_id
        JOIN seasons season ON strftime('%Y', e.event_date) = CAST(season.year AS TEXT)
        JOIN driver_teams dt ON rs.driver_id = dt.driver_id AND dt.season_id = season.season_id
        JOIN teams t ON dt.team_id = t.team_id
        WHERE e.event_id = ? AND s.session_type_id = 4  -- Race session
    )
    SELECT 
        td.team_name,
        td.team_color,
        td.compound,
        ROUND(AVG(td.stint_length), 1) AS avg_stint_length,
        COUNT(*) AS stint_count
    FROM TireData td
    GROUP BY td.team_name, td.compound
    ORDER BY td.team_name, avg_stint_length DESC
    """
    tire_analysis = pd.read_sql_query(query, conn, params=(event_id,))
    conn.close()
    return tire_analysis

def get_average_qualifying_positions(season_id):
    """
    Find the average qualifying positions of drivers across races
    For project requirement: Find the average qualifying positions of drivers across races
    """
    conn = get_db_connection()
    query = """
    SELECT 
        d.full_name AS driver_name,
        d.abbreviation,
        t.name AS team_name,
        t.team_color,
        COUNT(r.grid_position) AS qualifying_count,
        ROUND(AVG(r.grid_position), 2) AS avg_grid_position,
        MIN(r.grid_position) AS best_grid_position
    FROM results r
    JOIN drivers d ON r.driver_id = d.driver_id
    JOIN sessions s ON r.session_id = s.session_id
    JOIN session_types st ON s.session_type_id = st.session_type_id
    JOIN events e ON s.event_id = e.event_id
    JOIN seasons season ON strftime('%Y', e.event_date) = CAST(season.year AS TEXT)
    JOIN driver_teams dt ON r.driver_id = dt.driver_id AND dt.season_id = season.season_id
    JOIN teams t ON dt.team_id = t.team_id
    WHERE season.season_id = ? AND st.code = 'R' AND r.grid_position IS NOT NULL
    GROUP BY d.full_name
    ORDER BY avg_grid_position
    """
    quali_positions = pd.read_sql_query(query, conn, params=(season_id,))
    conn.close()
    return quali_positions

# Note: Weather conditions are not fully implemented in the database schema
# This would require adding a weather table to store track conditions
def compare_lap_times_by_weather(season_id):
    """
    Find the difference in Lap times for different drivers based on weather conditions across different races
    For project requirement: Find the difference in Lap times for different drivers based on weather conditions across different races
    
    Note: This is a placeholder function since weather data isn't fully implemented in the schema
    """
    conn = get_db_connection()
    query = """
    SELECT 
        d.full_name AS driver_name,
        d.abbreviation,
        t.name AS team_name,
        t.team_color,
        e.event_name,
        r.fastest_lap_time
    FROM results r
    JOIN drivers d ON r.driver_id = d.driver_id
    JOIN sessions s ON r.session_id = s.session_id
    JOIN session_types st ON s.session_type_id = st.session_type_id
    JOIN events e ON s.event_id = e.event_id
    JOIN seasons season ON strftime('%Y', e.event_date) = CAST(season.year AS TEXT)
    JOIN driver_teams dt ON r.driver_id = dt.driver_id AND dt.season_id = season.season_id
    JOIN teams t ON dt.team_id = t.team_id
    WHERE season.season_id = ? AND st.code = 'R' AND r.fastest_lap_time IS NOT NULL
    ORDER BY d.full_name, e.event_date
    """
    lap_times = pd.read_sql_query(query, conn, params=(season_id,))
    conn.close()
    return lap_times

# Add more query functions as needed