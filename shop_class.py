import threading
from food_shops import FOOD_SHOPS
from merch_shops import MERCH_SHOPS
import time

print_lock = threading.Lock() 
t0 = time.time()

def log(msg):
    with print_lock:
        now = time.time() - t0
        print(f"[{now:6.2f}s] {msg}")

SHOP_QUEUE_MAX = 12  # Max fans allowed in shop queue
CASHIERS = 2            # Number of cashiers available

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