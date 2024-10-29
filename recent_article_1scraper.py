import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd

# List of URLs to be processed
urls = [
    "https://www.ingentaconnect.com/content/asprs/pers/2024/00000090/00000010",
    "https://www.ingentaconnect.com/content/asprs/pers/2024/00000090/00000009",
    "https://www.ingentaconnect.com/content/asprs/pers/2024/00000090/00000008",
    "https://www.ingentaconnect.com/content/asprs/pers/2024/00000090/00000007",
    "https://www.ingentaconnect.com/content/asprs/pers/2024/00000090/00000006",
    "https://www.ingentaconnect.com/content/asprs/pers/2024/00000090/00000005",
    "https://www.ingentaconnect.com/content/asprs/pers/2024/00000090/00000004",
    "https://www.ingentaconnect.com/content/asprs/pers/2024/00000090/00000003",
    "https://www.ingentaconnect.com/content/asprs/pers/2024/00000090/00000002",
    "https://www.ingentaconnect.com/content/asprs/pers/2024/00000090/00000001",
    "https://www.ingentaconnect.com/content/asprs/pers/2023/00000089/00000012",
    "https://www.ingentaconnect.com/content/asprs/pers/2023/00000089/00000011",
    "https://www.ingentaconnect.com/content/asprs/pers/2023/00000089/00000010",
    "https://www.ingentaconnect.com/content/asprs/pers/2023/00000089/00000009",
    "https://www.ingentaconnect.com/content/asprs/pers/2023/00000089/00000008",
    "https://www.ingentaconnect.com/content/asprs/pers/2023/00000089/00000007",
    "https://www.ingentaconnect.com/content/asprs/pers/2023/00000089/00000006",
    "https://www.ingentaconnect.com/content/asprs/pers/2023/00000089/00000005",
    "https://www.ingentaconnect.com/content/asprs/pers/2023/00000089/00000004",
    "https://www.ingentaconnect.com/content/asprs/pers/2023/00000089/00000003",
    "https://www.ingentaconnect.com/content/asprs/pers/2023/00000089/00000002",
    "https://www.ingentaconnect.com/content/asprs/pers/2023/00000089/00000001"
    # Add more URLs here
    # "https://www.ingentaconnect.com/content/asprs/pers/2024/00000090/00000011",
    # "https://www.ingentaconnect.com/content/asprs/pers/2024/00000090/00000012",
    # ...
]

# Request headers for simulating a browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# List to store all articles data across URLs
all_articles_data = []

# Iterate over each URL
for url in urls:
    # Request the page content
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Check if page was fetched correctly
    if response.status_code != 200:
        print(f"Failed to fetch the page at {url}")
        continue  # Skip this URL if it failed to fetch

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

                    # Extract URL
                    article_link_tag = sibling.find('a')
                    article_url = "https://www.ingentaconnect.com" + article_link_tag['href'] if article_link_tag else 'N/A'

                    # Extract access status using the title attribute of the <img> inside the access icon
                    access_icon_img = sibling.find('span', class_='access-icon').find('img')
                    access_status = access_icon_img['title'] if access_icon_img and 'title' in access_icon_img.attrs else 'N/A'

                    # Append to the all articles data list
                    all_articles_data.append({
                        'Title': title,
                        'Authors': authors,
                        'Pages': pages,
                        'Access': access_status,
                        'URL': article_url
                    })

# Convert to DataFrame to remove duplicates
df = pd.DataFrame(all_articles_data)
df.drop_duplicates(inplace=True)

# Write data to CSV without duplicates
csv_filename = 'filtered_articles_info.csv'
df.to_csv(csv_filename, index=False)

print(f"Data successfully saved to {csv_filename} without duplicates")
