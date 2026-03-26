#!/usr/bin/env python3
"""
一键更新脚本：从 S3 元数据自动更新所有模块
用法: python update_from_s3.py <excel_filename>
示例: python update_from_s3.py 26-04_April_metadata.xlsx
"""
import sys
import os
import subprocess
import pandas as pd
import gdown
import re
from datetime import datetime

INPRESS_PATTERN = re.compile(r'in[\s-]?press', re.IGNORECASE)


def is_inpress_category(value):
    """判断是否为 In-Press 类别（兼容 In-Press/InPress/In Press）"""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return False
    return bool(INPRESS_PATTERN.search(str(value)))


INPRESS_PATTERN = re.compile(r'in[\s-]?press', re.IGNORECASE)


def is_inpress_category(value):
    """判断是否为 In-Press 类别（兼容 In-Press/InPress/In Press）"""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return False
    return bool(INPRESS_PATTERN.search(str(value)))


# AWS 配置（从环境变量读取，不要硬编码！）
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

if not AWS_ACCESS_KEY or not AWS_SECRET_KEY:
    print("❌ 错误: 未设置 AWS 凭证环境变量")
    print("   请先运行:")
    print("   export AWS_ACCESS_KEY_ID='your_key'")
    print("   export AWS_SECRET_ACCESS_KEY='your_secret'")
    sys.exit(1)

def download_from_s3(excel_filename):
    """从 S3 下载元数据文件"""
    print(f"\n📥 正在从 S3 下载 {excel_filename}...")
    
    import subprocess
    cmd = [
        'aws', 's3', 'cp',
        f's3://persearlyaccess/Metadata/{excel_filename}',
        excel_filename
    ]
    env = os.environ.copy()
    env['AWS_ACCESS_KEY_ID'] = AWS_ACCESS_KEY
    env['AWS_SECRET_ACCESS_KEY'] = AWS_SECRET_KEY
    env['AWS_DEFAULT_REGION'] = 'us-east-1'
    
    result = subprocess.run(cmd, env=env, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ 下载失败: {result.stderr}")
        return False
    
    print(f"✅ 已下载到: {excel_filename}")
    return True

def clean_authors(authors):
    """清理作者名中的数字"""
    cleaned = re.sub(r'\s*\d+\s*[;,]', ';', str(authors))
    cleaned = re.sub(r'\s*\d+\s*$', '', cleaned)
    cleaned = re.sub(r';;+', ';', cleaned)
    return cleaned.strip()

def parse_excel_metadata(excel_path):
    """解析 Excel 元数据"""
    print(f"\n📊 解析元数据: {excel_path}")
    df = pd.read_excel(excel_path)
    
    # 清理作者名
    df['Authors'] = df['Authors'].apply(clean_authors)
    
    print(f"   发现 {len(df)} 篇文章")
    print(f"   期刊: Volume {df['Volume'].iloc[0]}, Issue {df['Issue Number'].iloc[0]}")
    
    return df

def convert_to_csv_format(df_excel):
    """转换为标准 CSV 格式"""
    result_df = pd.DataFrame()
    result_df['Title'] = df_excel['Title']
    result_df['Authors'] = df_excel['Authors']
    
    # Pages: In-Press 用日期，Research Article 用页码（加 pp. 前缀）
    result_df['Pages'] = df_excel.apply(
        lambda row: row['Date MMDDYY'].strftime('%B %-d, %Y')
        if is_inpress_category(row['Article Category'])
        else f"pp. {row['Page Numbers']}",
        axis=1
    )
    
    result_df['Access'] = df_excel['Access Status'].apply(
        lambda x: "Open Access content" if x == "OA" else "Subscribed content"
    )
    result_df['URL'] = df_excel['DOI'].apply(lambda x: f"https://doi.org/{x}")
    result_df['Abstract'] = df_excel['Abstract']
    
    # 添加元数据
    result_df['PubDate'] = df_excel['Date MMDDYY'].dt.strftime('%B %Y')
    result_df['Year'] = df_excel['Date MMDDYY'].dt.year.astype(str)
    result_df['Volume'] = df_excel['Volume'].astype(str)
    result_df['Issue'] = df_excel['Issue Number'].astype(str).str.zfill(2)
    result_df['IssueKey'] = result_df['Year'] + result_df['Issue']
    result_df['GA_Link'] = df_excel['Graphical Abstract']
    result_df['Category'] = df_excel['Article Category']
    
    return result_df


def download_ga_images(df, year, issue_no):
    """下载图形摘要图片并在 DataFrame 中添加 GA_Path
    
    关键逻辑：
    - Excel 每一行就是一条完整记录（包括 GA_Link）
    - 下载后在**同一行**添加 GA_Path
    - 文件名用 file_id（或任意唯一名），无需匹配
    - 生成 HTML 时，同一行的数据自然对应
    """
    output_dir = f'IssuesArticles/html/img/{year}/{issue_no}'
    os.makedirs(output_dir, exist_ok=True)
    
    base_url = f"https://raw.githubusercontent.com/tang1693/PERShtml/refs/heads/main/IssuesArticles/html/img/{year}/{issue_no}"
    
    print(f"\n📥 下载 GA 图片到: {output_dir}")
    
    success_count = 0
    for index, row in df.iterrows():
        title = row['Title']
        ga_link = row['GA_Link']
        
        if pd.isna(ga_link):
            print(f"   ⚠️  无 GA 链接: {title[:50]}...")
            continue
        
        # 提取 Google Drive file ID
        match = re.search(r'/d/([^/]+)/', ga_link)
        if not match:
            print(f"   ⚠️  无法解析链接: {title[:50]}...")
            continue
        
        file_id = match.group(1)
        # 文件名就用 file_id（唯一且简单）
        filename = f"{file_id}.png"
        output_path = os.path.join(output_dir, filename)
        
        # 下载（如果不存在）
        if os.path.exists(output_path):
            print(f"   ⏭️  {title[:50]}... (已存在)")
            success_count += 1
        else:
            try:
                print(f"   📥 {title[:50]}...")
                gdown.download(f"https://drive.google.com/uc?id={file_id}", output_path, quiet=True)
                success_count += 1
            except Exception as e:
                print(f"   ❌ 下载失败: {str(e)}")
                continue
        
        # 关键：在同一行添加 GA_Path
        # HTML 生成时会读取同一行的所有数据，自然对应
        df.loc[index, 'GA_Path'] = f"{base_url}/{filename}"
    
    print(f"\n✅ GA 下载: {success_count}/{len(df)}")
    return df

def update_module_1_inpress(df_inpress):
    """更新模块1: InPress"""
    print("\n📌 模块 1: InPress")
    
    if len(df_inpress) == 0:
        print("   ℹ️  本月没有 In-Press 文章，生成空文件")
        pd.DataFrame(columns=['Title', 'Authors', 'Pages', 'Access', 'URL', 'Abstract']).to_csv(
            '1_InPress/filtered_InPress_articles_info_abs.csv', index=False
        )
    else:
        df_inpress[['Title', 'Authors', 'Pages', 'Access', 'URL', 'Abstract']].to_csv(
            '1_InPress/filtered_InPress_articles_info_abs.csv', index=False
        )
        print(f"   ✅ 已更新: 1_InPress/filtered_InPress_articles_info_abs.csv ({len(df_inpress)} 篇)")
    
    # 生成 HTML
    import subprocess
    result = subprocess.run(['python3', '1_InPress/3_csv_2_html.py'], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"   ✅ 已生成: in_press_articles.html")
    else:
        print(f"   ❌ HTML 生成失败: {result.stderr}")

def update_module_2_issues():
    """更新模块2: Issues - 重新生成整个 issues.html"""
    print("\n📌 模块 2: Issues")
    
    # 运行 issues_generate_html.py 重新生成
    result = subprocess.run(
        ['python3', '2_Issues/issues_generate_html.py'],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print(f"   ✅ issues.html 已重新生成")
    else:
        print(f"   ❌ 生成失败: {result.stderr}")

def update_module_5_recent():
    """
    更新模块5: Recent Articles
    从 ALL_articles_Update_cleaned.csv 提取最近6个月的所有文章
    """
    print("\n📌 模块 5: Recent Articles")
    
    from dateutil.relativedelta import relativedelta
    
    # 读取总库
    all_csv = '6_IssuesArticles/ALL_articles_Update_cleaned.csv'
    if not os.path.exists(all_csv):
        print(f"   ⚠️  {all_csv} 不存在，跳过")
        return
    
    df_all = pd.read_csv(all_csv)
    
    # 解析日期：优先从 IssueKey，否则从 URL 解析
    def parse_issue_date(row):
        """解析文章的发布日期"""
        # 方法1: 从 IssueKey
        if pd.notna(row.get('IssueKey')):
            try:
                issue_key_str = str(int(row['IssueKey']))
                if len(issue_key_str) == 6:
                    year = int(issue_key_str[:4])
                    month = int(issue_key_str[4:])
                    return datetime(year, month, 1)
            except:
                pass
        
        # 方法2: 从 Ingenta URL 解析
        # 格式: .../pers/{year}/0000{volume}/0000{issue}/...
        url = row.get('URL', '')
        if 'ingentaconnect.com' in url:
            import re
            match = re.search(r'/pers/(\d{4})/\d+/(\d+)/', url)
            if match:
                year = int(match.group(1))
                issue = int(match.group(2))  # 去掉前导0
                return datetime(year, issue, 1)
        
        return None
    
    df_all['IssueDate'] = df_all.apply(parse_issue_date, axis=1)
    
    # 计算6个月前的日期
    current_date = datetime.now()
    six_months_ago = current_date - relativedelta(months=6)
    
    # 筛选最近6个月的文章（基于 IssueKey）
    df_recent = df_all[df_all['IssueDate'].notna()].copy()
    df_recent = df_recent[df_recent['IssueDate'] >= six_months_ago]
    
    # 按日期倒序排序
    df_recent = df_recent.sort_values('IssueDate', ascending=False)
    
    # 补充 PubDate（如果没有）
    for idx, row in df_recent.iterrows():
        if pd.isna(row.get('PubDate')) and pd.notna(row['IssueDate']):
            df_recent.loc[idx, 'PubDate'] = row['IssueDate'].strftime('%B %Y')
    
    # 保存到 CSV
    csv_path = '5_RecentArticles/filtered_articles_info_abs.csv'
    columns = ['Title', 'Authors', 'Pages', 'Access', 'URL', 'Abstract', 'PubDate', 'IssueKey']
    df_recent[columns].to_csv(csv_path, index=False)
    
    print(f"   ✅ 已更新: {csv_path} ({len(df_recent)} 篇，最近6个月)")
    
    # 显示月份分布
    month_counts = df_recent['IssueDate'].dt.strftime('%Y-%m').value_counts().sort_index(ascending=False)
    for month, count in month_counts.head(6).items():
        print(f"      {month}: {count} 篇")
    
    # 生成 HTML
    result = subprocess.run(['python3', '5_RecentArticles/recent_article_2generate_html.py'], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"   ✅ 已生成: open_access_articles.html & member_only_articles.html")
    else:
        print(f"   ❌ HTML 生成失败: {result.stderr}")

def update_module_7_most_cited():
    """更新模块7: Most Cited Articles（最近2年）"""
    print("\n📌 模块 7: Most Cited Articles")
    
    # 运行脚本：提取数据 + 获取引用数
    result = subprocess.run(
        ['python3', '7_MostCited/fetch_citations.py'],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"   ❌ 数据提取失败: {result.stderr}")
        return
    
    # 显示输出
    for line in result.stdout.split('\n'):
        if line.strip():
            print(f"   {line}")
    
    # 生成 HTML
    result = subprocess.run(
        ['python3', '7_MostCited/generate_html.py'],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print(f"   ✅ top_6_articles.html 已生成")
    else:
        print(f"   ❌ HTML 生成失败: {result.stderr}")

def update_module_6_articles(df_research):
    """更新模块6: IssuesArticles"""
    print("\n📌 模块 6: IssuesArticles")
    
    if len(df_research) == 0:
        print("   ⚠️  本月没有 Research Article，跳过")
        return
    
    # 追加到总库
    all_csv_path = '6_IssuesArticles/ALL_articles_Update_cleaned.csv'
    
    if os.path.exists(all_csv_path):
        existing_df = pd.read_csv(all_csv_path)
        
        # 备份
        backup_path = f'6_IssuesArticles/ALL_articles_Update_cleaned.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        existing_df.to_csv(backup_path, index=False)
        print(f"   📦 已备份: {backup_path}")
        
        # 删除本次 IssueKey 的旧数据（避免重复）
        issue_key = df_research['IssueKey'].iloc[0]
        existing_df = existing_df[existing_df['IssueKey'].astype(str) != issue_key]
        existing_df = existing_df[existing_df['IssueKey'].astype(str) != f"{issue_key}.0"]
        
        # 合并
        combined_df = pd.concat([existing_df, df_research], ignore_index=True)
        combined_df.drop_duplicates(subset=['Title', 'URL'], keep='last', inplace=True)
        
        combined_df.to_csv(all_csv_path, index=False)
        print(f"   ✅ 已更新: {all_csv_path}")
        print(f"      原有: {len(existing_df)} 条 | 新增: {len(df_research)} 条 | 总计: {len(combined_df)} 条")
    else:
        print(f"   ⚠️  未找到现有文件，创建新文件")
        df_research.to_csv(all_csv_path, index=False)
    
    # 清除 log 中的本期记录（强制重新生成）
    log_path = '6_IssuesArticles/processed_issues.log'
    if os.path.exists(log_path):
        with open(log_path, 'r') as f:
            lines = f.readlines()
        issue_key = df_research['IssueKey'].iloc[0]
        with open(log_path, 'w') as f:
            for line in lines:
                if issue_key not in line:
                    f.write(line)
    
    # 生成 HTML
    import subprocess
    result = subprocess.run(['python3', '6_IssuesArticles/generate_article_page_v3.py'], capture_output=True, text=True)
    if result.returncode == 0:
        issue_key = df_research['IssueKey'].iloc[0]
        print(f"   ✅ 已生成: IssuesArticles/html/{issue_key}.html")
    else:
        print(f"   ❌ HTML 生成失败: {result.stderr}")

def main():
    if len(sys.argv) < 2:
        print("用法: python update_from_s3.py <excel_filename>")
        print("示例: python update_from_s3.py 26-04_April_metadata.xlsx")
        sys.exit(1)
    
    excel_filename = sys.argv[1]
    
    print("=" * 70)
    print("🦞 PERShtml 自动更新工具 - 基于 S3 元数据")
    print("=" * 70)
    
    # 1. 下载 Excel
    if not os.path.exists(excel_filename):
        if not download_from_s3(excel_filename):
            sys.exit(1)
    
    # 2. 解析元数据
    df_excel = parse_excel_metadata(excel_filename)
    
    # 3. 转换格式
    df = convert_to_csv_format(df_excel)
    
    # 4. 分离 In-Press 和 Research Article
    inpress_mask = df['Category'].apply(is_inpress_category)
    research_mask = df['Category'].str.contains('Research', case=False, na=False)
    df_inpress = df[inpress_mask]
    df_research = df[research_mask & ~inpress_mask]
    
    print(f"\n📊 文章分类:")
    print(f"   In-Press: {len(df_inpress)} 篇")
    print(f"   Research Article: {len(df_research)} 篇")
    
    # 5. 提取期刊信息
    year = df['Year'].iloc[0]
    issue_no = df['Issue'].iloc[0]
    month_name = df['PubDate'].iloc[0].split()[0]
    
    print(f"\n🎯 本次更新目标: {year} 年 {int(issue_no)} 月 ({month_name})")
    
    # 6. 下载 GA 图片（仅 Research Article），同时添加 GA_Path
    if len(df_research) > 0:
        df_research = download_ga_images(df_research, year, issue_no)
    
    # 7. 更新各模块
    update_module_1_inpress(df_inpress)
    update_module_2_issues()  # 重新生成整个 issues.html
    
    if len(df_research) > 0:
        update_module_6_articles(df_research)
    
    update_module_5_recent()  # 总是更新（从总库提取最近6个月）
    update_module_7_most_cited()  # 总是更新（从总库提取最近2年+引用数）
    
    print("\n" + "=" * 70)
    print("✅ 所有模块更新完成！")
    print("=" * 70)
    print("\n📋 生成的文件:")
    print("   - in_press_articles.html")
    if len(df_research) > 0:
        print("   - issues.html")
        print("   - open_access_articles.html")
        print("   - member_only_articles.html")
        print(f"   - IssuesArticles/html/{year}{issue_no}.html")
    print("   - top_6_articles.html (最近2年，Top 6)")
    print("\n💡 下一步:")
    print(f"   1. 检查生成的 HTML 文件")
    print(f"   2. git add . && git commit -m 'Update {month_name} {year}'")
    print(f"   3. git push")

if __name__ == '__main__':
    main()
