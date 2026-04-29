#!/usr/bin/env python3
"""
发送 Telegram 消息通知
纯 Python 实现，无需 AI
"""

import os
import sys
import json
import urllib.request
import urllib.parse
from datetime import datetime

def send_telegram(message, chat_id=None, bot_token=None):
    """发送 Telegram 消息"""
    
    # 从环境变量读取（如果未提供）
    if not bot_token:
        bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    
    if not chat_id:
        chat_id = os.environ.get('TELEGRAM_CHAT_ID', '5469433156')
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN 未配置")
        return False
    
    # Telegram API endpoint
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    # 构建请求数据
    data = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML',
        'disable_web_page_preview': True
    }
    
    try:
        # 发送 POST 请求
        req_data = urllib.parse.urlencode(data).encode('utf-8')
        req = urllib.request.Request(url, data=req_data)
        
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            if result.get('ok'):
                print("✅ Telegram 消息发送成功")
                return True
            else:
                print(f"❌ Telegram API 错误: {result.get('description')}")
                return False
    
    except Exception as e:
        print(f"❌ 发送失败: {e}")
        return False

def format_daily_report(log_file=None):
    """格式化每日报告（纯程序生成，无 AI 参与）"""

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    message = f"""🦞 <b>PERShtml 每日检查报告</b>
<i>程序自动生成</i>

📅 时间: {now}
"""

    if log_file and os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            log_content = f.read()

        import re

        marker = '🦞 PERShtml 全自动更新'
        if marker in log_content:
            section_text = log_content[log_content.rfind(marker):]
        else:
            section_text = log_content
        lines = section_text.split('\n')

        # 📦 S3 文件列表（取最新一次）
        s3_files = []
        in_s3_section = False
        current_s3 = []
        for line in lines:
            if '📊 S3 文件列表:' in line:
                in_s3_section = True
                current_s3 = []
                continue
            if in_s3_section:
                stripped = line.strip()
                if stripped.startswith('-'):
                    current_s3.append(stripped[2:])
                elif not stripped or '📌' in stripped:
                    if current_s3:
                        s3_files = current_s3
                    in_s3_section = False
        if in_s3_section and current_s3:
            s3_files = current_s3

        if s3_files:
            message += "\n📦 <b>S3 文件:</b>\n"
            for item in s3_files:
                message += f"  • {item}\n"

        # ✅/⚠️ 状态
        if '没有新文件或变化需要处理' in section_text:
            message += "\n✅ 状态: 无新文件或变化"
        elif '成功处理:' in section_text:
            match = re.search(r'成功处理: (\d+) 个文件', section_text)
            if match:
                count = match.group(1)
                message += f"\n✅ 状态: 已处理 {count} 个文件"

                processed_files = []
                in_processed = False
                for line in lines:
                    if '已处理的文件:' in line:
                        in_processed = True
                        continue
                    if in_processed:
                        stripped = line.strip()
                        if stripped.startswith('-'):
                            processed_files.append(stripped[2:])
                        elif stripped.startswith('❌') or not stripped:
                            in_processed = False
                if processed_files:
                    message += "\n\n📝 <b>处理详情:</b>\n"
                    for item in processed_files:
                        message += f"  • {item}\n"
            else:
                message += "\n✅ 状态: 运行成功"
        else:
            message += "\n⚠️ 状态: 需要检查日志"

        # 📄 HTML 更新
        html_files = []
        in_html_section = False
        for line in lines:
            stripped = line.strip()
            if '生成的文件:' in line or '📋 生成的文件:' in line:
                in_html_section = True
                continue
            if in_html_section:
                if stripped.startswith('-'):
                    filename = stripped[2:].strip()
                    if filename.endswith('.html') and filename not in html_files:
                        html_files.append(filename)
                elif stripped.startswith('💡') or stripped.startswith('✅') or not stripped:
                    in_html_section = False
            if '已生成:' in line or '✅ 已生成:' in line:
                parts = line.split('已生成:')
                if len(parts) > 1:
                    filename = parts[1].strip().split()[0]
                    if filename.endswith('.html') and filename not in html_files:
                        html_files.append(filename)

        if html_files:
            message += "\n\n📄 <b>更新的 HTML:</b>\n"
            for item in html_files:
                message += f"  • {item}\n"

        # 统计信息
        stats_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('📊 In-Press 统计:') or stripped.startswith('📊 Issue '):
                stats_lines.append(stripped)

        if stats_lines:
            message += "\n\n📊 <b>变动统计:</b>\n"
            for s in stats_lines:
                message += f"  • {s}\n"

        # 📦 Git 状态
        git_notes = []
        if '✅ Git commit 完成' in section_text:
            git_notes.append('commit ✅ 已提交')
        elif '⚠️  Git 操作失败' in section_text:
            git_notes.append('commit ⚠️ 失败（详见日志）')
        elif 'ℹ️  没有变化需要提交' in section_text:
            git_notes.append('commit ℹ️ 无变化，跳过')

        if '📤 Pushing to GitHub' in section_text:
            if 'Successfully' in section_text or 'main ->' in section_text or '✅ GitHub push 成功' in section_text:
                git_notes.append('push ✅ 已推送到 GitHub')
            elif 'Everything up-to-date' in section_text:
                git_notes.append('push ℹ️ 无新 commit（Everything up-to-date）')
            elif '❌ GitHub push 失败' in section_text or 'fatal:' in section_text:
                git_notes.append('push ❌ 失败（请检查 token/权限）')
            else:
                git_notes.append('push ⚠️ 请检查日志')

        if git_notes:
            message += "\n\n📦 <b>Git 状态:</b>\n"
            for note in git_notes:
                message += f"  • {note}\n"
    else:
        message += "\n✅ 状态: 运行完成"

    message += f"""

🔗 <a href=\"https://github.com/tang1693/PERShtml\">查看 GitHub</a>
"""

    return message

if __name__ == '__main__':
    # 如果提供了命令行参数，作为消息内容
    if len(sys.argv) > 1:
        msg = sys.argv[1]
    else:
        # 否则，查找最新的日志文件
        log_dir = 'logs'
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = f"{log_dir}/daily-check-{today}.log"
        
        msg = format_daily_report(log_file)
    
    # 发送消息
    send_telegram(msg)
