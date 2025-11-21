import threading
import time
import random
from enum import Enum

print_lock = threading.Lock() 
t0 = time.time()

def log(msg):
    with print_lock:
        now = time.time() - t0
        print(f"[{now:6.2f}s] {msg}")

class Role(Enum):
    GK = "GK"
    DEF = "DEF"
    MID = "MID"
    FWD = "FWD"

TICK_SECONDS = 5                  # 5 seconds = 5 minutes
MATCH_TICKS = 18                  # 90 minutes total
NUM_FANS = 50
TEAM_SIZE = 11

# Probabilities of events
PROB_FOUL_DEF = 0.10              # Faul from Defender to Forward (either team)
PROB_FOUL_MID = 0.06              # MID fouls (only when FWD has ball)
PROB_STEAL_FWD_BY_DEF_OR_GK = 0.20 #Probability of a successful steal by defender or goalkeeper
PROB_STEAL_MID_BY_MID = 0.15   #Probability of a successful steal by midfielder
PROB_STEAL_DEF_BY_FWD = 0.20 #Probabilirt of a successful steal by forward.
PROB_SHOT_FWD = 0.25              # FWD with ball chooses to shoot or pass
PROB_SAVE_BY_GK = 0.55            # GK save chance if shot on target
PROB_SHOT_ON_TARGET = 0.40
PROB_QUEUE_VISIT = 0.75           # fan decides to enter a shop
PROB_BUY_SOMETHING = 0.85  #fan decides to actually buy something

# Streakers
PROB_STREAK_MATCH = 0.0000001        # 0.00001% per fan 

# Shop config
SHOP_STOCK = {"pies": 60, "sodas": 90, "scarves": 30}
SHOP_PRICES = {"pies": 8, "sodas": 5, "scarves": 15}
SHOP_QUEUE_MAX = 12
CASHIERS = 2
# Define stock and prices for food and merch shops
FOOD_SHOPS = [
  {"stock": {"hotdogs": 50, "burgers": 40, "fries": 100}, "prices": {"hotdogs": 6, "burgers": 8, "fries": 4}},
  {"stock": {"pizza": 30, "sodas": 80, "water": 100}, "prices": {"pizza": 10, "sodas": 5, "water": 2}},
  {"stock": {"nachos": 40, "popcorn": 60, "sodas": 70}, "prices": {"nachos": 7, "popcorn": 5, "sodas": 4}},
  {"stock": {"sandwiches": 50, "coffee": 40, "tea": 30}, "prices": {"sandwiches": 6, "coffee": 3, "tea": 2}},
  {"stock": {"churros": 60, "chocolate": 50, "water": 90}, "prices": {"churros": 5, "chocolate": 4, "water": 2}},
]

MERCH_SHOPS = [
  {"stock": {"Barca scarves": 20, "Barca jerseys": 15}, "prices": {"Barca scarves": 15, "Barca jerseys": 80}},
  {"stock": {"Barca hats": 25, "Barca flags": 10}, "prices": {"Barca hats": 10, "Barca flags": 12}},
  {"stock": {"Real scarves": 30, "Real jerseys": 20}, "prices": {"Real scarves": 15, "Real jerseys": 85}},
  {"stock": {"Real hats": 40, "Real flags": 15}, "prices": {"Real hats": 12, "Real flags": 10}},
  {"stock": {"Real mugs": 25, "Real keychains": 50}, "prices": {"Real mugs": 8, "Real keychains": 5}},
]

random.seed(7)

# Lists of names (Barcelona and Real)
PLAYER_NAMES = [
    # Barcelona (Inverted order)
    "Marc-André ter Stegen",
    "Jules Koundé", "Pau Cubarsí", "Ronald Araújo", "Alejandro Balde",
    "Frenkie de Jong", "Gavi", "Pedri",
    "Raphinha", "Robert Lewandowski", "Lamine Yamal",
    # Real Madrid (Inverted order) 
    "Thibaut Courtois",
    "Trent Alexander-Arnold", "Dani Carvajal", "Antonio Rüdiger", "Éder Militão",
    "Aurélien Tchouaméni", "Federico Valverde", "Jude Bellingham",
    "Rodrygo", "Vinícius Júnior", "Kylian Mbappé"
]

# ---------------------------
# Anthem
# ---------------------------

ANTHEM_LINES_BARCELONA = [
    "♪ Tot el camp és un clam,",
    "♪ Som la gent blaugrana,",
    "♪ Tant se val d’on venim,",
    "♪ Si del sud o del nord,",
    "♪ Ara estem d’acord, estem d’acord,",
    "♪ Una bandera ens agermana."]

ANTHEM_LINES_MADRID = [
    "♪ Historia que tú hiciste,",
    "♪ Historia por hacer,",
    "♪ Porque nadie resiste,",
    "♪ Tus ganas de vencer.",]

FAN_NAMES = [
    "Sergio Álvarez", "Alejandro Ruiz", "Jordi Navarro", "Tomás Ortega", "Carlos Vega",
    "Marcos León", "Raúl Molina", "Diego Herrera", "Iván Castillo", "Luis Romero",
    "Rubén Torres", "Javier Delgado", "Hugo Ramos", "Óscar Peña", "Pablo Lozano",
    "Mario Iglesias", "Adrián Flores", "Miguel Duarte", "Andrés Cabrera", "David Serrano",
    "Álvaro Morales", "Nicolás Herrera", "Gabriel Domínguez", "Pedro Vargas", "Lucas Fuentes",
    "Martín Gutiérrez", "Daniel Bravo", "Manuel Calderón", "Francisco Pardo", "Cristian Rivas",
    "Eduardo Campos", "Samuel Espinoza", "Antonio Méndez", "Enrique Pastor", "Joaquín Luna",
    "Fernando Sanz", "Ricardo Cortés", "Julián Suárez", "Ramiro Ávila", "Héctor Gil",
    "Víctor Salas", "Emilio Benítez", "Rodrigo Arias", "Esteban Cruz", "Adriano Nieto",
    "Mateo Vargas", "Rafael Castillo", "Santiago Blanco", "Álex Navarro", "Ignacio Muñoz"
]

#Stadium class, essentially multiple event flags.
class Stadium:
    def __init__(self):
        self.gates_open = threading.Event()
        self.anthem_start = threading.Event()
        self.match_start = threading.Event()

stadium = Stadium()

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
        self.stock_lock = threading.Lock()
        self.queue_slots = threading.Semaphore(queue_max) #Initialized to 12
        self.cashiers = threading.Semaphore(cashiers)

    def enter_queue(self, fan_name):
        log(f"🧍 {fan_name} attempts to enter food queue.")
        self.queue_slots.acquire()
        log(f"🧍 {fan_name} entered the food queue.")

    def leave_queue(self, fan_name):
        self.queue_slots.release()
        log(f"🏃 {fan_name} leaves the food queue.")

    def buy(self, fan, item, price):
        with self.cashiers:
            with self.stock_lock:
                if self.stock.get(item, 0) <= 0:
                    log(f"💥 {fan.name} tried to buy {item}, but OUT OF STOCK.")
                    return False
                if fan.money < price:
                    log(f"💸 {fan.name} cannot afford {item} (${price}).")
                    return False
                self.stock[item] -= 1
                fan.money -= price
                log(f"🧾 {fan.name} bought {item} for ${price}. Remaining ${fan.money}.")
                return True

# Create food and merch shops
food_shops = [Shop(shop["stock"], SHOP_QUEUE_MAX, CASHIERS) for shop in FOOD_SHOPS]
merch_shops = [Shop(shop["stock"], SHOP_QUEUE_MAX, CASHIERS) for shop in MERCH_SHOPS]

# Teams, Players, Ball

class Team:
    def __init__(self, name):
        self.name = name
        self.players = []
        self.arrival_barrier = threading.Barrier(TEAM_SIZE)
        self.field_barrier = threading.Barrier(TEAM_SIZE)

class Ball:
    def __init__(self):
        self.mutex = threading.Lock()
        self.possession_lock = threading.Lock()
        self.owner = None
        self.last_team = None

    def set_owner(self, player):
        with self.possession_lock:
            self.owner = player
            self.last_team = player.team.name

    def get_owner(self):
        with self.possession_lock:
            return self.owner

ball = Ball()

score_lock = threading.Lock()
scoreboard = {"Barcelona": 0, "Real Madrid": 0}

# Clock

class MatchClock(threading.Thread):
    def __init__(self, tick_event, end_event):
        super().__init__(daemon=True)
        self.tick_event = tick_event
        self.end_event = end_event
        self.current_tick = 0

    def run(self):
        stadium.match_start.wait()
        log("⏱️ Match clock starts.")
        while self.current_tick < MATCH_TICKS and not self.end_event.is_set():
            pause_event.wait()
            start = time.time()
            while True:
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
        super().__init__(daemon=True)
        self.name = FAN_NAMES[idx]
        # Money: 20% rich, buy more/expensive
        if random.random() < 0.2:
            self.money = random.randint(50, 200)
            self.is_rich = True
        else:
            self.money = random.randint(5, 50)
            self.is_rich = False

    def streak_during_match_loop(self):
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

    def run(self):
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
                    if item in SHOP_PRICES:
                        return SHOP_PRICES[item]
                    for shop_info in FOOD_SHOPS + MERCH_SHOPS:
                        prices = shop_info.get("prices", {})
                        if item in prices:
                            return prices[item]
                    return 0

                for _ in range(num_purchases):
                    if random.random() < PROB_BUY_SOMETHING and self.money > 0:
                        items = list(shop_obj.stock.keys())
                        if not items:
                            break

                        if self.is_rich:
                            # weight choices by price (fallback to 1)
                            weights = []
                            for it in items:
                                p = lookup_price(it) or 1
                                weights.append(p)
                            choice = random.choices(items, weights=weights, k=1)[0]
                        else:
                            choice = random.choice(items)

                        price = lookup_price(choice)
                        if shop_obj.buy(self, choice, price):
                            time.sleep(random.uniform(0.1, 0.3))
                        else:
                            break
                shop_obj.leave_queue(self.name)

            time.sleep(random.uniform(0.1, 0.5))

            self.streak_during_match_loop()

# ---------------------------
# Player helpers
# ---------------------------

def role_str(role: Role):
    return role.value

def allowed_pass_targets(player):
    if player.role == Role.FWD:
        return [Role.FWD, Role.MID]
    if player.role == Role.MID:
        return [Role.FWD, Role.MID, Role.DEF]
    if player.role == Role.DEF:
        return [Role.MID, Role.DEF, Role.GK]
    if player.role == Role.GK:
        return [Role.DEF, Role.MID, Role.FWD]
    return []

def can_steal(attacker, owner):
    if owner is None or attacker.team.name == owner.team.name:
        return False, 0.0
    base_p = 0.0
    if owner.role == Role.FWD and attacker.role in (Role.DEF, Role.GK):
        base_p = PROB_STEAL_FWD_BY_DEF_OR_GK
    elif owner.role == Role.MID and attacker.role == Role.MID:
        base_p = PROB_STEAL_MID_BY_MID
    elif owner.role == Role.DEF and attacker.role == Role.FWD:
        base_p = PROB_STEAL_DEF_BY_FWD
    modified_p = base_p * (1 + (attacker.skill - 0.5) * 0.4)  # Skill adjusts ±20%
    return base_p > 0, min(max(modified_p, 0.0), 1.0)

def choose_midfielder(team):
    mids = [p for p in team.players if p.role == Role.MID]
    if mids:
        return random.choice(mids)
    non_gk = [p for p in team.players if p.role != Role.GK]
    return random.choice(non_gk) if non_gk else team.players[0]

def restart_after_goal(scoring_team):
    other = teamA if scoring_team.name == "B" else teamB
    mid = choose_midfielder(other)
    log(f"🔁 Kickoff: {other.name} restarts via {mid}.")
    ball.set_owner(mid)
    log(f"⚽ Ball now with {mid}.")

# ---------------------------
# Player Thread
# ---------------------------

class Player(threading.Thread):
    def __init__(self, team, name, role, team_arrival_barrier, field_barrier):
        super().__init__(daemon=True)
        self.team = team
        self.pname = name
        self.role = role
        self.team_arrival_barrier = team_arrival_barrier
        self.field_barrier = field_barrier
        self.skill = random.uniform(0.0, 1.0)  # Weight for probabilities

    def __str__(self):
        return f"{self.team.name}-{self.pname}({role_str(self.role)}, skill={self.skill:.2f})"

    def pass_ball(self):
        roles = allowed_pass_targets(self)
        candidates = [p for p in self.team.players if p != self and p.role in roles]
        if not candidates:
            return None
        target = random.choice(candidates)
        log(f"➡️  {self} passes to {target}.")
        ball.set_owner(target)
        log(f"⚽ Ball now with {target}.")
        return target

    def consider_shot(self):
        if self.role != Role.FWD:
            return False
        modified_shot_prob = PROB_SHOT_FWD * (1 + (self.skill - 0.5) * 0.4)
        if random.random() < min(max(modified_shot_prob, 0.0), 1.0):
            modified_on_target = PROB_SHOT_ON_TARGET * (1 + (self.skill - 0.5) * 0.4)
            on_target = random.random() < min(max(modified_on_target, 0.0), 1.0)
            other_team = teamA if self.team.name == "B" else teamB
            gk = [p for p in other_team.players if p.role == Role.GK][0]
            modified_save_prob = PROB_SAVE_BY_GK * (1 + (gk.skill - 0.5) * 0.4)
            if on_target:
                if random.random() < min(max(modified_save_prob, 0.0), 1.0):
                    log(f"🧤 Shot by {self} ON TARGET! Saved by {gk}!")
                    ball.set_owner(gk)
                    log(f"⚽ Ball now with {gk}.")
                else:
                    with score_lock:
                        scoreboard[self.team.name] += 1
                    log(f"🥅 GOAL! {self} scores!  Score: {scoreboard['Barcelona']} - {scoreboard['Real Madrid']}")
                    restart_after_goal(self.team)
            else:
                log(f"🎯 Shot by {self} is OFF target. Goal kick to {gk}.")
                ball.set_owner(gk)
                log(f"⚽ Ball now with {gk}.")
            return True
        return False

    def attempt_foul_on_forward_owner(self):
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
            base_p = PROB_FOUL_DEF if self.role == Role.DEF else PROB_FOUL_MID
            modified_p = base_p * (1 - self.skill * 0.3)  # High skill lowers foul chance
            if random.random() < modified_p:
                committed = True
                log(f"🟨 {self} fouls {owner}! PENALTY to Team {owner.team.name}!")
                self.handle_penalty(fouled_forward=owner)
        finally:
            if not committed:
                foul_lock.release()

    def handle_penalty(self, fouled_forward):
        stoppage_lock.acquire()
        try:
            pause_event.clear() #Event is paused when the threading event is not set.
            log("⏸️  Play paused for penalty setup.")
            time.sleep(0.8)
            shooting_team = fouled_forward.team
            other_team = teamA if shooting_team.name == "B" else teamB
            gk = [p for p in other_team.players if p.role == Role.GK][0]
            modified_on_target = PROB_SHOT_ON_TARGET * (1 + (fouled_forward.skill - 0.5) * 0.4)
            on_target = random.random() < min(max(modified_on_target, 0.0), 1.0)
            modified_save_prob = PROB_SAVE_BY_GK * (1 + (gk.skill - 0.5) * 0.4)
            if on_target and random.random() >= min(max(modified_save_prob, 0.0), 1.0):
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
        if random.random() < p:
            got = ball.mutex.acquire(timeout=0.01)
            if got:
                try:
                    if ball.get_owner() == owner and pause_event.is_set():
                        log(f"🧨 STEAL! {self} dispossesses {owner}.")
                        ball.set_owner(self)
                        log(f"⚽ Ball now with {self}.")
                finally:
                    ball.mutex.release()

    def ball_handler_tick(self):
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
            

    def run(self):
        log(f"🚌 {self} arriving at stadium.")
        self.team_arrival_barrier.wait()
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
                self.ball_handler_tick()
            else:
                self.attempt_foul_on_forward_owner()
                self.attempt_steal_window()

        log(f"🏁 {self} done.")

# ---------------------------
# Build Teams & Roster
# ---------------------------

def build_team(name, start_idx):
    team = Team(name)
    roles = [Role.GK] + [Role.DEF]*4 + [Role.MID]*4 + [Role.FWD]*2
    for i in range(TEAM_SIZE):
        p_name = PLAYER_NAMES[start_idx + i]
        p = Player(team, p_name, roles[i], team.arrival_barrier, team.field_barrier)
        team.players.append(p)
    return team

teamA = build_team("Barcelona", 0)
teamB = build_team("Real Madrid", TEAM_SIZE)


class MatchOrchestrator: #threads are started here, will basically work as our main() function.
    def __init__(self):
        self.clock = MatchClock(tick_event, end_event)

    def start(self):
        log("🚨 Simulation boot.")

        fans = [Fan(i) for i in range(NUM_FANS)]
        for f in fans: f.start()

        time.sleep(0.4)
        log("🔓 Stadium gates OPEN.")
        stadium.gates_open.set()

        for p in teamA.players + teamB.players:
            p.start()

        time.sleep(1.0)
        log("🎤 Anthem starts.")
        stadium.anthem_start.set()

        time.sleep(0.8)
        kickoff_owner = random.choice(teamA.players + teamB.players)
        log("🏟️ Match starts!")
        ball.set_owner(kickoff_owner)
        log(f"⚽ Ball now with {kickoff_owner}.")
        stadium.match_start.set()

        self.clock.start()

        end_event.wait()
        time.sleep(0.3)
        log(f"🔚 Final score: Barcelona {scoreboard['Barcelona']} - {scoreboard['Real Madrid']} Madrid")


MatchOrchestrator().start()