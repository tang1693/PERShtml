#!/usr/bin/env python3
"""
从 S3 元数据 Excel 转换为 PERShtml 各模块需要的 CSV 格式
"""
import pandas as pd
import os
from datetime import datetime

def convert_access_status(status):
    """转换访问状态：SUB -> Subscribed content, OA -> Open access"""
    return "Open access" if status == "OA" else "Subscribed content"

def build_url_from_doi(doi):
    """从 DOI 构建文章 URL"""
    return f"https://doi.org/{doi}"

def format_date_as_pages(date_obj):
    """将日期格式化为类似 'March 1, 2026' 的字符串（用于 InPress）"""
    return date_obj.strftime("%B %-d, %Y")

def convert_metadata_to_csv(excel_path, output_csv_path, module_type='inpress'):
    """
    转换元数据 Excel 到 CSV 格式
    
    Args:
        excel_path: S3 下载的 Excel 文件路径
        output_csv_path: 输出 CSV 路径
        module_type: 模块类型 ('inpress', 'issues', 'recent', 'all')
    """
    # 读取 Excel
    df = pd.read_excel(excel_path)
    
    print(f"读取到 {len(df)} 条记录")
    
    # 清理作者名中的数字
    def clean_authors(authors):
        import re
        cleaned = re.sub(r'\s*\d+\s*[;,]', ';', str(authors))
        cleaned = re.sub(r'\s*\d+\s*$', '', cleaned)
        cleaned = re.sub(r';;+', ';', cleaned)
        return cleaned.strip()
    
    df['Authors'] = df['Authors'].apply(clean_authors)
    
    # 转换为目标格式
    result_df = pd.DataFrame()
    result_df['Title'] = df['Title']
    result_df['Authors'] = df['Authors']
    
    # Pages 字段根据模块类型不同而不同
    if module_type == 'inpress':
        # InPress 使用日期
        result_df['Pages'] = df['Date MMDDYY'].apply(format_date_as_pages)
    else:
        # Issues/Recent/All 使用页码，添加 "pp. " 前缀
        result_df['Pages'] = 'pp. ' + df['Page Numbers'].astype(str)
    
    # Access 字段
    result_df['Access'] = df['Access Status'].apply(convert_access_status)
    
    # URL 从 DOI 构建
    result_df['URL'] = df['DOI'].apply(build_url_from_doi)
    
    # Abstract
    result_df['Abstract'] = df['Abstract']
    
    # 添加发布日期（用于 Recent Articles）
    result_df['PubDate'] = df['Date MMDDYY'].dt.strftime('%B %Y')
    
    # 添加 IssueKey（用于分组）
    year = df['Date MMDDYY'].dt.year.iloc[0]
    issue = str(df['Issue Number'].iloc[0]).zfill(2)
    result_df['IssueKey'] = f"{year}{issue}"
    
    # 添加 GA 链接
    result_df['GA_Link'] = df['Graphical Abstract']
    
    # 保存 CSV
    result_df.to_csv(output_csv_path, index=False)
    print(f"✅ 已生成：{output_csv_path}")
    print(f"   共 {len(result_df)} 条记录")
    
    return result_df

def main():
    # 配置
    excel_file = '26-04_April_metadata.xlsx'
    
    if not os.path.exists(excel_file):
        print(f"❌ 错误：找不到文件 {excel_file}")
        return
    
    # 创建输出目录（如果不存在）
    os.makedirs('output', exist_ok=True)
    
    print("=" * 60)
    print("🔄 开始转换 S3 元数据...")
    print("=" * 60)
    
    # 1. InPress 模块
    print("\n📌 模块 1: InPress")
    convert_metadata_to_csv(
        excel_file, 
        '1_InPress/filtered_InPress_articles_info_abs.csv',
        module_type='inpress'
    )
    
    # 2. Issues 模块（暂时使用同样数据，后续可以根据需求调整）
    print("\n📌 模块 2: Issues")
    # Issues 模块主要是生成 issues.html，不需要额外 CSV
    print("   ℹ️  Issues 模块从期刊结构生成，无需单独 CSV")
    
    # 5. Recent Articles 模块
    print("\n📌 模块 5: Recent Articles")
    df = pd.read_excel(excel_file)
    
    # 分别生成 OA 和订阅文章
    df_oa = df[df['Access Status'] == 'OA']
    df_sub = df[df['Access Status'] == 'SUB']
    
    print(f"   开放获取文章: {len(df_oa)} 篇")
    print(f"   订阅文章: {len(df_sub)} 篇")
    
    # 保存到 Recent Articles 目录
    if len(df_oa) > 0:
        convert_metadata_to_csv(
            excel_file,
            '5_RecentArticles/open_access_pool.csv',
            module_type='recent'
        )
    
    if len(df_sub) > 0:
        convert_metadata_to_csv(
            excel_file,
            '5_RecentArticles/member_only_pool.csv',
            module_type='recent'
        )
    
    # 6. IssuesArticles 模块（追加到总库）
    print("\n📌 模块 6: IssuesArticles")
    convert_metadata_to_csv(
        excel_file,
        'output/april_2026_articles.csv',
        module_type='all'
    )
    
    # 检查是否需要追加到总库
    all_articles_path = '6_IssuesArticles/ALL_articles_Update_cleaned.csv'
    if os.path.exists(all_articles_path):
        existing_df = pd.read_csv(all_articles_path)
        new_df = pd.read_csv('output/april_2026_articles.csv')
        
        # 合并（去重）
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        combined_df.drop_duplicates(subset=['Title', 'URL'], keep='last', inplace=True)
        
        # 保存备份
        backup_path = f'6_IssuesArticles/ALL_articles_Update_cleaned.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        existing_df.to_csv(backup_path, index=False)
        print(f"   📦 已备份原数据到：{backup_path}")
        
        # 保存新数据
        combined_df.to_csv(all_articles_path, index=False)
        print(f"   ✅ 已更新总库：{all_articles_path}")
        print(f"      原有: {len(existing_df)} 条")
        print(f"      新增: {len(new_df)} 条")
        print(f"      总计: {len(combined_df)} 条")
    else:
        print(f"   ⚠️  未找到总库文件，请手动检查")
    
    print("\n" + "=" * 60)
    print("✅ 转换完成！")
    print("=" * 60)

if __name__ == '__main__':
    main()
