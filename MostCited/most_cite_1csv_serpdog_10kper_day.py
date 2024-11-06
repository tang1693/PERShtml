import pandas as pd
import requests
import time

# Load the CSV file
csv_filename = 'filtered_articles_info.csv'
articles = pd.read_csv(csv_filename)

# Add a new column to store citation counts
articles['Citations'] = None

# Set your Serpdog API key
API_KEY = 'API_KEY'
BASE_URL = 'https://api.serpdog.io/scholar'

# Function to get citation count from Serpdog Google Scholar API
def get_citation_count(title):
    params = {
        'api_key': API_KEY,
        'q': title,
        'num': 1,  # Get only the top result
    }
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()

        # Check if there are scholar results
        if data.get('scholar_results'):
            first_result = data['scholar_results'][0]
            citation_info = first_result.get('inline_links', {}).get('cited_by', {})

            # Check if 'total' exists and is a numeric citation count
            citation_total = citation_info.get('total', "")
            if citation_total.startswith("Cited by"):
                return int(citation_total.replace("Cited by ", "").strip())
    except Exception as e:
        print(f"Error retrieving citation count for '{title}': {e}")
    
    # Return None if no citation count is found or if there's an error
    return None

# Process each title
for index, row in articles.iterrows():
    title = row['Title']
    print(f"Searching citation count for: {title}")

    # Retrieve the citation count
    citation_count = get_citation_count(title)
    articles.at[index, 'Citations'] = citation_count
    
    # Delay to respect API rate limits
    time.sleep(2)  # Adjust this delay based on your API rate limits

# Save updated data to a new CSV
updated_csv_filename = 'articles_with_citations.csv'
articles.to_csv(updated_csv_filename, index=False)

print(f"Citation counts successfully added and saved to {updated_csv_filename}")
