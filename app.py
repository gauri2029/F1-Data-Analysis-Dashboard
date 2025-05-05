from flask import Flask, jsonify, render_template, request
import os
import sys
import traceback
from database.db_setup import init_db, get_db_connection
from services import query_service

try:
    from flask_cors import CORS
    has_cors = True
except ImportError:
    has_cors = False
    print("Warning: flask_cors not installed. Cross-origin requests will be blocked.")
    print("Install with: pip install flask-cors")

app = Flask(__name__)

if has_cors:
    CORS(app)

print("Initializing database...")
try:
    with app.app_context():
        db_initialized = init_db()
        if db_initialized:
            print("Database initialized successfully!")
        else:
            print("Database already exists or initialization failed. Continuing...")
except Exception as e:
    print(f"WARNING: Database initialization error: {e}")
    traceback.print_exc()
    print("Continuing with application startup...")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/seasons', methods=['GET'])
def get_seasons():
    try:
        seasons = query_service.get_all_seasons()
        return jsonify(seasons.to_dict(orient='records'))
    except Exception as e:
        print(f"Error fetching seasons: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/circuits', methods=['GET'])
def get_circuits():
    try:
        circuits = query_service.get_all_circuits()
        return jsonify(circuits.to_dict(orient='records'))
    except Exception as e:
        print(f"Error fetching circuits: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/drivers', methods=['GET'])
def get_drivers():
    try:
        drivers = query_service.get_all_drivers()
        return jsonify(drivers.to_dict(orient='records'))
    except Exception as e:
        print(f"Error fetching drivers: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/teams', methods=['GET'])
def get_teams():
    try:
        teams = query_service.get_all_teams()
        return jsonify(teams.to_dict(orient='records'))
    except Exception as e:
        print(f"Error fetching teams: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/events/<int:year>', methods=['GET'])
def get_events(year):
    try:
        events = query_service.get_events_by_season(year)
        return jsonify(events.to_dict(orient='records'))
    except Exception as e:
        print(f"Error fetching events for year {year}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/sessions/<int:event_id>', methods=['GET'])
def get_sessions(event_id):
    try:
        sessions = query_service.get_sessions_by_event(event_id)
        return jsonify(sessions.to_dict(orient='records'))
    except Exception as e:
        print(f"Error fetching sessions for event {event_id}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/results/<int:session_id>', methods=['GET'])
def get_results(session_id):
    try:
        results = query_service.get_results_by_session(session_id)
        return jsonify(results.to_dict(orient='records'))
    except Exception as e:
        print(f"Error fetching results for session {session_id}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/qualifying/<int:session_id>', methods=['GET'])
def get_qualifying(session_id):
    try:
        quali_times = query_service.get_qualifying_times_by_session(session_id)
        return jsonify(quali_times.to_dict(orient='records'))
    except Exception as e:
        print(f"Error fetching qualifying times for session {session_id}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/strategies/<int:session_id>', methods=['GET'])
def get_strategies(session_id):
    try:
        strategies = query_service.get_race_strategies_by_session(session_id)
        return jsonify(strategies.to_dict(orient='records'))
    except Exception as e:
        print(f"Error fetching strategies for session {session_id}: {e}")
        return jsonify({"error": str(e)}), 500

# Custom analysis endpoints
@app.route('/api/analysis/driver-performance/<int:season_id>', methods=['GET'])
def get_driver_performance(season_id):
    try:
        performance = query_service.get_driver_performance_by_season(season_id)
        return jsonify(performance.to_dict(orient='records'))
    except Exception as e:
        print(f"Error fetching driver performance for season {season_id}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/analysis/team-performance/<int:season_id>', methods=['GET'])
def get_team_performance(season_id):
    try:
        performance = query_service.get_team_performance_by_season(season_id)
        return jsonify(performance.to_dict(orient='records'))
    except Exception as e:
        print(f"Error fetching team performance for season {season_id}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/analysis/lap-times-comparison/<int:event_id>', methods=['GET'])
def compare_lap_times(event_id):
    try:
        comparison = query_service.compare_lap_times_by_race(event_id)
        return jsonify(comparison.to_dict(orient='records'))
    except Exception as e:
        print(f"Error comparing lap times for event {event_id}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/analysis/podium-finishes/<int:season_id>', methods=['GET'])
def count_podium_finishes(season_id):
    try:
        podiums = query_service.count_podium_finishes_by_team(season_id)
        return jsonify(podiums.to_dict(orient='records'))
    except Exception as e:
        print(f"Error counting podium finishes for season {season_id}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/analysis/tire-age/<int:event_id>', methods=['GET'])
def analyze_tire_age(event_id):
    try:
        analysis = query_service.analyze_lap_times_by_tire_age(event_id)
        return jsonify(analysis.to_dict(orient='records'))
    except Exception as e:
        print(f"Error analyzing tire age for event {event_id}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/analysis/qualifying-positions/<int:season_id>', methods=['GET'])
def get_qualifying_positions(season_id):
    try:
        positions = query_service.get_average_qualifying_positions(season_id)
        return jsonify(positions.to_dict(orient='records'))
    except Exception as e:
        print(f"Error getting qualifying positions for season {season_id}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/analysis/weather-conditions/<int:season_id>', methods=['GET'])
def compare_weather_conditions(season_id):
    try:
        comparison = query_service.compare_lap_times_by_weather(season_id)
        return jsonify(comparison.to_dict(orient='records'))
    except Exception as e:
        print(f"Error comparing weather conditions for season {season_id}: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("\nStarting Formula 1 Data Analysis Dashboard...")
    print(f"Python version: {sys.version}")
    # Run the app with debug mode enabled
    app.run(debug=True, port=5000)