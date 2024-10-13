import requests
from bs4 import BeautifulSoup
import time

def get_page_content(url):
    # Send a GET request to the URL
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return None

def extract_commander_names(html_content):
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all span elements with the class 'card-grid-item-invisible-label'
    name_elements = soup.find_all('span', class_='card-grid-item-invisible-label')
    
    commander_names = []
    for element in name_elements:
        # Extract the text content of the span element
        name = element.text.strip()
        if name:
            commander_names.append(name)
    
    return commander_names

def get_next_page_url(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    # Find all 'a' tags with class 'button-n'
    button_n_tags = soup.find_all('a', class_='button-n')
    
    # Iterate through these tags to find the one with 'Next 60'
    for button in button_n_tags:
        if button.find('b', string='Next 60'):
            return 'https://scryfall.com' + button['href']
    
    # If we don't find a 'Next 60' button, return None
    return None

def scrape_commanders():
    base_url = "https://scryfall.com/search?q=f%3Aedh+is%3Acommander&order=name&as=grid"
    current_url = base_url
    all_commanders = []
    page_count = 0

    while current_url:
        page_count += 1
        # print(f"Scraping page {page_count}...")
        
        html_content = get_page_content(current_url)
        if html_content:
            commanders = extract_commander_names(html_content)
            all_commanders.extend(commanders)
            
            current_url = get_next_page_url(html_content)
            if current_url:
                time.sleep(1)  # Be nice to the server, wait 1 second between requests
        else:
            break

    return all_commanders, page_count

def main():
    # Run the Scraper
    commander_list, total_pages = scrape_commanders()

    # print(f"Total pages found: {total_pages}")
    # print(f"Total commanders found: {len(commander_list)}")

    # Write the results to a file
    with open('commander_names.txt', 'w', encoding='utf-8') as file:
        for commander in commander_list:
            file.write(f"-{commander}\n")

    # print("Commander names have been written to 'commander_names.txt'")
    
    return commander_list, total_pages

if __name__ == "__main__":
    main()