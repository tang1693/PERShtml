import pandas as pd
import os
import time
from scholarly import scholarly

# Check if 'articles_with_citations_scholarly.csv' exists
if os.path.exists('articles_with_citations_scholarly.csv'):
    articles = pd.read_csv('articles_with_citations_scholarly.csv')
else:
    # Load 'filtered_articles_info.csv' and add 'Citations' column
    articles = pd.read_csv('filtered_articles_info.csv')
    articles['Citations'] = None
    articles.to_csv('articles_with_citations_scholarly.csv', index=False)

# Identify articles without citation counts
pending_articles = articles[articles['Citations'].isnull()]

if len(pending_articles) == 0:
    print("All articles have citation counts.")
else:
    # Process next 3 articles
    num_to_process = min(3, len(pending_articles))
    articles_to_process = pending_articles.iloc[:num_to_process]

    def get_citation_count(title):
        try:
            search_query = scholarly.search_pubs(title)
            first_result = next(search_query)
            citation_count = first_result.get('num_citations', 0)
            return citation_count
        except StopIteration:
            print(f"No results found for title: {title}")
        except Exception as e:
            print(f"Error retrieving citation count for '{title}': {e}")
        return None

    for index, row in articles_to_process.iterrows():
        title = row['Title']
        print(f"Searching citation count for: {title}")
        citation_count = get_citation_count(title)
        articles.at[index, 'Citations'] = citation_count
        # Delay to be polite
        time.sleep(2)

    # Save updated data
    articles.to_csv('articles_with_citations_scholarly.csv', index=False)
    print(f"Citation counts updated for {num_to_process} articles and saved to articles_with_citations_scholarly.csv")
