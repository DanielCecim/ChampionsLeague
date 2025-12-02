# Disclaimer: AI has been used to assist in the creation of this file.
import random
import threading
import time
from fans import FAN_NAMES

class Fan(threading.Thread):
    
    def __init__(self, idx, stadium=None, end_event=None, pause_event=None, tick_event=None, ball=None, log=None, stoppage_lock=None, prob_streak_match=None, prob_queue_visit=None, prob_buy_something=0.9,food_shops=None, merch_shops=None, food_shops_data=None, merch_shops_data=None, data_collector=None, anthems=None, supporting_team=None):
        super().__init__(daemon=True)
        self.name = FAN_NAMES[idx]
        
        # Shared match resources
        self.stadium = stadium
        self.end_event = end_event
        self.pause_event = pause_event
        self.tick_event = tick_event
        self.ball = ball
        self.log = log
        self.stoppage_lock = stoppage_lock
        self.data_collector = data_collector
        self.anthems = anthems  # Store anthem lines
        self.supporting_team = supporting_team  # Which team this fan supports
        
        # Probabilities and shop data
        self.prob_streak_match = prob_streak_match
        self.prob_queue_visit = prob_queue_visit
        self.prob_buy_something = prob_buy_something
        self.food_shops = food_shops
        self.merch_shops = merch_shops
        self.food_shops_data = food_shops_data
        self.merch_shops_data = merch_shops_data
        
        # People have a random chance of having more money than others
        if random.random() < 0.2:
            self.money = random.randint(300, 500)  # Wealthy fans bring more money
            self.is_rich = True
        else:
            self.money = random.randint(100, 250)  # Regular fans have less money
            self.is_rich = False
        
        self.initial_money = self.money  # Track initial money
        self.has_shopped = False  # Track if fan has already shopped. Once they shop, they dont shop again. This is reasonable for a single match.

    def lookup_price(self, item):
        # Helper to find price from globals. Item prices are stored in food_shops_data and merch_shops_data
        for shop_info in self.food_shops_data + self.merch_shops_data: # combine both food and merch shop data
            prices = shop_info.get("prices", {}) # get prices dict
            if item in prices:
                return prices[item] # return price if found
        return 0

    def shop_during_match(self):
        # Don't shop if already visited shops
        if self.has_shopped:
            return
        
        # Lower probability to visit shops during match (1%)
        if random.random() < 0.01 and self.money > 0: #random.random must be less than 0.01 to shop during match
            all_shops = self.food_shops + self.merch_shops
            shop_obj = random.choice(all_shops) # random shop is picked from the union of food and merch shops
            
            # Determine shop type
            shop_type = "food" if shop_obj in self.food_shops else "merch"
            
            shop_obj.enter_queue(self.name) # Fan tries to enter queue
            
            # Track shop visit
            if self.data_collector:
                self.data_collector.record_shop_visit(self.name) # Record that fan visited a shop
            
            time.sleep(random.uniform(0.3, 0.6)) # Simulate time in queue
            
            # Buy 1-2 items during match
            num_purchases = random.randint(1, 2) if self.is_rich else 1
            
            for _ in range(num_purchases):
                if random.random() < random.choice(self.prob_buy_something) and self.money > 0: # Can only buy if they have money and prob condition met
                    items = list(shop_obj.stock.keys()) # available items in shop
                    if not items: # no items to buy
                        break
                    
                    if self.is_rich:
                        weights = [self.lookup_price(i) or 1 for i in items] #
                        choice = random.choices(items, weights=weights, k=1)[0] # choose based on price weights
                    else:
                        choice = random.choice(items) # regular fans choose randomly
                    
                    price = self.lookup_price(choice)
                    if shop_obj.buy(self, choice, price):
                        # Track purchase
                        if self.data_collector:
                            self.data_collector.record_purchase(self.name, choice, price, shop_type)
                        time.sleep(random.uniform(0.2, 0.4))
                    else:
                        break
            shop_obj.leave_queue(self.name) # Fan leaves the queue
            self.has_shopped = True  # Mark as shopped

    def match_activities_loop(self):
        self.stadium.match_start.wait() # Wait for match to start
        last_owner = None # Track last ball owner for streaking. This is to restore ball possession after streaking.
        tick_count = 0 # Track ticks for shopping intervals
        
        while not self.end_event.is_set(): # Loop until match ends
            self_tick_seen = self.tick_event.wait(timeout=0.5)
            if not self_tick_seen:
                continue
            
            tick_count += 1 # Increment tick count
            
            # Check for streaking (very rare)
            if random.random() < self.prob_streak_match:
                if self.stoppage_lock.acquire(blocking=False): # Try to acquire streak lock
                    try: # Only one fan can streak at a time
                        if not self.pause_event.is_set():
                            continue
                        self.pause_event.clear()
                        last_owner = self.ball.get_owner()
                        self.log(f"🫣 {self.name} streaks onto the field! Players stop!")
                        
                        # Track streak
                        if self.data_collector:
                            self.data_collector.record_streak(self.name)
                        
                        time.sleep(1.2) # Streak duration
                        if last_owner:
                            self.ball.set_owner(last_owner)
                            self.log(f"⚽ Ball now with {last_owner}.")
                        self.log(f"🛡️ Security removed {self.name}. Play resumes.")
                        self.pause_event.set()
                    finally:
                        self.stoppage_lock.release() # Release streak lock
            
            # Shop every few ticks (every ~15 minutes of game time)
            if tick_count % 3 == 0:
                self.shop_during_match()

    def run(self):
        # Initialize fan stats in data collector
        if self.data_collector:
            self.data_collector.init_fan(self.name, self.initial_money, self.is_rich)
        
        self.log(f"🚶 {self.name} heading to stadium.")
        self.stadium.gates_open.wait() # Wait for gates to open
        self.log(f"🚪 {self.name} enters the stadium.")

        time.sleep(random.uniform(0.1, 0.6)) # Simulate time to find seat
        
        # Wait for anthem ceremony and sing with their team
        self.stadium.anthem_start.wait()
        if self.supporting_team and self.anthems:
            anthem_lines = self.anthems.get(self.supporting_team, [])
            if anthem_lines:
                # Determine which anthem event to wait for based on team
                # Check if this fan supports team1 (first to sing)
                team_names = list(self.anthems.keys())
                is_team1 = self.supporting_team == team_names[0] if len(team_names) > 0 else False
                
                if is_team1:
                    self.stadium.team1_anthem.wait()
                else:
                    self.stadium.team2_anthem.wait()
                
                # Sing a random line from their team's anthem
                line = random.choice(anthem_lines)
                self.log(f"🎵 {self.name} sings: {line}")
        if random.random() < self.prob_queue_visit:
            # random shop is picked from the union of food and merch shops
            all_shops = self.food_shops + self.merch_shops
            shop_obj = random.choice(all_shops)
            
            # Determine shop type
            shop_type = "food" if shop_obj in self.food_shops else "merch" # Determine if shop is food or merch. Necessary for data collection.

            shop_obj.enter_queue(self.name) # Fan tries to enter queue
            
            # Track shop visit
            if self.data_collector: 
                self.data_collector.record_shop_visit(self.name)
            
            time.sleep(random.uniform(0.3, 0.8))
            num_purchases = random.randint(2, 4) if self.is_rich else 1 #  Rich fans buy 2-4 items, regular fans buy 1 item

            for _ in range(num_purchases):
                if random.random() < random.choice(self.prob_buy_something) and self.money > 0:  # Can only buy if they have money
                    items = list(shop_obj.stock.keys())
                    if not items:  # no items to buy
                        break

                    if self.is_rich:
                        # choosing items based on price weights for rich fans
                        weights = [] # Rich fans prefer expensive items
                        for i in items:
                            p = self.lookup_price(i) or 1
                            weights.append(p)
                        choice = random.choices(items, weights=weights, k=1)[0]
                    else:
                        choice = random.choice(items)

                    price = self.lookup_price(choice)
                    if shop_obj.buy(self, choice, price):
                        # Track purchase
                        if self.data_collector:
                            self.data_collector.record_purchase(self.name, choice, price, shop_type)
                        time.sleep(random.uniform(0.2, 0.5))
                    else:
                        break
            shop_obj.leave_queue(self.name)  # Fan leaves the queue
            self.has_shopped = True  # Mark as shopped

        time.sleep(random.uniform(0.1, 0.5))

        self.match_activities_loop()  # Shop and potentially streak during match
        
        # Update final money amount
        if self.data_collector:
            self.data_collector.update_fan_money(self.name, self.money)

