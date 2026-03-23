#!/usr/bin/env python3
"""
测试 Telegram 通知格式
模拟日志内容，检查输出
"""

import os
import sys

# 模拟日志内容
mock_log = """======================================================================
🦞 PERShtml 全自动更新
======================================================================
📋 加载环境变量 (.env)

📋 已处理的文件数: 0

📡 扫描 S3 bucket: s3://persearlyaccess/Metadata/
   找到 1 个 Excel 文件

📊 S3 文件列表:
   - 26-04_April_metadata.xlsx: 17.6 KB

📌 发现 1 个文件需要处理:
   - 26-04_April_metadata.xlsx: 新文件

======================================================================
📊 处理总结
======================================================================
✅ 成功处理: 1 个文件

已处理的文件:
   - 26-04_April_metadata.xlsx (17.6 KB): 新文件

📦 提交到 Git...
   ✅ Git commit 完成

======================================================================
✅ 所有模块更新完成！
======================================================================

📋 生成的文件:
   - in_press_articles.html
   - issues.html
   - open_access_articles.html
   - member_only_articles.html
   - IssuesArticles/html/202604.html
   - top_6_articles.html

✅ Success
📤 Pushing to GitHub...
To https://github.com/tang1693/PERShtml.git
   abc1234..def5678  main -> main
"""

# 写入临时日志文件
test_log = '/tmp/test-daily-check.log'
with open(test_log, 'w') as f:
    f.write(mock_log)

# 导入 send_telegram 模块
sys.path.insert(0, os.path.dirname(__file__))
from send_telegram import format_daily_report

# 生成报告
report = format_daily_report(test_log)

print("=" * 70)
print("Telegram 通知预览:")
print("=" * 70)
print(report)
print("=" * 70)

# 清理
os.remove(test_log)
