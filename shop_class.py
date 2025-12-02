# Disclaimer: AI has been used to assist in the creation of this file.
import threading
from food_shops import SPANISH_FOOD_SHOPS, GERMAN_FOOD_SHOPS
from merch_shops import BARCA_REAL_MERCH, ATLETICO_PSG_MERCH, get_finals_merch
import time

print_lock = threading.Lock() 
t0 = time.time()

def log(msg):
    with print_lock:
        now = time.time() - t0
        print(f"[{now:6.2f}s] {msg}")

SHOP_QUEUE_MAX = 6  # Max fans allowed in shop queue
CASHIERS = 2            # Number of cashiers available

class Shop:
    def __init__(self, stock, queue_max, cashiers, shop_type="shop"):
        self.stock = dict(stock)
        self.stock_lock = threading.Lock() # Lock for stock access
        self.queue_slots = threading.Semaphore(queue_max)  # Max fans in queue. 
        self.cashiers = threading.Semaphore(cashiers) # Number of cashiers
        self.shop_type = shop_type  # Track whether this is food or merch
        self.queue_max = queue_max  # Store max queue size
        self.current_queue_count = 0  # Track current queue occupancy
        self.queue_count_lock = threading.Lock()  # Lock for queue count

    def enter_queue(self, fan_name): # Fan tries to enter queue
        with self.queue_count_lock:
            current = self.current_queue_count
        log(f"🧍 {fan_name} tried to enter the queue (Current queue: {current}/{self.queue_max})")
        self.queue_slots.acquire()
        with self.queue_count_lock:
            self.current_queue_count += 1
            current = self.current_queue_count
        log(f"🧍 {fan_name} entered the {self.shop_type} queue (Current queue: {current}/{self.queue_max})")

    def leave_queue(self, fan_name): # Fan leaves queue
        self.queue_slots.release()
        with self.queue_count_lock:
            self.current_queue_count -= 1
            current = self.current_queue_count
        log(f"🏃 {fan_name} leaves the {self.shop_type} queue (Current queue: {current}/{self.queue_max})")

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

def create_shops_for_match(stadium_location, team1_name=None, team2_name=None):
    # Create appropriate food and merch shops based on stadium location and teams
    if stadium_location == "Allianz Arena":
        food_data = GERMAN_FOOD_SHOPS
    else:  # Bernabeu or Camp Nou
        food_data = SPANISH_FOOD_SHOPS
    
    # Determine merch based on teams
    if team1_name and team2_name:
        # Finals - dynamic based on finalists
        if stadium_location == "Allianz Arena":
            merch_data = get_finals_merch(team1_name, team2_name)
        # Semi-final 1: Barcelona vs Real Madrid
        elif "Barcelona" in [team1_name, team2_name] and "Real Madrid" in [team1_name, team2_name]:
            merch_data = BARCA_REAL_MERCH
        # Semi-final 2: Atletico vs PSG
        else:
            merch_data = ATLETICO_PSG_MERCH
    else:
        merch_data = BARCA_REAL_MERCH  # Default
    
    food_shops = [Shop(shop["stock"], SHOP_QUEUE_MAX, CASHIERS, "food") for shop in food_data]
    
    # Merge all merch shops into one shop with combined stock
    combined_merch_stock = {}
    for shop in merch_data:
        combined_merch_stock.update(shop["stock"])
    
    merch_shops = [Shop(combined_merch_stock, SHOP_QUEUE_MAX, CASHIERS, "merch")]
    
    return food_shops, merch_shops, food_data, merch_data

# Default shops for backward compatibility
food_shops = [Shop(shop["stock"], SHOP_QUEUE_MAX, CASHIERS, "food") for shop in SPANISH_FOOD_SHOPS]
merch_shops = [Shop(shop["stock"], SHOP_QUEUE_MAX, CASHIERS, "merch") for shop in BARCA_REAL_MERCH]