import requests
from bs4 import BeautifulSoup
import csv

# Define the URL (testing)
# url = "https://www.ingentaconnect.com/content/title?j_type=online&j_startat=Af&j_endat=Aj&j_pagesize=20000&j_page=1&j_availability=all"  # Replace with the actual URL

url = "https://www.ingentaconnect.com/content/title?j_type=online&j_startat=Aa&j_endat=Z%5b&j_pagesize=20000&j_page=1&j_availability=all"  # Replace with the actual URL



# Send a GET request to the URL
response = requests.get(url)

# Parse the HTML content
soup = BeautifulSoup(response.content, "html.parser")

# Find the relevant HTML elements
journals = soup.find_all("li", class_="journalTitle")

# Open a CSV file to store the results
with open("journals_cleaned.csv", "w", newline="", encoding="utf-8") as csvfile:
    csvwriter = csv.writer(csvfile)
    # Write the header row
    csvwriter.writerow(["Journal Title", "Publisher Name", "Link to Journal"])
    
    # Iterate through the journalTitle elements
    for journal in journals:
        # Extract the journal title
        title = journal.find("a").text.replace("\n", " ").strip() if journal.find("a") else "N/A"
        # Extract the publisher name (next sibling element)
        publisher = journal.find_next("li", class_="publishername")
        publisher_text = publisher.text.replace("\n", " ").strip() if publisher else "N/A"
        # Extract the journal link
        link = journal.find("a")["href"].replace("\n", " ").strip() if journal.find("a") and "href" in journal.find("a").attrs else "N/A"
        
        # Write the cleaned data to the CSV
        csvwriter.writerow([title, publisher_text, link])

print("Data has been successfully cleaned and written to 'journals_cleaned.csv'.")
