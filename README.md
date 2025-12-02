# Champions League Match Simulator

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
## Usage

### Run Tournament
```bash
python3 ChampionsLeagueMatch.py
```

This runs 3 matches sequentially:
1. **Semi-Final 1**: Barcelona vs Real Madrid @ Camp Nou
2. **Semi-Final 2**: Atletico Madrid vs PSG @ Bernabeu
3. **Final**: Winners @ Allianz Arena (Munich)

After completion, visualizations are automatically generated in the `charts/` folder.

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

#### Thread Inventory

| Thread Type | Count | Class | Daemon | Purpose |
|-------------|-------|-------|--------|---------|
| **Match Clock** | 1 | `MatchClock` | Yes | Ticks every 5 seconds for 90 minutes |
| **Players** | 22 | `Player` | Yes | 11 per team - handle ball, shoot, pass, foul |
| **Fans** | 100 | `Fan` | Yes | Shop, watch match, rare streaking events |
| **Main Thread** | 1 | - | No | Orchestrates match flow, sets events |
| **Total** | **124** | - | - | **123 daemon + 1 main** |

#### Synchronization Primitives

| Type | Name | Location | Purpose | Critical Region |
|------|------|----------|---------|-----------------|
| **Event** | `stadium.gates_open` | `Stadium` class | Signals fans can enter | N/A (signaling only) |
| **Event** | `stadium.anthem_start` | `Stadium` class | Releases players to sing anthems | N/A (signaling only) |
| **Event** | `stadium.match_start` | `Stadium` class | Starts clock and gameplay | N/A (signaling only) |
| **Event** | `end_event` | Global | Signals match is over | N/A (signaling only) |
| **Event** | `pause_event` | Global | Pauses match for penalties/streakers | N/A (signaling only) |
| **Event** | `tick_event` | Global | Signals 5-second tick elapsed | N/A (signaling only) |
| **Lock** | `print_lock` | Global | Protects console output | `log()` function |
| **Lock** | `score_lock` | Global | Protects scoreboard updates | Reading/writing `scoreboard` dict |
| **Lock** | `ball.mutex` | `Ball` class | Protects ball steal attempts | Ball ownership changes during steals |
| **Lock** | `ball.possession_lock` | `Ball` class | Protects ball owner changes | `set_owner()` and `get_owner()` |
| **Lock** | `stoppage_lock` | Global | Ensures one stoppage event at a time | Penalty kicks, streaker pauses |
| **Lock** | `foul_lock` | Global | Ensures one foul at a time | Foul processing and penalties |
| **Lock** | `shop.stock_lock` | `Shop` class | Protects shop inventory | Purchasing items, checking stock |
| **Lock** | `data_collector.lock` | `DataCollector` | Protects database writes | All `record_*()` and `update_*()` methods |
| **Semaphore** | `shop.queue_slots` | `Shop` class | Limits queue to 12 fans | `enter_queue()` / `leave_queue()` |
| **Semaphore** | `shop.cashiers` | `Shop` class | Limits service to 2 fans | `buy()` method (checkout process) |
| **Barrier** | `team.arrival_barrier` | `Team` class | Waits for all 11 players to arrive | Stadium arrival phase |
| **Barrier** | `team.field_barrier` | `Team` class | Waits for all 11 players on field | Pre-anthem synchronization |

#### Critical Regions Details

| Critical Region | Protected Resource | Lock(s) Used | Accessing Threads | Contention Level |
|----------------|-------------------|--------------|-------------------|------------------|
| **Console Output** | `stdout` | `print_lock` | All 124 threads | High |
| **Scoreboard** | `scoreboard` dict | `score_lock` | 22 players | Low (only on goals) |
| **Ball Ownership** | `ball.owner` | `ball.possession_lock` | 22 players | High (constant) |
| **Ball Stealing** | Ball possession change | `ball.mutex` | 22 players | Medium |
| **Shop Stock** | `shop.stock` dict | `shop.stock_lock` | 100 fans | High |
| **Shop Queue** | Queue capacity | `shop.queue_slots` (Semaphore) | 100 fans | High |
| **Shop Cashier** | Cashier availability | `shop.cashiers` (Semaphore) | 100 fans | Medium |
| **Database Writes** | SQLite database | `data_collector.lock` | 122 threads (not clock) | High |
| **Match Pause** | `pause_event` state | `stoppage_lock` | 22 players + 100 fans | Very Low |
| **Foul Processing** | Penalty execution | `foul_lock` | 22 players | Very Low |

**Thread Lifecycle:**
1. Fans start → wait at gates → enter stadium → shop/watch
2. Players start → arrive → locker room → tunnel → anthems → match
3. Clock starts → ticks every 5 seconds → ends after 90 minutes
4. All threads exit when `end_event` is set

**Match-to-Match Reset:**
- `reset_shared_state()` creates fresh synchronization objects
- Old daemon threads exit gracefully
- New 123 threads spawned for each match

#### Component Explanations

**Threads:**
- **Match Clock Thread**: Counts down 90 minutes by setting a tick event every 5 seconds until the match ends.
- **Player Threads (22)**: Each player independently attempts to pass, shoot, steal, or commit fouls based on their role and probabilities.
- **Fan Threads (100)**: Each fan independently decides whether to visit shops, purchase items, or (rarely) streak across the field.
- **Main Thread**: Orchestrates the match by creating other threads, setting event flags at the right moments, and waiting for match completion.

**Events:**
- **stadium.gates_open**: Signals to all 100 fan threads that they can now enter the stadium.
- **stadium.anthem_start**: Releases all 22 player threads to begin singing their team anthems simultaneously.
- **stadium.match_start**: Signals all threads that the match has officially begun and the clock should start ticking.
- **end_event**: Tells all 123 threads to exit their loops and terminate because the 90-minute match is over.
- **pause_event**: When cleared, freezes all gameplay threads (players/fans) during penalties, streaking, or other stoppages.
- **tick_event**: Signals all threads that 5 seconds (representing 5 game minutes) have elapsed, triggering fatigue updates and fan behavior checks.

**Locks:**
- **print_lock**: Prevents log messages from multiple threads from interleaving and creating garbled console output.
- **score_lock**: Ensures only one thread can read or update the scoreboard at a time, preventing race conditions on goal counts.
- **ball.mutex**: Prevents multiple players from simultaneously attempting to steal the ball, ensuring atomic steal operations.
- **ball.possession_lock**: Guarantees that changing or checking who has the ball happens atomically without interference.
- **stoppage_lock**: Ensures only one stoppage event (penalty or streaker) can pause the match at any given time.
- **foul_lock**: Prevents multiple fouls from being processed simultaneously, ensuring penalties are handled one at a time.
- **shop.stock_lock**: Protects shop inventory from simultaneous purchases that could cause negative stock or race conditions.
- **data_collector.lock**: Ensures database write operations from different threads don't corrupt data or cause SQLite errors.

**Semaphores:**
- **shop.queue_slots (12)**: Limits the number of fans waiting in a shop queue to 12, blocking additional fans until space opens.
- **shop.cashiers (2)**: Restricts concurrent checkout operations to 2 fans per shop, simulating limited cashier availability.

**Barriers:**
- **team.arrival_barrier**: Blocks each player thread until all 11 teammates have arrived at the stadium together.
- **team.field_barrier**: Holds all 11 players at the tunnel entrance until the entire team is ready to enter the field.

**Critical Regions:**
- **Console Output (print_lock)**: The `log()` function formats and prints timestamps, requiring exclusive access to prevent message corruption from 124 threads.
- **Scoreboard (score_lock)**: Reading and incrementing team scores during goals must be atomic to prevent lost updates or incorrect totals.
- **Ball Ownership (ball.possession_lock)**: The `set_owner()` and `get_owner()` methods must execute atomically to prevent inconsistent ball state.
- **Ball Stealing (ball.mutex)**: Checking current owner and transferring possession during steals must happen as one uninterruptible operation.
- **Shop Stock (shop.stock_lock)**: Checking inventory, charging the fan, and decrementing stock must occur atomically to prevent overselling.
- **Shop Queue (queue_slots semaphore)**: Acquiring a queue slot, shopping, and releasing the slot must be properly sequenced to maintain the 12-fan limit.
- **Shop Cashier (cashiers semaphore)**: The entire checkout process (check stock, check money, deduct both) must hold a cashier slot for fairness.
- **Database Writes (data_collector.lock)**: All INSERT and UPDATE operations require exclusive database access to prevent SQLite concurrency errors.
- **Match Pause (stoppage_lock)**: Acquiring this lock, clearing pause_event, handling the stoppage, then setting pause_event again must be atomic.
- **Foul Processing (foul_lock)**: Checking if a foul occurred, assigning yellow card, and potentially executing a penalty must not be interrupted by another foul.

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

