import random
import threading
import time
from fans import FAN_NAMES


class Fan(threading.Thread):
    """Fan thread representing a stadium attendee who shops and may streak"""
    
    def __init__(self, idx, stadium=None, end_event=None, pause_event=None, 
                 tick_event=None, ball=None, log=None, stoppage_lock=None,
                 prob_streak_match=None, prob_queue_visit=None, prob_buy_something=0.9,
                 food_shops=None, merch_shops=None, food_shops_data=None, 
                 merch_shops_data=None, data_collector=None):
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
        self.has_shopped = False  # Track if fan has already shopped

    def shop_during_match(self):
        """Fan shops periodically during the match."""
        # Don't shop if already visited shops
        if self.has_shopped:
            return
        
        def lookup_price(item):
            for shop_info in self.food_shops_data + self.merch_shops_data:
                prices = shop_info.get("prices", {})
                if item in prices:
                    return prices[item]
            return 0
        
        # Lower probability to visit shops during match (1%)
        if random.random() < 0.01 and self.money > 0:
            all_shops = self.food_shops + self.merch_shops
            shop_obj = random.choice(all_shops)
            
            # Determine shop type
            shop_type = "food" if shop_obj in self.food_shops else "merch"
            
            shop_obj.enter_queue(self.name)
            
            # Track shop visit
            if self.data_collector:
                self.data_collector.record_shop_visit(self.name)
            
            time.sleep(random.uniform(0.1, 0.3))
            
            # Buy 1-2 items during match
            num_purchases = random.randint(1, 2) if self.is_rich else 1
            
            for _ in range(num_purchases):
                if random.random() < random.choice(self.prob_buy_something) and self.money > 0:
                    items = list(shop_obj.stock.keys())
                    if not items:
                        break
                    
                    if self.is_rich:
                        weights = [lookup_price(i) or 1 for i in items]
                        choice = random.choices(items, weights=weights, k=1)[0]
                    else:
                        choice = random.choice(items)
                    
                    price = lookup_price(choice)
                    if shop_obj.buy(self, choice, price):
                        # Track purchase
                        if self.data_collector:
                            self.data_collector.record_purchase(self.name, choice, price, shop_type)
                        time.sleep(random.uniform(0.05, 0.15))
                    else:
                        break
            shop_obj.leave_queue(self.name)
            self.has_shopped = True  # Mark as shopped

    def match_activities_loop(self):
        """Fan may streak or shop during match."""
        self.stadium.match_start.wait()
        last_owner = None
        tick_count = 0
        
        while not self.end_event.is_set():
            self_tick_seen = self.tick_event.wait(timeout=0.5)
            if not self_tick_seen:
                continue
            
            tick_count += 1
            
            # Check for streaking (very rare)
            if random.random() < self.prob_streak_match:
                if self.stoppage_lock.acquire(blocking=False):
                    try:
                        if not self.pause_event.is_set():
                            continue
                        self.pause_event.clear()
                        last_owner = self.ball.get_owner()
                        self.log(f"🫣 {self.name} streaks onto the field! Players stop!")
                        
                        # Track streak
                        if self.data_collector:
                            self.data_collector.record_streak(self.name)
                        
                        time.sleep(1.2)
                        if last_owner:
                            self.ball.set_owner(last_owner)
                            self.log(f"⚽ Ball now with {last_owner}.")
                        self.log(f"🛡️ Security removed {self.name}. Play resumes.")
                        self.pause_event.set()
                    finally:
                        self.stoppage_lock.release()
            
            # Shop every few ticks (every ~15 minutes of game time)
            if tick_count % 3 == 0:
                self.shop_during_match()

    def run(self):
        """Main fan loop. From entering stadium to shopping to streaking."""
        # Initialize fan stats in data collector
        if self.data_collector:
            self.data_collector.init_fan(self.name, self.initial_money, self.is_rich)
        
        self.log(f"🚶 {self.name} heading to stadium.")
        self.stadium.gates_open.wait()
        self.log(f"🚪 {self.name} enters the stadium.")

        time.sleep(random.uniform(0.1, 0.6))
        if random.random() < self.prob_queue_visit:
            # random shop is picked from the union of food and merch shops
            all_shops = self.food_shops + self.merch_shops
            shop_obj = random.choice(all_shops)
            
            # Determine shop type
            shop_type = "food" if shop_obj in self.food_shops else "merch"

            shop_obj.enter_queue(self.name)
            
            # Track shop visit
            if self.data_collector:
                self.data_collector.record_shop_visit(self.name)
            
            time.sleep(random.uniform(0.1, 0.5))
            num_purchases = random.randint(2, 4) if self.is_rich else 1

            # helper to find price from globals
            def lookup_price(item):
                for shop_info in self.food_shops_data + self.merch_shops_data:
                    prices = shop_info.get("prices", {})
                    if item in prices:
                        return prices[item]
                return 0

            for _ in range(num_purchases):
                if random.random() < random.choice(self.prob_buy_something) and self.money > 0:  # Can only buy if they have money
                    items = list(shop_obj.stock.keys())
                    if not items:  # no items to buy
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
                        # Track purchase
                        if self.data_collector:
                            self.data_collector.record_purchase(self.name, choice, price, shop_type)
                        time.sleep(random.uniform(0.1, 0.3))
                    else:
                        break
            shop_obj.leave_queue(self.name)  # Fan leaves the queue
            self.has_shopped = True  # Mark as shopped

        time.sleep(random.uniform(0.1, 0.5))

        self.match_activities_loop()  # Shop and potentially streak during match
        
        # Update final money amount
        if self.data_collector:
            self.data_collector.update_fan_money(self.name, self.money)

