#!/usr/bin/env python3
"""
一键更新脚本：从 S3 元数据自动更新所有模块
用法: python update_from_s3.py <excel_filename>
示例: python update_from_s3.py 26-04_April_metadata.xlsx
"""
import sys
import os
import pandas as pd
import gdown
import re
from datetime import datetime

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

def parse_excel_metadata(excel_path):
    """解析 Excel 元数据"""
    print(f"\n📊 解析元数据: {excel_path}")
    df = pd.read_excel(excel_path)
    
    print(f"   发现 {len(df)} 篇文章")
    print(f"   期刊: {df['Volume'].iloc[0]}, Issue {df['Issue Number'].iloc[0]}")
    
    return df

def check_new_articles(df_new):
    """检查哪些文章是新增的"""
    csv_path = '6_IssuesArticles/ALL_articles_Update_cleaned.csv'
    
    if not os.path.exists(csv_path):
        print(f"⚠️  未找到现有数据文件: {csv_path}")
        return df_new
    
    df_existing = pd.read_csv(csv_path)
    
    # 使用 DOI 作为唯一标识
    existing_dois = set(df_existing['URL'].str.replace('https://doi.org/', '').values)
    new_dois = df_new['DOI'].values
    
    new_articles = df_new[~df_new['DOI'].isin(existing_dois)]
    
    print(f"\n🔍 数据对比:")
    print(f"   现有文章: {len(df_existing)} 篇")
    print(f"   本次提取: {len(df_new)} 篇")
    print(f"   新增文章: {len(new_articles)} 篇")
    
    return new_articles

def convert_to_csv_format(df_excel):
    """转换为标准 CSV 格式"""
    result_df = pd.DataFrame()
    result_df['Title'] = df_excel['Title']
    result_df['Authors'] = df_excel['Authors']
    result_df['Pages'] = df_excel['Page Numbers']
    result_df['Access'] = df_excel['Access Status'].apply(
        lambda x: "Open Access content" if x == "OA" else "Subscribed content"
    )
    result_df['URL'] = df_excel['DOI'].apply(lambda x: f"https://doi.org/{x}")
    result_df['Abstract'] = df_excel['Abstract']
    
    # 添加元数据
    result_df['Year'] = df_excel['Date MMDDYY'].dt.year.astype(str)
    result_df['Volume'] = df_excel['Volume'].astype(str)
    result_df['Issue'] = df_excel['Issue Number'].astype(str).str.zfill(2)
    result_df['IssueKey'] = result_df['Year'] + result_df['Issue']
    result_df['PubDate'] = df_excel['Date MMDDYY'].dt.strftime('%B %Y')
    result_df['GA_Link'] = df_excel['Graphical Abstract']
    
    return result_df

def download_ga_images(df, year, issue_no):
    """下载图形摘要图片"""
    output_dir = f'IssuesArticles/html/img/{year}/{issue_no}'
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n📥 下载 GA 图片到: {output_dir}")
    
    success_count = 0
    for index, row in df.iterrows():
        title = row['Title']
        ga_link = row['GA_Link']
        
        # 生成安全文件名
        safe_title = re.sub(r'[^\w\s-]', '', title).strip()
        safe_title = re.sub(r'[\s]+', '_', safe_title)[:100]
        
        # 提取 Google Drive file ID
        match = re.search(r'/d/([^/]+)/', ga_link)
        if not match:
            print(f"   ⚠️  无法解析链接: {title[:50]}...")
            continue
        
        file_id = match.group(1)
        output_path = os.path.join(output_dir, f"{safe_title}.png")
        
        # 如果文件已存在，跳过
        if os.path.exists(output_path):
            print(f"   ⏭️  已存在: {safe_title[:60]}...")
            success_count += 1
            continue
        
        try:
            print(f"   📥 下载: {title[:60]}...")
            gdown.download(f"https://drive.google.com/uc?id={file_id}", output_path, quiet=True)
            success_count += 1
        except Exception as e:
            print(f"   ❌ 失败: {str(e)}")
    
    print(f"\n✅ GA 图片下载完成: {success_count}/{len(df)}")

def update_module_1_inpress(df):
    """更新模块1: InPress"""
    print("\n📌 模块 1: InPress")
    
    csv_path = '1_InPress/filtered_InPress_articles_info_abs.csv'
    df.to_csv(csv_path, index=False)
    print(f"   ✅ 已更新: {csv_path}")
    
    # 生成 HTML
    import subprocess
    result = subprocess.run(['python3', '1_InPress/3_csv_2_html.py'], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"   ✅ 已生成: in_press_articles.html")
    else:
        print(f"   ❌ HTML 生成失败: {result.stderr}")

def update_module_2_issues(year, issue_no, month_name):
    """更新模块2: Issues"""
    print("\n📌 模块 2: Issues")
    
    html_path = 'issues.html'
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 新条目
    issue_key = f"{year}{issue_no}"
    new_issue = f'''
<li>
<a href="javascript:void(0);" onclick="openCustomModal('https://tang1693.github.io/PERShtml/IssuesArticles/html/{issue_key}.html');">No. {int(issue_no)}, {month_name} {year}</a> <strong style="color: red;">NEW</strong>
</li>'''
    
    # 移除旧的 NEW 标记
    content = content.replace('<strong style="color: red;">NEW</strong>\n</li>', '</li>')
    
    # 插入新条目
    volume = int(year) - 1934
    vol_header = f'<li class="issueVolume" style="font-size: 12px; font-weight: 700;">Volume {volume}</li>'
    content = content.replace(vol_header, vol_header + new_issue)
    
    # 保存
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"   ✅ 已更新: {html_path}")
    print(f"      添加: No. {int(issue_no)}, {month_name} {year}")

def update_module_5_recent(df):
    """更新模块5: Recent Articles"""
    print("\n📌 模块 5: Recent Articles")
    
    csv_path = '5_RecentArticles/filtered_articles_info_abs.csv'
    df.to_csv(csv_path, index=False)
    print(f"   ✅ 已更新: {csv_path}")
    
    # 生成 HTML
    import subprocess
    result = subprocess.run(['python3', '5_RecentArticles/recent_article_2generate_html.py'], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"   ✅ 已生成: open_access_articles.html & member_only_articles.html")
    else:
        print(f"   ❌ HTML 生成失败: {result.stderr}")

def update_module_6_articles(df):
    """更新模块6: IssuesArticles"""
    print("\n📌 模块 6: IssuesArticles")
    
    # 追加到总库
    all_csv_path = '6_IssuesArticles/ALL_articles_Update_cleaned.csv'
    
    if os.path.exists(all_csv_path):
        existing_df = pd.read_csv(all_csv_path)
        
        # 备份
        backup_path = f'6_IssuesArticles/ALL_articles_Update_cleaned.backup.{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        existing_df.to_csv(backup_path, index=False)
        print(f"   📦 已备份: {backup_path}")
        
        # 只保留需要的列（兼容旧格式）
        df_append = df[['Title', 'Authors', 'Pages', 'Access', 'URL', 'Abstract']].copy()
        df_append['IssueKey'] = df['IssueKey'].iloc[0]
        
        # 合并
        combined_df = pd.concat([existing_df, df_append], ignore_index=True)
        combined_df.drop_duplicates(subset=['Title', 'URL'], keep='last', inplace=True)
        
        combined_df.to_csv(all_csv_path, index=False)
        print(f"   ✅ 已更新: {all_csv_path}")
        print(f"      原有: {len(existing_df)} 条 | 新增: {len(df_append)} 条 | 总计: {len(combined_df)} 条")
    else:
        print(f"   ⚠️  未找到现有文件，创建新文件")
        df[['Title', 'Authors', 'Pages', 'Access', 'URL', 'Abstract', 'IssueKey']].to_csv(all_csv_path, index=False)
    
    # 生成 HTML
    import subprocess
    result = subprocess.run(['python3', '6_IssuesArticles/generate_article_page_v2.py'], capture_output=True, text=True)
    if result.returncode == 0:
        issue_key = df['IssueKey'].iloc[0]
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
    
    # 4. 检查新增
    new_articles = check_new_articles(df)
    
    if len(new_articles) == 0:
        print("\n✅ 没有新文章，无需更新")
        return
    
    # 5. 提取期刊信息
    year = df['Year'].iloc[0]
    issue_no = df['Issue'].iloc[0]
    month_name = df['PubDate'].iloc[0].split()[0]  # 提取月份名
    
    print(f"\n🎯 本次更新目标: {year} 年 {int(issue_no)} 月 ({month_name})")
    
    # 6. 下载 GA 图片
    download_ga_images(df, year, issue_no)
    
    # 7. 更新各模块
    update_module_1_inpress(df)
    update_module_2_issues(year, issue_no, month_name)
    update_module_5_recent(df)
    update_module_6_articles(df)
    
    print("\n" + "=" * 70)
    print("✅ 所有模块更新完成！")
    print("=" * 70)
    print("\n📋 生成的文件:")
    print("   - in_press_articles.html")
    print("   - issues.html")
    print("   - open_access_articles.html")
    print("   - member_only_articles.html")
    print(f"   - IssuesArticles/html/{year}{issue_no}.html")
    print("\n💡 下一步:")
    print("   1. 检查生成的 HTML 文件")
    print("   2. git add . && git commit -m 'Update {month_name} {year}'")
    print("   3. git push")

if __name__ == '__main__':
    main()
