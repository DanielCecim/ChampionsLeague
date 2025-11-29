import threading
import time
import random
from enum import Enum

# Re-import what Player needs
from players import (
    PROB_FOUL_DEF, PROB_FOUL_MID, PROB_STEAL_DEF_BY_FWD,
    PROB_STEAL_MID_BY_MID, PROB_STEAL_FWD_BY_DEF_OR_GK,
    PROB_SHOT_FWD, PROB_SAVE_BY_GK, PROB_SHOT_ON_TARGET
)

# Role enum
class Role(Enum):
    GK = "GK"
    DEF = "DEF"
    MID = "MID"
    FWD = "FWD"

# Player helper functions

def role_str(role: Role):
    """Convert role enum to string"""
    return role.value

def allowed_pass_targets(player):
    """Determine allowed pass targets based on player role"""
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
    """Determine if attacker can steal from owner and the probability"""
    if owner is None or attacker.team.name == owner.team.name:
        return False, 0.0
    if owner.role == Role.FWD and attacker.role in (Role.DEF, Role.GK):
        return True, attacker.probs.get(PROB_STEAL_FWD_BY_DEF_OR_GK, 0.0)
    elif owner.role == Role.MID and attacker.role == Role.MID:
        return True, attacker.probs.get(PROB_STEAL_MID_BY_MID, 0.0)
    elif owner.role == Role.DEF and attacker.role == Role.FWD:
        return True, attacker.probs.get(PROB_STEAL_DEF_BY_FWD, 0.0)
    return False, 0.0

def choose_midfielder(team):
    """Choose a midfielder from the team for kickoff"""
    mids = [p for p in team.players if p.role == Role.MID]
    if mids:
        return random.choice(mids)
    non_gk = [p for p in team.players if p.role != Role.GK]
    return random.choice(non_gk) if non_gk else team.players[0]

def restart_after_goal(scoring_team, ball, log, scoreboard, score_lock, get_opponent):
    """Restart match after a goal"""
    other = get_opponent(scoring_team)
    if other is None:
        return
    mid = choose_midfielder(other)
    log(f"🔁 Kickoff: {other.name} restarts via {mid}.")
    ball.set_owner(mid)
    log(f"⚽ Ball now with {mid}.")

# Player Thread

class Player(threading.Thread):
    """Player thread representing a soccer player"""
    
    def __init__(self, team, name, role, team_arrival_barrier, field_barrier, data=None,
                 stadium=None, end_event=None, pause_event=None, tick_event=None,
                 ball=None, log=None, anthems=None, scoreboard=None, score_lock=None,
                 stoppage_lock=None, foul_lock=None, get_opponent=None):
        super().__init__(daemon=True)
        self.team = team
        self.pname = name
        self.role = role
        self.team_arrival_barrier = team_arrival_barrier
        self.field_barrier = field_barrier
        self.data = data or {}
        
        # Shared match resources
        self.stadium = stadium
        self.end_event = end_event
        self.pause_event = pause_event
        self.tick_event = tick_event
        self.ball = ball
        self.log = log
        self.anthems = anthems
        self.scoreboard = scoreboard
        self.score_lock = score_lock
        self.stoppage_lock = stoppage_lock
        self.foul_lock = foul_lock
        self.get_opponent = get_opponent

        pos = self.data.get("pos", None)
        if pos:
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
        
        # Copy probs to allow per-player fatigue modifications
        self.probs = dict(self.data.get("probs", {}))
        self.original_probs = dict(self.probs)  # Keep original values
        self.fatigue_reduction = 0.001  # Amount to reduce per tick
        
        # Yellow card tracking
        self.yellow_cards = 0
        self.is_expelled = False

    def apply_fatigue(self):
        """Reduce all player probabilities due to fatigue"""
        for prob_key in self.probs:
            self.probs[prob_key] = max(0.0, self.probs[prob_key] - self.fatigue_reduction)

    def __str__(self):
        """String representation of player"""
        return f"{self.team.name}-{self.pname}({role_str(self.role)})"

    def pass_ball(self):
        """Player attempts to pass the ball"""
        if self.is_expelled:  # Expelled players can't pass
            return None
        roles = allowed_pass_targets(self)
        candidates = [p for p in self.team.players if p != self and p.role in roles and not p.is_expelled]
        if not candidates:
            return None
        target = random.choice(candidates)
        self.log(f"➡️  {self} passes to {target}.")
        self.ball.set_owner(target)
        return target

    def consider_shot(self):
        """Player considers taking a shot"""
        if self.is_expelled:  # Expelled players can't shoot
            return False
        if self.role != Role.FWD:
            return False
        modified_shot_prob = self.probs.get(PROB_SHOT_FWD, 0.0)
        if random.random() < modified_shot_prob:
            modified_on_target = self.probs.get(PROB_SHOT_ON_TARGET, 0.0)
            on_target = random.random() < modified_on_target
            other_team = self.get_opponent(self.team)
            if other_team is None:
                return False
            gk = [p for p in other_team.players if p.role == Role.GK][0]
            modified_save_prob = gk.probs.get(PROB_SAVE_BY_GK, 0.0)
            if on_target:
                if random.random() < modified_save_prob:
                    self.log(f"🧤 Shot by {self} ON TARGET! Saved by {gk}!")
                    self.ball.set_owner(gk)
                    self.log(f"⚽ Ball now with {gk}.")
                else:
                    with self.score_lock:
                        self.scoreboard[self.team.name] += 1
                        s_scoring = self.scoreboard.get(self.team.name, 0)
                        opponent = self.get_opponent(self.team)
                        s_opponent = self.scoreboard.get(opponent.name if opponent else "", 0)
                    self.log(f"🥅 GOAL! {self} scores!  Score: {self.team.name} {s_scoring} - {s_opponent} {opponent.name if opponent else ''}")
                    restart_after_goal(self.team, self.ball, self.log, self.scoreboard, self.score_lock, self.get_opponent)
            else:
                self.log(f"🎯 Shot by {self} is OFF target. Goal kick to {gk}.")
                self.ball.set_owner(gk)
            return True
        return False

    def attempt_foul_on_forward_owner(self):
        """Attempt to foul the forward who has the ball"""
        if self.role not in (Role.DEF, Role.MID):
            return
        if self.is_expelled:  # Expelled players can't foul
            return
        owner = self.ball.get_owner()
        if owner is None or owner.team.name == self.team.name or owner.role != Role.FWD:
            return
        if not self.foul_lock.acquire(blocking=False):
            return
        committed = False
        try:
            owner_now = self.ball.get_owner()
            if owner_now != owner or not self.pause_event.is_set():
                return
            base_p = self.probs.get(PROB_FOUL_DEF, 0.0) if self.role == Role.DEF else self.probs.get(PROB_FOUL_MID, 0.0)
            if random.random() < base_p:
                committed = True
                self.yellow_cards += 1
                if self.yellow_cards >= 2:
                    self.is_expelled = True
                    self.log(f"🟥 {self} gets a SECOND YELLOW CARD and is EXPELLED!")
                    self.log(f"⚽ Ball awarded to {owner}. No penalty due to expulsion.")
                    self.ball.set_owner(owner)
                else:
                    self.log(f"🟨 {self} fouls {owner}! YELLOW CARD! PENALTY to Team {owner.team.name}!")
                    self.handle_penalty(fouled_forward=owner)
        finally:
            if not committed:
                self.foul_lock.release()

    def handle_penalty(self, fouled_forward):
        """Handle a penalty kick"""
        self.stoppage_lock.acquire()
        try:
            self.pause_event.clear()
            self.log("⏸️  Play paused for penalty setup.")
            time.sleep(0.8)
            shooting_team = fouled_forward.team
            other_team = self.get_opponent(shooting_team)
            if other_team is None:
                return
            gk = [p for p in other_team.players if p.role == Role.GK][0]
            modified_on_target = fouled_forward.probs.get(PROB_SHOT_ON_TARGET, 0.0)
            on_target = random.random() < min(max(modified_on_target, 0.0), 1.0)
            modified_save_prob = gk.probs.get(PROB_SAVE_BY_GK, 0.0)
            if on_target and random.random() >= modified_save_prob:
                with self.score_lock:
                    self.scoreboard[shooting_team.name] += 1
                    s_scoring = self.scoreboard.get(shooting_team.name, 0)
                    opponent = self.get_opponent(shooting_team)
                    s_opponent = self.scoreboard.get(opponent.name if opponent else "", 0)
                self.log(f"🥅 PENALTY GOAL by {fouled_forward}! Score: {shooting_team.name} {s_scoring} - {s_opponent} {opponent.name if opponent else ''}")
                restart_after_goal(shooting_team, self.ball, self.log, self.scoreboard, self.score_lock, self.get_opponent)
            else:
                if on_target:
                    self.log(f"🧤 Penalty by {fouled_forward} SAVED by {gk}!")
                else:
                    self.log(f"🎯 Penalty by {fouled_forward} OFF target. {gk} restarts.")
                self.ball.set_owner(gk)
                self.log(f"⚽ Ball now with {gk}.")
            time.sleep(0.4)
            self.log("▶️  Play resumes after penalty.")
            self.pause_event.set()
        finally:
            self.stoppage_lock.release()
            self.foul_lock.release()

    def attempt_steal_window(self):
        """Attempt to steal the ball from opponent"""
        if self.is_expelled:  # Expelled players can't steal
            return
        owner = self.ball.get_owner()
        allowed, p = can_steal(self, owner)
        if not allowed or not self.pause_event.is_set():
            return
        if random.random() < float(p or 0.0):
            got = self.ball.mutex.acquire(timeout=0.01)
            if got:
                try:
                    if self.ball.get_owner() == owner and self.pause_event.is_set():
                        self.log(f"🥷 STEAL! {self} dispossesses {owner}.")
                        self.ball.set_owner(self)
                finally:
                    self.ball.mutex.release()

    def ball_handler_tick(self):
        """Handle ball possession on tick"""
        if self.is_expelled:  # Expelled players can't handle ball
            return
        if not self.pause_event.is_set():
            return
        got = self.ball.mutex.acquire(timeout=0.05)
        if not got:
            return
        try:
            if self.ball.get_owner() != self or not self.pause_event.is_set():
                return
            if not self.consider_shot():
                self.pass_ball()
        finally:
            self.ball.mutex.release()

    def run(self):
        """Main player loop"""
        self.log(f"🚌 {self} arriving at stadium.")
        self.team_arrival_barrier.wait()
        self.log(f"🧳 {self} heads to locker room.")
        time.sleep(random.uniform(0.1, 0.4))

        self.log(f"🚶 {self} walking to tunnel.")
        self.field_barrier.wait()

        self.stadium.anthem_start.wait()
        
        # Get anthem lines for this team
        anthem_lines = self.anthems.get(self.team.name, [])
        for line in anthem_lines:
            self.log(f"🎶 {self} sings: {line}")
            time.sleep(0.03)

        # Reset stats to original before match starts
        self.probs = dict(self.original_probs)
        self.yellow_cards = 0
        self.is_expelled = False

        self.stadium.match_start.wait()

        while not self.end_event.is_set():
            self.pause_event.wait()
            tick_seen = self.tick_event.wait(timeout=0.2)
            if self.end_event.is_set():
                break
            
            # Apply fatigue every tick (every 5 minutes)
            if tick_seen:
                self.apply_fatigue()
            
            if self.ball.get_owner() == self:
                self.ball_handler_tick()
            else:
                self.attempt_foul_on_forward_owner()
                self.attempt_steal_window()

        self.log(f"🏁 {self} done.")
