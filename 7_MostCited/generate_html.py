#!/usr/bin/env python3
"""
生成 top_6_articles.html
使用原来的 HTML 模板（3_MostCited/most_cite_3generate_html.py）
只更新数据，不改格式
"""

import os
import pandas as pd
import re

def generate_top_6_html():
    """生成 Top 6 HTML（使用原来的模板）"""
    
    csv_path = '7_MostCited/most_cited_articles.csv'
    if not os.path.exists(csv_path):
        print(f"❌ {csv_path} 不存在")
        return
    
    # Load the sorted CSV file
    articles = pd.read_csv(csv_path)
    
    # Sort by Citations (descending)
    articles = articles.sort_values('Citations', ascending=False)
    
    # Filter out articles with "No Abstract"
    articles = articles[articles["Abstract"] != "No Abstract"]
    
    # Select the top 6 articles
    articles = articles.head(6)
    
    print(f"\n生成 Top 6 Most Cited HTML: {len(articles)} 篇文章")
    
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
        border_style = "border-top: 1px solid #000; padding: 15px;" #if index > 0 else "padding: 15px;"
        
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
        article_html += f'        <a href="{row["URL"]}" target="_blank" rel="noopener noreferrer" style="text-decoration: none; color: #1b5faa;">\n'
        article_html += f'            {row["Title"]}\n'
        article_html += f'        </a>\n'
        article_html += f'    </h3>\n'
        
        # Add the publication info (date and pages)
        article_html += f'    <div style="font-style: italic;">{pub_date}, {row["Pages"]}</div>\n'
        
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
    
        # Append the article HTML to the main content
        html_content += article_html
    
    # Close the main div
    html_content += '</div>\n'
    
    # Save to a single HTML file (root directory)
    html_filename = 'top_6_articles.html'
    with open(html_filename, 'w', encoding='utf-8') as file:
        file.write(html_content)
    
    print(f"✅ HTML content for the top 6 articles successfully saved to {html_filename}")

if __name__ == '__main__':
    generate_top_6_html()
