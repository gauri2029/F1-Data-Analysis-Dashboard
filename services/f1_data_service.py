import fastf1
import pandas as pd
import os
import sqlite3
from database.db_setup import get_db_connection, get_db_path, init_db
from fastf1.ergast import Ergast  # Added Ergast API import

# Set FastF1 cache directory
cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'cache')
os.makedirs(cache_dir, exist_ok=True)
fastf1.Cache.enable_cache(cache_dir)

def fetch_season_calendar(year):
    """Fetch the F1 calendar for a specific season"""
    try:
        schedule = fastf1.get_event_schedule(year)
        return schedule
    except Exception as e:
        print(f"Error fetching calendar for {year}: {e}")
        return None

def fetch_session_data(year, round_number, session_name):
    """
    Fetch data for a specific session
    
    Parameters:
    - year: Season year (e.g., 2023)
    - round_number: Race round number
    - session_name: Session name ('Q', 'SQ', 'R', 'S')
    
    Returns:
    - fastf1.core.Session object
    """
    try:
        session = fastf1.get_session(year, round_number, session_name)
        session.load()
        return session
    except Exception as e:
        print(f"Error loading {session_name} data for {year} round {round_number}: {e}")
        return None

def get_driver_info_ergast(year):
    """
    Get comprehensive driver information from Ergast API
    This replaces the original function that had missing data
    """
    try:
        ergast = Ergast()
        response = ergast.get_driver_info(season=year, result_type='raw')
        
        drivers = []
        for driver in response:
            full_name = f"{driver.get('givenName', '')} {driver.get('familyName', '')}".strip()
            driver_info = {
                'driver_id': int(driver.get('permanentNumber', 0)),
                'full_name': full_name,
                'abbreviation': driver.get('code', ''),
                'number': int(driver.get('permanentNumber', 0)),
                'driver_ref': driver['driverId'],
                'nationality': driver.get('nationality', '')
            }
            drivers.append(driver_info)
        
        return pd.DataFrame(drivers)
    except Exception as e:
        print(f"Error fetching driver info from Ergast for {year}: {e}")
        return None

def get_driver_info(session):
    """Extract driver information from a session (original function preserved)"""
    if session is None:
        return None
    
    try:
        # Get driver information
        driver_info = session.get_driver_info()
        
        # Create a DataFrame with driver details
        drivers_df = pd.DataFrame([
            {
                'driver_id': int(row['DriverNumber']),
                'full_name': row['FullName'],
                'abbreviation': row['Abbreviation'],
                'number': int(row['DriverNumber']),
                'driver_ref': row['LastName'].lower().replace(' ', '_'),
                'nationality': row.get('Nationality', '')
            }
            for _, row in driver_info.iterrows()
        ])
        
        return drivers_df
    except Exception as e:
        print(f"Error extracting driver info: {e}")
        return None

def get_team_info_ergast(year):
    """
    Get comprehensive team information from Ergast API
    This addresses the missing nationality data
    """
    try:
        ergast = Ergast()
        response = ergast.get_constructor_info(season=year, result_type='raw')
        
        teams = []
        for i, team in enumerate(response, start=1):
            team_info = {
                'team_id': i,
                'name': team['name'],
                'nationality': team['nationality'],
                'constructor_ref': team['constructorId'],
                'team_color': get_team_color(team['name'])
            }
            teams.append(team_info)
        
        return pd.DataFrame(teams)
    except Exception as e:
        print(f"Error fetching team info from Ergast for {year}: {e}")
        return None

def get_team_color(team_name):
    """Get team color from FastF1's TEAM_COLORS dictionary or fallback to default"""
    try:
        from fastf1.plotting import TEAM_COLORS
        
        for key in TEAM_COLORS:
            if key.lower() in team_name.lower():
                return TEAM_COLORS[key]
    except Exception as e:
        print(f"Error getting team color: {e}")
    
    # Fallback to a default color if no match found
    return '#000000'

def get_team_info(session):
    """Extract team information from a session (original function preserved)"""
    if session is None:
        return None
    
    try:
        # Get team information
        teams = {}
        results = session.results
        
        for _, row in results.iterrows():
            team_name = row['TeamName']
            if team_name not in teams:
                constructor_ref = team_name.lower().replace(' ', '_')
                team_color = row.get('TeamColor', '#000000')
                teams[team_name] = {
                    'team_id': len(teams) + 1,
                    'name': team_name,
                    'nationality': '',  # FastF1 might not provide this directly
                    'constructor_ref': constructor_ref,
                    'team_color': team_color
                }
        
        teams_df = pd.DataFrame(list(teams.values()))
        return teams_df
    except Exception as e:
        print(f"Error extracting team info: {e}")
        return None

def get_driver_team_mapping(session, season_id):
    """Map drivers to teams for a specific season"""
    if session is None:
        return None
    
    try:
        # Get driver-team relationships
        results = session.results
        driver_teams = []
        
        for _, row in results.iterrows():
            driver_number = row['DriverNumber']
            team_name = row['TeamName']
            
            # You'll need to get the driver_id and team_id from the database
            # For now, we'll use placeholder IDs based on the session data
            driver_teams.append({
                'driver_id': int(driver_number),
                'team_name': team_name,
                'season_id': season_id
            })
        
        return pd.DataFrame(driver_teams)
    except Exception as e:
        print(f"Error extracting driver-team mapping: {e}")
        return None

def get_driver_team_mapping_ergast(year):
    """
    Get driver-team mapping from Ergast API for a specific season
    """
    try:
        ergast = Ergast()
        pairings = []
        
        for round_num in range(1, 25):  # Up to 24 rounds per season to be safe
            try:
                races = ergast.get_race_results(season=year, round=round_num, result_type='raw')
                
                if not races:
                    continue
                
                race = races[0]
                results = race['Results']
                
                for entry in results:
                    driver_id = int(entry['Driver'].get('permanentNumber', 0))
                    constructor_id = entry['Constructor']['constructorId']
                    
                    pairings.append({
                        'driver_id': driver_id,
                        'constructor_ref': constructor_id,
                        'season_id': get_season_id_by_year(year)
                    })
            except Exception as e:
                print(f"Error fetching results for {year} Round {round_num}: {e}")
        
        # Convert to DataFrame and deduplicate
        df_pairings = pd.DataFrame(pairings).drop_duplicates()
        return df_pairings
    except Exception as e:
        print(f"Error getting driver-team mapping for {year}: {e}")
        return None

def get_season_id_by_year(year):
    """Helper function to get season_id by year"""
    # In this simplified version, we're just converting it directly
    return year - 2000  # This is just a simple mapping, adjust as needed

def get_race_result(session):
    """Extract race results from a session"""
    if session is None or not hasattr(session, 'results'):
        return None
    
    try:
        results = session.results
        race_results = []
        
        for _, row in results.iterrows():
            result = {
                'driver_id': int(row['DriverNumber']),
                'finishing_position': row.get('Position', None),
                'grid_position': row.get('GridPosition', None),
                'status': row.get('Status', 'Unknown'),
                'points': row.get('Points', 0.0),
            }
            
            # Add fastest lap info if available
            if 'FastestLap' in row and pd.notna(row['FastestLap']):
                result['fastest_lap_number'] = row['FastestLap']
                
                if 'FastestLapTime' in row and pd.notna(row['FastestLapTime']):
                    # Convert lap time to seconds if it's in timedelta format
                    if hasattr(row['FastestLapTime'], 'total_seconds'):
                        result['fastest_lap_time'] = row['FastestLapTime'].total_seconds()
                    else:
                        result['fastest_lap_time'] = row['FastestLapTime']
            
            race_results.append(result)
        
        return pd.DataFrame(race_results)
    except Exception as e:
        print(f"Error extracting race results: {e}")
        return None

def get_qualifying_times(session):
    """Extract qualifying times from a qualifying session"""
    if session is None or session.name != 'Qualifying':
        return None
    
    try:
        quali_results = session.results
        q_times = []
        
        for _, row in quali_results.iterrows():
            q_time = {
                'driver_id': int(row['DriverNumber']),
                'q1_time': None,
                'q2_time': None,
                'q3_time': None
            }
            
            # Convert qualifying times to seconds
            for q_session in ['Q1', 'Q2', 'Q3']:
                if q_session in row and pd.notna(row[q_session]):
                    time_key = q_session.lower() + '_time'
                    if hasattr(row[q_session], 'total_seconds'):
                        q_time[time_key] = row[q_session].total_seconds()
                    else:
                        q_time[time_key] = row[q_session]
            
            q_times.append(q_time)
        
        return pd.DataFrame(q_times)
    except Exception as e:
        print(f"Error extracting qualifying times: {e}")
        return None

def get_race_strategies(session):
    """Extract race strategies (tire stints) from a race session"""
    if session is None or session.name not in ['Race', 'Sprint']:
        return None
    
    try:
        # If the session has laps loaded
        if hasattr(session, 'laps') and hasattr(session.laps, 'get_stints'):
            # Try to get stint data
            stints = session.laps.get_stints(aggregate=False)
            if stints is None or stints.empty:
                return fetch_strategies_fallback(session)
            
            strategies = []
            
            for _, stint in stints.iterrows():
                strategy = {
                    'driver_id': int(stint['DriverNumber']),
                    'stint_number': int(stint['StintNumber']),
                    'compound': stint['Compound'],
                    'stint_start_lap': int(stint['StartLap']),
                    'stint_end_lap': int(stint['EndLap']),
                    'stint_length': int(stint['EndLap'] - stint['StartLap'] + 1)
                }
                strategies.append(strategy)
            
            return pd.DataFrame(strategies)
        else:
            return fetch_strategies_fallback(session)
    except Exception as e:
        print(f"Error extracting race strategies: {e}")
        return fetch_strategies_fallback(session)

def fetch_strategies_fallback(session):
    """
    Fallback strategy to get tire data when the primary method fails
    
    This attempts to reconstruct strategy data by analyzing the lap-by-lap telemetry
    """
    try:
        if not hasattr(session, 'laps'):
            print("Session doesn't have lap data for strategy analysis")
            return None
            
        # Get the race lap data
        lap_data = session.laps
        
        # Get unique drivers
        drivers = lap_data['DriverNumber'].unique()
        
        strategies = []
        
        for driver in drivers:
            # Get all laps for this driver
            driver_laps = lap_data[lap_data['DriverNumber'] == driver].sort_values('LapNumber')
            
            if driver_laps.empty or 'Compound' not in driver_laps.columns:
                continue
                
            # Identify tire changes by looking for compound changes
            current_compound = None
            stint_start = 1
            stint_num = 1
            
            for idx, lap in driver_laps.iterrows():
                lap_num = lap['LapNumber']
                compound = lap.get('Compound')
                
                if pd.isna(compound):
                    continue
                    
                # If compound changed or this is the first lap with a compound
                if compound != current_compound and not pd.isna(compound):
                    # If this isn't the first compound, log the previous stint
                    if current_compound is not None:
                        strategies.append({
                            'driver_id': int(driver),
                            'stint_number': stint_num,
                            'compound': current_compound,
                            'stint_start_lap': stint_start,
                            'stint_end_lap': lap_num - 1,
                            'stint_length': lap_num - stint_start
                        })
                        stint_num += 1
                    
                    # Start a new stint
                    current_compound = compound
                    stint_start = lap_num
            
            # Don't forget to add the last stint
            if current_compound is not None:
                final_lap = driver_laps['LapNumber'].max()
                strategies.append({
                    'driver_id': int(driver),
                    'stint_number': stint_num,
                    'compound': current_compound,
                    'stint_start_lap': stint_start,
                    'stint_end_lap': final_lap,
                    'stint_length': final_lap - stint_start + 1
                })
        
        if strategies:
            return pd.DataFrame(strategies)
        else:
            return None
    except Exception as e:
        print(f"Error in strategy fallback: {e}")
        return None

def insert_seasons(conn, years):
    """Insert seasons into the database"""
    cursor = conn.cursor()
    
    for i, year in enumerate(years, start=1):
        cursor.execute(
            "INSERT OR IGNORE INTO seasons (season_id, year) VALUES (?, ?)",
            (i, year)
        )
    
    conn.commit()
    
def insert_circuits(conn, schedule):
    """Insert circuit information into the database"""
    cursor = conn.cursor()
    
    for i, (_, event) in enumerate(schedule.iterrows(), start=1):
        cursor.execute(
            "INSERT OR IGNORE INTO circuits (circuit_id, name, country, location) VALUES (?, ?, ?, ?)",
            (i, event['EventName'], event['Country'], event['Location'])
        )
    
    conn.commit()

def insert_events(conn, schedule, year):
    """Insert event information into the database"""
    cursor = conn.cursor()
    
    for _, event in schedule.iterrows():
        # Get circuit_id by matching circuit name
        cursor.execute(
            "SELECT circuit_id FROM circuits WHERE name = ?",
            (event['EventName'],)
        )
        circuit_id = cursor.fetchone()
        
        if circuit_id:
            circuit_id = circuit_id[0]
            # Format the date
            event_date = pd.to_datetime(event['EventDate']).strftime('%Y-%m-%d')
            
            cursor.execute(
                "INSERT OR IGNORE INTO events (circuit_id, event_name, event_date, round) VALUES (?, ?, ?, ?)",
                (circuit_id, event['EventName'], event_date, event['RoundNumber'])
            )
    
    conn.commit()

def insert_session(conn, event_id, session_type_id, session_data):
    """Insert session information into the database"""
    cursor = conn.cursor()
    
    if session_data and hasattr(session_data, 'date'):
        start_time = session_data.date.strftime('%Y-%m-%d %H:%M:%S')
        # Assuming a session lasts 2 hours (this is approximate)
        end_time = (session_data.date + pd.Timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute(
            "INSERT INTO sessions (event_id, session_type_id, start_time, end_time) VALUES (?, ?, ?, ?)",
            (event_id, session_type_id, start_time, end_time)
        )
        
        session_id = cursor.lastrowid
        conn.commit()
        return session_id
    
    return None

def insert_drivers(conn, drivers_df):
    """Insert driver information into the database"""
    if drivers_df is None or drivers_df.empty:
        return
    
    cursor = conn.cursor()
    
    for _, driver in drivers_df.iterrows():
        cursor.execute(
            """
            INSERT OR IGNORE INTO drivers 
            (driver_id, full_name, abbreviation, number, driver_ref, nationality) 
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                driver['driver_id'],
                driver['full_name'],
                driver['abbreviation'],
                driver['number'],
                driver['driver_ref'],
                driver['nationality']
            )
        )
    
    conn.commit()

def insert_teams(conn, teams_df):
    """Insert team information into the database"""
    if teams_df is None or teams_df.empty:
        return
    
    cursor = conn.cursor()
    
    for _, team in teams_df.iterrows():
        cursor.execute(
            """
            INSERT OR IGNORE INTO teams 
            (team_id, name, nationality, constructor_ref, team_color) 
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                team['team_id'],
                team['name'],
                team['nationality'],
                team['constructor_ref'],
                team['team_color']
            )
        )
    
    conn.commit()

def insert_driver_teams(conn, driver_teams_df):
    """Insert driver-team relationships into the database"""
    if driver_teams_df is None or driver_teams_df.empty:
        return
    
    cursor = conn.cursor()
    
    for _, relationship in driver_teams_df.iterrows():
        # Check if we have constructor_ref or team_name
        if 'constructor_ref' in relationship:
            # Get team_id by constructor_ref
            cursor.execute("SELECT team_id FROM teams WHERE constructor_ref = ?", (relationship['constructor_ref'],))
            team_id_row = cursor.fetchone()
        else:
            # Get team_id by name
            cursor.execute("SELECT team_id FROM teams WHERE name = ?", (relationship['team_name'],))
            team_id_row = cursor.fetchone()
        
        if team_id_row:
            team_id = team_id_row[0]
            
            # Create a unique driver_team_id
            cursor.execute(
                """
                INSERT OR IGNORE INTO driver_teams 
                (driver_id, team_id, season_id) 
                VALUES (?, ?, ?)
                """,
                (
                    relationship['driver_id'],
                    team_id,
                    relationship['season_id']
                )
            )
    
    conn.commit()

def insert_results(conn, session_id, results_df):
    """Insert race results into the database"""
    if results_df is None or results_df.empty or session_id is None:
        return
    
    cursor = conn.cursor()
    
    for _, result in results_df.iterrows():
        cursor.execute(
            """
            INSERT INTO results 
            (session_id, driver_id, finishing_position, grid_position, status, points, 
             fastest_lap_time, fastest_lap_number) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session_id,
                result['driver_id'],
                result.get('finishing_position'),
                result.get('grid_position'),
                result.get('status'),
                result.get('points', 0.0),
                result.get('fastest_lap_time'),
                result.get('fastest_lap_number')
            )
        )
    
    conn.commit()

def insert_qualifying_times(conn, session_id, quali_times_df):
    """Insert qualifying times into the database"""
    if quali_times_df is None or quali_times_df.empty or session_id is None:
        return
    
    cursor = conn.cursor()
    
    for _, q_time in quali_times_df.iterrows():
        cursor.execute(
            """
            INSERT INTO qualifying_times 
            (session_id, driver_id, q1_time, q2_time, q3_time) 
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                session_id,
                q_time['driver_id'],
                q_time.get('q1_time'),
                q_time.get('q2_time'),
                q_time.get('q3_time')
            )
        )
    
    conn.commit()

def insert_race_strategies(conn, session_id, strategies_df):
    """Insert race strategies into the database"""
    if strategies_df is None or strategies_df.empty or session_id is None:
        return
    
    cursor = conn.cursor()
    
    for _, strategy in strategies_df.iterrows():
        cursor.execute(
            """
            INSERT INTO race_strategies 
            (session_id, driver_id, stint_number, compound, stint_start_lap, stint_end_lap, stint_length) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session_id,
                strategy['driver_id'],
                strategy['stint_number'],
                strategy['compound'],
                strategy['stint_start_lap'],
                strategy['stint_end_lap'],
                strategy['stint_length']
            )
        )
    
    conn.commit()

def load_season_data(year):
    """
    Load and insert data for an entire F1 season
    
    Parameters:
    - year: The season year (e.g., 2023)
    """
    print(f"Loading data for {year} season...")
    
    # Get database connection
    conn = get_db_connection()
    
    try:
        # Get the season_id for this year
        cursor = conn.cursor()
        cursor.execute("SELECT season_id FROM seasons WHERE year = ?", (year,))
        season_id_row = cursor.fetchone()
        
        if not season_id_row:
            print(f"Season {year} not found in database. Inserting...")
            insert_seasons(conn, [year])
            cursor.execute("SELECT season_id FROM seasons WHERE year = ?", (year,))
            season_id_row = cursor.fetchone()
        
        season_id = season_id_row[0]
        
        # Fetch calendar for the season
        calendar = fetch_season_calendar(year)
        if calendar is None:
            print(f"Could not fetch calendar for {year}")
            return
        
        # Insert circuits
        insert_circuits(conn, calendar)
        
        # Insert events
        insert_events(conn, calendar, year)
        
        # Fetch and insert team data from Ergast API (solves missing nationality)
        teams_df = get_team_info_ergast(year)
        insert_teams(conn, teams_df)
        
        # Fetch and insert driver data from Ergast API (solves missing driver data)
        drivers_df = get_driver_info_ergast(year) 
        insert_drivers(conn, drivers_df)
        
        # Fetch and insert driver-team mapping from Ergast API
        driver_teams_df = get_driver_team_mapping_ergast(year)
        insert_driver_teams(conn, driver_teams_df)
        
        # Process each round in the calendar
        for _, event in calendar.iterrows():
            round_number = event['RoundNumber']
            event_name = event['EventName']
            
            print(f"Processing {year} Round {round_number}: {event_name}")
            
            # Get event_id from database
            cursor.execute(
                "SELECT event_id FROM events WHERE round = ? AND event_date LIKE ?", 
                (round_number, f"{year}%")
            )
            event_id_row = cursor.fetchone()
            
            if not event_id_row:
                print(f"Event not found for {year} Round {round_number}")
                continue
                
            event_id = event_id_row[0]
            
            # Process Qualifying session
            quali_session = fetch_session_data(year, round_number, 'Q')
            if quali_session:
                # Insert the session
                quali_session_id = insert_session(conn, event_id, 1, quali_session)  # 1 = Qualifying
                
                # Insert qualifying results
                results_df = get_race_result(quali_session)
                insert_results(conn, quali_session_id, results_df)
                
                # Insert qualifying times
                quali_times_df = get_qualifying_times(quali_session)
                insert_qualifying_times(conn, quali_session_id, quali_times_df)
            
            # Process Sprint Qualifying if it exists for this event
            sprint_quali_session = fetch_session_data(year, round_number, 'SQ')
            if sprint_quali_session:
                # Insert the session
                sprint_quali_session_id = insert_session(conn, event_id, 2, sprint_quali_session)  # 2 = Sprint Qualifying
                
                # Insert sprint qualifying results
                results_df = get_race_result(sprint_quali_session)
                insert_results(conn, sprint_quali_session_id, results_df)
            
            # Process Sprint Race if it exists for this event
            sprint_session = fetch_session_data(year, round_number, 'S')
            if sprint_session:
                # Insert the session
                sprint_session_id = insert_session(conn, event_id, 3, sprint_session)  # 3 = Sprint Race
                
                # Insert sprint results
                results_df = get_race_result(sprint_session)
                insert_results(conn, sprint_session_id, results_df)
                
                # Insert sprint race strategies
                strategies_df = get_race_strategies(sprint_session)
                if strategies_df is not None and not strategies_df.empty:
                    insert_race_strategies(conn, sprint_session_id, strategies_df)
                else:
                    print(f"No strategy data available for {year} round {round_number} sprint race")
            
            # Process Main Race
            race_session = fetch_session_data(year, round_number, 'R')
            if race_session:
                # Insert the session
                race_session_id = insert_session(conn, event_id, 4, race_session)  # 4 = Race
                
                # Insert race results
                results_df = get_race_result(race_session)
                insert_results(conn, race_session_id, results_df)
                
                # Try to load full lap data for more accurate strategy information
                try:
                    race_session.load_laps(with_telemetry=True)
                except Exception as e:
                    print(f"Could not load detailed lap data: {e}")
                
                # Insert race strategies
                strategies_df = get_race_strategies(race_session)
                if strategies_df is not None and not strategies_df.empty:
                    insert_race_strategies(conn, race_session_id, strategies_df)
                else:
                    print(f"No strategy data available for {year} round {round_number} race")
    
    except Exception as e:
        print(f"Error loading data for {year} season: {e}")
    finally:
        conn.close()
        
    print(f"Completed loading data for {year} season!")

if __name__ == "__main__":
    # Initialize the database
    init_db()
    
    # Load data for seasons (expanded range)
    for year in [2023, 2024]:
        load_season_data(year)