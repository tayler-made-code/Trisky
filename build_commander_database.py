import json
import os
from datetime import date
import re
from collections import defaultdict

def build_commander_database():
    # Load the bulk data
    with open('bulk_data/bulk_data.json', 'r') as file:
        data = json.load(file)

    # Load the scraped commander names
    with open('commander_names.txt', 'r', encoding='utf-8') as file:
        commander_names = [line.strip()[1:] for line in file if line.strip()]

    # Filter the cards based on the scraped commander names, exclude tokens
    commanders = [card for card in data if card['name'] in commander_names and 'token' not in card['layout'].lower()]

    # Check if commanders.json already exists
    if os.path.exists('commanders.json'):
        # Get current date
        current_date = date.today().strftime("%m_% d_%Y")
        # Rename existing file
        os.rename('commanders.json', f'commanders_retired_on_{current_date}.json')

    # Save the commander cards into a new JSON file
    with open('commanders.json', 'w') as outfile:
        json.dump(list(commanders), outfile, indent=4)

    print(f"Found {len(commanders)} commander cards.")

if __name__ == "__main__":
    build_commander_database()