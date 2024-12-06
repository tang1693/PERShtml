import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

# return df
def fetch_to_csv(how_many_months=25):
    # Base volume number; adjust if the pattern changes in future years
    VOLUME_BASE_YEAR = 2023
    VOLUME_BASE_NUMBER = 89  # Volume 89 corresponds to the year 2023

    # Generate URLs for the previous 25 months
    urls = []

    today = datetime.today()
    # Uncomment the following line to fix the date for testing purposes
    # today = datetime(2024, 11, 6)

    for i in range(how_many_months):
        date = today - relativedelta(months=i)
        year = date.year
        month = date.month
        volume = VOLUME_BASE_NUMBER + (year - VOLUME_BASE_YEAR)
        issue_number = month

        volume_str = f"{volume:08d}"
        issue_str = f"{issue_number:08d}"

        url = f"https://www.ingentaconnect.com/content/asprs/pers/{year}/{volume_str}/{issue_str}"
        print(url)
        urls.append(url)

    # Request headers for simulating a browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                    ' Chrome/58.0.3029.110 Safari/537.3'
    }

    # List to store all articles data across URLs
    all_articles_data = []

    # Iterate over each URL
    for url in urls:
        # Request the page content
        response = requests.get(url, headers=headers)
    
        # Check if page was fetched correctly
        if response.status_code != 200:
            print(f"Failed to fetch the page at {url}")
            continue  # Skip this URL if it failed to fetch

        soup = BeautifulSoup(response.content, 'html.parser')

        # Locate all sections with a heading that contains "Articles" but exclude "In-Press Articles"
        for section in soup.find_all('p', class_='heading'):
            heading_text = section.get_text(strip=True)
            if "Articles" in heading_text and heading_text != "In-Press Articles":
                # Iterate through siblings until the next heading is encountered
                for sibling in section.find_next_siblings():
                    if sibling.name == "p" and "heading" in sibling.get("class", []):
                        break  # Stop if we reach the next section heading
                    if sibling.name == "div" and "data" in sibling.get("class", []):
                        # Process each relevant article entry with class "data"

                        # Extract title
                        title_tag = sibling.find('strong')
                        title = title_tag.get_text(strip=True) if title_tag else 'N/A'
                        
                        # Extract URL
                        article_link_tag = sibling.find('a')
                        article_url = "https://www.ingentaconnect.com" + article_link_tag['href'] if article_link_tag else 'N/A'
                        
                        # Extract Abstract by visiting the article URL
                        abstract = 'N/A'  # Default value in case of failure
                        if article_url != 'N/A':
                            print(f"Fetching abstract for {article_url}")
                            try:
                                article_response = requests.get(article_url, headers=headers)
                                if article_response.status_code == 200:
                                    article_soup = BeautifulSoup(article_response.content, 'html.parser')

                                    # Locate the abstract section (adjust selector based on the actual HTML structure)
                                    abstract_div = article_soup.find('div', id="Abst")  
                                    if abstract_div:
                                        abstract = abstract_div.get_text(strip=True).replace('\n', ' ').replace('\r', '').strip()
                            except Exception as e:
                                print(f"Failed to fetch abstract for {article_url}: {e}")

                        # Extract authors
                        authors_tag = sibling.find('em')
                        authors = authors_tag.get_text(strip=True) if authors_tag else 'N/A'

                        # Extract page number, specifically the text with "pp."
                        page_info = None
                        for line in sibling.find_all('br'):
                            if line.next_sibling and "pp." in line.next_sibling:
                                page_info = line.next_sibling.strip()
                                break
                        pages = page_info if page_info else 'N/A'


                        # Extract access status using the title attribute of the <img> inside the access icon
                        access_icon = sibling.find('span', class_='access-icon')
                        if access_icon:
                            access_icon_img = access_icon.find('img')
                            access_status = access_icon_img['title'] if access_icon_img and 'title' in access_icon_img.attrs else 'N/A'
                        else:
                            access_status = 'N/A'

                        # Append to the all articles data list
                        all_articles_data.append({
                            'Title': title,
                            'Authors': authors,
                            'Pages': pages,
                            'Access': access_status,
                            'URL': article_url,
                            'Abstract': abstract  
                        })

    # Convert to DataFrame to remove duplicates
    # df = pd.DataFrame(all_articles_data)
    df = pd.DataFrame(all_articles_data, columns=['Title', 'Authors', 'Pages', 'Access', 'URL', 'Abstract'])
    return df


df = fetch_to_csv()

# load csv file to df
df = pd.read_csv('filtered_articles_info_abs.csv')

# drop duplicates
df.drop_duplicates(inplace=True)
# drop if title is has contain "mapping matters" and "Gis tips", case insensitive
df = df[~df['Title'].str.contains('mapping matters|gis tips', case=False)]
# drop if abstract is N/A
df = df[df['Abstract'] != 'N/A']
# drop if authors is N/A
df = df[df['Authors'] != 'N/A']
# drop if abstract contains "no abstract"
df = df[~df['Abstract'].str.contains('no abstract', case=False)]

# Write data to CSV without duplicates
csv_filename = 'filtered_articles_info_abs.csv'
df.to_csv(csv_filename, index=False)

print(f"Data successfully saved to {csv_filename} without duplicates")
