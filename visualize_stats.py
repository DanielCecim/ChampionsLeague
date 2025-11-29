import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
import os

DB_NAME = "champions_league.db"

def get_data():
    if not os.path.exists(DB_NAME):
        print(f"Database {DB_NAME} not found.")
        return None, None

    conn = sqlite3.connect(DB_NAME)
    
    # Match Events
    events_df = pd.read_sql_query("SELECT * FROM match_events", conn)
    
    # Store Sales
    sales_df = pd.read_sql_query("SELECT * FROM store_sales", conn)
    
    conn.close()
    return events_df, sales_df

def plot_match_stats(events_df):
    if events_df.empty:
        print("No match events found.")
        return

    # Count events by type and team
    event_counts = events_df.groupby(['team_name', 'event_type']).size().unstack(fill_value=0)
    
    if event_counts.empty:
        print("No events to plot.")
        return

    # Plot
    event_counts.plot(kind='bar', stacked=True, figsize=(10, 6))
    plt.title('Match Events by Team')
    plt.xlabel('Team')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('match_events.png')
    print("Saved match_events.png")

def plot_sales_stats(sales_df):
    if sales_df.empty:
        print("No sales data found.")
        return

    # Revenue by Item
    item_revenue = sales_df.groupby('item_name')['price'].sum().sort_values(ascending=False)
    
    plt.figure(figsize=(10, 6))
    item_revenue.plot(kind='bar', color='green')
    plt.title('Revenue by Product')
    plt.xlabel('Product')
    plt.ylabel('Revenue ($)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('store_revenue.png')
    print("Saved store_revenue.png")

    # Sales count by Item
    item_counts = sales_df['item_name'].value_counts()
    plt.figure(figsize=(10, 6))
    item_counts.plot(kind='bar', color='orange')
    plt.title('Sales Count by Product')
    plt.xlabel('Product')
    plt.ylabel('Number of Sales')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('store_sales_count.png')
    print("Saved store_sales_count.png")

if __name__ == "__main__":
    events, sales = get_data()
    if events is not None:
        print(f"Loaded {len(events)} match events.")
        plot_match_stats(events)
    
    if sales is not None:
        print(f"Loaded {len(sales)} sales records.")
        plot_sales_stats(sales)
