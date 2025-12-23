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
    
    
    # remove the issues articles:
    # =========================
    # NEW: Exclude already-issued articles (title fuzzy match)
    # =========================
    issued_csv = "6_IssuesArticles/ALL_articles_Update_cleaned.csv"

    from difflib import SequenceMatcher

    def clean_title(t: str) -> str:
        """Normalize titles for matching: remove extra quotes, collapse spaces, lowercase."""
        if not t:
            return ""
        t = t.strip()

        # remove surrounding double quotes if the whole field is quoted
        if len(t) >= 2 and t[0] == '"' and t[-1] == '"':
            t = t[1:-1].strip()

        # remove doubled quotes inside CSV-escaped text
        t = t.replace('""', '"')

        # remove any remaining raw double quotes
        t = t.replace('"', "")

        # collapse whitespace and lowercase
        t = " ".join(t.split()).lower()
        return t

    def similar(a: str, b: str) -> float:
        return SequenceMatcher(None, a, b).ratio()

    issued_titles = []
    if os.path.exists(issued_csv):
        with open(issued_csv, mode="r", encoding="utf-8", newline="") as f_issued:
            reader = csv.DictReader(f_issued)
            for r in reader:
                issued_titles.append(clean_title(r.get("Title", "")))

    issued_title_set = set(t for t in issued_titles if t)

    before_n = len(unique_data)
    kept = []
    removed = 0

    for (title, date, link, status) in unique_data:
        ct = clean_title(title)

        # drop empty titles after cleaning
        if not ct:
            removed += 1
            continue

        # fast exact match first
        if ct in issued_title_set:
            removed += 1
            continue

        # fuzzy match (90% or higher) against issued titles
        # this is O(N*M), but Fast Track is small so it's usually fine
        is_dup = False
        for it in issued_title_set:
            if similar(ct, it) >= 0.90:
                is_dup = True
                break

        if is_dup:
            removed += 1
            continue

        # store the cleaned title back (optional but recommended)
        kept.append((title.replace('""', '"').replace('"', '').strip(), date, link, status))

    unique_data = kept
    print(f"🧹 Removed {removed} already-issued (exact or >=0.90 title match) or empty-title items.")

    
    
    
    
    

    # # Save to CSV
    # output_csv = "1_InPress/fast_track_items.csv"
    # with open(output_csv, mode='w', newline='', encoding='utf-8') as f:
    #     writer = csv.writer(f)
    #     writer.writerow(['Title', 'Date', 'Link', 'Access Status'])
    #     for row in unique_data:
    #         writer.writerow(row)
    # Save to CSV
    os.makedirs("1_InPress", exist_ok=True)

    # Clear downstream cached outputs so removed Fast Track items don't linger
    for fp in [
        "1_InPress/processed_urls.log",
        "1_InPress/filtered_InPress_articles_info_abs.csv",
    ]:
        if os.path.exists(fp):
            os.remove(fp)

    output_csv = "1_InPress/fast_track_items.csv"
    with open(output_csv, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Title', 'Date', 'Link', 'Access Status'])
        for row in unique_data:
            writer.writerow(row)


    print(f"✅ Successfully saved {len(unique_data)} items to '{output_csv}'!")

finally:
    driver.quit()
