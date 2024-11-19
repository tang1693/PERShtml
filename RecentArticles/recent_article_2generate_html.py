import pandas as pd
import re

# Load the CSV file
csv_filename = 'filtered_articles_info_abs.csv'
articles = pd.read_csv(csv_filename)

# Filter out articles with "No Abstract"
articles = articles[articles["Abstract"] != "No Abstract"]

# Start the HTML content for Open Access and non-Open Access
html_open_access = ""
html_member_only = ""

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
        member_entry = ""

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
    
    # Add abstract with foldable content
    article_html += f'''    <div>
        Abstract: <span id="abstract-short-{index}" style="display: inline;">{row["Abstract"][:100]}...</span>
        <span id="abstract-full-{index}" style="display: none;">{row["Abstract"]}</span>
        <a href="#" id="toggle-abstract-{index}" onclick="toggleAbstract({index}); return false;" style="color: #1b5faa; text-decoration: none;">[Read more]</a>
    </div>\n'''
    
    # Close the article section
    article_html += '</article>\n'

    # Append the article HTML to the appropriate content based on access level
    if row['Access'] == "Open Access content":
        html_open_access += article_html
    else:
        html_member_only += article_html

# Add JavaScript and CSS for foldable functionality
foldable_script = '''
<script>
    function toggleAbstract(index) {
        var shortAbstract = document.getElementById(`abstract-short-${index}`);
        var fullAbstract = document.getElementById(`abstract-full-${index}`);
        var toggleLink = document.getElementById(`toggle-abstract-${index}`);
        
        if (shortAbstract.style.display === "none") {
            shortAbstract.style.display = "inline";
            fullAbstract.style.display = "none";
            toggleLink.textContent = "[Read more]";
        } else {
            shortAbstract.style.display = "none";
            fullAbstract.style.display = "inline";
            toggleLink.textContent = "[Read less]";
        }
    }
</script>
'''

# Include the script in the HTML files
html_open_access = foldable_script + html_open_access
html_member_only = foldable_script + html_member_only

# Save to HTML files
open_access_filename = 'open_access_articles.html'
member_only_filename = 'member_only_articles.html'

with open(open_access_filename, 'w', encoding='utf-8') as file:
    file.write(html_open_access)

with open(member_only_filename, 'w', encoding='utf-8') as file:
    file.write(html_member_only)

print(f"Open Access HTML content successfully saved to {open_access_filename}")
print(f"Member Only HTML content successfully saved to {member_only_filename}")
