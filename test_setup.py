#!/usr/bin/env python3
"""
Test script to verify data collection and visualization setup
"""

import os
import sys

def check_file_exists(filepath):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"✓ {filepath}")
        return True
    else:
        print(f"✗ {filepath} - NOT FOUND")
        return False

def check_imports():
    """Check if required modules can be imported"""
    print("\nChecking imports...")
    
    modules = [
        ('sqlite3', 'SQLite (built-in)'),
        ('matplotlib', 'Matplotlib'),
        ('numpy', 'NumPy'),
        ('tabulate', 'Tabulate')
    ]
    
    all_ok = True
    for module_name, display_name in modules:
        try:
            __import__(module_name)
            print(f"✓ {display_name}")
        except ImportError:
            print(f"✗ {display_name} - NOT INSTALLED")
            all_ok = False
    
    return all_ok

def main():
    print("=" * 60)
    print("Champions League Data Collection - Setup Check")
    print("=" * 60)
    
    print("\nChecking files...")
    files = [
        'ChampionsLeagueMatch.py',
        'player_class.py',
        'fan_class.py',
        'data_collector.py',
        'visualizations.py',
        'query_database.py',
        'players.py',
        'fans.py',
        'food_shops.py',
        'merch_shops.py',
        'anthems.py'
    ]
    
    files_ok = all(check_file_exists(f) for f in files)
    imports_ok = check_imports()
    
    print("\n" + "=" * 60)
    if files_ok and imports_ok:
        print("✅ All checks passed! Ready to run simulation.")
        print("\nTo run the simulation with data collection:")
        print("  python3 ChampionsLeagueMatch.py")
        print("\nTo view the database:")
        print("  python3 query_database.py")
    else:
        print("❌ Some checks failed. Please install missing packages:")
        print("  pip install matplotlib numpy tabulate")
    print("=" * 60)

if __name__ == "__main__":
    main()
