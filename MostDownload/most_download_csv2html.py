import pandas as pd
import re

# Load the CSV file
csv_filename = 'MostDownload/asprs_all_views_per_article_per_month.csv'
df = pd.read_csv(csv_filename)
# Remove duplicate article titles, keeping the row with the largest "Total Downloads"
df = df.sort_values(by="Total Downloads", ascending=False).drop_duplicates(subset="Item Title", keep="first")

# Sort the remaining data by "Total Downloads" in descending order
top_articles = df.head(6)  # Get the top articles as needed

# Initialize HTML content
html_content = '<div id="articles-content">\n'

# Helper function to generate the URL based on DOI
def generate_url(doi):
    return f"https://doi.org/{doi}" if doi else "#"

# Generate HTML for each article
for index, row in top_articles.iterrows():
    border_style = "border-top: 1px solid #000; padding: 15px;" if index > 0 else "padding: 15px;"

    # Start the article section
    article_html = f'<article style="{border_style}">\n'
    
    # Add the title and link
    article_html += f'    <h3 style="margin: 5px 0;">\n'
    article_html += f'        <a href="{generate_url(row["DOI"])}" style="text-decoration: none; color: #1b5faa;">\n'
    article_html += f'            {row["Item Title"]}\n'
    article_html += f'        </a>\n'
    article_html += f'    </h3>\n'
    
    # Publication info
    article_html += f'    <div style="font-style: italic;">{row["Year"]}, {row["Volume"]}, {row["Issue"]}</div>\n'
    
    # Publisher
    article_html += f'    <div>Publisher: {row["Publisher"]}</div>\n'
    
    # Close the article section
    article_html += '</article>\n'

    # Append the article HTML to the main content
    html_content += article_html

# Close the main div
html_content += '</div>\n'


# Save to a single HTML file
html_filename = 'most_download_articles.html'
with open(html_filename, 'w', encoding='utf-8') as file:
    file.write(html_content)

print(f"HTML content for the top articles successfully saved to {html_filename}")
