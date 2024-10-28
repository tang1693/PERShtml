import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd

# URL of the IngentaConnect page
url = "https://www.ingentaconnect.com/content/asprs/pers/2024/00000090/00000010"

# Request headers for simulating a browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

# Request the page content
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

# Check if page was fetched correctly
if response.status_code != 200:
    print("Failed to fetch the page")
else:
    print("Page fetched successfully")

# List to store article data
articles_data = []

# Locate all sections with a heading that contains "Articles" but exclude "In-Press Articles"
for section in soup.find_all('p', class_='heading'):
    heading_text = section.get_text(strip=True)
    if "Articles" in heading_text and heading_text != "In-Press Articles":
        print("Section heading found:")
        print(heading_text)
        
        # Iterate through siblings until the next heading is encountered
        for sibling in section.find_next_siblings():
            if sibling.name == "p" and "heading" in sibling.get("class", []):
                # Stop if we reach the next section heading
                break
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

                # Print current article data
                print("Current article data:")
                print({
                    'Title': title,
                    'Authors': authors,
                    'Pages': pages,
                    'Access': access_status,
                    'URL': article_url
                })

                # Append to the articles data list
                articles_data.append({
                    'Title': title,
                    'Authors': authors,
                    'Pages': pages,
                    'Access': access_status,
                    'URL': article_url
                })

# Print the entire list of articles
print("Entire list of articles:")
for article in articles_data:
    print(article)

# Convert to DataFrame to remove duplicates
df = pd.DataFrame(articles_data)
df.drop_duplicates(inplace=True)

# Write data to CSV without duplicates
csv_filename = 'filtered_articles_info.csv'
df.to_csv(csv_filename, index=False)

print(f"Data successfully saved to {csv_filename} without duplicates")
