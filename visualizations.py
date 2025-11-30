"""
Visualization Module
Generates bar charts and other visualizations from Champions League match data
Organized by match and overall tournament statistics
"""

import sqlite3
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Stadium capacity multiplier: 100 fans * 1000 = 100,000 (Camp Nou capacity)
STADIUM_CAPACITY_MULTIPLIER = 1000


def get_database_connection(db_path):
    """Get a connection to the SQLite database"""
    return sqlite3.connect(db_path)


def get_all_matches(db_path):
    """Get list of all matches with their IDs and details"""
    conn = get_database_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT match_id, team1, team2, match_type, stadium_location
        FROM matches
        ORDER BY match_id
    """)
    matches = cursor.fetchall()
    conn.close()
    return matches


def generate_player_goals_chart_per_match(db_path, match_id, match_label, output_dir="charts"):
    """Generate bar chart of top goal scorers for a specific match"""
    Path(output_dir).mkdir(exist_ok=True)
    
    conn = get_database_connection(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT player_name, team, goals
        FROM player_stats
        WHERE match_id = ? AND goals > 0
        ORDER BY goals DESC
        LIMIT 10
    """, (match_id,))
    
    data = cursor.fetchall()
    conn.close()
    
    if not data:
        return
    
    players = [f"{row[0]} ({row[1]})" for row in data]
    goals = [row[2] for row in data]
    
    plt.figure(figsize=(12, 6))
    bars = plt.bar(players, goals, color='#2E7D32')
    plt.xlabel('Player', fontsize=12, fontweight='bold')
    plt.ylabel('Goals', fontsize=12, fontweight='bold')
    plt.title(f'Top Goal Scorers - {match_label}', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontweight='bold')
    
    filename = f"{output_dir}/match_{match_id}_goal_scorers.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: {filename}")


def generate_player_goals_chart(db_path, output_dir="charts"):
    """Generate bar chart of top goal scorers across ALL matches"""
    Path(output_dir).mkdir(exist_ok=True)
    
    conn = get_database_connection(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT player_name, team, SUM(goals) as total_goals
        FROM player_stats
        WHERE goals > 0
        GROUP BY player_name, team
        ORDER BY total_goals DESC
        LIMIT 10
    """)
    
    data = cursor.fetchall()
    conn.close()
    
    if not data:
        print("No goal data available")
        return
    
    players = [f"{row[0]} ({row[1]})" for row in data]
    goals = [row[2] for row in data]
    
    plt.figure(figsize=(12, 6))
    bars = plt.bar(players, goals, color='#2E7D32')
    plt.xlabel('Player', fontsize=12, fontweight='bold')
    plt.ylabel('Goals', fontsize=12, fontweight='bold')
    plt.title('Top Goal Scorers - Tournament Overall', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontweight='bold')
    
    plt.savefig(f"{output_dir}/tournament_top_goal_scorers.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: {output_dir}/tournament_top_goal_scorers.png")


def generate_player_passes_chart_per_match(db_path, match_id, match_label, output_dir="charts"):
    """Generate bar chart of players with most passes for a specific match"""
    Path(output_dir).mkdir(exist_ok=True)
    
    conn = get_database_connection(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT player_name, team, passes
        FROM player_stats
        WHERE match_id = ? AND passes > 0
        ORDER BY passes DESC
        LIMIT 10
    """, (match_id,))
    
    data = cursor.fetchall()
    conn.close()
    
    if not data:
        return
    
    players = [f"{row[0]} ({row[1]})" for row in data]
    passes = [row[2] for row in data]
    
    plt.figure(figsize=(12, 6))
    bars = plt.bar(players, passes, color='#1976D2')
    plt.xlabel('Player', fontsize=12, fontweight='bold')
    plt.ylabel('Passes', fontsize=12, fontweight='bold')
    plt.title(f'Top Passers - {match_label}', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontweight='bold')
    
    filename = f"{output_dir}/match_{match_id}_top_passers.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: {filename}")



def generate_player_passes_chart(db_path, output_dir="charts"):
    """Generate bar chart of players with most passes across ALL matches"""
    Path(output_dir).mkdir(exist_ok=True)
    
    conn = get_database_connection(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT player_name, team, SUM(passes) as total_passes
        FROM player_stats
        WHERE passes > 0
        GROUP BY player_name, team
        ORDER BY total_passes DESC
        LIMIT 10
    """)
    
    data = cursor.fetchall()
    conn.close()
    
    if not data:
        print("No pass data available")
        return
    
    players = [f"{row[0]} ({row[1]})" for row in data]
    passes = [row[2] for row in data]
    
    plt.figure(figsize=(12, 6))
    bars = plt.bar(players, passes, color='#1976D2')
    plt.xlabel('Player', fontsize=12, fontweight='bold')
    plt.ylabel('Passes', fontsize=12, fontweight='bold')
    plt.title('Top Passers - Tournament Overall', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontweight='bold')
    
    plt.savefig(f"{output_dir}/tournament_top_passers.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: {output_dir}/tournament_top_passers.png")


def generate_player_steals_chart_per_match(db_path, match_id, match_label, output_dir="charts"):
    """Generate bar chart of players with most steals for a specific match"""
    Path(output_dir).mkdir(exist_ok=True)
    
    conn = get_database_connection(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT player_name, team, steals
        FROM player_stats
        WHERE match_id = ? AND steals > 0
        ORDER BY steals DESC
        LIMIT 10
    """, (match_id,))
    
    data = cursor.fetchall()
    conn.close()
    
    if not data:
        return
    
    players = [f"{row[0]} ({row[1]})" for row in data]
    steals = [row[2] for row in data]
    
    plt.figure(figsize=(12, 6))
    bars = plt.bar(players, steals, color='#D32F2F')
    plt.xlabel('Player', fontsize=12, fontweight='bold')
    plt.ylabel('Steals', fontsize=12, fontweight='bold')
    plt.title(f'Top Ball Winners - {match_label}', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontweight='bold')
    
    filename = f"{output_dir}/match_{match_id}_top_steals.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: {filename}")



def generate_player_steals_chart(db_path, output_dir="charts"):
    """Generate bar chart of players with most steals across ALL matches"""
    Path(output_dir).mkdir(exist_ok=True)
    
    conn = get_database_connection(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT player_name, team, SUM(steals) as total_steals
        FROM player_stats
        WHERE steals > 0
        GROUP BY player_name, team
        ORDER BY total_steals DESC
        LIMIT 10
    """)
    
    data = cursor.fetchall()
    conn.close()
    
    if not data:
        print("No steal data available")
        return
    
    players = [f"{row[0]} ({row[1]})" for row in data]
    steals = [row[2] for row in data]
    
    plt.figure(figsize=(12, 6))
    bars = plt.bar(players, steals, color='#D32F2F')
    plt.xlabel('Player', fontsize=12, fontweight='bold')
    plt.ylabel('Steals', fontsize=12, fontweight='bold')
    plt.title('Top Ball Winners - Tournament Overall', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontweight='bold')
    
    plt.savefig(f"{output_dir}/tournament_top_steal_winners.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: {output_dir}/tournament_top_steal_winners.png")


def generate_yellow_cards_chart_per_match(db_path, match_id, match_label, output_dir="charts"):
    """Generate bar chart of disciplinary records for a specific match"""
    Path(output_dir).mkdir(exist_ok=True)
    
    conn = get_database_connection(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT player_name, team, yellow_cards, expelled
        FROM player_stats
        WHERE match_id = ? AND (yellow_cards > 0 OR expelled > 0)
        ORDER BY yellow_cards DESC, expelled DESC
        LIMIT 10
    """, (match_id,))
    
    data = cursor.fetchall()
    conn.close()
    
    if not data:
        return
    
    players = [f"{row[0]} ({row[1]})" for row in data]
    yellows = [row[2] for row in data]
    expelled_flags = [row[3] for row in data]
    
    plt.figure(figsize=(12, 6))
    colors = ['#B71C1C' if expelled else '#FBC02D' for expelled in expelled_flags]
    bars = plt.bar(players, yellows, color=colors)
    plt.xlabel('Player', fontsize=12, fontweight='bold')
    plt.ylabel('Yellow Cards', fontsize=12, fontweight='bold')
    plt.title(f'Disciplinary Record - {match_label} (Red = Expelled)', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    for bar, expelled in zip(bars, expelled_flags):
        height = bar.get_height()
        label = f'{int(height)} 🟥' if expelled else f'{int(height)}'
        plt.text(bar.get_x() + bar.get_width()/2., height,
                label,
                ha='center', va='bottom', fontweight='bold')
    
    filename = f"{output_dir}/match_{match_id}_disciplinary.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: {filename}")



def generate_yellow_cards_chart(db_path, output_dir="charts"):
    """Generate bar chart of players with most yellow cards across ALL matches"""
    Path(output_dir).mkdir(exist_ok=True)
    
    conn = get_database_connection(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT player_name, team, SUM(yellow_cards) as total_yellows, SUM(expelled) as expelled
        FROM player_stats
        WHERE yellow_cards > 0 OR expelled > 0
        GROUP BY player_name, team
        ORDER BY total_yellows DESC, expelled DESC
        LIMIT 10
    """)
    
    data = cursor.fetchall()
    conn.close()
    
    if not data:
        print("No disciplinary data available")
        return
    
    players = [f"{row[0]} ({row[1]})" for row in data]
    yellows = [row[2] for row in data]
    expelled_flags = [row[3] for row in data]
    
    plt.figure(figsize=(12, 6))
    colors = ['#B71C1C' if expelled else '#FBC02D' for expelled in expelled_flags]
    bars = plt.bar(players, yellows, color=colors)
    plt.xlabel('Player', fontsize=12, fontweight='bold')
    plt.ylabel('Yellow Cards', fontsize=12, fontweight='bold')
    plt.title('Disciplinary Record - Tournament Overall (Red = Expelled)', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    for bar, expelled in zip(bars, expelled_flags):
        height = bar.get_height()
        label = f'{int(height)} 🟥' if expelled else f'{int(height)}'
        plt.text(bar.get_x() + bar.get_width()/2., height,
                label,
                ha='center', va='bottom', fontweight='bold')
    
    plt.savefig(f"{output_dir}/tournament_disciplinary_record.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: {output_dir}/tournament_disciplinary_record.png")


def generate_goalkeeper_saves_chart_per_match(db_path, match_id, match_label, output_dir="charts"):
    """Generate bar chart of goalkeeper saves for a specific match"""
    Path(output_dir).mkdir(exist_ok=True)
    
    conn = get_database_connection(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT player_name, team, saves
        FROM player_stats
        WHERE match_id = ? AND role = 'GK' AND saves > 0
        ORDER BY saves DESC
    """, (match_id,))
    
    data = cursor.fetchall()
    conn.close()
    
    if not data:
        return
    
    players = [f"{row[0]} ({row[1]})" for row in data]
    saves = [row[2] for row in data]
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(players, saves, color='#7B1FA2')
    plt.xlabel('Goalkeeper', fontsize=12, fontweight='bold')
    plt.ylabel('Saves', fontsize=12, fontweight='bold')
    plt.title(f'Goalkeeper Saves - {match_label}', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontweight='bold')
    
    filename = f"{output_dir}/match_{match_id}_goalkeeper_saves.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: {filename}")



def generate_goalkeeper_saves_chart(db_path, output_dir="charts"):
    """Generate bar chart of goalkeeper saves across ALL matches"""
    Path(output_dir).mkdir(exist_ok=True)
    
    conn = get_database_connection(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT player_name, team, SUM(saves) as total_saves
        FROM player_stats
        WHERE role = 'GK' AND saves > 0
        GROUP BY player_name, team
        ORDER BY total_saves DESC
    """)
    
    data = cursor.fetchall()
    conn.close()
    
    if not data:
        print("No goalkeeper save data available")
        return
    
    players = [f"{row[0]} ({row[1]})" for row in data]
    saves = [row[2] for row in data]
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(players, saves, color='#7B1FA2')
    plt.xlabel('Goalkeeper', fontsize=12, fontweight='bold')
    plt.ylabel('Saves', fontsize=12, fontweight='bold')
    plt.title('Goalkeeper Saves - Tournament Overall', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontweight='bold')
    
    plt.savefig(f"{output_dir}/tournament_goalkeeper_saves.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: {output_dir}/tournament_goalkeeper_saves.png")


def generate_fan_spending_chart_per_match(db_path, match_id, match_label, output_dir="charts"):
    """Generate bar chart of top fan spenders for a specific match"""
    Path(output_dir).mkdir(exist_ok=True)
    
    conn = get_database_connection(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT fan_name, total_spent
        FROM fan_stats
        WHERE match_id = ? AND total_spent > 0
        ORDER BY total_spent DESC
        LIMIT 10
    """, (match_id,))
    
    data = cursor.fetchall()
    conn.close()
    
    if not data:
        return
    
    fans = [row[0] for row in data]
    spending = [row[1] for row in data]
    
    plt.figure(figsize=(12, 6))
    bars = plt.bar(fans, spending, color='#F57C00')
    plt.xlabel('Fan', fontsize=12, fontweight='bold')
    plt.ylabel('Total Spending ($)', fontsize=12, fontweight='bold')
    plt.title(f'Top Fan Spenders - {match_label}', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'${height:.0f}',
                ha='center', va='bottom', fontweight='bold')
    
    filename = f"{output_dir}/match_{match_id}_top_spenders.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: {filename}")



def generate_fan_spending_chart(db_path, output_dir="charts"):
    """Generate bar chart of top fan spenders across ALL matches"""
    Path(output_dir).mkdir(exist_ok=True)
    
    conn = get_database_connection(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT fan_name, SUM(total_spent) as total_spending
        FROM fan_stats
        WHERE total_spent > 0
        GROUP BY fan_name
        ORDER BY total_spending DESC
        LIMIT 10
    """)
    
    data = cursor.fetchall()
    conn.close()
    
    if not data:
        print("No fan spending data available")
        return
    
    fans = [row[0] for row in data]
    spending = [row[1] for row in data]
    
    plt.figure(figsize=(12, 6))
    bars = plt.bar(fans, spending, color='#F57C00')
    plt.xlabel('Fan', fontsize=12, fontweight='bold')
    plt.ylabel('Total Spending ($)', fontsize=12, fontweight='bold')
    plt.title('Top Fan Spenders - Tournament Overall', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'${height:.0f}',
                ha='center', va='bottom', fontweight='bold')
    
    plt.savefig(f"{output_dir}/tournament_top_fan_spenders.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: {output_dir}/tournament_top_fan_spenders.png")


def generate_fan_purchases_by_item_chart_per_match(db_path, match_id, match_label, output_dir="charts"):
    """Generate bar chart of most purchased items for a specific match"""
    Path(output_dir).mkdir(exist_ok=True)
    
    conn = get_database_connection(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT item_name, COUNT(*) as purchase_count, SUM(price) as total_revenue
        FROM purchases
        WHERE match_id = ?
        GROUP BY item_name
        ORDER BY purchase_count DESC
        LIMIT 15
    """, (match_id,))
    
    data = cursor.fetchall()
    conn.close()
    
    if not data:
        return
    
    items = [row[0] for row in data]
    counts = [row[1] for row in data]
    
    plt.figure(figsize=(14, 6))
    bars = plt.bar(items, counts, color='#00897B')
    plt.xlabel('Item', fontsize=12, fontweight='bold')
    plt.ylabel('Purchases', fontsize=12, fontweight='bold')
    plt.title(f'Most Popular Items - {match_label}', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontweight='bold', fontsize=9)
    
    filename = f"{output_dir}/match_{match_id}_popular_items.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: {filename}")



def generate_fan_purchases_by_item_chart(db_path, output_dir="charts"):
    """Generate bar chart of most purchased items across ALL matches"""
    Path(output_dir).mkdir(exist_ok=True)
    
    conn = get_database_connection(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT item_name, COUNT(*) as purchase_count, SUM(price) as total_revenue
        FROM purchases
        GROUP BY item_name
        ORDER BY purchase_count DESC
        LIMIT 15
    """)
    
    data = cursor.fetchall()
    conn.close()
    
    if not data:
        print("No purchase data available")
        return
    
    items = [row[0] for row in data]
    counts = [row[1] for row in data]
    
    plt.figure(figsize=(14, 6))
    bars = plt.bar(items, counts, color='#00897B')
    plt.xlabel('Item', fontsize=12, fontweight='bold')
    plt.ylabel('Purchases', fontsize=12, fontweight='bold')
    plt.title('Most Popular Items - Tournament Overall', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontweight='bold', fontsize=9)
    
    plt.savefig(f"{output_dir}/tournament_most_popular_items.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: {output_dir}/tournament_most_popular_items.png")


def generate_shop_revenue_chart_per_match(db_path, match_id, match_label, output_dir="charts"):
    """Generate bar chart of shop revenue by type for a specific match"""
    Path(output_dir).mkdir(exist_ok=True)
    
    conn = get_database_connection(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT shop_type, SUM(price) as total_revenue, COUNT(*) as num_purchases
        FROM purchases
        WHERE match_id = ?
        GROUP BY shop_type
        ORDER BY total_revenue DESC
    """, (match_id,))
    
    data = cursor.fetchall()
    conn.close()
    
    if not data:
        return
    
    shop_types = [row[0].title() for row in data]
    revenue = [row[1] for row in data]
    
    plt.figure(figsize=(8, 6))
    bars = plt.bar(shop_types, revenue, color=['#FF6F00', '#0277BD'])
    plt.xlabel('Shop Type', fontsize=12, fontweight='bold')
    plt.ylabel('Revenue ($)', fontsize=12, fontweight='bold')
    plt.title(f'Revenue by Shop Type - {match_label}', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'${height:.0f}',
                ha='center', va='bottom', fontweight='bold', fontsize=11)
    
    filename = f"{output_dir}/match_{match_id}_shop_revenue.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: {filename}")



def generate_shop_revenue_chart(db_path, output_dir="charts"):
    """Generate bar chart of shop revenue by type across ALL matches"""
    Path(output_dir).mkdir(exist_ok=True)
    
    conn = get_database_connection(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT shop_type, SUM(price) as total_revenue, COUNT(*) as num_purchases
        FROM purchases
        GROUP BY shop_type
        ORDER BY total_revenue DESC
    """)
    
    data = cursor.fetchall()
    conn.close()
    
    if not data:
        print("No shop revenue data available")
        return
    
    shop_types = [row[0].title() for row in data]
    revenue = [row[1] for row in data]
    
    plt.figure(figsize=(8, 6))
    bars = plt.bar(shop_types, revenue, color=['#FF6F00', '#0277BD'])
    plt.xlabel('Shop Type', fontsize=12, fontweight='bold')
    plt.ylabel('Revenue ($)', fontsize=12, fontweight='bold')
    plt.title('Revenue by Shop Type - Tournament Overall', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'${height:.0f}',
                ha='center', va='bottom', fontweight='bold', fontsize=11)
    
    plt.savefig(f"{output_dir}/tournament_shop_revenue.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: {output_dir}/tournament_shop_revenue.png")


def generate_team_statistics_comparison_per_match(db_path, match_id, match_label, output_dir="charts"):
    """Generate grouped bar chart comparing team statistics for a specific match"""
    Path(output_dir).mkdir(exist_ok=True)
    
    conn = get_database_connection(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT team, 
               SUM(goals) as total_goals,
               SUM(shots) as total_shots,
               SUM(passes) as total_passes,
               SUM(steals) as total_steals
        FROM player_stats
        WHERE match_id = ?
        GROUP BY team
        ORDER BY total_goals DESC
    """, (match_id,))
    
    data = cursor.fetchall()
    conn.close()
    
    if not data or len(data) < 2:
        return
    
    teams = [row[0] for row in data]
    goals = [row[1] for row in data]
    shots = [row[2] for row in data]
    passes = [row[3] for row in data]
    steals = [row[4] for row in data]
    
    x = np.arange(len(teams))
    width = 0.2
    
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.bar(x - 1.5*width, goals, width, label='Goals', color='#2E7D32')
    ax.bar(x - 0.5*width, shots, width, label='Shots', color='#1976D2')
    ax.bar(x + 0.5*width, passes, width, label='Passes', color='#F57C00')
    ax.bar(x + 1.5*width, steals, width, label='Steals', color='#D32F2F')
    
    ax.set_xlabel('Team', fontsize=12, fontweight='bold')
    ax.set_ylabel('Count', fontsize=12, fontweight='bold')
    ax.set_title(f'Team Performance - {match_label}', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(teams)
    ax.legend()
    plt.tight_layout()
    
    filename = f"{output_dir}/match_{match_id}_team_stats.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: {filename}")



def generate_team_statistics_comparison(db_path, output_dir="charts"):
    """Generate grouped bar chart comparing team statistics across ALL matches"""
    Path(output_dir).mkdir(exist_ok=True)
    
    conn = get_database_connection(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT team, 
               SUM(goals) as total_goals,
               SUM(shots) as total_shots,
               SUM(passes) as total_passes,
               SUM(steals) as total_steals
        FROM player_stats
        GROUP BY team
        ORDER BY total_goals DESC
    """)
    
    data = cursor.fetchall()
    conn.close()
    
    if not data:
        print("No team statistics available")
        return
    
    teams = [row[0] for row in data]
    goals = [row[1] for row in data]
    shots = [row[2] for row in data]
    passes = [row[3] for row in data]
    steals = [row[4] for row in data]
    
    x = np.arange(len(teams))
    width = 0.2
    
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.bar(x - 1.5*width, goals, width, label='Goals', color='#2E7D32')
    ax.bar(x - 0.5*width, shots, width, label='Shots', color='#1976D2')
    ax.bar(x + 0.5*width, passes, width, label='Passes', color='#F57C00')
    ax.bar(x + 1.5*width, steals, width, label='Steals', color='#D32F2F')
    
    ax.set_xlabel('Team', fontsize=12, fontweight='bold')
    ax.set_ylabel('Count', fontsize=12, fontweight='bold')
    ax.set_title('Team Performance - Tournament Overall', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(teams)
    ax.legend()
    plt.tight_layout()
    
    plt.savefig(f"{output_dir}/tournament_team_statistics.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: {output_dir}/tournament_team_statistics.png")


def generate_match_summary_card(db_path, match_id, match_label, output_dir="charts"):
    """Generate a summary card for a specific match showing final score and key stats"""
    Path(output_dir).mkdir(exist_ok=True)
    
    conn = get_database_connection(db_path)
    cursor = conn.cursor()
    
    # Get match info
    cursor.execute("""
        SELECT team1, team2, score_team1, score_team2, winner, stadium_location
        FROM matches
        WHERE match_id = ?
    """, (match_id,))
    
    match_data = cursor.fetchone()
    if not match_data:
        conn.close()
        return
    
    team1, team2, score1, score2, winner, stadium = match_data
    
    # Get total revenue
    cursor.execute("""
        SELECT SUM(price) as total_revenue
        FROM purchases
        WHERE match_id = ?
    """, (match_id,))
    
    revenue_data = cursor.fetchone()
    total_revenue = revenue_data[0] if revenue_data[0] else 0
    
    conn.close()
    
    # Create the card
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis('off')
    
    # Title
    ax.text(0.5, 0.85, match_label, ha='center', fontsize=20, fontweight='bold')
    ax.text(0.5, 0.78, f'🏟️  {stadium}', ha='center', fontsize=14, style='italic')
    
    # Score display
    ax.text(0.5, 0.60, f'{team1}  {score1}  -  {score2}  {team2}', 
            ha='center', fontsize=18, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='lightblue', alpha=0.5))
    
    # Winner
    winner_text = f'🏆 Winner: {winner}' if winner != 'Draw' else '🤝 Match Ended in a Draw'
    ax.text(0.5, 0.45, winner_text, ha='center', fontsize=16, fontweight='bold', color='green')
    
    # Revenue
    ax.text(0.5, 0.30, f'💰 Total Revenue: ${total_revenue:.2f}', 
            ha='center', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    filename = f"{output_dir}/match_{match_id}_summary.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: {filename}")


def generate_all_match_visualizations(db_path, match_id, match_label, output_dir="charts"):
    """Generate all visualizations for a specific match"""
    print(f"\n📊 Generating visualizations for {match_label}...")
    
    generate_match_summary_card(db_path, match_id, match_label, output_dir)
    generate_player_goals_chart_per_match(db_path, match_id, match_label, output_dir)
    generate_player_passes_chart_per_match(db_path, match_id, match_label, output_dir)
    generate_player_steals_chart_per_match(db_path, match_id, match_label, output_dir)
    generate_yellow_cards_chart_per_match(db_path, match_id, match_label, output_dir)
    generate_goalkeeper_saves_chart_per_match(db_path, match_id, match_label, output_dir)
    generate_fan_spending_chart_per_match(db_path, match_id, match_label, output_dir)
    generate_fan_purchases_by_item_chart_per_match(db_path, match_id, match_label, output_dir)
    generate_shop_revenue_chart_per_match(db_path, match_id, match_label, output_dir)
    generate_team_statistics_comparison_per_match(db_path, match_id, match_label, output_dir)



def generate_all_visualizations(db_path, output_dir="charts"):
    """Generate all visualization charts - both per-match and tournament overall"""
    print("\n📊 Generating visualizations...")
    
    # Get all matches
    matches = get_all_matches(db_path)
    
    if not matches:
        print("No match data available")
        return
    
    # Generate per-match visualizations
    for match in matches:
        match_id, team1, team2, match_type, stadium = match
        match_label = f"{team1} vs {team2}"
        if match_type:
            match_label += f" ({match_type.title()})"
        
        generate_all_match_visualizations(db_path, match_id, match_label, output_dir)
    
    # Generate tournament-wide statistics
    print(f"\n📊 Generating tournament overall statistics...")
    generate_player_goals_chart(db_path, output_dir)
    generate_player_passes_chart(db_path, output_dir)
    generate_player_steals_chart(db_path, output_dir)
    generate_yellow_cards_chart(db_path, output_dir)
    generate_goalkeeper_saves_chart(db_path, output_dir)
    generate_fan_spending_chart(db_path, output_dir)
    generate_fan_purchases_by_item_chart(db_path, output_dir)
    generate_shop_revenue_chart(db_path, output_dir)
    generate_team_statistics_comparison(db_path, output_dir)
    
    print(f"\n✅ All visualizations saved to '{output_dir}/' directory")
    print(f"   - Generated {len(matches)} match-specific visualization sets")
    print(f"   - Generated tournament overall statistics")


if __name__ == "__main__":
    # Can be run standalone to regenerate charts
    import sys
    db_path = sys.argv[1] if len(sys.argv) > 1 else "champions_league_data.db"
    generate_all_visualizations(db_path)

