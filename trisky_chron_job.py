import os
import json
import requests
from datetime import date
import scrape_scryfall
import build_commander_database
import build_all_database

def download_bulk_data():
    print("Downloading bulk data from Scryfall...")
    api_url = "https://api.scryfall.com/bulk-data/oracle-cards"
    
    try:
        # Get the download URL from the API
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        download_url = data['download_uri']
        
        # Download the bulk data
        response = requests.get(download_url)
        response.raise_for_status()
        
        # Check if there's an existing bulk_data.json file
        bulk_data_path = './bulk_data/bulk_data.json'
        if os.path.exists(bulk_data_path):
            # Rename the existing file to retired_bulk_data.json
            backup_data = './bulk_data/backup_data.json'
            os.rename(bulk_data_path, backup_data)
            print(f"Renamed existing bulk data to {backup_data}")
        
        # Save the new bulk data
        with open(bulk_data_path, 'w', encoding='utf-8') as f:
            json.dump(response.json(), f)
        print(f"New bulk data downloaded and saved to {bulk_data_path}")
    
    except requests.RequestException as e:
        print(f"Failed to download bulk data: {e}")

def update_databases():
    print("Routine Database Updates Starting...")
    
    # Step 1: Download new bulk data
    download_bulk_data()
    
    # Step 2: Scrape the website for the commander list
    print("Scraping Scryfall for commander list...")
    scraped_commander_list, scraped_total_pages = scrape_scryfall.main()
    
    print(f"Scraped {len(scraped_commander_list)} commanders from {scraped_total_pages} pages.")
    
    # Step 3: Rebuild the database with scraped data
    print("Rebuilding commander database with scraped data...")
    build_commander_database.build_commander_database()
    
    # Step 4: Rebuild the all cards database
    print("Rebuilding all cards database...")
    build_all_database.build_all_database()

    print("Routine Database Updates Completed.")

if __name__ == "__main__":
    update_databases()