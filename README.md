# Formula 1 Data Analysis Dashboard

This project is a web-based dashboard for analyzing Formula 1 race data for the 2023 and 2024 seasons.

## Project Overview

The dashboard provides insights into Formula 1 driver performance, race outcomes, team statistics, and track conditions using data fetched from the FastF1 API.

## Features

- Interactive visualization dashboards displaying driver and team comparisons
- Race results and statistics
- Driver and team performance analysis
- Tire strategy analysis
- Qualifying performance analysis

## Technologies Used

- **Database**: SQLite for storing F1 data
- **Backend**: Python (Flask) for server-side scripting
- **API Integration**: FastF1 library for accessing F1 data
- **Frontend**: HTML, CSS, JavaScript with Plotly for visualization
- **CSS Framework**: Bootstrap 5

## Installation and Setup

1. Clone the repository:
   ```
   git clone https://github.com/gauri2029/ADT_Project.git
   cd ADT_Project
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the requirements:
   ```
   pip install -r requirements.txt
   ```

4. Initialize the database and load F1 data:
   ```
   python -m database.data_loader
   ```

5. Run the Flask application:
   ```
   python app.py
   ```

6. Open your browser and navigate to `http://localhost:5000`

## Project Structure

```
ADT_Project/
├── app.py                    # Main Flask application
├── requirements.txt          # Project dependencies
├── database/
│   ├── __init__.py           
│   ├── db_setup.py           # Database initialization
│   ├── schema.sql            # SQL schema
│   └── data_loader.py        # Data loading
├── services/
│   ├── __init__.py           
│   ├── f1_data_service.py    # FastF1 data fetching
│   └── query_service.py      # Database queries for dashboard
├── static/                   
│   ├── css/
│   │   └── style.css         
│   └── js/
│       └── dashboard.js      
├── templates/                
    └── index.html           
```

## Data Analysis Features

The dashboard enables users to explore queries such as:
- Draw a comparison between average lap times between different drivers for a specific race
- Find the number of podium finishes achieved by different teams over a season
- Analyze and compare lap times based on tire age for different teams
- Find the average qualifying positions of drivers across races
- Find the difference in lap times for different drivers based on weather conditions across different races

## Contributors

- Gauri Markandey - gsmarkan
- Krisha Elle - kelle
- Suraj Iyer - suraiyer
