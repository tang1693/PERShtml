#!/bin/bash
# PERShtml 每日自动检查脚本
# 每天早上 10:00 运行

# 切换到项目目录
cd /root/workspace/PERShtml-project

# 加载环境变量
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# 创建日志目录
mkdir -p logs

# 日志文件（按日期）
LOG_FILE="logs/daily-check-$(date +%Y-%m-%d).log"

echo "========================================" >> "$LOG_FILE"
echo "🦞 PERShtml Daily Check" >> "$LOG_FILE"
echo "Time: $(date '+%Y-%m-%d %H:%M:%S')" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# 运行自动更新
python3 auto_update.py >> "$LOG_FILE" 2>&1

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Success" >> "$LOG_FILE"
    
    # 如果有新 commit，自动推送到 GitHub
    if git status -sb | grep -q '\[ahead'; then
        echo "📤 Pushing to GitHub..." >> "$LOG_FILE"

        if [ -n "$GITHUB_TOKEN" ]; then
            git remote set-url origin "https://${GITHUB_TOKEN}@github.com/tang1693/PERShtml.git" >> "$LOG_FILE" 2>&1
            git push origin main >> "$LOG_FILE" 2>&1
            git remote set-url origin "https://github.com/tang1693/PERShtml.git" >> "$LOG_FILE" 2>&1
        else
            echo "⚠️  GITHUB_TOKEN not set, skipping push" >> "$LOG_FILE"
        fi
    else
        echo "ℹ️  无需推送（没有新的 commit）" >> "$LOG_FILE"
    fi
else
    echo "❌ Failed (exit code: $EXIT_CODE)" >> "$LOG_FILE"
fi

echo "========================================" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# 发送 Telegram 通知
if [ -n "$TELEGRAM_BOT_TOKEN" ]; then
    echo "📤 发送 Telegram 通知..." >> "$LOG_FILE"
    python3 send_telegram.py >> "$LOG_FILE" 2>&1
fi

# 清理 7 天前的日志
find logs/ -name "daily-check-*.log" -mtime +7 -delete

exit $EXIT_CODE
