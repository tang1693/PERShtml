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
    """格式化每日报告"""
    
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    message = f"""🦞 <b>PERShtml 每日检查报告</b>

📅 时间: {now}
"""
    
    # 如果提供了日志文件，解析结果
    if log_file and os.path.exists(log_file):
        with open(log_file, 'r', encoding='utf-8') as f:
            log_content = f.read()
        
        import re
        
        # 提取 S3 文件列表
        s3_files = []
        in_s3_section = False
        for line in log_content.split('\n'):
            if '📊 S3 文件列表:' in line:
                in_s3_section = True
                continue
            if in_s3_section:
                if line.strip().startswith('-'):
                    # 格式: - filename: XX.X KB
                    s3_files.append(line.strip()[2:])  # 去掉 "- "
                elif not line.strip() or '📌' in line:
                    break
        
        if s3_files:
            message += "\n📦 <b>S3 文件:</b>\n"
            for f in s3_files:
                message += f"  • {f}\n"
        
        # 提取处理结果
        if '没有新文件或变化需要处理' in log_content:
            message += "\n✅ 状态: 无新文件或变化"
        elif '成功处理:' in log_content:
            # 提取处理的文件数
            match = re.search(r'成功处理: (\d+) 个文件', log_content)
            if match:
                count = match.group(1)
                message += f"\n✅ 状态: 已处理 {count} 个文件"
                
                # 提取已处理的文件列表
                processed_files = []
                in_processed_section = False
                for line in log_content.split('\n'):
                    if '已处理的文件:' in line:
                        in_processed_section = True
                        continue
                    if in_processed_section:
                        if line.strip().startswith('-'):
                            # 格式: - filename (XX.X KB): reason
                            processed_files.append(line.strip()[2:])
                        elif line.strip().startswith('❌') or not line.strip():
                            break
                
                if processed_files:
                    message += "\n\n📝 <b>处理详情:</b>\n"
                    for f in processed_files:
                        message += f"  • {f}\n"
            else:
                message += "\n✅ 状态: 运行成功"
        else:
            message += "\n⚠️ 状态: 需要检查日志"
    else:
        message += "\n✅ 状态: 运行完成"
    
    message += f"""
🔗 <a href="https://github.com/tang1693/PERShtml">查看 GitHub</a>
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
