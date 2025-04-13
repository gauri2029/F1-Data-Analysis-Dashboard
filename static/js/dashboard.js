document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const seasonSelect = document.getElementById('seasonSelect');
    const loadSeasonBtn = document.getElementById('loadSeasonBtn');
    const raceSelect = document.getElementById('raceSelect');
    const loadRaceBtn = document.getElementById('loadRaceBtn');
    
    // Initialize variables
    let currentSeasonId = 1; // Default to 2023 (season_id = 1)
    let currentEventId = null;
    
    // Event listeners
    loadSeasonBtn.addEventListener('click', function() {
        const selectedYear = seasonSelect.value;
        loadSeasonData(selectedYear);
        
        // Update currentSeasonId based on the selected year
        currentSeasonId = selectedYear === '2023' ? 1 : 2;
        
        // Reset race selection
        raceSelect.innerHTML = '<option value="">Select a race...</option>';
        currentEventId = null;
    });
    
    loadRaceBtn.addEventListener('click', function() {
        const selectedEventId = raceSelect.value;
        if (selectedEventId) {
            currentEventId = selectedEventId;
            loadRaceData(currentEventId);
        } else {
            alert('Please select a race first.');
        }
    });
    
    // Functions to fetch data from API
    async function loadSeasonData(year) {
        try {
            // Fetch events for the selected season
            const eventsResponse = await fetch(`/api/events/${year}`);
            const events = await eventsResponse.json();
            
            // Populate race selection dropdown
            raceSelect.innerHTML = '<option value="">Select a race...</option>';
            events.forEach(event => {
                const option = document.createElement('option');
                option.value = event.event_id;
                option.textContent = `Round ${event.round}: ${event.event_name}`;
                raceSelect.appendChild(option);
            });
            
            // Load podium finishes by team (season-level analysis)
            loadPodiumFinishes(currentSeasonId);
            
            // Load qualifying positions (season-level analysis)
            loadQualifyingPositions(currentSeasonId);
            
            // Show a message
            alert(`Loaded ${events.length} races for the ${year} season.`);
        } catch (error) {
            console.error('Error loading season data:', error);
            alert('Error loading season data. Check the console for details.');
        }
    }
    
    async function loadRaceData(eventId) {
        try {
            // Fetch sessions for the selected event
            const sessionsResponse = await fetch(`/api/sessions/${eventId}`);
            const sessions = await sessionsResponse.json();
            
            // Find the race session (code = 'R')
            const raceSession = sessions.find(session => session.session_code === 'R');
            
            if (raceSession) {
                // Load lap times comparison (race-level analysis)
                loadLapTimesComparison(eventId);
                
                // Load tire age analysis (race-level analysis)
                loadTireAgeAnalysis(eventId);
                
                // Show a message
                alert(`Loaded data for race session on ${raceSession.start_time}.`);
            } else {
                alert('No race session found for this event.');
            }
        } catch (error) {
            console.error('Error loading race data:', error);
            alert('Error loading race data. Check the console for details.');
        }
    }
    
    // Functions to load analysis data and create charts
    async function loadLapTimesComparison(eventId) {
        try {
            const response = await fetch(`/api/analysis/lap-times-comparison/${eventId}`);
            const data = await response.json();
            
            // Group by driver name
            const driverData = {};
            data.forEach(item => {
                if (!driverData[item.driver_name]) {
                    driverData[item.driver_name] = {
                        name: item.driver_name,
                        abbreviation: item.abbreviation,
                        team_name: item.team_name,
                        team_color: item.team_color,
                        compounds: {}
                    };
                }
                driverData[item.driver_name].compounds[item.compound] = item.avg_lap_time;
            });
            
            // Create data for the chart
            const chartData = [];
            Object.values(driverData).forEach(driver => {
                const trace = {
                    x: Object.keys(driver.compounds),
                    y: Object.values(driver.compounds),
                    type: 'bar',
                    name: driver.abbreviation,
                    marker: {
                        color: driver.team_color || '#000000'
                    }
                };
                chartData.push(trace);
            });
            
            // Create the chart
            Plotly.newPlot('lapTimesChart', chartData, {
                title: 'Average Lap Times by Compound',
                xaxis: { title: 'Tire Compound' },
                yaxis: { title: 'Average Lap Time (seconds)' },
                barmode: 'group'
            });
        } catch (error) {
            console.error('Error loading lap times comparison:', error);
        }
    }
    
    async function loadPodiumFinishes(seasonId) {
        try {
            const response = await fetch(`/api/analysis/podium-finishes/${seasonId}`);
            const data = await response.json();
            
            // Create data for the chart
            const chartData = [{
                x: data.map(item => item.team_name),
                y: data.map(item => item.podium_count),
                type: 'bar',
                marker: {
                    color: data.map(item => item.team_color || '#000000')
                }
            }];
            
            // Create the chart
            Plotly.newPlot('podiumsChart', chartData, {
                title: 'Podium Finishes by Team',
                xaxis: { title: 'Team' },
                yaxis: { title: 'Number of Podiums' }
            });
        } catch (error) {
            console.error('Error loading podium finishes:', error);
        }
    }
    
    async function loadTireAgeAnalysis(eventId) {
        try {
            const response = await fetch(`/api/analysis/tire-age/${eventId}`);
            const data = await response.json();
            
            // Group by compound
            const compoundData = {};
            data.forEach(item => {
                if (!compoundData[item.compound]) {
                    compoundData[item.compound] = {
                        compound: item.compound,
                        teams: [],
                        stint_lengths: [],
                        colors: []
                    };
                }
                compoundData[item.compound].teams.push(item.team_name);
                compoundData[item.compound].stint_lengths.push(item.avg_stint_length);
                compoundData[item.compound].colors.push(item.team_color || '#000000');
            });
            
            // Create data for the chart
            const chartData = [];
            Object.values(compoundData).forEach(compound => {
                const trace = {
                    x: compound.teams,
                    y: compound.stint_lengths,
                    type: 'bar',
                    name: compound.compound,
                    marker: {
                        color: compound.colors
                    }
                };
                chartData.push(trace);
            });
            
            // Create the chart
            Plotly.newPlot('tireAgeChart', chartData, {
                title: 'Average Stint Length by Tire Compound',
                xaxis: { title: 'Team' },
                yaxis: { title: 'Average Stint Length (laps)' },
                barmode: 'group'
            });
        } catch (error) {
            console.error('Error loading tire age analysis:', error);
        }
    }
    
    async function loadQualifyingPositions(seasonId) {
        try {
            const response = await fetch(`/api/analysis/qualifying-positions/${seasonId}`);
            const data = await response.json();
            
            // Sort data by average qualifying position
            data.sort((a, b) => a.avg_grid_position - b.avg_grid_position);
            
            // Create data for the chart
            const chartData = [{
                x: data.map(item => item.abbreviation),
                y: data.map(item => item.avg_grid_position),
                type: 'bar',
                marker: {
                    color: data.map(item => item.team_color || '#000000')
                }
            }];
            
            // Create the chart
            Plotly.newPlot('qualifyingChart', chartData, {
                title: 'Average Qualifying Positions',
                xaxis: { title: 'Driver' },
                yaxis: { title: 'Average Grid Position' }
            });
        } catch (error) {
            console.error('Error loading qualifying positions:', error);
        }
    }
    
    // Initialize with 2023 season data
    loadSeasonData('2023');
});