import fitz  # PyMuPDF
import re
import pandas as pd

# Load the PDF file
pdf_path = 'InPress/s13.pdf'
doc = fitz.open(pdf_path)

# Initialize an empty list to hold article data
articles_data = []

# Regex pattern to capture the details more accurately
article_pattern = re.compile(
    r'^(.*?),\s*(.+?)\.\s*(\d{4})\.\s+([A-Za-z0-9\s\&\(\)\,\.\-\:\/]+?)\s+(\d+\(?[a-zA-Z0-9]*\)?):([0-9\–]+)\.', re.MULTILINE
)

# Loop through each page to extract text
for page in doc:
    text = page.get_text("text")
    matches = article_pattern.findall(text)
    
    for match in matches:
        # Combine author and title
        authors_and_title = f"{match[0].strip()}, {match[1].strip()}"
        
        # Extract the first sentence as title and the rest as publication info
        year = match[2].strip()
        journal_info = f"{match[3].strip()}, {year}"
        volume_issue = match[4].strip()
        pages = match[5].strip()
        
        # Split the journal information into title and publication info
        title, _, remaining_info = journal_info.partition('. ')
        publication_info = f"{remaining_info} Volume/Issue: {volume_issue}, Pages: {pages}"

        # Append the extracted information as a dictionary to the articles_data list
        articles_data.append({
            "Authors": authors_and_title,
            "Title": title,
            "Publication Info": publication_info
        })

# Convert to DataFrame for further manipulation or exporting
df_articles = pd.DataFrame(articles_data)

# Generate HTML content
html_content = '<div id="articles-content">\n'

for index, row in df_articles.iterrows():
    border_style = "border-top: 1px solid #000; padding: 15px;" if index > 0 else "padding: 15px;"
    
    # Start the article section
    article_html = f'<article style="{border_style}">\n'
    
    # Add title
    article_html += f'    <h3 style="margin: 5px 0;">{row["Title"]}</h3>\n'
    
    # Add authors
    article_html += f'    <div>Authors: {row["Authors"]}</div>\n'
    
    # Add publication info
    article_html += f'    <div style="font-style: italic;">{row["Publication Info"]}</div>\n'
    
    # Close the article section
    article_html += '</article>\n'
    
    # Append the article HTML to the main content
    html_content += article_html

# Close the main div
html_content += '</div>\n'

# Save to a single HTML file
html_filename = 'in_press_articles.html'
with open(html_filename, 'w', encoding='utf-8') as file:
    file.write(html_content)

print(f"HTML content for in-press articles successfully saved to {html_filename}")
