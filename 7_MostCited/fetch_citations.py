#!/usr/bin/env python3
"""
提取最近2年的论文，调用 Scopus API 获取引用数，生成 Most Cited HTML
"""

import os
import sys
import pandas as pd
import requests
import time
from datetime import datetime, timedelta
import re

# Scopus API 配置
SCOPUS_API_KEY = os.environ.get('SCOPUS_API_KEY', '')
SCOPUS_API_URL = 'https://api.elsevier.com/content/search/scopus'

def parse_article_date(row):
    """解析文章日期（从 IssueKey 或 URL）"""
    # 方法1: IssueKey
    if pd.notna(row.get('IssueKey')):
        try:
            issue_key_str = str(int(row['IssueKey']))
            if len(issue_key_str) == 6:
                year = int(issue_key_str[:4])
                month = int(issue_key_str[4:])
                return datetime(year, month, 1)
        except:
            pass
    
    # 方法2: Ingenta URL
    url = row.get('URL', '')
    if 'ingentaconnect.com' in url:
        match = re.search(r'/pers/(\d{4})/\d+/(\d+)/', url)
        if match:
            year = int(match.group(1))
            issue = int(match.group(2))
            return datetime(year, issue, 1)
    
    return None

def extract_doi(row):
    """从 URL 或 DOI 列提取 DOI"""
    # 方法1: 直接从 URL（新格式：https://doi.org/...）
    url = row.get('URL', '')
    if 'doi.org' in url:
        doi = url.split('doi.org/')[-1]
        return doi.strip()
    
    # 方法2: 从 Ingenta URL 中的 DOI 参数（如果有）
    # 这个需要根据实际 URL 格式调整
    
    return None

def get_citation_count(doi=None, title=None):
    """
    通过 Scopus API 获取引用数
    
    Args:
        doi: DOI 号（优先使用）
        title: 文章标题（DOI 不存在时使用）
    
    Returns:
        int: 引用数，失败返回 0
    """
    if not SCOPUS_API_KEY:
        return 0
    
    if not doi and not title:
        return 0
    
    try:
        # 构建查询
        if doi:
            query = f'DOI({doi})'
        else:
            # 使用标题搜索（需要清理特殊字符）
            clean_title = title.replace('"', '').replace("'", "")
            query = f'TITLE("{clean_title}")'
        
        params = {
            'query': query,
            'apiKey': SCOPUS_API_KEY,
            'count': 1
        }
        
        headers = {
            'Accept': 'application/json'
        }
        
        response = requests.get(SCOPUS_API_URL, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            entries = data.get('search-results', {}).get('entry', [])
            
            if entries and len(entries) > 0:
                # 获取引用数
                cited_by = entries[0].get('citedby-count', '0')
                return int(cited_by)
        elif response.status_code == 429:
            print(f"   ⚠️  API 限流，等待30秒...")
            time.sleep(30)
            return 0
        else:
            # 其他错误静默处理
            pass
        
        # 避免 API 限流
        time.sleep(0.5)
        
    except Exception as e:
        # 静默处理错误
        pass
    
    return 0

def main():
    print("=" * 70)
    print("📊 Most Cited Articles - 提取最近2年论文并获取引用数")
    print("=" * 70)
    
    # 1. 读取总库
    # 支持从项目根目录或 7_MostCited/ 目录运行
    all_csv = '6_IssuesArticles/ALL_articles_Update_cleaned.csv'
    if not os.path.exists(all_csv):
        all_csv = '../6_IssuesArticles/ALL_articles_Update_cleaned.csv'
    
    if not os.path.exists(all_csv):
        print(f"❌ ALL_articles_Update_cleaned.csv 不存在")
        sys.exit(1)
    
    df_all = pd.read_csv(all_csv)
    print(f"\n✅ 读取总库: {len(df_all)} 篇文章")
    
    # 2. 解析日期
    df_all['ParsedDate'] = df_all.apply(parse_article_date, axis=1)
    
    # 3. 筛选最近2年
    two_years_ago = datetime.now() - timedelta(days=730)
    df_recent = df_all[df_all['ParsedDate'] >= two_years_ago].copy()
    
    print(f"✅ 最近2年论文: {len(df_recent)} 篇")
    print(f"   日期范围: {df_recent['ParsedDate'].min().strftime('%Y-%m')} 到 {df_recent['ParsedDate'].max().strftime('%Y-%m')}")
    
    # 4. 提取 DOI
    df_recent['DOI'] = df_recent.apply(extract_doi, axis=1)
    has_doi = df_recent['DOI'].notna().sum()
    print(f"   有 DOI: {has_doi} 篇")
    
    # 5. 获取引用数（如果配置了 API key）
    if SCOPUS_API_KEY:
        print(f"\n📥 获取引用数（Scopus API）...")
        print(f"   总数: {len(df_recent)} 篇")
        
        citation_counts = []
        total = len(df_recent)
        
        for idx, row in df_recent.iterrows():
            doi = row['DOI']
            title = row['Title']
            
            # 优先使用 DOI，否则用 Title
            citations = get_citation_count(doi=doi if pd.notna(doi) else None, 
                                          title=title)
            citation_counts.append(citations)
            
            # 显示进度
            current = len(citation_counts)
            if current % 10 == 0 or current == total:
                print(f"   进度: {current}/{total} ({current*100//total}%)")
        
        df_recent['Citations'] = citation_counts
        
        # 统计
        total_citations = sum(citation_counts)
        articles_with_citations = sum(1 for c in citation_counts if c > 0)
        
        print(f"✅ 引用数获取完成")
        print(f"   总引用数: {total_citations}")
        print(f"   有引用的文章: {articles_with_citations}/{total}")
    else:
        print(f"\n⚠️  未配置 SCOPUS_API_KEY，跳过引用数获取")
        print(f"   提示: 设置环境变量 SCOPUS_API_KEY 后可获取引用数")
        df_recent['Citations'] = 0
    
    # 6. 按引用数排序
    df_sorted = df_recent.sort_values('Citations', ascending=False)
    
    # 7. 保存 CSV
    # 根据运行位置决定输出路径
    if os.path.exists('7_MostCited'):
        output_csv = '7_MostCited/most_cited_articles.csv'
    else:
        output_csv = 'most_cited_articles.csv'
    columns_to_save = ['Title', 'Authors', 'Pages', 'Access', 'URL', 'Abstract', 
                       'PubDate', 'DOI', 'Citations', 'ParsedDate']
    df_sorted[columns_to_save].to_csv(output_csv, index=False)
    
    print(f"\n✅ 已保存: {output_csv}")
    
    # 显示 Top 10
    if len(df_sorted) > 0:
        print("\n📈 Top 10 Most Cited:")
        top10 = df_sorted.head(10)
        for idx, row in top10.iterrows():
            print(f"   {row.get('Citations', 0):3d} 引用 - {row['Title'][:60]}...")
    
    print("\n" + "=" * 70)
    print("✅ 完成")
    print("=" * 70)

if __name__ == '__main__':
    main()
