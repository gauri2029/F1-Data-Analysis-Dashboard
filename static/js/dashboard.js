// Dashboard.js (Full CSV-based visualizations with strict event_id matching fix)

const loadCSV = (path) => {
  return new Promise((resolve, reject) => {
    Papa.parse(path, {
      header: true,
      download: true,
      complete: (results) => resolve(results.data),
      error: reject
    });
  });
};

const normalize = str => str?.toLowerCase().trim();

document.addEventListener('DOMContentLoaded', () => {
  const seasonSelect = document.getElementById('seasonSelect');
  const loadSeasonBtn = document.getElementById('loadSeasonBtn');
  const raceSelect = document.getElementById('raceSelect');
  const loadRaceBtn = document.getElementById('loadRaceBtn');

  const lapTimesChart = document.getElementById('lapTimesChart');
  const podiumsChart = document.getElementById('podiumsChart');
  const tireAgeChart = document.getElementById('tireAgeChart');
  const driverStandingsBody = document.getElementById('driverStandingsBody');

  loadSeasonBtn.addEventListener('click', async () => {
    const year = seasonSelect.value;
    const events = await loadCSV(`/static/data/events.csv`);
    const filteredEvents = events.filter(e => e.season === year);

    raceSelect.innerHTML = '<option value="">Select a race...</option>';
    filteredEvents.forEach(ev => {
      const opt = document.createElement('option');
      opt.value = ev.event_id;
      opt.textContent = `Round ${ev.round}: ${ev.event_name}`;
      raceSelect.appendChild(opt);
    });

    await loadPodiumsChart(year);
    await loadDriverStandings(year);
  });

  loadRaceBtn.addEventListener('click', async () => {
    const eventId = raceSelect.value;
    if (!eventId) return alert("Please select a race to view results.");
    await loadLapTimesChart(eventId);
    await loadTireAgeChart(eventId);
  });

  async function loadPodiumsChart(year) {
    const results = await loadCSV('/static/data/results_raw.csv');
    const teams = await loadCSV('/static/data/teams.csv');

    const podiums = {};
    results.filter(r => r.season === year && ['1', '2', '3'].includes(r.position)).forEach(r => {
      const teamKey = normalize(r.team_name);
      podiums[teamKey] = (podiums[teamKey] || 0) + 1;
    });

    const labels = Object.keys(podiums);
    const values = Object.values(podiums);
    const colors = labels.map(t => teams.find(team => normalize(team.team_name) === t)?.team_color || '#333');

    Plotly.newPlot(podiumsChart, [{
      x: labels,
      y: values,
      type: 'bar',
      marker: { color: colors }
    }], {
      title: 'Podium Finishes by Team',
      xaxis: { title: 'Team' },
      yaxis: { title: 'Podium Count' }
    });
  }

  async function loadLapTimesChart(eventId) {
    const lapTimes = await loadCSV('/static/data/results_raw.csv');
    const drivers = await loadCSV('/static/data/drivers.csv');

    const filtered = lapTimes.filter(l => String(l.event_id) === String(eventId) && l.avg_lap_time);
    const grouped = {};

    filtered.forEach(r => {
      const key = normalize(r.driver_name);
      if (!grouped[key]) grouped[key] = [];
      grouped[key].push(parseFloat(r.avg_lap_time));
    });

    const data = Object.keys(grouped).map(driver => {
      const driverObj = drivers.find(d => normalize(d.driver_name) === driver);
      return {
        x: [driverObj?.abbreviation || driver],
        y: [grouped[driver].reduce((a, b) => a + b, 0) / grouped[driver].length],
        type: 'bar',
        name: driverObj?.abbreviation || driver,
        marker: { color: driverObj?.team_color || '#444' }
      };
    });

    console.log('Lap Times Chart Data:', data);
    Plotly.newPlot(lapTimesChart, data, {
      title: 'Average Lap Times',
      xaxis: { title: 'Driver' },
      yaxis: { title: 'Avg Lap Time (s)' }
    });
  }

  async function loadTireAgeChart(eventId) {
    const data = await loadCSV('/static/data/results_raw.csv');
    const teams = await loadCSV('/static/data/teams.csv');

    const filtered = data.filter(r => String(r.event_id) === String(eventId) && r.compound && r.avg_stint_length);
    const compoundMap = {};

    filtered.forEach(row => {
      const compound = row.compound;
      const team = normalize(row.team_name);
      if (!compoundMap[compound]) compoundMap[compound] = [];
      compoundMap[compound].push({
        x: row.team_name,
        y: parseFloat(row.avg_stint_length),
        color: teams.find(t => normalize(t.team_name) === team)?.team_color || '#666'
      });
    });

    const chartData = Object.keys(compoundMap).map(compound => {
      const values = compoundMap[compound];
      return {
        x: values.map(v => v.x),
        y: values.map(v => v.y),
        type: 'bar',
        name: compound,
        marker: { color: values.map(v => v.color) }
      };
    });

    console.log('Tire Age Chart Data:', chartData);
    Plotly.newPlot(tireAgeChart, chartData, {
      title: 'Average Stint Length by Tire Compound and Team',
      xaxis: { title: 'Team' },
      yaxis: { title: 'Avg Stint Length (laps)' },
      barmode: 'group'
    });
  }

  async function loadDriverStandings(year) {
    const results = await loadCSV('/static/data/results_raw.csv');
    const drivers = await loadCSV('/static/data/drivers.csv');

    const seasonResults = results.filter(r => r.season === year);
    const driverMap = {};

    seasonResults.forEach(r => {
      const driverKey = normalize(r.driver_name);
      if (!driverMap[driverKey]) {
        driverMap[driverKey] = { points: 0, wins: 0, podiums: 0 };
      }
      const d = driverMap[driverKey];
      d.points += parseFloat(r.points || 0);
      if (r.position === '1') d.wins++;
      if (['1', '2', '3'].includes(r.position)) d.podiums++;
    });

    const sorted = Object.entries(driverMap).map(([name, stats]) => {
      const d = drivers.find(dr => normalize(dr.driver_name) === name);
      return {
        driver_name: d?.driver_name || name,
        abbreviation: d?.abbreviation || name,
        team_name: d?.team_name || 'Unknown',
        team_color: d?.team_color || '#444',
        wins: stats.wins,
        podiums: stats.podiums,
        total_points: stats.points
      };
    }).sort((a, b) => b.total_points - a.total_points);

    driverStandingsBody.innerHTML = '';
    sorted.forEach((driver, i) => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td>${i + 1}</td>
        <td style="border-left: 4px solid ${driver.team_color}; padding-left: 5px;">${driver.driver_name}</td>
        <td>${driver.team_name}</td>
        <td>${driver.wins}</td>
        <td>${driver.podiums}</td>
        <td>${driver.total_points.toFixed(1)}</td>
      `;
      driverStandingsBody.appendChild(row);
    });
  }
});
