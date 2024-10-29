import pandas as pd
import re

# Load the sorted CSV file and get the top 6 articles
csv_filename = 'sorted_articles_by_citations.csv'
articles = pd.read_csv(csv_filename).head(6)  # Select the top 6 articles

# Initialize HTML content
html_content = '<div id="articles-content">\n'

# Helper function to parse date from the URL
def parse_date_from_url(url):
    match = re.search(r'/(\d{4})/000000(\d+)/000000(\d+)', url)
    if match:
        year = match.group(1)
        volume = int(match.group(2))
        issue = int(match.group(3))
        
        # Convert the issue number to month
        month = {
            1: "January", 2: "February", 3: "March", 4: "April",
            5: "May", 6: "June", 7: "July", 8: "August",
            9: "September", 10: "October", 11: "November", 12: "December"
        }.get(issue, "Unknown")
        
        return f"{month} {year}"
    return "Unknown Date"

# Generate HTML for each article
for index, row in articles.iterrows():
    # Set article border-top style except for the first article
    border_style = "border-top: 1px solid #000; padding: 15px;" if index > 0 else "padding: 15px;"
    
    # Parse the publication date
    pub_date = parse_date_from_url(row["URL"])
    
    # Start the article section
    article_html = f'<article style="{border_style}">\n'
    
    # Add the header section with "ASPRS Member entry" if not open access
    if row['Access'] == "Open Access content":
        access_text = '<span style="color: rgb(0, 191, 255);">Open Access</span>'
        member_entry = ""
    else:
        access_text = ""
        member_entry = ('<a href="https://my.asprs.org/ASPRSMember/Contacts/Sign_In.aspx?LoginRedirect=true&amp;returnurl=%2f" '
                        'style="font-style: italic; padding: 3px 8px; background-color: #f1f1f1; border: 1px solid #1b5faa; '
                        'border-radius: 3px; text-decoration: none; color: #1b5faa;">ASPRS Member entry</a>')

    # Header with access info and ASPRS Member entry link if needed
    article_html += f'    <div style="display: flex; justify-content: space-between; align-items: center;">\n'
    article_html += f'        <div style="font-weight: bold; color: gray;">Research Articles {access_text}</div>\n'
    article_html += f'        {member_entry}\n'
    article_html += f'    </div>\n'
    
    # Add the title and link
    article_html += f'    <h3 style="margin: 5px 0;">\n'
    article_html += f'        <a href="{row["URL"]}" style="text-decoration: none; color: #1b5faa;">\n'
    article_html += f'            {row["Title"]}\n'
    article_html += f'        </a>\n'
    article_html += f'    </h3>\n'
    
    # Add the publication info (date and pages)
    article_html += f'    <div style="font-style: italic;">{pub_date}, {row["Pages"]}</div>\n'
    
    # Add authors
    article_html += f'    <div>Authors: {row["Authors"]}</div>\n'
    
    # Close the article section
    article_html += '</article>\n'

    # Append the article HTML to the main content
    html_content += article_html

# Close the main div
html_content += '</div>\n'

# Save to a single HTML file
html_filename = 'top_6_articles.html'
with open(html_filename, 'w', encoding='utf-8') as file:
    file.write(html_content)

print(f"HTML content for the top 6 articles successfully saved to {html_filename}")
