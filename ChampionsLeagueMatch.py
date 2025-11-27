import threading
import time
import random
from enum import Enum
from players import (
    PROB_FOUL_DEF, PROB_FOUL_MID, PROB_STEAL_DEF_BY_FWD,
    PROB_STEAL_MID_BY_MID, PROB_STEAL_FWD_BY_DEF_OR_GK,
    PROB_SHOT_FWD, PROB_SAVE_BY_GK, PROB_SHOT_ON_TARGET,
    TEAM_BARCA_PLAYERS, TEAM_REAL_PLAYERS, TEAM_ATLETICO_PLAYERS, TEAM_PSG_PLAYERS
)
from food_shops import (
    PROB_BUY_SOMETHING, SHOP_QUEUE_MAX, CASHIERS, FOOD_SHOPS
)
from merch_shops import MERCH_SHOPS
from anthems import (ANTHEM_LINES_BARCELONA, ANTHEM_LINES_MADRID, ANTHEM_LINES_ATLETICO, ANTHEM_LINES_PSG)
from fans import FAN_NAMES
import sys
import multiprocessing as mp

# Lock that allows only one thread to print at a time
print_lock = threading.Lock() 
t0 = time.time()

# Custom logging function with timestamp
def log(msg):
    with print_lock:
        now = time.time() - t0
        print(f"[{now:6.2f}s] {msg}")

# Roles as Enum. Mapping position to strings
class Role(Enum):
    GK = "GK"
    DEF = "DEF"
    MID = "MID"
    FWD = "FWD"

TICK_SECONDS = 5                  # 5 seconds = 5 minutes
MATCH_TICKS = 18                  # 90 minutes total
NUM_FANS = 50
TEAM_SIZE = 11

# Fan probabilities
PROB_QUEUE_VISIT = 0.5 # Chance to visit a shop
PROB_STREAK_MATCH = 0.0000001        # 0.00001% per fan

random.seed(7)

#Stadium class, essentially multiple event flags.
class Stadium:
    def __init__(self):
        self.gates_open = threading.Event() # Fans can enter
        self.anthem_start = threading.Event() # Anthems start
        self.match_start = threading.Event() # Match starts

stadium = Stadium() # Our main stadium object

tick_event = threading.Event()    # flag, every 5 seconds
end_event = threading.Event()     # set when match is over
pause_event = threading.Event()   # to pause the match when there is a streaker or halftime
pause_event.set() # initially set, match hasnt started

stoppage_lock = threading.Lock()  #There are multiple events that can stop a match, streaks, penalties, faults, etc. Only one event can stop the clock at the time.
foul_lock = threading.Lock()      # Only one faul can be happening at one time

# Shop class

class Shop:
    def __init__(self, stock, queue_max, cashiers):
        self.stock = dict(stock)
        self.stock_lock = threading.Lock() # Lock for stock access
        self.queue_slots = threading.Semaphore(queue_max)  # Max fans in queue. 
        self.cashiers = threading.Semaphore(cashiers) # Number of cashiers

    def enter_queue(self, fan_name): # Fan tries to enter queue
        log(f"🧍 {fan_name} attempts to enter food queue.")
        self.queue_slots.acquire()
        log(f"🧍 {fan_name} entered the food queue.")

    def leave_queue(self, fan_name): # Fan leaves queue
        self.queue_slots.release()
        log(f"🏃 {fan_name} leaves the food queue.")

    def buy(self, fan, item, price): # Fan tries to buy an item
        with self.cashiers: # Wait for a cashier availability
            with self.stock_lock: # Lock stock access
                if self.stock.get(item, 0) <= 0: # Check stock
                    log(f"📦{fan.name} tried to buy {item}, but OUT OF STOCK.")
                    return False
                if fan.money < price: # Check if fan can afford
                    log(f"💶{fan.name} cannot afford {item} (${price}).")
                    return False
                self.stock[item] -= 1 # Deduct stock
                fan.money -= price # Deduct money
                log(f"🧾 {fan.name} bought {item} for ${price}. Remaining ${fan.money}.")
                return True

# Create food and merch shops using list comprehension
food_shops = [Shop(shop["stock"], SHOP_QUEUE_MAX, CASHIERS) for shop in FOOD_SHOPS]
merch_shops = [Shop(shop["stock"], SHOP_QUEUE_MAX, CASHIERS) for shop in MERCH_SHOPS]

# Teams, Players, Ball

class Team:
    def __init__(self, name):
        self.name = name # "Barcelona" or "Real Madrid"
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

ball = Ball() # Our main ball object

score_lock = threading.Lock() # Lock for score updates
scoreboard = {"Barcelona": 0, "Real Madrid": 0} # Initial scores

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

# Fans

class Fan(threading.Thread):
    def __init__(self, idx):
        super().__init__(daemon=True) # Daemon thread that won't block program exit.
        self.name = FAN_NAMES[idx]
        #People have a random chance of having more money than others.
        if random.random() < 0.2:
            self.money = random.randint(300, 500) # Wealthy fans bring more money.
            self.is_rich = True
        else:
            self.money = random.randint(100, 250) # Regular fans have less money.
            self.is_rich = False

    def streak_during_match_loop(self): # Fan may streak during match. Although very rare. Probability defined globally.
        stadium.match_start.wait()
        last_owner = None
        while not end_event.is_set():
            self_tick_seen = tick_event.wait(timeout=0.5)
            if not self_tick_seen:
                continue
            if random.random() < PROB_STREAK_MATCH:
                if stoppage_lock.acquire(blocking=False):
                    try:
                        if not pause_event.is_set():
                            continue
                        pause_event.clear()
                        last_owner = ball.get_owner()
                        log(f"🫣 {self.name} streaks onto the field! Players stop!")
                        time.sleep(1.2)
                        if last_owner:
                            ball.set_owner(last_owner)
                            log(f"⚽ Ball now with {last_owner}.")
                        log(f"🛡️ Security removed {self.name}. Play resumes.")
                        pause_event.set()
                    finally:
                        stoppage_lock.release()

    def run(self): # Main fan loop. From entering stadium to shopping to streaking.
            log(f"🚶 {self.name} heading to stadium.")
            stadium.gates_open.wait()
            log(f"🚪 {self.name} enters the stadium.")

            time.sleep(random.uniform(0.1, 0.6))
            if random.random() < PROB_QUEUE_VISIT:
                # random shop is picked from the union of food and merch shops
                all_shops = food_shops + merch_shops
                shop_obj = random.choice(all_shops)

                shop_obj.enter_queue(self.name)
                time.sleep(random.uniform(0.1, 0.5))
                num_purchases = random.randint(2, 4) if self.is_rich else 1

                # helper to find price from globals
                def lookup_price(item):
                    for shop_info in FOOD_SHOPS + MERCH_SHOPS:
                        prices = shop_info.get("prices", {})
                        if item in prices:
                            return prices[item]
                    return 0

                for _ in range(num_purchases):
                    if random.random() < random.choice(PROB_BUY_SOMETHING) and self.money > 0: # Can only buy if they have money
                        items = list(shop_obj.stock.keys())
                        if not items: # no items to buy
                            break

                        if self.is_rich:
                            # choosing items based on price weights for rich fans
                            weights = []
                            for i in items:
                                p = lookup_price(i) or 1
                                weights.append(p)
                            choice = random.choices(items, weights=weights, k=1)[0]
                        else:
                            choice = random.choice(items)

                        price = lookup_price(choice)
                        if shop_obj.buy(self, choice, price):
                            time.sleep(random.uniform(0.1, 0.3))
                        else:
                            break
                shop_obj.leave_queue(self.name) # Fan leaves the queue

            time.sleep(random.uniform(0.1, 0.5))

            self.streak_during_match_loop() # Start streaking possibility during match

# Player helpers

def role_str(role: Role): # Convert role enum to string
    return role.value

def allowed_pass_targets(player): # Determine allowed pass targets based on player role
    if player.role == Role.FWD:
        return [Role.FWD, Role.MID]
    if player.role == Role.MID:
        return [Role.FWD, Role.MID, Role.DEF]
    if player.role == Role.DEF:
        return [Role.MID, Role.DEF, Role.GK]
    if player.role == Role.GK:
        return [Role.DEF, Role.MID, Role.FWD]
    return []

def can_steal(attacker, owner): # Determine if attacker can steal from owner and the probability
    if owner is None or attacker.team.name == owner.team.name:
        return False, 0.0
    if owner.role == Role.FWD and attacker.role in (Role.DEF, Role.GK):
        return True, attacker.data.get("probs", {}).get(PROB_STEAL_FWD_BY_DEF_OR_GK,0.0)
    elif owner.role == Role.MID and attacker.role == Role.MID:
        return True, attacker.data.get("probs",{}).get(PROB_STEAL_MID_BY_MID,0.0)
    elif owner.role == Role.DEF and attacker.role == Role.FWD:
        return True, attacker.data.get("probs", {}).get(PROB_STEAL_DEF_BY_FWD, 0.0)
    return False, 0.0

def choose_midfielder(team): # Choose a midfielder from the team for kickoff
    mids = [p for p in team.players if p.role == Role.MID]
    if mids:
        return random.choice(mids)
    non_gk = [p for p in team.players if p.role != Role.GK]
    return random.choice(non_gk) if non_gk else team.players[0]

def restart_after_goal(scoring_team): # Restart match after a goal
    other = teamA if scoring_team.name == "B" else teamB
    mid = choose_midfielder(other)
    log(f"🔁 Kickoff: {other.name} restarts via {mid}.")
    ball.set_owner(mid)
    log(f"⚽ Ball now with {mid}.")

# Player Thread

class Player(threading.Thread): # Player thread representing a soccer player
    def __init__(self, team, name, role, team_arrival_barrier, field_barrier, data=None):
        super().__init__(daemon=True) # Daemon thread that won't block program exit.
        self.team = team # Team object
        self.pname = name # Player name
        self.role = role
        self.team_arrival_barrier = team_arrival_barrier
        self.field_barrier = field_barrier
        self.data = data or {}

        pos = self.data.get("pos", None)
        if pos: # Override role if position provided
              pos_upper = pos.upper()
              if pos_upper == "GK":
                  self.role = Role.GK
              elif pos_upper == "DEF":
                  self.role = Role.DEF
              elif pos_upper == "MID":
                  self.role = Role.MID
              elif pos_upper in ("FWD", "ST", "FW"):
                  self.role = Role.FWD
              else:
                  self.role = None
        else:
              self.role = None
          # probabilities or special params per-player
        self.probs = self.data.get("probs", {})

    def __str__(self): # String representation of player
        return f"{self.team.name}-{self.pname}({role_str(self.role)})"

    def pass_ball(self): # Player attempts to pass the ball
        roles = allowed_pass_targets(self) # Get allowed pass targets
        candidates = [p for p in self.team.players if p != self and p.role in roles]
        if not candidates:
            return None
        target = random.choice(candidates) # Randomly choose a target
        log(f"➡️  {self} passes to {target}.")
        ball.set_owner(target)
        return target

    def consider_shot(self): # Player considers taking a shot
        if self.role != Role.FWD: # Only forwards take shots
            return False
        modified_shot_prob = self.probs[PROB_SHOT_FWD] # Get shot probability
        if random.random() < modified_shot_prob: # Attempt shot
            modified_on_target = self.probs[PROB_SHOT_ON_TARGET]
            on_target = random.random() < modified_on_target # Determine if shot is on target
            other_team = teamA if self.team.name == "B" else teamB # Get opposing team
            gk = [p for p in other_team.players if p.role == Role.GK][0] # Get opposing goalkeeper
            modified_save_prob = gk.probs[PROB_SAVE_BY_GK]
            if on_target: # Shot is on target
                if random.random() < modified_save_prob:
                    log(f"🧤 Shot by {self} ON TARGET! Saved by {gk}!")
                    ball.set_owner(gk)
                    log(f"⚽ Ball now with {gk}.")
                else: # Goal scored
                    with score_lock:
                        scoreboard[self.team.name] += 1
                    log(f"🥅 GOAL! {self} scores!  Score: {scoreboard['Barcelona']} - {scoreboard['Real Madrid']}")
                    restart_after_goal(self.team)
            else: # Shot is off target
                log(f"🎯 Shot by {self} is OFF target. Goal kick to {gk}.")
                ball.set_owner(gk)
            return True
        return False

    def attempt_foul_on_forward_owner(self): # Attempt to foul the forward who has the ball
        if self.role not in (Role.DEF, Role.MID):
            return
        owner = ball.get_owner()
        if owner is None or owner.team.name == self.team.name or owner.role != Role.FWD:
            return
        if not foul_lock.acquire(blocking=False):
            return
        committed = False
        try:
            owner_now = ball.get_owner()
            if owner_now != owner or not pause_event.is_set():
                return
            base_p = self.probs.get(PROB_FOUL_DEF, 0.0) if self.role == Role.DEF else self.probs.get(PROB_FOUL_MID, 0.0)  # High skill lowers foul chance
            if random.random() < base_p:
                committed = True
                log(f"🟨 {self} fouls {owner}! PENALTY to Team {owner.team.name}!")
                self.handle_penalty(fouled_forward=owner)
        finally:
            if not committed:
                foul_lock.release()

    def handle_penalty(self, fouled_forward):
        stoppage_lock.acquire() # Ensure only one stoppage at a time
        try:
            pause_event.clear() #Event is paused when the threading event is not set.
            log("⏸️  Play paused for penalty setup.")
            time.sleep(0.8)
            shooting_team = fouled_forward.team
            other_team = teamA if shooting_team.name == "B" else teamB
            gk = [p for p in other_team.players if p.role == Role.GK][0]
            modified_on_target = self.probs[PROB_SHOT_ON_TARGET]
            on_target = random.random() < min(max(modified_on_target, 0.0), 1.0)
            modified_save_prob = self.probs[PROB_SAVE_BY_GK]
            if on_target and random.random() >= modified_save_prob:
                with score_lock:
                    scoreboard[shooting_team.name] += 1
                log(f"🥅 PENALTY GOAL by {fouled_forward}! Score: {scoreboard['Barcelona']} - {scoreboard['Real Madrid']}")
                restart_after_goal(shooting_team)
            else:
                if on_target:
                    log(f"🧤 Penalty by {fouled_forward} SAVED by {gk}!")
                else:
                    log(f"🎯 Penalty by {fouled_forward} OFF target. {gk} restarts.")
                ball.set_owner(gk)
                log(f"⚽ Ball now with {gk}.")
            time.sleep(0.4)
            log("▶️  Play resumes after penalty.")
            pause_event.set()
        finally:
            stoppage_lock.release()
            foul_lock.release()

    def attempt_steal_window(self):
        owner = ball.get_owner()
        allowed, p = can_steal(self, owner)
        if not allowed or not pause_event.is_set():
            return
        if random.random() < float(p or 0.0):
            got = ball.mutex.acquire(timeout=0.01)
            if got:
                try:
                    if ball.get_owner() == owner and pause_event.is_set():
                        log(f"🧨 STEAL! {self} dispossesses {owner}.")
                        ball.set_owner(self)
                finally:
                    ball.mutex.release()

    def ball_handler_tick(self): # Handle ball possession on tick
        if not pause_event.is_set():
            return
        got = ball.mutex.acquire(timeout=0.05)
        if not got:
            return
        try:
            if ball.get_owner() != self or not pause_event.is_set():
                return
            if not self.consider_shot():
                self.pass_ball()
        finally:
            ball.mutex.release()
            

    def run(self): # Main player loop
        log(f"🚌 {self} arriving at stadium.")
        self.team_arrival_barrier.wait() # Wait for all team members to arrive
        log(f"🧳 {self} heads to locker room.")
        time.sleep(random.uniform(0.1, 0.4))

        log(f"🚶 {self} walking to tunnel.")
        self.field_barrier.wait()

        stadium.anthem_start.wait()
        if self.team.name == "Barcelona":
          for line in ANTHEM_LINES_BARCELONA:
              log(f"🎶 {self} sings: {line}")
              time.sleep(0.03)
        else:
          for line in ANTHEM_LINES_MADRID:
            log(f"🎶 {self} sings: {line}")
            time.sleep(0.03)

        stadium.match_start.wait()

        while not end_event.is_set():
            pause_event.wait()
            tick_event.wait(timeout=0.2)
            if end_event.is_set():
                break
            if ball.get_owner() == self:
                self.ball_handler_tick() # 
            else:
                self.attempt_foul_on_forward_owner()
                self.attempt_steal_window()

        log(f"🏁 {self} done.")

# Build Teams

def build_team(name, players_dict):
    team = Team(name) # Create team object
    roles = [Role.GK] + [Role.DEF]*4 + [Role.MID]*4 + [Role.FWD]*2 # Define roles
    player_names = list(players_dict.keys())
    for i in range(min(TEAM_SIZE, len(player_names))): # Create players from the provided dict
        p_name = player_names[i]
        p = Player(team, p_name, roles[i], team.arrival_barrier, team.field_barrier, players_dict.get(p_name, {}))
        team.players.append(p)
    gks = [p for p in team.players if p.role == Role.GK]
    if len(gks) == 0: # Ensure at least one goalkeeper.
        team.players[0].role = Role.GK
    elif len(gks) > 1:
        for p in gks[1:]:
            p.role = Role.DEF
    return team

teamA = build_team("Barcelona", TEAM_BARCA_PLAYERS) # Build Barcelona team from first 11 players
teamB = build_team("Real Madrid", TEAM_REAL_PLAYERS) # Build Real Madrid team from next 11 players
teamC = build_team("Atletico Madrid", TEAM_ATLETICO_PLAYERS) # Build Atletico Madrid team
teamD = build_team("PSG", TEAM_PSG_PLAYERS) # Build PSG team


class MatchOrchestrator:  # Threads are started here, acts like main()
    def __init__(self, team1, team2):
        self.team1 = team1
        self.team2 = team2
        self.clock = MatchClock(tick_event, end_event)

        # Reset shared state for a fresh match with any two teams
        with score_lock:
            scoreboard.clear()
            scoreboard[self.team1.name] = 0
            scoreboard[self.team2.name] = 0

    def start(self):
        log(f"CHAMPIONS LEAGUE MATCH: {self.team1.name} vs {self.team2.name}")

        fans = [Fan(i) for i in range(NUM_FANS)]
        for f in fans:
            f.start()

        time.sleep(0.4)
        log("🔓 Stadium gates OPEN. Fans are crowding in.")
        stadium.gates_open.set()

        # Start only the players from the selected teams
        for p in self.team1.players + self.team2.players:
            p.start()

        time.sleep(1.0)
        log("🎤 Anthem starts.")
        stadium.anthem_start.set()

        time.sleep(0.8)
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
def run_single_match(team1, team2):
    reset_shared_state()
    MatchOrchestrator(team1, team2).start()

# Allow sequential or concurrent (using processes) execution
if __name__ == "__main__":

    mode = "sequential"
    if len(sys.argv) > 1:
        mode = sys.argv[1].strip().lower()  # "sequential" or "concurrent"

    if mode == "concurrent":
        # Use processes so each match has isolated globals
        p1 = mp.Process(target=run_single_match, args=(teamA, teamB))
        p2 = mp.Process(target=run_single_match, args=(teamC, teamD))
        p1.start()
        p2.start()
        p1.join()
        p2.join()
    else:
        # Run one after the other in the same process
        run_single_match(teamA, teamB)
        run_single_match(teamC, teamD)