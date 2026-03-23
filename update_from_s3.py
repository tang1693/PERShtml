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
    
    # 根据 Article Category 判断
    is_inpress = df_excel['Article Category'].str.contains('In-Press', case=False, na=False)
    
    # Pages: In-Press 用日期，Research Article 用页码（加 pp. 前缀）
    result_df['Pages'] = df_excel.apply(
        lambda row: row['Date MMDDYY'].strftime('%B %-d, %Y') 
                    if 'In-Press' in str(row['Article Category']) 
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

def add_ga_paths(df, year, issue_no):
    """为每篇文章添加 GA_Path（基于文件名前缀匹配）"""
    ga_dir = f'IssuesArticles/html/img/{year}/{issue_no}'
    
    if not os.path.exists(ga_dir):
        print(f"   ⚠️  GA 目录不存在: {ga_dir}")
        return df
    
    base_url = f"https://raw.githubusercontent.com/tang1693/PERShtml/refs/heads/main/IssuesArticles/html/img/{year}/{issue_no}"
    
    # 获取目录中的所有文件
    ga_files = os.listdir(ga_dir)
    
    for idx, row in df.iterrows():
        title = row['Title']
        
        # 策略：使用标题的前几个单词生成前缀，与文件名匹配
        # 1. 清理标题，转为下划线格式
        title_clean = re.sub(r'[^\w\s-]', '', title)
        title_clean = re.sub(r'\s+', '_', title_clean)
        
        # 2. 取前50个字符作为前缀
        title_prefix = title_clean[:50].lower()
        
        # 3. 尝试匹配文件名（文件名也是下划线格式）
        matched_file = None
        best_match_len = 0
        
        for ga_file in ga_files:
            ga_file_lower = ga_file.lower()
            # 查找最长的公共前缀
            common_len = 0
            for i, (c1, c2) in enumerate(zip(title_prefix, ga_file_lower)):
                if c1 == c2:
                    common_len = i + 1
                else:
                    break
            
            # 如果匹配超过20个字符，且是当前最佳匹配
            if common_len > 20 and common_len > best_match_len:
                best_match_len = common_len
                matched_file = ga_file
        
        if matched_file:
            df.loc[idx, 'GA_Path'] = f"{base_url}/{matched_file}"
            print(f"   ✅ GA: {title[:50]}... -> {matched_file[:50]}...")
        else:
            print(f"   ⚠️  未找到 GA: {title[:50]}...")
    
    return df

def download_ga_images(df, year, issue_no):
    """下载图形摘要图片"""
    output_dir = f'IssuesArticles/html/img/{year}/{issue_no}'
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n📥 下载 GA 图片到: {output_dir}")
    
    success_count = 0
    for index, row in df.iterrows():
        title = row['Title']
        ga_link = row['GA_Link']
        
        if pd.isna(ga_link):
            print(f"   ⚠️  无 GA 链接: {title[:50]}...")
            continue
        
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

def update_module_2_issues(year, issue_no, month_name):
    """更新模块2: Issues"""
    print("\n📌 模块 2: Issues")
    
    html_path = 'issues.html'
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    issue_key = f"{year}{issue_no}"
    volume = int(year) - 1934
    
    # 检查是否已存在
    if f"No. {int(issue_no)}, {month_name} {year}" in content:
        print(f"   ℹ️  {month_name} {year} 已存在，跳过")
        return
    
    # 新条目
    new_issue = f'''
<li>
<a href="javascript:void(0);" onclick="openCustomModal('https://tang1693.github.io/PERShtml/IssuesArticles/html/{issue_key}.html');">No. {int(issue_no)}, {month_name} {year}</a> <strong style="color: red;">NEW</strong>
</li>'''
    
    # 移除旧的 NEW 标记
    content = content.replace('<strong style="color: red;">NEW</strong>\n</li>', '</li>')
    
    # 插入新条目
    vol_header = f'<li class="issueVolume" style="font-size: 12px; font-weight: 700;">Volume {volume}</li>'
    content = content.replace(vol_header, vol_header + new_issue)
    
    # 保存
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"   ✅ 已更新: {html_path}")
    print(f"      添加: No. {int(issue_no)}, {month_name} {year}")

def update_module_5_recent(df_research):
    """更新模块5: Recent Articles"""
    print("\n📌 模块 5: Recent Articles")
    
    if len(df_research) == 0:
        print("   ⚠️  本月没有 Research Article，跳过")
        return
    
    csv_path = '5_RecentArticles/filtered_articles_info_abs.csv'
    df_research[['Title', 'Authors', 'Pages', 'Access', 'URL', 'Abstract', 'PubDate', 'IssueKey']].to_csv(
        csv_path, index=False
    )
    print(f"   ✅ 已更新: {csv_path} ({len(df_research)} 篇)")
    
    # 生成 HTML
    import subprocess
    result = subprocess.run(['python3', '5_RecentArticles/recent_article_2generate_html.py'], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"   ✅ 已生成: open_access_articles.html & member_only_articles.html")
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
    df_inpress = df[df['Category'].str.contains('In-Press', case=False, na=False)]
    df_research = df[df['Category'].str.contains('Research', case=False, na=False)]
    
    print(f"\n📊 文章分类:")
    print(f"   In-Press: {len(df_inpress)} 篇")
    print(f"   Research Article: {len(df_research)} 篇")
    
    # 5. 提取期刊信息
    year = df['Year'].iloc[0]
    issue_no = df['Issue'].iloc[0]
    month_name = df['PubDate'].iloc[0].split()[0]
    
    print(f"\n🎯 本次更新目标: {year} 年 {int(issue_no)} 月 ({month_name})")
    
    # 6. 下载 GA 图片（仅 Research Article）
    if len(df_research) > 0:
        download_ga_images(df_research, year, issue_no)
        df_research = add_ga_paths(df_research, year, issue_no)
    
    # 7. 更新各模块
    update_module_1_inpress(df_inpress)
    
    if len(df_research) > 0:
        update_module_2_issues(year, issue_no, month_name)
        update_module_5_recent(df_research)
        update_module_6_articles(df_research)
    
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
    print("\n💡 下一步:")
    print(f"   1. 检查生成的 HTML 文件")
    print(f"   2. git add . && git commit -m 'Update {month_name} {year}'")
    print(f"   3. git push")

if __name__ == '__main__':
    main()
