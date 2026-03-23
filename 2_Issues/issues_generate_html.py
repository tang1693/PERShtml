import os
import glob
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil.relativedelta import relativedelta

def calculate_volume(year):
    """计算卷号（基于年份）"""
    return year - 1934

def is_full_access(year, issue_no):
    """
    判断是否为 Full access
    规则：12个月之前的都是 Full access
    
    例如：当前 2026-03，则 2025-03 及之前的都是 Full access
    """
    current_date = datetime.now()
    twelve_months_ago = current_date - relativedelta(months=12)
    
    issue_date = datetime(year, issue_no, 1)
    
    return issue_date <= twelve_months_ago

def generate_issue_links(year, volume, start_issue=1, end_issue=12):
    """生成指定年份的所有 issue"""
    issues = []
    base_url = "https://tang1693.github.io/PERShtml/IssuesArticles/html"
    
    for issue in range(end_issue, start_issue - 1, -1):  # 从 12月到1月倒序
        issue_key = f"{year}{issue:02d}"
        issue_url = f"{base_url}/{issue_key}.html"
        
        # 月份缩写（Apr, Mar, Feb 等）
        month_abbr = datetime(year, issue, 1).strftime('%b')
        issue_name = f"No. {issue}, {month_abbr} {year}"
        
        # 判断 Full access
        full_access = is_full_access(year, issue)
        
        issues.append((issue_url, issue_name, full_access))
    
    return issues

def get_latest_issue():
    """
    扫描 IssuesArticles/html/ 目录，找出最新的期号
    返回 (year, issue_no)
    """
    html_files = glob.glob('IssuesArticles/html/2*.html')
    if not html_files:
        # 如果没有文件，返回当前月份
        now = datetime.now()
        return now.year, now.month
    
    # 提取所有 YYYYMM
    issue_keys = []
    for f in html_files:
        basename = os.path.basename(f).replace('.html', '')
        if len(basename) == 6 and basename.isdigit():
            year = int(basename[:4])
            issue = int(basename[4:])
            issue_keys.append((year, issue))
    
    if not issue_keys:
        now = datetime.now()
        return now.year, now.month
    
    # 返回最新的
    return max(issue_keys)

def generate_html():
    """生成完整的 issues.html"""
    start_year = 2003
    latest_year, latest_issue = get_latest_issue()
    base_url = "https://tang1693.github.io/PERShtml/IssuesArticles/html"

    # JavaScript for modal
    script_block = '''
    <script>
        function openCustomModal(url) {
            const modal = document.getElementById('customModal');
            const iframe = document.getElementById('customModalContent');
            iframe.src = url;
            modal.style.display = 'block';
        }

        function closeCustomModal() {
            const modal = document.getElementById('customModal');
            const iframe = document.getElementById('customModalContent');
            modal.style.display = 'none';
            iframe.src = '';
        }
        
        function closeCustomModalOnOutsideClick(event) {
            const modal = document.getElementById('customModal');
            if (event.target === modal) {
                closeCustomModal();
            }
        }
    </script>
    '''

    # HTML header
    html_output = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PE&RS Issues</title>
        {script_block}
    </head>
    <body>
    <div style="margin: 40px;">
        <div style="display: flex; flex-wrap: wrap; gap: 20px;">
    '''

    # 生成所有年份的 issues
    for year in range(latest_year, start_year - 1, -1):
        volume = calculate_volume(year)
        start_issue = 1
        end_issue = 12 if year != latest_year else latest_issue

        issues = generate_issue_links(year, volume, start_issue, end_issue)
        
        html_output += f'''
        <div style="flex: 1 1 calc(20% - 20px);">
            <ul class="bobby" style="padding: 0; list-style: none;">
                <li class="issueVolume" style="font-size: 12px; font-weight: 700;">Volume {volume}</li>
        '''
        
        for issue_url, issue_name, full_access in issues:
            # 提取期号
            issue_no = int(issue_name.split(",")[0].replace("No. ", "").strip())
            
            # 判断是否是最新一期
            is_latest = (year == latest_year and issue_no == latest_issue)
            
            # 构建 HTML
            if is_latest:
                access_html = ' <strong style="color: red;">NEW</strong>'
            elif full_access:
                access_html = ' <strong style="color: green;">Full access</strong>'
            else:
                access_html = ''
            
            html_output += f'''
                <li>
                    <a href="javascript:void(0);" onclick="openCustomModal('{issue_url}');">{issue_name}</a>{access_html}
                </li>
            '''

        html_output += '''
            </ul>
        </div>
        '''

    # HTML footer
    html_output += '''
        </div>
        <div style="text-align: center; margin-top: 20px;">
        </div>
    </div>

    <!-- Modal structure -->
    <div id="customModal" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.8); z-index: 1000; text-align: center; padding-top: 50px;" onclick="closeCustomModalOnOutsideClick(event);">
        <div style="position: relative; display: inline-block; width: 70%; height: 95%; background: #fff; border-radius: 10px; overflow: hidden;" onclick="event.stopPropagation();">
            <div style="position: absolute; top: 10px; right: 10px; font-size: 18px; padding: 5px 10px; background: red; color: white; border: none; border-radius: 5px; cursor: pointer;" onclick="closeCustomModal();">
                Close
            </div>
            <iframe id="customModalContent" src="" style="width: 100%; height: 100%; border: none;"></iframe>
        </div>
    </div>
    </body>
    </html>
    '''

    return html_output

# 生成 HTML
html_content = generate_html()

# 保存（自动检测运行位置）
output_path = '../issues.html' if os.path.basename(os.getcwd()) == '2_Issues' else 'issues.html'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"✅ issues.html 已生成: {output_path}")
