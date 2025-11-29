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
                 merch_shops_data=None):
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

    def streak_during_match_loop(self):
        """Fan may streak during match. Although very rare. Probability defined globally."""
        self.stadium.match_start.wait()
        last_owner = None
        while not self.end_event.is_set():
            self_tick_seen = self.tick_event.wait(timeout=0.5)
            if not self_tick_seen:
                continue
            if random.random() < self.prob_streak_match:
                if self.stoppage_lock.acquire(blocking=False):
                    try:
                        if not self.pause_event.is_set():
                            continue
                        self.pause_event.clear()
                        last_owner = self.ball.get_owner()
                        self.log(f"🫣 {self.name} streaks onto the field! Players stop!")
                        time.sleep(1.2)
                        if last_owner:
                            self.ball.set_owner(last_owner)
                            self.log(f"⚽ Ball now with {last_owner}.")
                        self.log(f"🛡️ Security removed {self.name}. Play resumes.")
                        self.pause_event.set()
                    finally:
                        self.stoppage_lock.release()

    def run(self):
        """Main fan loop. From entering stadium to shopping to streaking."""
        self.log(f"🚶 {self.name} heading to stadium.")
        self.stadium.gates_open.wait()
        self.log(f"🚪 {self.name} enters the stadium.")

        time.sleep(random.uniform(0.1, 0.6))
        if random.random() < self.prob_queue_visit:
            # random shop is picked from the union of food and merch shops
            all_shops = self.food_shops + self.merch_shops
            shop_obj = random.choice(all_shops)

            shop_obj.enter_queue(self.name)
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
                        time.sleep(random.uniform(0.1, 0.3))
                    else:
                        break
            shop_obj.leave_queue(self.name)  # Fan leaves the queue

        time.sleep(random.uniform(0.1, 0.5))

        self.streak_during_match_loop()  # Start streaking possibility during match
