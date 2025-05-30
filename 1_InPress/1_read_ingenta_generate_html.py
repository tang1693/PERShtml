from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import csv
import os
import time

# Set up Chrome options
options = Options()
options.add_argument("--headless")  # Run headless
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
# Set a custom cache directory to avoid permission warnings
options.add_argument(f"--user-data-dir={os.path.expanduser('~')}/.selenium_cache")

# Initialize the Chrome driver
driver = webdriver.Chrome(options=options)

try:
    # Open the ASPRS PERS page
    driver.get('https://www.ingentaconnect.com/content/asprs/pers')

    # Wait until the tab appears and click it
    wait = WebDriverWait(driver, 15)
    fast_track_tab = wait.until(EC.element_to_be_clickable((By.ID, "tab-fast")))
    fast_track_tab.click()

    # Wait for the fast track content to load
    wait.until(EC.presence_of_element_located((By.ID, "fasttrackItems")))
    time.sleep(2)  # slight extra wait to ensure all items loaded

    # Get page source after clicking
    html_content = driver.page_source

    # Parse with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    items = soup.select('ul#fasttrackItems li')

    extracted_data = []

    base_url = "https://www.ingentaconnect.com"

    for item in items:
        # Title and link
        a_tag = item.find('a')
        title = a_tag['title'].strip()
        link = base_url + a_tag['href'].strip()

        # Date
        date_text = ''
        date_br = a_tag.find_parent('p').find_all('br')
        if date_br:
            # Normally date appears after <br>
            date_parts = date_br[-1].next_sibling
            if date_parts:
                date_text = str(date_parts).replace('Appeared or available online:', '').strip()

        # Access status
        img_tag = item.find('img')
        access_status = img_tag['title'].strip() if img_tag else 'Unknown'

        extracted_data.append((title, date_text, link, access_status))

    # Remove duplicates
    unique_data = list({(title, date, link, status) for title, date, link, status in extracted_data})

    # Save to CSV
    output_csv = "InPress/fast_track_items.csv"
    with open(output_csv, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Title', 'Date', 'Link', 'Access Status'])
        for row in unique_data:
            writer.writerow(row)

    print(f"✅ Successfully saved {len(unique_data)} items to '{output_csv}'!")

finally:
    driver.quit()
