import pandas as pd
import os
import re
import unicodedata
from rapidfuzz import fuzz, process

# Load the CSV file
csv_filename = '6_IssuesArticles/ALL_articles_Update_cleaned.csv'
articles = pd.read_csv(csv_filename)

# Log file to track processed issues
log_filename = '6_IssuesArticles/processed_issues.log'

# Base URL for graphical abstracts
ga_base_url = "https://raw.githubusercontent.com/tang1693/PERShtml/refs/heads/main/IssuesArticles/html/img"

# Helper function to get issue key
def get_issue_key(row):
    """
    从行中获取期刊key (格式: YYYYMM)
    优先使用 IssueKey 列，否则尝试从 URL 解析
    """
    # 方法1: 直接使用 IssueKey 列（如果存在）
    if 'IssueKey' in row.index and pd.notna(row['IssueKey']):
        # 转为字符串，去掉可能的 .0 后缀
        issue_key = str(row['IssueKey'])
        if issue_key.endswith('.0'):
            issue_key = issue_key[:-2]
        return issue_key
    
    # 方法2: 从 Ingenta URL 解析
    url = row['URL']
    match = re.search(r'/(\d{4})/000000(\d+)/000000(\d+)', url)
    if match:
        year = match.group(1)
        issue = int(match.group(3))
        return f"{year}{issue:02d}"
    
    return None

# Helper function to find GA image
def find_ga_image(article_title, issue):
    year = issue[:4]
    issue_no = issue[4:].replace('.0', '').zfill(2)
    
    relative_path = os.path.join("IssuesArticles/html/img", year, issue_no)
    absolute_path = os.path.abspath(relative_path)
    
    print(f"---> Searching for GA in: {absolute_path}")

    if not os.path.exists(relative_path):
        print(f"!!! FOLDER NOT FOUND: {relative_path}")
        return None 

    file_list = os.listdir(relative_path)
    filenames = [os.path.splitext(filename)[0] for filename in file_list]

    result = process.extractOne(article_title, filenames, scorer=fuzz.token_sort_ratio)

    if result:
        best_match, score, _ = result 
        if score >= 30: 
            matched_filename = file_list[filenames.index(best_match)]
            full_github_url = f"{ga_base_url}/{year}/{issue_no}/{matched_filename}"
            print(f"SUCCESS: Match found ({score}%). URL: {full_github_url}")
            return full_github_url
    
    print(f"FAILED: No match for '{article_title[:30]}...' in {relative_path}")
    return None

# Read processed issues from log file
processed_issues = set()
if os.path.exists(log_filename):
    with open(log_filename, 'r') as log_file:
        processed_issues = set(log_file.read().splitlines())

# Add IssueKey column for grouping
articles['_issue_key'] = articles.apply(get_issue_key, axis=1)

# Filter out articles without valid issue key
articles = articles[articles['_issue_key'].notna()]

print(f"📊 共有 {len(articles)} 篇文章待处理")
print(f"📊 涉及 {articles['_issue_key'].nunique()} 个期刊号")

# Process articles by issue
grouped_articles = articles.groupby('_issue_key')

for issue, issue_articles in grouped_articles:
    if not issue or issue in processed_issues:
        print(f"⏭️  跳过期刊 {issue} (已处理或无效)")
        continue

    year = issue[:4]
    issue_no = issue[4:].replace('.0', '').zfill(2)
    title = f"Issue {issue_no} - Year {year}"
    
    # 构建期刊 URL（尝试从第一篇文章获取，否则使用默认）
    first_url = issue_articles.iloc[0]["URL"]
    if '/content/asprs/pers/' in first_url:
        issue_url = first_url.rsplit("/", 1)[0]
    else:
        # DOI URL，构建 Ingenta URL
        volume = int(year) - 1934  # PERS 从1934年开始
        issue_url = f"https://www.ingentaconnect.com/content/asprs/pers/{year}/000000{volume:02d}/000000{int(issue_no):02d}"

    print(f"\n{'='*60}")
    print(f"📄 处理期刊: {title} ({len(issue_articles)} 篇文章)")
    print(f"{'='*60}")

    # Generate HTML content for the issue
    issue_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 0;
                background-color: #f9f9f9;
                color: #333;
            }}
            header {{
                background-color: #1b5faa;
                color: white;
                padding: 20px;
                text-align: center;
            }}
            article {{
                background-color: #fff;
                margin: 20px auto;
                padding: 20px;
                border: 1px solid #ddd;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                max-width: 900px;
            }}
            h3 {{
                color: #1b5faa;
                margin-bottom: 10px;
            }}
            a {{
                text-decoration: none;
                color: #1b5faa;
            }}
            a:hover {{
                text-decoration: underline;
            }}
            .graphical-abstract {{
                width: 100%;
                max-width: 800px;
                height: auto;
                margin-top: 15px;
                border: 1px solid #ccc;
                border-radius: 5px;
            }}
            details {{
                margin-top: 10px;
            }}
            summary {{
                color: #1b5faa;
                cursor: pointer;
            }}
            summary:hover {{
                text-decoration: underline;
            }}
            footer {{
                text-align: center;
                padding: 20px;
                background-color: #1b5faa;
                color: white;
                margin-top: 40px;
            }}
        </style>
    </head>
    <body>
        <header>
            <h1>{title}</h1>
            <p><a href="{issue_url}" style="color: white; text-decoration: underline;">View Full Issue</a></p>
        </header>
    """

    # Generate articles for this issue
    for index, row in issue_articles.iterrows():
        ga_image_url = find_ga_image(row['Title'], issue)
        ga_image_html = f'<img src="{ga_image_url}" alt="Graphical Abstract" class="graphical-abstract">' if ga_image_url else ''

        access_badge = '<span style="color: rgb(0, 191, 255);">Open Access</span>' if row['Access'] == "Open Access content" else ''

        article_html = f"""
        <article>
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="font-weight: bold; color: gray;">Research Articles {access_badge}</div>
            </div>
            <h3><a href="{row['URL']}">{row['Title']}</a></h3>
            <div style="font-style: italic;">Pages: {row['Pages']}</div>
            <div>Authors: {row['Authors']}</div>
            <div>
                Abstract:
                <details>
                    <summary>Read more...</summary>
                    {row['Abstract']}
                </details>
            </div>
            {ga_image_html}
        </article>
        """
        issue_html += article_html

    issue_html += """
        <footer>
            <p>&copy; 2026 ASPRS. All rights reserved.</p>
        </footer>
    </body>
    </html>
    """

    # Save HTML file
    output_filename = f"IssuesArticles/html/{issue}.html"
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    with open(output_filename, 'w', encoding='utf-8') as file:
        file.write(issue_html)

    print(f"✅ 已生成: {output_filename}")

    # Log the processed issue
    with open(log_filename, 'a') as log_file:
        log_file.write(f"{issue}\n")

print("\n" + "="*60)
print("✅ HTML 生成完成！")
print("="*60)
