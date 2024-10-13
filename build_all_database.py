import json
import os
from datetime import date
import re
from collections import defaultdict

# Function to extract numeric part of collector number
def extract_number(collector_number):
    return int(re.search(r'\d+', collector_number).group())

def build_all_database():
    # Load the bulk data
    with open('bulk_data/bulk_data.json', 'r') as file:
        data = json.load(file)

    all_cards = [card for card in data if 'token' not in card['layout'].lower() and 'emblem' not in card['layout'].lower() and 'art_series' not in card['layout'].lower()]

    # Check if all_cards.json already exists
    if os.path.exists('all_cards.json'):
        # Get current date
        current_date = date.today().strftime("%m_%d_%Y")
        # Rename existing file
        os.rename('all_cards.json', f'all_cards_retired_on_{current_date}.json')

    # Save the unique cards into a new JSON file
    with open('all_cards.json', 'w') as outfile:
        json.dump(list(all_cards), outfile, indent=4)

if __name__ == "__main__":
    build_all_database()