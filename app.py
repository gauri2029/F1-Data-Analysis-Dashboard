from flask import Flask, jsonify, render_template, request
import os
from database.db_setup import init_db, get_db_connection
from services import query_service

app = Flask(__name__)

# Initialize the database on startup
# @app.before_first_request
# def initialize_database():
#     init_db()

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# API endpoints
@app.route('/api/seasons', methods=['GET'])
def get_seasons():
    seasons = query_service.get_all_seasons()
    return jsonify(seasons.to_dict(orient='records'))

@app.route('/api/circuits', methods=['GET'])
def get_circuits():
    circuits = query_service.get_all_circuits()
    return jsonify(circuits.to_dict(orient='records'))

@app.route('/api/drivers', methods=['GET'])
def get_drivers():
    drivers = query_service.get_all_drivers()
    return jsonify(drivers.to_dict(orient='records'))

@app.route('/api/teams', methods=['GET'])
def get_teams():
    teams = query_service.get_all_teams()
    return jsonify(teams.to_dict(orient='records'))

@app.route('/api/events/<int:year>', methods=['GET'])
def get_events(year):
    events = query_service.get_events_by_season(year)
    return jsonify(events.to_dict(orient='records'))

@app.route('/api/sessions/<int:event_id>', methods=['GET'])
def get_sessions(event_id):
    sessions = query_service.get_sessions_by_event(event_id)
    return jsonify(sessions.to_dict(orient='records'))

@app.route('/api/results/<int:session_id>', methods=['GET'])
def get_results(session_id):
    results = query_service.get_results_by_session(session_id)
    return jsonify(results.to_dict(orient='records'))

@app.route('/api/qualifying/<int:session_id>', methods=['GET'])
def get_qualifying(session_id):
    quali_times = query_service.get_qualifying_times_by_session(session_id)
    return jsonify(quali_times.to_dict(orient='records'))

@app.route('/api/strategies/<int:session_id>', methods=['GET'])
def get_strategies(session_id):
    strategies = query_service.get_race_strategies_by_session(session_id)
    return jsonify(strategies.to_dict(orient='records'))

# Custom analysis endpoints
@app.route('/api/analysis/driver-performance/<int:season_id>', methods=['GET'])
def get_driver_performance(season_id):
    performance = query_service.get_driver_performance_by_season(season_id)
    return jsonify(performance.to_dict(orient='records'))

@app.route('/api/analysis/team-performance/<int:season_id>', methods=['GET'])
def get_team_performance(season_id):
    performance = query_service.get_team_performance_by_season(season_id)
    return jsonify(performance.to_dict(orient='records'))

@app.route('/api/analysis/lap-times-comparison/<int:event_id>', methods=['GET'])
def compare_lap_times(event_id):
    comparison = query_service.compare_lap_times_by_race(event_id)
    return jsonify(comparison.to_dict(orient='records'))

@app.route('/api/analysis/podium-finishes/<int:season_id>', methods=['GET'])
def count_podium_finishes(season_id):
    podiums = query_service.count_podium_finishes_by_team(season_id)
    return jsonify(podiums.to_dict(orient='records'))

@app.route('/api/analysis/tire-age/<int:event_id>', methods=['GET'])
def analyze_tire_age(event_id):
    analysis = query_service.analyze_lap_times_by_tire_age(event_id)
    return jsonify(analysis.to_dict(orient='records'))

@app.route('/api/analysis/qualifying-positions/<int:season_id>', methods=['GET'])
def get_qualifying_positions(season_id):
    positions = query_service.get_average_qualifying_positions(season_id)
    return jsonify(positions.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(debug=True)