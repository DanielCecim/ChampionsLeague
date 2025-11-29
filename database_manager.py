import sqlite3
import threading
import time

class DatabaseManager:
    def __init__(self, db_name="champions_league.db"):
        self.db_name = db_name
        self.lock = threading.Lock()
        self.init_db()

    def init_db(self):
        with self.lock:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Table for match events (passes, goals, fouls, etc.)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS match_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    event_type TEXT,
                    player_name TEXT,
                    team_name TEXT,
                    details TEXT
                )
            ''')
            
            # Table for store sales
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS store_sales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    fan_name TEXT,
                    item_name TEXT,
                    price REAL,
                    shop_type TEXT
                )
            ''')
            
            conn.commit()
            conn.close()

    def log_event(self, event_type, player_name, team_name, details=""):
        with self.lock:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO match_events (timestamp, event_type, player_name, team_name, details)
                VALUES (?, ?, ?, ?, ?)
            ''', (time.time(), event_type, player_name, team_name, details))
            conn.commit()
            conn.close()

    def log_sale(self, fan_name, item_name, price, shop_type="Unknown"):
        with self.lock:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO store_sales (timestamp, fan_name, item_name, price, shop_type)
                VALUES (?, ?, ?, ?, ?)
            ''', (time.time(), fan_name, item_name, price, shop_type))
            conn.commit()
            conn.close()

    def get_match_stats(self):
        with self.lock:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM match_events")
            events = cursor.fetchall()
            conn.close()
            return events

    def get_sales_stats(self):
        with self.lock:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM store_sales")
            sales = cursor.fetchall()
            conn.close()
            return sales
