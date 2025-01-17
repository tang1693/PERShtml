import pandas as pd
import os
import re
import unicodedata
from rapidfuzz import fuzz, process  # Faster alternative to fuzzywuzzy

# Load the CSV file
csv_filename = 'ALL_articles_Update.csv'
articles = pd.read_csv(csv_filename)

# Log file to track processed issues
log_filename = 'processed_issues.log'

# Base URL for graphical abstracts
ga_base_url = "https://raw.githubusercontent.com/tang1693/PERShtml/refs/heads/main/IssuesArticles/html/img"

# Helper function to parse year and issue from URL
def parse_year_issue_from_url(url):
    match = re.search(r'/(\d{4})/000000(\d+)/000000(\d+)', url)
    if match:
        year = match.group(1)
        volume = int(match.group(2))
        issue = int(match.group(3))
        return f"{year}{issue:02d}"
    return None

# Normalize string for comparison (case-insensitive, remove punctuation and extra spaces)
def normalize_string(s):
    s = unicodedata.normalize("NFKD", s)  # Normalize Unicode
    s = re.sub(r'[^\w\s]', '', s)  # Remove punctuation
    s = re.sub(r'\s+', ' ', s)  # Remove extra whitespace
    return s.strip().lower()  # Convert to lowercase

# Find the GA image URL for an article using similarity scoring
def find_ga_image(article_title, issue):
    year = issue[:4]
    issue_no = issue[4:]
    ga_dir = os.path.join("IssuesArticles/html/img", year, issue_no)

    # Check if the directory exists
    if not os.path.exists(ga_dir):
        print(f"Directory {ga_dir} does not exist. Skipping GA for this article.")
        return None  # No directory for this issue

    # List all files in the GA directory
    file_list = os.listdir(ga_dir)
    # Extract filenames without extensions
    filenames = [os.path.splitext(filename)[0] for filename in file_list]

    # Find the best match using similarity scoring
    result = process.extractOne(article_title, filenames, scorer=fuzz.token_sort_ratio)

    if result:
        best_match, score, _ = result  # Unpack result (best_match, score, index)
        # If the score is above a threshold, consider it a match
        if score >= 30:  # Adjust threshold as needed
            matched_filename = file_list[filenames.index(best_match)]
            print(f"Best match for article '{article_title}' -> '{matched_filename}' (Score: {score})")
            return f"{ga_base_url}/{year}/{issue_no}/{matched_filename}"  # Return full URL
    else:
        print(f"No sufficiently similar match found for article '{article_title}'.")
    return None


# Read processed issues from log file
processed_issues = set()
if os.path.exists(log_filename):
    with open(log_filename, 'r') as log_file:
        processed_issues = set(log_file.read().splitlines())

# Process articles by issue
grouped_articles = articles.groupby(articles['URL'].apply(parse_year_issue_from_url))

for issue, issue_articles in grouped_articles:
    if not issue or issue in processed_issues:
        print(f"Skipping issue {issue} (already processed or invalid).")
        continue

    # Generate HTML content for the issue
    issue_html = ""
    for index, row in issue_articles.iterrows():
        border_style = "padding: 15px;"

        article_html = f'<article style="{border_style}">\n'
        access_text = '<span style="color: rgb(0, 191, 255);">Open Access</span>' if row['Access'] == "Open Access content" else ""
        pub_date = parse_year_issue_from_url(row["URL"])  # Simplified publication date

        article_html += f'    <div style="display: flex; justify-content: space-between; align-items: center;">\n'
        article_html += f'        <div style="font-weight: bold; color: gray;">Research Articles {access_text}</div>\n'
        article_html += f'    </div>\n'
        article_html += f'    <h3 style="margin: 5px 0;">\n'
        article_html += f'        <a href="{row["URL"]}" rel="noreferrer" style="text-decoration: none; color: #1b5faa;">\n'
        article_html += f'            {row["Title"]}\n'
        article_html += f'        </a>\n'
        article_html += f'    </h3>\n'
        article_html += f'    <div style="font-style: italic;">{pub_date}, {row["Pages"]}</div>\n'
        article_html += f'    <div>Authors: {row["Authors"]}</div>\n'

        # Add the graphical abstract if it exists
        ga_image_url = find_ga_image(row["Title"], issue)
        if ga_image_url:
            article_html += f'    <div>\n'
            article_html += f'        <img src="{ga_image_url}" alt="Graphical Abstract" style="width: 600px; max-width: 100%;">\n'
            article_html += f'    </div>\n'

        # Add abstract with foldable content using <details> and <summary>
        article_html += f'''    <div>
            Abstract: 
            <details>
                <summary style="color: #1b5faa;">{'Read more'}...</summary>
                {row["Abstract"]}
            </details>
        </div>\n'''
        article_html += '</article>\n'

        issue_html += article_html

    # Save the issue HTML to a file
    issue_filename = f'IssuesArticles/html/{issue}.html'
    with open(issue_filename, 'w', encoding='utf-8') as issue_file:
        issue_file.write(issue_html)

    # Log the processed issue
    with open(log_filename, 'a') as log_file:
        log_file.write(issue + '\n')

    print(f"Issue {issue} successfully processed and saved to {issue_filename}.")
