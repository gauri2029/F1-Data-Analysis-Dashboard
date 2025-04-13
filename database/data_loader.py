import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from database.db_setup import init_db
from services.f1_data_service import load_season_data

def main():
    """Initializing the database and loading F1 data in this function"""
    print("Initializing the database...")
    init_db()
    
    # Loading the data for seasons  2023 and 2024 seasons
    seasons = [2023, 2024]
    for year in seasons:
        print(f"Loading data for {year} F1 season...")
        load_season_data(year) # Loading for specific season
        print(f"Completed loading data for {year} F1 season.")
    print("Database loading complete!")

if __name__ == "__main__":
    main()