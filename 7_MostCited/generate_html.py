#!/usr/bin/env python3
"""
生成 Most Cited Articles HTML
"""

import pandas as pd
import os

def generate_most_cited_html():
    """生成 Most Cited HTML"""
    
    csv_path = '7_MostCited/most_cited_articles.csv'
    if not os.path.exists(csv_path):
        print(f"❌ {csv_path} 不存在")
        return
    
    df = pd.read_csv(csv_path)
    
    # 只显示有引用的文章（或全部显示，按引用数排序）
    df_sorted = df.sort_values('Citations', ascending=False)
    
    # 限制显示数量（Top 6）
    max_articles = 6
    df_display = df_sorted.head(max_articles)
    
    print(f"\n生成 Top 6 Most Cited HTML: {len(df_display)} 篇文章")
    
    # HTML 模板
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Most Cited Articles (Last 2 Years)</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 40px;
            line-height: 1.6;
        }
        h1 {
            color: #1b5faa;
            margin-bottom: 10px;
        }
        .subtitle {
            color: gray;
            font-size: 14px;
            margin-bottom: 30px;
        }
        article {
            padding: 15px;
            margin-bottom: 10px;
        }
        article:not(:first-child) {
            border-top: 1px solid #ddd;
        }
        .rank {
            display: inline-block;
            width: 40px;
            font-weight: bold;
            color: #1b5faa;
        }
        .citations {
            display: inline-block;
            background: #e3f2fd;
            padding: 2px 8px;
            border-radius: 3px;
            font-weight: bold;
            color: #1976d2;
            margin-left: 10px;
        }
        .title {
            margin: 5px 0;
        }
        .title a {
            text-decoration: none;
            color: #1b5faa;
            font-size: 16px;
            font-weight: 500;
        }
        .title a:hover {
            text-decoration: underline;
        }
        .metadata {
            color: #666;
            font-size: 14px;
            margin: 5px 0;
        }
        .authors {
            color: #444;
            font-size: 14px;
        }
        .abstract {
            color: #555;
            font-size: 14px;
            margin-top: 8px;
        }
        details {
            cursor: pointer;
        }
        summary {
            color: #1b5faa;
            font-weight: 500;
        }
    </style>
</head>
<body>
    <h1>Most Cited Articles</h1>
    <div class="subtitle">Top 6 articles from the last 2 years (based on Scopus citations)</div>
'''
    
    html_content = html_content.replace('{count}', str(len(df_display)))
    
    # 生成每篇文章的 HTML
    for idx, (_, row) in enumerate(df_display.iterrows(), 1):
        title = row['Title']
        authors = row.get('Authors', 'Unknown')
        url = row['URL']
        pub_date = row.get('PubDate', 'Unknown Date')
        pages = row.get('Pages', '')
        citations = int(row.get('Citations', 0))
        abstract = row.get('Abstract', 'No abstract available.')
        
        # 处理 Abstract
        if pd.isna(abstract) or abstract == 'No Abstract':
            abstract = 'No abstract available.'
        
        article_html = f'''
    <article>
        <div>
            <span class="rank">#{idx}</span>
            <span class="citations">{citations} citations</span>
        </div>
        <div class="title">
            <a href="{url}" target="_blank" rel="noreferrer">{title}</a>
        </div>
        <div class="metadata">{pub_date}, {pages}</div>
        <div class="authors">Authors: {authors}</div>
        <div class="abstract">
            Abstract: 
            <details>
                <summary>Read more...</summary>
                <p>{abstract}</p>
            </details>
        </div>
    </article>
'''
        
        html_content += article_html
    
    # 结束 HTML
    html_content += '''
</body>
</html>
'''
    
    # 保存到项目根目录（覆盖原 top_6_articles.html）
    output_path = 'top_6_articles.html'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ 已生成: {output_path}")

if __name__ == '__main__':
    generate_most_cited_html()
