import glob
import os
import re
import pandas as pd

# Load the CSV file
csv_filename = '6_IssuesArticles/ALL_articles_Update_cleaned.csv'
articles = pd.read_csv(csv_filename)

# Log file to track processed issues
log_filename = '6_IssuesArticles/processed_issues.log'

# Base URL for graphical abstracts on GitHub
ga_base_url = "https://raw.githubusercontent.com/tang1693/PERShtml/refs/heads/main/IssuesArticles/html/img"


def normalize_title(title: str) -> str:
    return re.sub(r"\s+", " ", title.strip()).lower()


def build_access_overrides() -> dict:
    """从 metadata Excel 中读取 Access Status=OA 的文章"""
    overrides = {}
    for path in glob.glob("*_metadata.xlsx"):
        try:
            df = pd.read_excel(path)
        except Exception as exc:  # pragma: no cover - 调试信息
            print(f"⚠️ 无法读取 {path}: {exc}")
            continue
        if 'Title' not in df.columns or 'Access Status' not in df.columns:
            continue
        for _, row in df.iterrows():
            title = row.get('Title')
            status = row.get('Access Status')
            if isinstance(title, str) and isinstance(status, str):
                if status.strip().lower() == 'oa':
                    overrides[normalize_title(title)] = True
    return overrides


def is_open_access(row, overrides) -> bool:
    status = row.get('Access')
    if isinstance(status, str):
        status_normalized = status.strip().lower()
        if 'open access' in status_normalized or status_normalized == 'oa':
            return True
    title = row.get('Title')
    if isinstance(title, str):
        return overrides.get(normalize_title(title), False)
    return False


def get_issue_key(row):
    """从行中获取期刊key (格式: YYYYMM)"""
    if 'IssueKey' in row.index and pd.notna(row['IssueKey']):
        key = str(row['IssueKey']).replace('.0', '')
        return key if len(key) == 6 else None

    url = row['URL']
    match = re.search(r'/(\d{4})/000000(\d+)/000000(\d+)', url)
    if match:
        year = match.group(1)
        issue = int(match.group(3))
        return f"{year}{issue:02d}"

    return None


def get_ga_image_url(row, issue):
    if 'GA_Path' in row.index and pd.notna(row['GA_Path']):
        return str(row['GA_Path'])
    return None


access_overrides = build_access_overrides()

processed_issues = set()
if os.path.exists(log_filename):
    with open(log_filename, 'r') as log_file:
        processed_issues = set(log_file.read().splitlines())

articles['_issue_key'] = articles.apply(get_issue_key, axis=1)
articles = articles[articles['_issue_key'].notna()]

print(f"📊 共有 {len(articles)} 篇文章待处理")
print(f"📊 涉及 {articles['_issue_key'].nunique()} 个期刊号")

grouped_articles = articles.groupby('_issue_key')
link_attrs = 'target="_blank" rel="noopener noreferrer"'

for issue, issue_articles in grouped_articles:
    if not issue or issue in processed_issues:
        print(f"⏭️  跳过期刊 {issue} (已处理或无效)")
        continue

    year = issue[:4]
    issue_no = issue[4:].zfill(2)
    title = f"Issue {issue_no} - Year {year}"

    first_url = issue_articles.iloc[0]["URL"]
    if '/content/asprs/pers/' in first_url:
        issue_url = first_url.rsplit("/", 1)[0]
    else:
        volume = int(year) - 1934
        issue_url = f"https://www.ingentaconnect.com/content/asprs/pers/{year}/000000{volume:02d}/000000{int(issue_no):02d}"

    print(f"\n{'='*60}")
    print(f"📄 处理期刊: {title} ({len(issue_articles)} 篇文章)")
    print(f"{'='*60}")

    issue_html = f"""
    <!DOCTYPE html>
    <html lang=\"en\">
    <head>
        <meta charset=\"UTF-8\">
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
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
            <p><a href=\"{issue_url}\" style=\"color: white; text-decoration: underline;\">View Full Issue</a></p>
        </header>
    """

    for _, row in issue_articles.iterrows():
        ga_image_url = get_ga_image_url(row, issue)

        if ga_image_url:
            print(f"   ✅ GA: {row['Title'][:50]}... -> {ga_image_url.split('/')[-1]}")
            ga_image_html = f'<img src="{ga_image_url}" alt="Graphical Abstract" class="graphical-abstract">'
        else:
            print(f"   ⚠️  无 GA: {row['Title'][:50]}...")
            ga_image_html = ''

        oa_badge = '<span style="color: rgb(0, 191, 255);">Open Access</span>' if is_open_access(row, access_overrides) else ''
        title_text = row.get('Title', 'Untitled') or 'Untitled'
        url = row.get('URL')
        url = url if isinstance(url, str) and url.strip() else '#'

        pages_value = row.get('Pages', '')
        pages_text = '' if pd.isna(pages_value) else str(pages_value)
        authors_value = row.get('Authors', '')
        authors_text = '' if pd.isna(authors_value) else str(authors_value)
        abstract_value = row.get('Abstract', '')
        abstract_text = '' if pd.isna(abstract_value) else str(abstract_value)

        article_html = f"""
        <article>
            <div style=\"display: flex; justify-content: space-between; align-items: center;\">
                <div style=\"font-weight: bold; color: gray;\">Research Articles {oa_badge}</div>
            </div>
            <h3><a href=\"{url}\" {link_attrs}>{title_text}</a></h3>
            <div style=\"font-style: italic;\">Pages: {pages_text}</div>
            <div>Authors: {authors_text}</div>
            <div>
                Abstract:
                <details>
                    <summary>Read more...</summary>
                    {abstract_text}
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

    output_filename = f"IssuesArticles/html/{issue}.html"
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    with open(output_filename, 'w', encoding='utf-8') as file:
        file.write(issue_html)

    print(f"✅ 已生成: {output_filename}")

    with open(log_filename, 'a') as log_file:
        log_file.write(f"{issue}\n")

print("\n" + "="*60)
print("✅ HTML 生成完成！")
print("="*60)
