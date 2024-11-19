import pandas as pd
import re
from bs4 import BeautifulSoup  # Add this import statement
import requests  # Add this import statement
import os  # Add this import statement


def load_data_from_doi(csv_filename):
    """
    Reads a CSV file containing a 'DOI' column, fetches information from the corresponding web pages,
    and updates the same CSV file with the new data. Supports resuming from where it stopped.

    Parameters:
        csv_filename (str): Path to the input CSV file with a 'DOI' column.
    """

    # Load the input CSV file
    try:
        input_df = pd.read_csv(csv_filename)
    except FileNotFoundError:
        print(f"Error: The file {csv_filename} does not exist.")
        return

    # Check if 'DOI' column exists
    if 'DOI' not in input_df.columns:
        print("Error: The input CSV file must contain a 'DOI' column.")
        return

    # Extract DOIs and generate URLs
    all_dois = input_df['DOI'].dropna().tolist()
    do_urls = {doi: f"https://doi.org/{doi}" for doi in all_dois}

    # Check for already processed DOIs
    processed_dois = set(input_df['DOI'].dropna().tolist())
    print(f"Resuming from {len(processed_dois)} processed DOIs...")

    # Add new columns if they do not exist
    for column in ['Title', 'Abstract', 'Authors', 'Pages', 'Access', 'URL']:
        if column not in input_df.columns:
            input_df[column] = None

    # Headers for HTTP requests
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    # Process DOIs and update the file incrementally
    for doi, url in do_urls.items():
        if doi in processed_dois and not input_df[input_df['DOI'] == doi][['Title', 'Abstract', 'Authors']].isnull().values.any():
            print(f"Skipping already processed DOI: {doi}")
            continue

        print(f"Processing: {url}")
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Failed to fetch the page at {url}")
            continue

        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract data
        try:

            # Abstract (adjust selector based on actual webpage structure)
            abstract = 'N/A'
            abstract_div = soup.find('div', id="Abst")
            if abstract_div:
                abstract = abstract_div.get_text(strip=True).replace('\n', ' ').replace('\r', '').strip()
                print(abstract[:20])
                
            # Authors
            authors = 'N/A'
            authors_section = soup.find('strong', string='Authors: ')
            if authors_section:
                authors_list = soup.find_all('a', title="Search for articles by this author")
                authors = ', '.join([a.get_text(strip=True) for a in authors_list])
                print(authors)


            # Update the data for the DOI
            input_df.loc[input_df['DOI'] == doi, ['Abstract', 'Authors', 'URL']] = [abstract, authors, url]

            # Save the updated DataFrame back to the CSV file
            input_df.to_csv(csv_filename, index=False)
            # print(f"Updated record for DOI: {doi}")
        except Exception as e:
            print(f"Error processing {url}: {e}")

    print(f"Data successfully updated in {csv_filename}")


def sort_csv(csv_filename, sorted_column='Total Downloads'):

    # Load the CSV file with citation data
    articles = pd.read_csv(csv_filename)

    articles[sorted_column] = articles[sorted_column].astype(int)

    # Sort by Citations in descending order
    sorted_articles = articles.sort_values(by=sorted_column, ascending=False)
    
    # Remove duplicate rows based on all columns
    sorted_articles.drop_duplicates(inplace=True)
    
    # Remove duplicate rows based on the 'DOI' column
    sorted_articles.drop_duplicates(subset=['DOI'], inplace=True)

    # Save the sorted data back to a new CSV file
    sorted_csv_filename = 'MostDownload/asprs_all_views_per_article_per_month_sorted.csv'
    sorted_articles.head(20).to_csv(sorted_csv_filename, index=False)

    print(f"Sorted data saved to {sorted_csv_filename}")


def csv_clean(csv_filename):

    # Load the CSV file with citation data
    articles = pd.read_csv(csv_filename)

    # Remove rows where the 'Authors' column is empty
    articles.dropna(subset=['Authors'], inplace=True)

    # Remove abstracts that contain 'No Abstract'
    articles = articles[articles['Abstract'] != 'No Abstract']

    # Save the sorted data back to a new CSV file
    csv_filename = 'MostDownload/asprs_all_views_per_article_per_month_sorted.csv'
    articles.head(20).to_csv(csv_filename, index=False)

    print(f"Cleaned data saved to {csv_filename}")


def generate_top_articles_html(csv_filename, output_filename, top_n=6):
    """
    Generate an HTML file displaying the top N articles from a CSV file.

    Args:
        csv_filename (str): Path to the input CSV file.
        output_filename (str): Path to the output HTML file.
        top_n (int): Number of top articles to include in the output (default is 6).
    """
    # Load the CSV file
    articles = pd.read_csv(csv_filename)

    # Filter out articles with "No Abstract"
    articles = articles[articles["Abstract"] != "No Abstract"]

    # Limit to the top N articles
    articles = articles.head(top_n)

    # Start the HTML content
    html_content = ""


    # Generate HTML for each article
    for index, row in articles.iterrows():
        # Set article border-top style except for the first article
        border_style = "border-top: 1px solid #000; padding: 15px;" 
        
    
        # Start the article section
        article_html = f'<article style="{border_style}">\n'
        
        # Add the title and link
        article_html += f'    <h3 style="margin: 5px 0;">\n'
        article_html += f'        <a href="{row["URL"]}" style="text-decoration: none; color: #1b5faa;">\n'
        article_html += f'            {row["Item Title"]}\n'
        article_html += f'        </a>\n'
        article_html += f'    </h3>\n'
        
        # Add the publication info (date and pages)
        article_html += f"    <div style=\"font-style: italic;\">Year: {row['Year']}, Volume: {row['Volume']}, Issue: {row['Issue']}</div>\n"
        
        # Add authors
        article_html += f'    <div>Authors: {row["Authors"]}</div>\n'
        
        # Add abstract with foldable content using <details> and <summary>
        article_html += f'''    <div>
            Abstract: 
            <details>
                <summary style="color: #1b5faa;">{'Read more'}...</summary>
                {row["Abstract"]}
            </details>
        </div>\n'''

        # Close the article section
        article_html += '</article>\n'

        # Append the article HTML to the content
        html_content += article_html

    # Save to HTML file
    with open(output_filename, 'w', encoding='utf-8') as file:
        file.write(html_content)

    print(f"HTML content successfully saved to {output_filename}")


# Example usage
csv_filename = 'MostDownload/asprs_all_views_per_article_per_month.csv'  # Input CSV file with 'DOI' column
csv_filename_sorted = 'MostDownload/asprs_all_views_per_article_per_month_sorted.csv'  
# sort_csv(csv_filename)
# load_data_from_doi(csv_filename_sorted) 
# csv_clean(csv_filename_sorted)
output_filename = 'most_download_articles.html'
generate_top_articles_html(csv_filename_sorted, output_filename)