import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
import os

# Base volume number; adjust if the pattern changes in future years
VOLUME_BASE_YEAR = 2023
VOLUME_BASE_NUMBER = 89  # Volume 89 corresponds to the year 2023

# CSV filename
csv_filename = 'ALL_articles_Update.csv'
log_filename = 'processed_urls.log'

# Generate URLs for the previous months
def generate_urls(how_many_months=24):
    urls = []
    today = datetime.today()
    for i in range(how_many_months):
        date = today - relativedelta(months=i)
        year = date.year
        month = date.month
        volume = VOLUME_BASE_NUMBER + (year - VOLUME_BASE_YEAR)
        issue_number = month
        volume_str = f"{volume:08d}"
        issue_str = f"{issue_number:08d}"
        url = f"https://www.ingentaconnect.com/content/asprs/pers/{year}/{volume_str}/{issue_str}"
        urls.append(url)
    return urls

# Fetch articles from a single URL and save data incrementally
def fetch_articles(url, headers):
    all_articles_data = []
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch the page at {url}")
        return all_articles_data

    soup = BeautifulSoup(response.content, 'html.parser')
    for section in soup.find_all('p', class_='heading'):
        heading_text = section.get_text(strip=True)
        # if "Articles" in heading_text and heading_text != "In-Press Articles": # only worked after 2015 march issue
        if ("Article" in heading_text or "Original" in heading_text or "Columns" in heading_text) and heading_text != "In-Press Articles": # worked for all issues

            for sibling in section.find_next_siblings():
                if sibling.name == "p" and "heading" in sibling.get("class", []):
                    break
                if sibling.name == "div" and "data" in sibling.get("class", []):
                    title_tag = sibling.find('strong')
                    title = title_tag.get_text(strip=True) if title_tag else 'N/A'

                    article_link_tag = sibling.find('a')
                    article_url = "https://www.ingentaconnect.com" + article_link_tag['href'] if article_link_tag else 'N/A'

                    abstract = 'N/A'
                    if article_url != 'N/A':
                        try:
                            article_response = requests.get(article_url, headers=headers)
                            if article_response.status_code == 200:
                                article_soup = BeautifulSoup(article_response.content, 'html.parser')
                                abstract_div = article_soup.find('div', id="Abst")
                                if abstract_div:
                                    abstract = abstract_div.get_text(strip=True).replace('\n', ' ').replace('\r', '').strip()
                        except Exception as e:
                            print(f"Failed to fetch abstract for {article_url}: {e}")

                    authors_tag = sibling.find('em')
                    authors = authors_tag.get_text(strip=True) if authors_tag else 'N/A'

                    page_info = None
                    for line in sibling.find_all('br'):
                        if line.next_sibling and "pp." in line.next_sibling:
                            page_info = line.next_sibling.strip()
                            break
                    pages = page_info if page_info else 'N/A'

                    access_icon = sibling.find('span', class_='access-icon')
                    if access_icon:
                        access_icon_img = access_icon.find('img')
                        access_status = access_icon_img['title'] if access_icon_img and 'title' in access_icon_img.attrs else 'N/A'
                    else:
                        access_status = 'N/A'

                    all_articles_data.append({
                        'Title': title,
                        'Authors': authors,
                        'Pages': pages,
                        'Access': access_status,
                        'URL': article_url,
                        'Abstract': abstract
                    })
    return all_articles_data

# Main function with live CSV updates and resume functionality
def fetch_to_csv(how_many_months=24):
    urls = generate_urls(how_many_months)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                    ' Chrome/58.0.3029.110 Safari/537.3'
    }

    processed_urls = set()
    if os.path.exists(log_filename):
        with open(log_filename, 'r') as log_file:
            processed_urls = set(log_file.read().splitlines())

    if not os.path.exists(csv_filename):
        pd.DataFrame(columns=['Title', 'Authors', 'Pages', 'Access', 'URL', 'Abstract']).to_csv(csv_filename, index=False)

    for url in urls:
        if url in processed_urls:
            print(f"Skipping already processed URL: {url}")
            continue

        print(f"Processing URL: {url}")
        articles_data = fetch_articles(url, headers)

        if articles_data:
            df = pd.DataFrame(articles_data, columns=['Title', 'Authors', 'Pages', 'Access', 'URL', 'Abstract'])
            df.drop_duplicates(inplace=True)
            df = df[~df['Title'].str.contains('mapping matters|gis tips', case=False, na=False)]
            df = df[df['Abstract'] != 'N/A']
            df = df[df['Authors'] != 'N/A']
            df = df[~df['Abstract'].str.contains('no abstract', case=False, na=False)]
            df.to_csv(csv_filename, mode='a', header=False, index=False)

        with open(log_filename, 'a') as log_file:
            log_file.write(url + '\n')

        print(f"Data from {url} has been saved.")

fetch_to_csv(266)
