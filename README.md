# Champions League Match Simulator

A multi-threaded Python simulation of Champions League football matches featuring realistic player behaviors, fan interactions, stadium shops, and comprehensive statistics tracking.

## Overview

This project simulates a complete Champions League tournament with 3 matches (2 semi-finals + 1 final) featuring Barcelona, Real Madrid, Atletico Madrid, and PSG. The simulation uses Python threading to model concurrent behaviors of players, fans, and match events in real-time.

**Disclaimer:** AI has been used to assist in the creation of this project.

## Features

### Match Simulation
- **Real-time match clock**: 90 minutes divided into 18 ticks (5 seconds = 5 minutes)
- **Player actions**: Passing, shooting, stealing, fouls, yellow/red cards, penalties
- **Team anthems**: Players sing their team's anthem before kickoff
- **Dynamic gameplay**: Ball possession, goalkeeper saves, shot accuracy
- **Fatigue system**: Player probabilities decrease over time
- **Threading synchronization**: 123 threads per match (100 fans + 22 players + 1 clock)

### Fan Experience
- **Stadium entry**: 100 fans enter through gates
- **Shopping**: Fans visit food and merchandise shops with queue management (max 12 in queue, 2 cashiers)
- **Location-specific shops**: Spanish food at Camp Nou/Bernabeu, German food at Allianz Arena
- **Team merchandise**: Dynamic merch based on playing teams
- **Streaking**: Extremely rare random events (0.00001% chance per fan)
- **Financial tracking**: Each fan has a budget, spending is tracked

### Data Collection & Visualization
- **SQLite database**: Stores all match statistics
- **Comprehensive tracking**:
  - Player stats (goals, passes, shots, steals, cards, saves, ball possession)
  - Fan behavior (purchases, spending, shop visits)
  - Match results (scores, winners, stadium locations)
- **Visualizations**: Automatic generation of 9 charts per match + 9 tournament-wide charts
- **Stadium capacity scaling**: Financial data multiplied by 1000 to simulate 100,000 fans

## Project Structure

```
ChampionsLeague/
├── ChampionsLeagueMatch.py    # Main orchestrator, tournament execution
├── player_class.py            # Player thread class and game logic
├── fan_class.py               # Fan thread class and shopping behavior
├── shop_class.py              # Shop system with queue/cashier management
├── data_collector.py          # SQLite database management
├── visualizations.py          # Chart generation (matplotlib)
├── query_database.py          # Terminal-based statistics viewer
├── players.py                 # Player data and probabilities
├── fans.py                    # Fan names list
├── anthems.py                 # Team anthem lyrics
├── food_shops.py              # Food shop configurations
├── merch_shops.py             # Merchandise shop configurations
├── champions_league_data.db   # SQLite database (auto-generated)
└── charts/                    # Generated visualization images
```

## Requirements

```bash
pip install matplotlib numpy tabulate
```

## Usage

### Run Tournament (Sequential Mode)
```bash
python3 ChampionsLeagueMatch.py
```

This runs 3 matches sequentially:
1. **Semi-Final 1**: Barcelona vs Real Madrid @ Camp Nou
2. **Semi-Final 2**: Atletico Madrid vs PSG @ Bernabeu
3. **Final**: Winners @ Allianz Arena (Munich)

After completion, visualizations are automatically generated in the `charts/` folder.

### Run Concurrent Mode (Experimental)
```bash
python3 ChampionsLeagueMatch.py concurrent
```
Runs both semi-finals simultaneously using multiprocessing.

### View Database Statistics
```bash
python3 query_database.py
```

Displays formatted tables of:
- Match results
- Top goal scorers
- Team summaries
- Player statistics
- Fan spending
- Shop revenue
- Recent purchases

## Key Components

### Threading Architecture

**Synchronization Mechanisms:**
- **Event Flags**: `gates_open`, `anthem_start`, `match_start`, `end_event`, `pause_event`
- **Barriers**: `team_arrival_barrier`, `field_barrier` (ensure all 11 players sync)
- **Locks**: `ball.mutex`, `score_lock`, `stoppage_lock`, `foul_lock`, `print_lock`

**Thread Lifecycle:**
1. Fans start → wait at gates → enter stadium → shop/watch
2. Players start → arrive → locker room → tunnel → anthems → match
3. Clock starts → ticks every 5 seconds → ends after 90 minutes
4. All threads exit when `end_event` is set

**Match-to-Match Reset:**
- `reset_shared_state()` creates fresh synchronization objects
- Old daemon threads exit gracefully
- New 123 threads spawned for each match

### Shop System

**Queue Management:**
- Semaphore(12) limits fans in queue
- Semaphore(2) limits concurrent cashier service
- Separate queues for food vs merchandise
- Stock tracking per item

**Shop Types:**
- **Food**: Location-dependent (Spanish/German cuisine)
- **Merchandise**: Team-dependent (jerseys, scarves, hats, flags, etc.)

### Player Behavior

**Roles & Probabilities:**
- **GK**: Save probability (~60%)
- **DEF**: Steal from forwards, commit fouls
- **MID**: Pass/steal from midfielders
- **FWD**: Shot probability (~50%), shot accuracy (~60%)

**Game Events:**
- Fouls trigger yellow cards → penalties or expulsion on 2nd yellow
- Penalties pause the match
- Goals restart play with opposing team kickoff
- Fatigue reduces all probabilities by 0.01 per tick

## Configuration

**Edit constants in `ChampionsLeagueMatch.py`:**

```python
TICK_SECONDS = 5          # Real seconds per tick
MATCH_TICKS = 18          # Total ticks (90 minutes)
NUM_FANS = 100            # Fans per match
PROB_QUEUE_VISIT = 0.5    # Shop visit probability
PROB_BUY_SOMETHING = [0.9]  # Purchase probability
random.seed(7)            # Remove for varied results
```

**Stadium Capacity Multiplier:**
Located in `visualizations.py`:
```python
STADIUM_CAPACITY_MULTIPLIER = 1000  # 100 fans × 1000 = 100,000
```

## Database Schema

**Tables:**
- `matches`: Match details (teams, scores, winner, type, stadium)
- `player_stats`: Individual player performance per match
- `fan_stats`: Fan spending and behavior per match
- `purchases`: Individual purchase records

## Visualization Outputs

**Per-Match Charts (9):**
1. Match summary card
2. Top goal scorers
3. Most passes
4. Most steals
5. Disciplinary records (yellow cards)
6. Goalkeeper saves
7. Most purchased items
8. Shop revenue by type
9. Team statistics comparison

**Tournament Charts (9):**
Same categories aggregated across all matches.

## Technical Notes

- **Thread Safety**: All shared resources protected by locks
- **Daemon Threads**: All worker threads are daemons (won't block exit)
- **Database Cleanup**: Auto-cleared at tournament start
- **Logging**: Thread-safe timestamped output
- **Error Handling**: Try/except blocks in database operations

## Future Enhancements

- Remove `random.seed(7)` for varied outcomes
- Add halftime break logic
- Implement substitutions
- Add more teams
- Web-based visualization dashboard
- Real-time match viewer

## Authors

Created with assistance from AI.

## License

This project is for educational purposes.
