# Disclaimer: AI has been used to assist in the creation of this file.
import sqlite3
import threading
from datetime import datetime

# This DataCollector object will be used to collect and store match statistics

class DataCollector: # We create the data collector object in the main file
    def __init__(self, db_path="champions_league_data.db", clear_existing=False):
        self.db_path = db_path
        self.lock = threading.Lock()
        self.init_database()
        
        if clear_existing:
            self.clear_all_data()
        self.player_stats = {}
        self.fan_stats = {}
        self.match_id = None
        self.match_start_time = None
        
    def init_database(self): # Initialize SQLite database with required tables
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Matches table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS matches (
                match_id INTEGER PRIMARY KEY AUTOINCREMENT,
                team1 TEXT NOT NULL,
                team2 TEXT NOT NULL,
                score_team1 INTEGER DEFAULT 0,
                score_team2 INTEGER DEFAULT 0,
                winner TEXT,
                match_type TEXT,
                stadium_location TEXT,
                match_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        try:
            cursor.execute("SELECT stadium_location FROM matches LIMIT 1")
        except sqlite3.OperationalError:
            # Column doesn't exist, add it
            cursor.execute("ALTER TABLE matches ADD COLUMN stadium_location TEXT DEFAULT 'Unknown'")
            conn.commit()
            print("📊 Database updated: Added stadium_location column to matches table")
        
        # Player statistics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS player_stats (
                stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER,
                player_name TEXT NOT NULL,
                team TEXT NOT NULL,
                role TEXT NOT NULL,
                passes INTEGER DEFAULT 0,
                shots INTEGER DEFAULT 0,
                shots_on_target INTEGER DEFAULT 0,
                goals INTEGER DEFAULT 0,
                steals INTEGER DEFAULT 0,
                fouls_committed INTEGER DEFAULT 0,
                yellow_cards INTEGER DEFAULT 0,
                expelled INTEGER DEFAULT 0,
                saves INTEGER DEFAULT 0,
                ball_possessions INTEGER DEFAULT 0,
                final_fatigue REAL DEFAULT 0.0,
                FOREIGN KEY (match_id) REFERENCES matches(match_id)
            )
        """)
        
        # Fan statistics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fan_stats (
                stat_id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER,
                fan_name TEXT NOT NULL,
                initial_money REAL DEFAULT 0.0,
                final_money REAL DEFAULT 0.0,
                total_spent REAL DEFAULT 0.0,
                items_purchased INTEGER DEFAULT 0,
                shop_visits INTEGER DEFAULT 0,
                streaked INTEGER DEFAULT 0,
                is_rich INTEGER DEFAULT 0,
                FOREIGN KEY (match_id) REFERENCES matches(match_id)
            )
        """)
        
        # Purchase details table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS purchases (
                purchase_id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id INTEGER,
                fan_name TEXT NOT NULL,
                item_name TEXT NOT NULL,
                price REAL NOT NULL,
                shop_type TEXT,
                purchase_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (match_id) REFERENCES matches(match_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def clear_all_data(self):
        # Clear all existing data from the database (for fresh tournament start)
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM purchases")
            cursor.execute("DELETE FROM fan_stats")
            cursor.execute("DELETE FROM player_stats")
            cursor.execute("DELETE FROM matches")
            
            # Reset auto-increment counters
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='matches'")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='player_stats'")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='fan_stats'")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='purchases'")
            
            conn.commit()
            conn.close()
            print("🗑️  Cleared previous tournament data")
    
    def start_match(self, team1, team2, match_type="regular", stadium_location="Unknown"):
        # Start tracking a new match
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO matches (team1, team2, match_type, stadium_location)
                VALUES (?, ?, ?, ?)
            """, (team1, team2, match_type, stadium_location))
            self.match_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            self.match_start_time = datetime.now()
            self.player_stats = {}
            self.fan_stats = {}
            
        return self.match_id
    
    def end_match(self, score_team1, score_team2, winner):
        # Finalize match data
        if self.match_id is None:
            return
        
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE matches 
                SET score_team1 = ?, score_team2 = ?, winner = ?
                WHERE match_id = ?
            """, (score_team1, score_team2, winner, self.match_id))
            conn.commit()
            conn.close()
    
    def init_player(self, player_name, team, role):
        # Initialize player statistics
        key = (player_name, team)
        with self.lock:
            if key not in self.player_stats:
                self.player_stats[key] = {
                    'player_name': player_name,
                    'team': team,
                    'role': role,
                    'passes': 0,
                    'shots': 0,
                    'shots_on_target': 0,
                    'goals': 0,
                    'steals': 0,
                    'fouls_committed': 0,
                    'yellow_cards': 0,
                    'expelled': 0,
                    'saves': 0,
                    'ball_possessions': 0,
                    'final_fatigue': 0.0
                }
    
    def init_fan(self, fan_name, initial_money, is_rich):
        # Initialize fan statistics
        with self.lock:
            if fan_name not in self.fan_stats:
                self.fan_stats[fan_name] = {
                    'fan_name': fan_name,
                    'initial_money': initial_money,
                    'final_money': initial_money,
                    'total_spent': 0.0,
                    'items_purchased': 0,
                    'shop_visits': 0,
                    'streaked': 0,
                    'is_rich': 1 if is_rich else 0
                }
    
    def record_pass(self, player_name, team):
        # Record a pass
        key = (player_name, team)
        with self.lock:
            if key in self.player_stats:
                self.player_stats[key]['passes'] += 1
    
    def record_shot(self, player_name, team, on_target=False, goal=False):
        # Record a shot
        key = (player_name, team)
        with self.lock:
            if key in self.player_stats:
                self.player_stats[key]['shots'] += 1
                if on_target:
                    self.player_stats[key]['shots_on_target'] += 1
                if goal:
                    self.player_stats[key]['goals'] += 1
    
    def record_steal(self, player_name, team):
        # Record a steal
        key = (player_name, team)
        with self.lock:
            if key in self.player_stats:
                self.player_stats[key]['steals'] += 1
    
    def record_foul(self, player_name, team):
        # Record a foul
        key = (player_name, team)
        with self.lock:
            if key in self.player_stats:
                self.player_stats[key]['fouls_committed'] += 1
    
    def record_yellow_card(self, player_name, team):
        # Record a yellow card
        key = (player_name, team)
        with self.lock:
            if key in self.player_stats:
                self.player_stats[key]['yellow_cards'] += 1
    
    def record_expulsion(self, player_name, team):
        # Record an expulsion
        key = (player_name, team)
        with self.lock:
            if key in self.player_stats:
                self.player_stats[key]['expelled'] = 1
    
    def record_save(self, player_name, team):
        # Record a goalkeeper save
        key = (player_name, team)
        with self.lock:
            if key in self.player_stats:
                self.player_stats[key]['saves'] += 1
    
    def record_ball_possession(self, player_name, team):
        # Record ball possession
        key = (player_name, team)
        with self.lock:
            if key in self.player_stats:
                self.player_stats[key]['ball_possessions'] += 1
    
    def update_player_fatigue(self, player_name, team, fatigue_level):
        # Update player fatigue level
        key = (player_name, team)
        with self.lock:
            if key in self.player_stats:
                self.player_stats[key]['final_fatigue'] = fatigue_level
    
    def record_purchase(self, fan_name, item_name, price, shop_type):
        # Record a fan purchase
        with self.lock:
            if fan_name in self.fan_stats:
                self.fan_stats[fan_name]['items_purchased'] += 1
                self.fan_stats[fan_name]['total_spent'] += price
                
            # Store in database immediately
            if self.match_id:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO purchases (match_id, fan_name, item_name, price, shop_type)
                    VALUES (?, ?, ?, ?, ?)
                """, (self.match_id, fan_name, item_name, price, shop_type))
                conn.commit()
                conn.close()
    
    def record_shop_visit(self, fan_name):
        # Record a shop visit
        with self.lock:
            if fan_name in self.fan_stats:
                self.fan_stats[fan_name]['shop_visits'] += 1
    
    def record_streak(self, fan_name):
        # Record a fan streaking
        with self.lock:
            if fan_name in self.fan_stats:
                self.fan_stats[fan_name]['streaked'] = 1
    
    def update_fan_money(self, fan_name, final_money):
        # Update fan's final money amount
        with self.lock:
            if fan_name in self.fan_stats:
                self.fan_stats[fan_name]['final_money'] = final_money
    
    def save_all_stats(self):
        # Save all collected statistics to database
        if self.match_id is None:
            return
        
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Save player stats
            for key, stats in self.player_stats.items():
                cursor.execute("""
                    INSERT INTO player_stats (
                        match_id, player_name, team, role, passes, shots, 
                        shots_on_target, goals, steals, fouls_committed, 
                        yellow_cards, expelled, saves, ball_possessions, final_fatigue
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    self.match_id, stats['player_name'], stats['team'], 
                    stats['role'], stats['passes'], stats['shots'],
                    stats['shots_on_target'], stats['goals'], stats['steals'],
                    stats['fouls_committed'], stats['yellow_cards'], 
                    stats['expelled'], stats['saves'], stats['ball_possessions'],
                    stats['final_fatigue']
                ))
            
            # Save fan stats
            for fan_name, stats in self.fan_stats.items():
                cursor.execute("""
                    INSERT INTO fan_stats (
                        match_id, fan_name, initial_money, final_money, 
                        total_spent, items_purchased, shop_visits, streaked, is_rich
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    self.match_id, stats['fan_name'], stats['initial_money'],
                    stats['final_money'], stats['total_spent'], 
                    stats['items_purchased'], stats['shop_visits'],
                    stats['streaked'], stats['is_rich']
                ))
            
            conn.commit()
            conn.close()
    
    def get_match_summary(self, match_id):
        # Get summary of a specific match
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM matches WHERE match_id = ?", (match_id,))
        match = cursor.fetchone()
        
        cursor.execute("SELECT * FROM player_stats WHERE match_id = ?", (match_id,))
        players = cursor.fetchall()
        
        cursor.execute("SELECT * FROM fan_stats WHERE match_id = ?", (match_id,))
        fans = cursor.fetchall()
        
        conn.close()
        return {'match': match, 'players': players, 'fans': fans}
