# Formula 1 Data Analysis Dashboard

An interactive web-based dashboard for analyzing Formula 1 race data for the 2023 and 2024 seasons, featuring comprehensive data visualization and analysis tools.

![F1 Dashboard Preview](https://i.imgur.com/example-preview.jpg)

## Project Overview

This dashboard provides in-depth insights into Formula 1 driver performance, race outcomes, team statistics, and track conditions using data fetched from the FastF1 API. The application offers interactive visualizations for data analysis across multiple dimensions of F1 racing.

## Features

### Data Analysis Capabilities
- **Driver Lap Time Comparison**: Compare average lap times between different drivers for specific races
- **Team Podium Analysis**: Visualize the number of podium finishes achieved by teams over a season
- **Tire Strategy Analysis**: Examine lap times based on tire age and compound for different teams
- **Qualifying Performance**: Track average qualifying positions of drivers across races
- **Weather Impact Analysis**: Analyze lap time differences based on weather conditions

### Interactive Features
- **Dynamic Visualizations**: Real-time, interactive charts and graphs using Plotly
- **Personalized Analysis Saving**: Save custom analyses for future reference
- **Responsive Design**: Optimized for both desktop and mobile devices
- **Driver & Team Standings**: Up-to-date championship standings tables

## Technologies Used

- **Database**: SQLite for storing F1 data
- **Backend**: Python (Flask) for server-side operations
- **API Integration**: FastF1 library for accessing official Formula 1 data
- **Frontend**: HTML, CSS, JavaScript with Plotly for visualization
- **CSS Framework**: Bootstrap 5 for responsive design

## Installation and Setup

### Prerequisites
- Python 3.8 or higher
- Git

### Setup Instructions

1. **Clone the repository**:
   ```
   git clone https://github.com/yourusername/F1-Data-Analysis-Dashboard.git
   cd F1-Data-Analysis-Dashboard
   ```

2. **Create and activate a virtual environment**:
   ```
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install the required dependencies**:
   ```
   pip install -r requirements.txt
   ```

4. **Initialize the database and load F1 data**:
   ```
   python -m database.data_loader
   ```
   > **Note**: This process may take some time as it downloads and processes F1 data for the 2023 and 2024 seasons.

5. **Start the Flask application**:
   ```
   python app.py
   ```

6. **Access the dashboard**:
   Open your browser and navigate to `http://localhost:5000`

## Using the Dashboard

1. **Select a Season**: Choose between 2023 and 2024 F1 seasons
2. **Select a Race**: Choose a specific Grand Prix event
3. **Explore Data**: Navigate through the tabs to view different analyses:
   - Race Analysis (lap times, tire strategies)
   - Season Statistics (podiums, qualifying performance)
   - Driver and Team Standings
4. **Save Analyses**: Save your current view for future reference

## Data Analysis Features in Detail

### Lap Time Comparison
Visualizes and compares average lap times between different drivers for a specific race, helping to identify performance patterns across different drivers and teams.

### Podium Finishes Analysis
Analyzes the number of podium finishes achieved by different teams over a season, providing insights into team performance consistency.

### Tire Age Analysis
Examines how tire age affects lap times for different teams, helping to understand tire degradation patterns and team-specific tire management strategies.

### Qualifying Performance
Tracks average qualifying positions of drivers across races, showcasing driver performance in qualifying sessions throughout the season.

### Weather Condition Analysis
Analyzes how different weather conditions impact lap times for different drivers, highlighting driver skills in varying track conditions.

## Project Structure

```
F1-Data-Analysis-Dashboard/
├── app.py                    # Main Flask application entry point
├── requirements.txt          # Project dependencies
├── database/
│   ├── __init__.py           
│   ├── db_setup.py           # Database initialization
│   ├── schema.sql            # SQL schema
│   └── data_loader.py        # Data loading utility
├── services/
│   ├── __init__.py           
│   ├── f1_data_service.py    # FastF1 data fetching service
│   └── query_service.py      # Database queries for dashboard
├── static/                   
│   ├── css/
│   │   └── style.css         # Custom styling
│   └── js/
│       └── dashboard.js      # Dashboard interactivity
├── templates/                
│   └── index.html            # Main dashboard template
└── cache/                    # FastF1 cache directory
```

## Troubleshooting

- **Database Initialization Issues**: If you encounter database errors, try removing the database file (`database/f1_database.db`) and running the data loader again.
- **FastF1 API Errors**: FastF1 occasionally has rate limits. If you encounter API errors, wait a few minutes and try again.
- **Chart Display Issues**: If charts don't display properly, try clearing your browser cache or using another browser.

## Contributors

- Gauri Markandey - gsmarkan
- Krisha Elle - kelle
- Suraj Iyer - suraiyer

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [FastF1](https://github.com/theOehrly/Fast-F1) library for providing access to F1 data
- Formula 1 for the race data
- [Plotly](https://plotly.com/) for the visualization library