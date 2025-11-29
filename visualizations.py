"""
Visualization Module
Generates bar charts and other visualizations from Champions League match data
"""

import sqlite3
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path


def get_database_connection(db_path):
    """Get a connection to the SQLite database"""
    return sqlite3.connect(db_path)


def generate_player_goals_chart(db_path, output_dir="charts"):
    """Generate bar chart of top goal scorers"""
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
    plt.title('Top Goal Scorers', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontweight='bold')
    
    plt.savefig(f"{output_dir}/top_goal_scorers.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: {output_dir}/top_goal_scorers.png")


def generate_player_passes_chart(db_path, output_dir="charts"):
    """Generate bar chart of players with most passes"""
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
    plt.title('Top Passers', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontweight='bold')
    
    plt.savefig(f"{output_dir}/top_passers.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: {output_dir}/top_passers.png")


def generate_player_steals_chart(db_path, output_dir="charts"):
    """Generate bar chart of players with most steals"""
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
    plt.title('Top Ball Winners (Steals)', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontweight='bold')
    
    plt.savefig(f"{output_dir}/top_steal_winners.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: {output_dir}/top_steal_winners.png")


def generate_yellow_cards_chart(db_path, output_dir="charts"):
    """Generate bar chart of players with most yellow cards"""
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
    plt.title('Disciplinary Record (Red = Expelled)', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    for bar, expelled in zip(bars, expelled_flags):
        height = bar.get_height()
        label = f'{int(height)} 🟥' if expelled else f'{int(height)}'
        plt.text(bar.get_x() + bar.get_width()/2., height,
                label,
                ha='center', va='bottom', fontweight='bold')
    
    plt.savefig(f"{output_dir}/disciplinary_record.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: {output_dir}/disciplinary_record.png")


def generate_goalkeeper_saves_chart(db_path, output_dir="charts"):
    """Generate bar chart of goalkeeper saves"""
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
    plt.title('Goalkeeper Saves', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontweight='bold')
    
    plt.savefig(f"{output_dir}/goalkeeper_saves.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: {output_dir}/goalkeeper_saves.png")


def generate_fan_spending_chart(db_path, output_dir="charts"):
    """Generate bar chart of top fan spenders"""
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
    plt.title('Top Fan Spenders', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'${height:.0f}',
                ha='center', va='bottom', fontweight='bold')
    
    plt.savefig(f"{output_dir}/top_fan_spenders.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: {output_dir}/top_fan_spenders.png")


def generate_fan_purchases_by_item_chart(db_path, output_dir="charts"):
    """Generate bar chart of most purchased items"""
    Path(output_dir).mkdir(exist_ok=True)
    
    conn = get_database_connection(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT item_name, COUNT(*) as purchase_count, SUM(price) as total_revenue
        FROM purchases
        GROUP BY item_name
        ORDER BY purchase_count DESC
    """)
    
    data = cursor.fetchall()
    conn.close()
    
    if not data:
        print("No purchase data available")
        return
    
    items = [row[0] for row in data]
    counts = [row[1] for row in data]
    
    plt.figure(figsize=(12, 6))
    bars = plt.bar(items, counts, color='#00897B')
    plt.xlabel('Item', fontsize=12, fontweight='bold')
    plt.ylabel('Purchases', fontsize=12, fontweight='bold')
    plt.title('Most Popular Items', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontweight='bold')
    
    plt.savefig(f"{output_dir}/most_popular_items.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: {output_dir}/most_popular_items.png")


def generate_shop_revenue_chart(db_path, output_dir="charts"):
    """Generate bar chart of shop revenue by type"""
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
    plt.title('Revenue by Shop Type', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'${height:.0f}',
                ha='center', va='bottom', fontweight='bold', fontsize=11)
    
    plt.savefig(f"{output_dir}/shop_revenue.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: {output_dir}/shop_revenue.png")


def generate_team_statistics_comparison(db_path, output_dir="charts"):
    """Generate grouped bar chart comparing team statistics"""
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
    ax.set_title('Team Performance Comparison', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(teams)
    ax.legend()
    plt.tight_layout()
    
    plt.savefig(f"{output_dir}/team_statistics.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: {output_dir}/team_statistics.png")


def generate_match_results_chart(db_path, output_dir="charts"):
    """Generate chart showing match results"""
    Path(output_dir).mkdir(exist_ok=True)
    
    conn = get_database_connection(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT team1, team2, score_team1, score_team2, match_type
        FROM matches
        ORDER BY match_id
    """)
    
    data = cursor.fetchall()
    conn.close()
    
    if not data:
        print("No match data available")
        return
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    y_pos = np.arange(len(data))
    match_labels = [f"{row[0]} vs {row[1]}" for row in data]
    scores1 = [row[2] for row in data]
    scores2 = [row[3] for row in data]
    
    bars1 = ax.barh(y_pos, scores1, 0.4, label='Team 1', color='#1976D2', align='edge')
    bars2 = ax.barh(y_pos - 0.4, scores2, 0.4, label='Team 2', color='#D32F2F', align='edge')
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels(match_labels)
    ax.invert_yaxis()
    ax.set_xlabel('Goals', fontsize=12, fontweight='bold')
    ax.set_title('Match Results', fontsize=14, fontweight='bold')
    ax.legend()
    
    # Add score labels
    for i, (bar1, bar2) in enumerate(zip(bars1, bars2)):
        width1 = bar1.get_width()
        width2 = bar2.get_width()
        ax.text(width1 + 0.1, bar1.get_y() + bar1.get_height()/2,
                f'{int(width1)}', ha='left', va='center', fontweight='bold')
        ax.text(width2 + 0.1, bar2.get_y() + bar2.get_height()/2,
                f'{int(width2)}', ha='left', va='center', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/match_results.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Saved: {output_dir}/match_results.png")


def generate_all_visualizations(db_path, output_dir="charts"):
    """Generate all visualization charts"""
    print("\n📊 Generating visualizations...")
    
    generate_player_goals_chart(db_path, output_dir)
    generate_player_passes_chart(db_path, output_dir)
    generate_player_steals_chart(db_path, output_dir)
    generate_yellow_cards_chart(db_path, output_dir)
    generate_goalkeeper_saves_chart(db_path, output_dir)
    generate_fan_spending_chart(db_path, output_dir)
    generate_fan_purchases_by_item_chart(db_path, output_dir)
    generate_shop_revenue_chart(db_path, output_dir)
    generate_team_statistics_comparison(db_path, output_dir)
    generate_match_results_chart(db_path, output_dir)
    
    print(f"\n✅ All visualizations saved to '{output_dir}/' directory")


if __name__ == "__main__":
    # Can be run standalone to regenerate charts
    import sys
    db_path = sys.argv[1] if len(sys.argv) > 1 else "champions_league_data.db"
    generate_all_visualizations(db_path)
