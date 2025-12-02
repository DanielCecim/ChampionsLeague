# Disclaimer: AI has been used to assist in the creation of this file.
import sys
import multiprocessing as mp
import threading
import time
import random
from players import (
    TEAM_BARCA_PLAYERS, TEAM_REAL_PLAYERS, TEAM_ATLETICO_PLAYERS, TEAM_PSG_PLAYERS
)
from anthems import (ANTHEM_LINES_BARCELONA, ANTHEM_LINES_MADRID, ANTHEM_LINES_ATLETICO, ANTHEM_LINES_PSG)
from fan_class import Fan
from player_class import Player, Role
from shop_class import create_shops_for_match
from data_collector import DataCollector

t0 = time.time()

TICK_SECONDS = 5                 # 5 seconds = 5 minutes
MATCH_TICKS = 18                  # 90 minutes total
NUM_FANS = 100
TEAM_SIZE = 11
PROB_BUY_SOMETHING = [0.9]  # Probability that a fan buy
PROB_QUEUE_VISIT = 0.5 # Chance to visit a shop
PROB_STREAK_MATCH = 0.0000001        # 0.00001% per fan

# Custom logging function with timestamp
def log(msg):
    now = time.time() - t0
    print(f"[{now:6.2f}s] {msg}")

def get_opponent(team): # Given a team, return the opposing team in the current match
    t1, t2 = current_teams
    if t1 is None or t2 is None:
        return None
    return t2 if team is t1 else t1

#Stadium class, essentially multiple event flags.
class Stadium:
    def __init__(self):
        self.gates_open = threading.Event() # Fans can enter
        self.anthem_start = threading.Event() # Anthems start (for both teams to reach position)
        self.team1_anthem = threading.Event() # Team 1 sings
        self.team2_anthem = threading.Event() # Team 2 sings
        self.match_start = threading.Event() # Match starts

# Teams, Players, Ball

class Team:
    def __init__(self, name):
        self.name = name 
        self.players = [] # List of Player objects
        self.arrival_barrier = threading.Barrier(TEAM_SIZE) # All players must arrive before proceeding
        self.field_barrier = threading.Barrier(TEAM_SIZE) # All players must reach field before proceeding

class Ball:
    def __init__(self):
        self.mutex = threading.Lock() # Lock for ball possession.
        self.possession_lock = threading.Lock() # Lock for possession changes.
        self.owner = None # Player who currently has the ball
        self.last_team = None # Last team that had the ball

    def set_owner(self, player):
        with self.possession_lock: # Lock to change possession
            self.owner = player # Set new owner
            self.last_team = player.team.name
            log(f"⚽ Ball now with {player}.")

    def get_owner(self): # Get current owner
        with self.possession_lock:
            return self.owner

stadium = Stadium() # Our main stadium object
ball = Ball() # Our main ball object. Reset for each match.
tick_event = threading.Event()    # flag, every 5 seconds
end_event = threading.Event()     # set when match is over
pause_event = threading.Event()   # to pause the match when there is a streaker or faul
stoppage_lock = threading.Lock()  #There are multiple events that can stop a match, streaks, penalties, faults, etc. Only one event can stop the clock at the time.
foul_lock = threading.Lock()      # Only one faul can be happening at one time
score_lock = threading.Lock() # Lock for score updates
scoreboard = {} # Initial scores. Reset for each match.

# Track current teams for the active match (set by orchestrator)
current_teams = (None, None) 
pause_event.set() # initially set, match hasnt started

# Clock
class MatchClock(threading.Thread): # Match clock thread that ticks every 5 seconds to simulate 5 minutes.
    def __init__(self, tick_event, end_event):
        super().__init__(daemon=True) # This thread will not block program exit. This is important for cleanup.
        self.tick_event = tick_event
        self.end_event = end_event
        self.current_tick = 0 # Current tick count zero at start.

    def run(self): # Main clock loop
        stadium.match_start.wait() # Wait for match to start
        log("⏱️ Match clock starts.")
        while self.current_tick < MATCH_TICKS and not self.end_event.is_set(): # Loop until 90 minutes or match ends.
            pause_event.wait() # Wait if match is paused.
            start = time.time() # Record start time of tick.
            while True: # Wait for TICK_SECONDS, checking for pauses or end event.
                remaining = TICK_SECONDS - (time.time() - start)
                if remaining <= 0: break
                pause_event.wait(timeout=min(0.1, remaining))
                if self.end_event.is_set():
                    break
            if self.end_event.is_set(): break

            self.current_tick += 1
            log(f"⏱️ Minute {self.current_tick*5}/90")
            self.tick_event.set()
            time.sleep(0.03)
            self.tick_event.clear()

        log("⏱️ Match clock ends.")
        self.end_event.set()

# Build Teams
def build_team(name, players_dict):
    team = Team(name) # Create team object
    roles = [Role.GK] + [Role.DEF]*4 + [Role.MID]*4 + [Role.FWD]*2 # Define roles
    player_names = list(players_dict.keys())
    for i in range(min(TEAM_SIZE, len(player_names))): # Create players from the provided dict
        p_name = player_names[i]
        p = Player(
            team, p_name, roles[i], team.arrival_barrier, team.field_barrier, 
            players_dict.get(p_name, {}),
            stadium=None, end_event=None, pause_event=None, tick_event=None,
            ball=None, log=None, anthems=None, scoreboard=None, score_lock=None,
            stoppage_lock=None, foul_lock=None, get_opponent=None, data_collector=None
        )
        team.players.append(p)
    gks = [p for p in team.players if p.role == Role.GK]
    if len(gks) == 0: # Ensure at least one goalkeeper.
        team.players[0].role = Role.GK
    elif len(gks) > 1:
        for p in gks[1:]:
            p.role = Role.DEF
    return team

# Team builders
def create_team_barcelona():
    return build_team("Barcelona", TEAM_BARCA_PLAYERS)

def create_team_real_madrid():
    return build_team("Real Madrid", TEAM_REAL_PLAYERS)

def create_team_atletico():
    return build_team("Atletico Madrid", TEAM_ATLETICO_PLAYERS)

def create_team_psg():
    return build_team("PSG", TEAM_PSG_PLAYERS)


class MatchOrchestrator:  # Threads are started here, acts like main()
    def __init__(self, team1, team2, data_collector=None, stadium_location="Bernabeu"):
        self.team1 = team1
        self.team2 = team2
        self.clock = MatchClock(tick_event, end_event)
        self.data_collector = data_collector
        self.stadium_location = stadium_location

        # Reset shared state for a fresh match with any two teams
        with score_lock:
            scoreboard.clear()
            scoreboard[self.team1.name] = 0
            scoreboard[self.team2.name] = 0

    def start(self):
        log(f"🏟️  STADIUM: {self.stadium_location}")
        log(f"CHAMPIONS LEAGUE MATCH: {self.team1.name} vs {self.team2.name}")
        
        # Create location-specific shops
        food_shops, merch_shops, food_data, merch_data = create_shops_for_match(
            self.stadium_location, 
            self.team1.name, 
            self.team2.name
        )
        
        # Start match tracking
        if self.data_collector:
            match_type = "final" if hasattr(self, 'is_final') else "semi-final"
            self.data_collector.start_match(
                self.team1.name, 
                self.team2.name, 
                match_type,
                self.stadium_location
            )

        # Set current teams for helpers
        global current_teams
        current_teams = (self.team1, self.team2)
        
        # Prepare anthem mapping
        anthem_map = {
            "Barcelona": ANTHEM_LINES_BARCELONA,
            "Real Madrid": ANTHEM_LINES_MADRID,
            "Atletico Madrid": ANTHEM_LINES_ATLETICO,
            "PSG": ANTHEM_LINES_PSG
        }
        
        # Assigning values to players
        for p in self.team1.players:
            p.stadium = stadium
            p.end_event = end_event
            p.pause_event = pause_event
            p.tick_event = tick_event
            p.ball = ball
            p.log = log
            p.anthems = anthem_map
            p.scoreboard = scoreboard
            p.score_lock = score_lock
            p.stoppage_lock = stoppage_lock
            p.foul_lock = foul_lock
            p.get_opponent = get_opponent
            p.data_collector = self.data_collector
            p.is_team1 = True  # Mark as team1
        
        for p in self.team2.players:
            p.stadium = stadium
            p.end_event = end_event
            p.pause_event = pause_event
            p.tick_event = tick_event
            p.ball = ball
            p.log = log
            p.anthems = anthem_map
            p.scoreboard = scoreboard
            p.score_lock = score_lock
            p.stoppage_lock = stoppage_lock
            p.foul_lock = foul_lock
            p.get_opponent = get_opponent
            p.data_collector = self.data_collector
            p.is_team1 = False  # Mark as team2

        # Create fans
        fans = []
        # Filter anthems to only include teams playing in this match
        playing_teams = [self.team1.name, self.team2.name]
        match_anthems = {team: anthem_map[team] for team in playing_teams if team in anthem_map}
        
        # Split fans 50-50 between the two teams
        for i in range(NUM_FANS):
            # First 50 fans support team1, next 50 support team2
            supporting_team = self.team1.name if i < NUM_FANS // 2 else self.team2.name
            
            fan = Fan(
                i, 
                stadium=stadium, 
                end_event=end_event, 
                pause_event=pause_event,
                tick_event=tick_event, 
                ball=ball, 
                log=log, 
                stoppage_lock=stoppage_lock,
                prob_streak_match=PROB_STREAK_MATCH, 
                prob_queue_visit=PROB_QUEUE_VISIT,
                prob_buy_something=PROB_BUY_SOMETHING,
                food_shops=food_shops, 
                merch_shops=merch_shops,
                food_shops_data=food_data, 
                merch_shops_data=merch_data,
                data_collector=self.data_collector,
                anthems=match_anthems,  # Pass only anthems for teams playing
                supporting_team=supporting_team  # Assign which team this fan supports
            )
            fans.append(fan)

        for f in fans: # Start all fans threads
            f.start()

        time.sleep(0.4)
        log("🔓 Stadium gates OPEN. Fans are crowding in.")
        stadium.gates_open.set()

        # Start only the players from the selected teams
        for p in self.team1.players + self.team2.players:
            p.start() # Start player threads

        time.sleep(1.0)
        log("🎤 Anthems ceremony begins.")
        stadium.anthem_start.set()  # Signal both teams to get ready
        
        time.sleep(0.3)
        log(f"🎶 {self.team1.name} sings their anthem...")
        stadium.team1_anthem.set()  # Team 1 sings
        time.sleep(1.5)  # Wait for team 1 to finish
        
        log(f"🎶 {self.team2.name} sings their anthem...")
        stadium.team2_anthem.set()  # Team 2 sings
        time.sleep(1.5)  # Wait for team 2 to finish
        
        kickoff_owner = random.choice(self.team1.players + self.team2.players)
        log("🏟️ Match starts!")
        ball.set_owner(kickoff_owner)
        log(f"⚽ Ball now with {kickoff_owner}.")
        stadium.match_start.set()

        self.clock.start()

        end_event.wait()
        time.sleep(0.3)
        with score_lock:
            s1 = scoreboard.get(self.team1.name, 0)
            s2 = scoreboard.get(self.team2.name, 0)
        log(f"🔚 Final score: {self.team1.name} {s1} - {s2} {self.team2.name}")
        
        # Save match statistics
        if self.data_collector:
            if s1 > s2:
                winner = self.team1.name
            elif s2 > s1:
                winner = self.team2.name
            else:
                winner = "TIE"
            
            self.data_collector.end_match(s1, s2, winner)
            self.data_collector.save_all_stats()
        
        # Return the winning team
        if s1 > s2:
            return self.team1
        elif s2 > s1:
            return self.team2
        else:
            # In case of tie, pick winner randomly
            winner = random.choice([self.team1, self.team2])
            log(f"🎲 Match tied! {winner.name} advances by coin toss.")
            return winner


# Helper to reset global shared state for a fresh sequential match
def reset_shared_state():
    global stadium, tick_event, end_event, pause_event, stoppage_lock, foul_lock, ball
    stadium = Stadium()
    tick_event = threading.Event()
    end_event = threading.Event()
    pause_event = threading.Event()
    pause_event.set()
    stoppage_lock = threading.Lock()
    foul_lock = threading.Lock()
    ball = Ball()

# Run one match in this process
def run_single_match(team1, team2, data_collector=None, stadium_location="Bernabeu"):
    reset_shared_state()
    winner = MatchOrchestrator(team1, team2, data_collector, stadium_location).start()
    return winner

# Allow sequential or concurrent (using processes) execution
if __name__ == "__main__":

    mode = "sequential"
    if len(sys.argv) > 1:
        mode = sys.argv[1].strip().lower()  # "sequential" or "concurrent"

    # Create data collector - clear existing data for fresh tournament
    data_collector = DataCollector(clear_existing=True)

    if mode == "concurrent":
        # Use processes so each match has isolated globals
        p1 = mp.Process(target=run_single_match, args=(create_team_barcelona(), create_team_real_madrid()))
        p2 = mp.Process(target=run_single_match, args=(create_team_atletico(), create_team_psg()))
        p1.start()
        p2.start()
        p1.join()
        p2.join()
    else:
        # Run one after the other in the same process
        log("🏆 === SEMI-FINAL 1 ===")
        winner1 = run_single_match(create_team_barcelona(), create_team_real_madrid(), data_collector, "Camp Nou")
        log(f"🎉 {winner1.name} advances to the FINAL!\n")
        
        time.sleep(1.0)
        
        log("🏆 === SEMI-FINAL 2 ===")
        winner2 = run_single_match(create_team_atletico(), create_team_psg(), data_collector, "Riyadh Air Metropolitano")
        log(f"🎉 {winner2.name} advances to the FINAL!\n")
        
        time.sleep(2.0)
        
        log("🏆🏆🏆 CHAMPIONS LEAGUE FINAL 🏆🏆🏆 ")
        # Rebuild new threads with winning teams
        if winner1.name == "Barcelona":
            final_team1 = create_team_barcelona()
        elif winner1.name == "Real Madrid":
            final_team1 = create_team_real_madrid()
        elif winner1.name == "Atletico Madrid":
            final_team1 = create_team_atletico()
        else:  # PSG
            final_team1 = create_team_psg()
        
        if winner2.name == "Barcelona":
            final_team2 = create_team_barcelona()
        elif winner2.name == "Real Madrid":
            final_team2 = create_team_real_madrid()
        elif winner2.name == "Atletico Madrid":
            final_team2 = create_team_atletico()
        else:  # PSG
            final_team2 = create_team_psg()
        
        champion = run_single_match(final_team1, final_team2, data_collector, "Allianz Arena")
        log(f"\n🏆🏆🏆 {champion.name} are the CHAMPIONS LEAGUE WINNERS! 🏆🏆🏆")
        
        from visualizations import generate_all_visualizations
        generate_all_visualizations(data_collector.db_path)

