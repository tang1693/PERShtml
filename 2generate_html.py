import pandas as pd

# Load the CSV file
csv_filename = 'filtered_articles_info.csv'
articles = pd.read_csv(csv_filename)

# Start the HTML content
html_content = ""

# Generate HTML for each article
for index, row in articles.iterrows():
    # Set article border-top style except for the first article
    border_style = "border-top: 1px solid #000; padding: 15px;" if index > 0 else "padding: 15px;"

    # Start the article section
    html_content += f'<article style="{border_style}">\n'
    
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
    html_content += f'    <div style="display: flex; justify-content: space-between; align-items: center;">\n'
    html_content += f'        <div style="font-weight: bold; color: gray;">Research Articles {access_text}</div>\n'
    html_content += f'        {member_entry}\n'
    html_content += f'    </div>\n'
    
    # Add the title and link
    html_content += f'    <h3 style="margin: 5px 0;">\n'
    html_content += f'        <a href="{row["URL"]}" style="text-decoration: none; color: #1b5faa;">\n'
    html_content += f'            {row["Title"]}\n'
    html_content += f'        </a>\n'
    html_content += f'    </h3>\n'
    
    # Add the publication info (month and pages)
    html_content += f'    <div style="font-style: italic;">October 2024, {row["Pages"]}</div>\n'
    
    # Add authors
    html_content += f'    <div>Authors: {row["Authors"]}</div>\n'
    
    # Close the article section
    html_content += '</article>\n'

# Save to an HTML file
html_filename = 'articles.html'
with open(html_filename, 'w', encoding='utf-8') as file:
    file.write(html_content)

print(f"HTML content successfully saved to {html_filename}")
