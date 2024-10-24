import json
import os
from datetime import date
import re
import psycopg2
from psycopg2.extras import execute_batch
from db_config import DB_CONFIG

def load_banned_cards():
    with open('banned_cards.txt', 'r', encoding='utf-8') as file:
        return set(line.strip()[1:] for line in file if line.strip())

def create_database_if_not_exists(db_config):
    # Connect to the default 'postgres' database
    conn = psycopg2.connect(
        host=db_config['host'],
        user=db_config['user'],
        password=db_config['password'],
        database='postgres'
    )
    conn.autocommit = True
    cursor = conn.cursor()

    # Check if the database exists
    cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{db_config['database']}'")
    exists = cursor.fetchone()
    
    if not exists:
        print(f"Database '{db_config['database']}' does not exist. Creating it now...")
        cursor.execute(f"CREATE DATABASE {db_config['database']}")
        print(f"Database '{db_config['database']}' created successfully.")
    else:
        print(f"Database '{db_config['database']}' already exists.")

    cursor.close()
    conn.close()

def is_valid_card(card, banned_cards):
    # Add new invalid layouts here
    invalid_layouts = ['art_series']

    # Skip if card is an invalid layout
    if card['layout'].lower() in invalid_layouts:
        return False

    # Check if card is in banned list
    if card['name'] in banned_cards:
        return False
    
    return True

def build_consolidated_database():
    # First, ensure the database exists
    create_database_if_not_exists(DB_CONFIG)

    # Load the banned cards
    banned_cards = load_banned_cards()

    # Load the bulk data
    with open('bulk_data/bulk_data.json', 'r') as file:
        data = json.load(file)

    # Load the scraped commander names
    with open('commander_names.txt', 'r', encoding='utf-8') as file:
        commander_names = set(line.strip()[1:] for line in file if line.strip())

    all_cards = []
    commander_count = 0
    for card in data:
        if is_valid_card(card, banned_cards):
            # Add the Commanderable flag
            card['commanderable'] = card['name'] in commander_names and 'token' not in card['layout'].lower()
            if card['commanderable']:
                commander_count += 1
            all_cards.append(card)

    print(f"Processed {len(all_cards)} total cards.")
    print(f"Found {commander_count} commanders.")
    
    if commander_count < 2278:
        print(f"Warning: Expected 2278 commanders but found {commander_count}")
        print(f"Missing {2278 - commander_count} commanders")

    # Connect to the database
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Create the cards table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cards (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            color_identity VARCHAR(255),
            colors VARCHAR(50),
            mana_cost VARCHAR(255),
            mana_value INT,
            type_line TEXT,
            oracle_text TEXT,
            power VARCHAR(10),
            toughness VARCHAR(10),
            rarity VARCHAR(50),
            set_code VARCHAR(10),
            collector_number VARCHAR(20),
            image_uris JSON,
            legalities JSON,
            commanderable BOOLEAN
        )
    """)

    # Prepare the insert query
    insert_query = """
        INSERT INTO cards (name, color_identity, colors, mana_cost, mana_value, type_line, 
                           oracle_text, power, toughness, rarity, set_code, collector_number, 
                           image_uris, legalities, commanderable)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    # Prepare the data for batch insert
    card_data = [
        (
            card['name'],
            ','.join(card.get('color_identity', [])),
            ','.join(card.get('colors', [])),
            card.get('mana_cost', ''),
            card.get('cmc', 0),
            card.get('type_line', ''),
            card.get('oracle_text', ''),
            card.get('power', ''),
            card.get('toughness', ''),
            card.get('rarity', ''),
            card.get('set', ''),
            card.get('collector_number', ''),
            json.dumps(card.get('image_uris', {})),
            json.dumps(card.get('legalities', {})),
            card['commanderable']
        )
        for card in all_cards
    ]

    # Perform the batch insert
    execute_batch(cursor, insert_query, card_data)

    # Commit the changes and close the connection
    conn.commit()
    cursor.close()
    conn.close()

    print("Data successfully loaded into the database.")

if __name__ == "__main__":
    build_consolidated_database()