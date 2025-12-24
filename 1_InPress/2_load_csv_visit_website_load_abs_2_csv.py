import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
import time
import re

# Input and output file names
input_csv = '1_InPress/fast_track_items.csv'
log_filename = '1_InPress/processed_urls.log'
output_csv = '1_InPress/filtered_InPress_articles_info_abs.csv'

# Setup headers for requests
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
}

def fetch_articles(url, headers):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # --- Extract Authors ---
        authors = 'N/A'
        authors_strong = soup.find('strong', string=lambda text: text and 'Authors:' in text)
        if authors_strong:
            authors_parent_p = authors_strong.find_parent('p')
            if authors_parent_p:
                # 1. Get all text from <a> tags (names and numbers are often separated)
                author_links = authors_parent_p.find_all('a')
                raw_authors_str = '; '.join(a.get_text(strip=True) for a in author_links)
                
                # 2. Use regex to remove standalone numbers (affiliations)
                # This looks for digits that are either alone or surrounded by semicolons/spaces
                clean_step1 = re.sub(r'\b\d+\b', '', raw_authors_str)
                
                # 3. Clean up the resulting semicolons and whitespace
                # Split by semicolon, strip whitespace, and filter out empty strings
                names_list = [n.strip() for n in clean_step1.split(';') if n.strip()]
                authors = '; '.join(names_list)

        # --- Extract Abstract ---
        abstract = 'N/A'
        abstract_div = soup.find('div', id='Abst')
        if abstract_div:
            abstract = abstract_div.get_text(strip=True)
        
        return authors, abstract

    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return 'N/A', 'N/A'

# --- Main Processing Logic ---

# Read the input CSV
df_input = pd.read_csv(input_csv)

# Prepare log of already processed URLs
processed_urls = set()
if os.path.exists(log_filename):
    with open(log_filename, 'r') as log_file:
        processed_urls = set(log_file.read().splitlines())

# Prepare output CSV
if not os.path.exists(output_csv):
    pd.DataFrame(columns=['Title', 'Authors', 'Pages', 'Access', 'URL', 'Abstract']).to_csv(output_csv, index=False)

# Process each URL
for idx, row in df_input.iterrows():
    url = row['Link']

    if url in processed_urls:
        print(f"Skipping already processed URL: {url}")
        continue

    print(f"Processing URL: {url}")

    authors, abstract = fetch_articles(url, headers)

    # Use 'Date' as 'Pages'
    new_row = pd.DataFrame([{
        'Title': row['Title'],
        'Authors': authors,
        'Pages': row['Date'],
        'Access': row['Access Status'],
        'URL': url,
        'Abstract': abstract
    }])

    # Check if the output CSV already exists and whether it's empty
    write_header = not os.path.exists(output_csv) or os.path.getsize(output_csv) == 0

    # Append the new row
    new_row.to_csv(output_csv, mode='a', header=write_header, index=False)

    # Log this URL as processed
    with open(log_filename, 'a') as log_file:
        log_file.write(url + '\n')

    time.sleep(1)  # Be polite to the server

print("✅ All articles processed and saved with cleaned author names!")