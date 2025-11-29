# Champions League Simulation - Data Collection & Visualization

## Overview
This enhanced Champions League simulation now includes comprehensive data collection, SQL database storage, and visualization capabilities.

## New Features

### 1. Data Collection (`data_collector.py`)
- **Thread-safe data tracking** during matches
- **SQLite database** storage for all statistics
- **Automatic data persistence** at match end

### 2. Player Statistics Tracked
- **Performance**: Passes, shots, shots on target, goals, ball possessions
- **Defense**: Steals, fouls committed
- **Discipline**: Yellow cards, red cards (expulsions)
- **Goalkeepers**: Saves
- **Fatigue**: Stat degradation over match time

### 3. Fan Statistics Tracked
- **Financial**: Initial money, final money, total spent
- **Shopping**: Items purchased, shop visits
- **Behavior**: Streaking incidents, rich vs regular fans

### 4. Database Schema

#### Tables:
- `matches`: Match results and metadata
- `player_stats`: Per-match player performance
- `fan_stats`: Per-match fan behavior
- `purchases`: Detailed purchase history

### 5. Visualizations (`visualizations.py`)

Generated bar charts include:
- **Top Goal Scorers** - Players with most goals
- **Top Passers** - Players with most passes
- **Top Ball Winners** - Players with most steals
- **Disciplinary Record** - Yellow/red cards
- **Goalkeeper Saves** - Save statistics
- **Top Fan Spenders** - Fans who spent most
- **Most Popular Items** - Best-selling merchandise
- **Shop Revenue** - Revenue by shop type (food vs merch)
- **Team Statistics** - Comparative team performance
- **Match Results** - Score comparison

## Usage

### Run Simulation with Data Collection
```bash
python3 ChampionsLeagueMatch.py
```

This will:
1. Run 3 matches (2 semi-finals + final)
2. Collect all statistics in real-time
3. Save to `champions_league_data.db`
4. Generate all visualizations in `charts/` directory

### Query Database
```bash
python3 query_database.py
```

Displays comprehensive reports including:
- Match results
- Top scorers with conversion rates
- Team summaries
- Player statistics
- Fan statistics
- Revenue summaries
- Recent purchases

### Regenerate Visualizations
```bash
python3 visualizations.py champions_league_data.db
```

## Requirements

Install required packages:
```bash
pip install matplotlib numpy tabulate
```

## Output Files

- **Database**: `champions_league_data.db` - SQLite database with all match data
- **Charts**: `charts/*.png` - All generated visualizations (10 charts)

## Data Examples

### Player Stats Query
```sql
SELECT player_name, team, goals, passes, steals 
FROM player_stats 
WHERE goals > 0 
ORDER BY goals DESC;
```

### Fan Spending Query
```sql
SELECT fan_name, total_spent, items_purchased 
FROM fan_stats 
ORDER BY total_spent DESC 
LIMIT 10;
```

### Shop Revenue Query
```sql
SELECT shop_type, SUM(price) as revenue 
FROM purchases 
GROUP BY shop_type;
```

## Architecture

### Data Flow
1. **Match Start**: `DataCollector.start_match()` initializes tracking
2. **During Match**: Player/Fan threads call recording methods (thread-safe)
3. **Match End**: `DataCollector.save_all_stats()` persists to database
4. **Post-Match**: `generate_all_visualizations()` creates charts

### Thread Safety
- All data collection methods use locks
- In-memory caches reduce database writes
- Batch save at match end for performance

## Customization

### Add New Statistics
1. Add column to database schema in `data_collector.py`
2. Add tracking method (e.g., `record_new_stat()`)
3. Call from Player/Fan class when event occurs
4. Update visualization to display new data

### Add New Visualizations
1. Create function in `visualizations.py`
2. Query database for required data
3. Generate matplotlib chart
4. Add to `generate_all_visualizations()`

## Notes

- Database file is created automatically on first run
- Charts directory is created if it doesn't exist
- Each match run appends data (history preserved)
- Use `query_database.py` to view cumulative statistics across all matches
