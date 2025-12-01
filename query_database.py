# Database Query Script
# Query and display Champions League match statistics from the database

import sqlite3
import sys
from tabulate import tabulate


def display_matches(db_path):
    # Display all matches
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT match_id, team1, team2, score_team1, score_team2, winner, match_type, stadium_location
        FROM matches
        ORDER BY match_id
    """)
    
    data = cursor.fetchall()
    conn.close()
    
    headers = ["ID", "Team 1", "Team 2", "Score 1", "Score 2", "Winner", "Type", "Stadium"]
    print("\n=== MATCHES ===")
    print(tabulate(data, headers=headers, tablefmt="grid"))


def display_player_stats(db_path, match_id=None):
    # Display player statistics
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    if match_id:
        query = """
            SELECT player_name, team, role, passes, shots, shots_on_target, 
                   goals, steals, fouls_committed, yellow_cards, expelled, 
                   saves, ball_possessions
            FROM player_stats
            WHERE match_id = ?
            ORDER BY goals DESC, passes DESC
        """
        cursor.execute(query, (match_id,))
    else:
        query = """
            SELECT player_name, team, role, SUM(passes) as passes, 
                   SUM(shots) as shots, SUM(shots_on_target) as shots_on_target,
                   SUM(goals) as goals, SUM(steals) as steals, 
                   SUM(fouls_committed) as fouls, SUM(yellow_cards) as yellows,
                   SUM(expelled) as expelled, SUM(saves) as saves, 
                   SUM(ball_possessions) as possessions
            FROM player_stats
            GROUP BY player_name, team
            ORDER BY goals DESC, passes DESC
            LIMIT 20
        """
        cursor.execute(query)
    
    data = cursor.fetchall()
    conn.close()
    
    headers = ["Player", "Team", "Role", "Passes", "Shots", "On Target", 
               "Goals", "Steals", "Fouls", "Yellows", "Red", "Saves", "Possessions"]
    
    title = f"\n=== PLAYER STATS (Match {match_id}) ===" if match_id else "\n=== PLAYER STATS (All Matches) ==="
    print(title)
    print(tabulate(data, headers=headers, tablefmt="grid"))


def display_fan_stats(db_path, match_id=None):
    # Display fan statistics
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    if match_id:
        query = """
            SELECT fan_name, initial_money, final_money, total_spent, 
                   items_purchased, shop_visits, streaked, is_rich
            FROM fan_stats
            WHERE match_id = ?
            ORDER BY total_spent DESC
            LIMIT 20
        """
        cursor.execute(query, (match_id,))
    else:
        query = """
            SELECT fan_name, SUM(initial_money) as init_money, 
                   SUM(final_money) as final_money, SUM(total_spent) as spent,
                   SUM(items_purchased) as items, SUM(shop_visits) as visits,
                   SUM(streaked) as streaked, MAX(is_rich) as rich
            FROM fan_stats
            GROUP BY fan_name
            ORDER BY spent DESC
            LIMIT 20
        """
        cursor.execute(query)
    
    data = cursor.fetchall()
    conn.close()
    
    headers = ["Fan", "Initial $", "Final $", "Spent", "Items", "Visits", "Streaked", "Rich"]
    
    title = f"\n=== FAN STATS (Match {match_id}) ===" if match_id else "\n=== FAN STATS (All Matches) ==="
    print(title)
    print(tabulate(data, headers=headers, tablefmt="grid"))


def display_purchases(db_path, limit=20):
    # Display recent purchases
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT fan_name, item_name, price, shop_type, purchase_time
        FROM purchases
        ORDER BY purchase_id DESC
        LIMIT ?
    """, (limit,))
    
    data = cursor.fetchall()
    conn.close()
    
    headers = ["Fan", "Item", "Price", "Shop Type", "Time"]
    print(f"\n=== RECENT PURCHASES (Last {limit}) ===")
    print(tabulate(data, headers=headers, tablefmt="grid"))


def display_top_scorers(db_path):
    # Display top goal scorers
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT player_name, team, SUM(goals) as total_goals, 
               SUM(shots) as total_shots,
               ROUND(CAST(SUM(goals) AS FLOAT) / SUM(shots) * 100, 1) as conversion_rate
        FROM player_stats
        WHERE shots > 0
        GROUP BY player_name, team
        ORDER BY total_goals DESC
        LIMIT 10
    """)
    
    data = cursor.fetchall()
    conn.close()
    
    headers = ["Player", "Team", "Goals", "Shots", "Conversion %"]
    print("\n=== TOP SCORERS ===")
    print(tabulate(data, headers=headers, tablefmt="grid"))


def display_team_summary(db_path):
    # Display team summary statistics
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT team, 
               SUM(goals) as total_goals,
               SUM(shots) as total_shots,
               SUM(passes) as total_passes,
               SUM(steals) as total_steals,
               SUM(yellow_cards) as total_yellows,
               SUM(expelled) as total_reds
        FROM player_stats
        GROUP BY team
        ORDER BY total_goals DESC
    """)
    
    data = cursor.fetchall()
    conn.close()
    
    headers = ["Team", "Goals", "Shots", "Passes", "Steals", "Yellows", "Reds"]
    print("\n=== TEAM SUMMARY ===")
    print(tabulate(data, headers=headers, tablefmt="grid"))


def display_revenue_summary(db_path):
    # Display revenue summary
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT shop_type, COUNT(*) as num_purchases, 
               SUM(price) as total_revenue,
               AVG(price) as avg_price
        FROM purchases
        GROUP BY shop_type
    """)
    
    data = cursor.fetchall()
    conn.close()
    
    headers = ["Shop Type", "Purchases", "Revenue", "Avg Price"]
    print("\n=== REVENUE SUMMARY ===")
    print(tabulate(data, headers=headers, tablefmt="grid"))


def main():
    db_path = "champions_league_data.db"
    
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    
    print(f"\n{'='*60}")
    print(f"CHAMPIONS LEAGUE DATABASE REPORT")
    print(f"Database: {db_path}")
    print(f"{'='*60}")
    
    try:
        display_matches(db_path)
        display_top_scorers(db_path)
        display_team_summary(db_path)
        display_player_stats(db_path)
        display_fan_stats(db_path)
        display_revenue_summary(db_path)
        display_purchases(db_path, limit=15)
        
        print(f"\n{'='*60}\n")
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
