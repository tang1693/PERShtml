import requests
from bs4 import BeautifulSoup
import csv

# Input and output file paths
input_file = "journals_cleaned.csv"  # The CSV containing Journal Title, Publisher Name, and Link to Journal
output_file = "journals_cleaned_with_issn_and_latest_issue.csv"

# Function to scrape ISSNs and the latest issue from a given URL
def scrape_journal_details(url):
    try:
        # Send a GET request to the URL
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise HTTPError for bad responses
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Extract the Print ISSN
        print_issn_element = soup.find("a", class_="issnDevicestyle", text=lambda x: x and "-" in x)
        print_issn = print_issn_element.text.replace("-", "").strip() if print_issn_element else "N/A"
        
        # Extract the Online ISSN
        online_issn_element = soup.find("a", class_="issnDevicestyle", text=lambda x: x and "-" in x and "(Online)" in soup.text)
        online_issn = online_issn_element.text.replace("-", "").strip() if online_issn_element else "N/A"
        
        # Extract the latest issue
        latest_issue_element = soup.find("a", title=lambda t: t and "Number" in t)
        latest_issue = latest_issue_element["title"].strip() if latest_issue_element else "N/A"
        
        return print_issn, online_issn, latest_issue
    except Exception as e:
        print(f"Error fetching data for URL: {url} - {e}")
        return "Error", "Error", "Error"

# Load already processed journal links from the output file
processed_links = set()
try:
    with open(output_file, "r", encoding="utf-8") as outfile:
        reader = csv.DictReader(outfile)
        for row in reader:
            processed_links.add(row["Link to Journal"])
except FileNotFoundError:
    print(f"Output file '{output_file}' does not exist. A new file will be created.")

# Check if output file already exists and create/write headers only if it's new
try:
    with open(output_file, "x", newline="", encoding="utf-8") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=[
            "Journal Title", "Publisher Name", "Link to Journal", 
            "Print ISSN", "Online ISSN", "Latest Issue"
        ])
        writer.writeheader()  # Write header only once if the file is newly created
except FileExistsError:
    pass  # File exists, no need to rewrite headers

# Open input file and process rows
with open(input_file, "r", encoding="utf-8") as infile:
    reader = csv.DictReader(infile)
    
    for row in reader:
        # Extract details from the current row
        journal_title = row.get("Journal Title", "N/A")
        publisher_name = row.get("Publisher Name", "N/A")
        journal_link = row.get("Link to Journal")
        
        # Skip already processed links
        if journal_link in processed_links:
            print(f"Skipping already processed journal: {journal_title} ({journal_link})")
            continue

        print(f"Processing: {journal_title} ({journal_link})")
        
        if journal_link:
            # Scrape ISSNs and latest issue
            print_issn, online_issn, latest_issue = scrape_journal_details("https://www.ingentaconnect.com/" + journal_link)
            # Prepare the row for output
            output_row = {
                "Journal Title": journal_title,
                "Publisher Name": publisher_name,
                "Link to Journal": journal_link,
                "Print ISSN": print_issn,
                "Online ISSN": online_issn,
                "Latest Issue": latest_issue,
            }
        else:
            output_row = {
                "Journal Title": journal_title,
                "Publisher Name": publisher_name,
                "Link to Journal": journal_link,
                "Print ISSN": "N/A",
                "Online ISSN": "N/A",
                "Latest Issue": "N/A",
            }
        
        # Write the processed row to the output file incrementally
        with open(output_file, "a", newline="", encoding="utf-8") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=[
                "Journal Title", "Publisher Name", "Link to Journal", 
                "Print ISSN", "Online ISSN", "Latest Issue"
            ])
            writer.writerow(output_row)
            processed_links.add(journal_link)  # Add to processed set

print(f"Data has been successfully processed and saved to '{output_file}'.")
