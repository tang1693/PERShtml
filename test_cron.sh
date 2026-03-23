#!/bin/bash
# 测试 cron job 是否正确配置

echo "🦞 测试 PERShtml 定时任务配置"
echo ""

# 1. 检查 crontab
echo "📋 Crontab 配置:"
crontab -l | grep "PERShtml" -A 1
echo ""

# 2. 检查脚本存在且可执行
echo "📂 检查脚本:"
if [ -x /root/.openclaw/workspace/PERShtml-project/run_daily_check.sh ]; then
    echo "✅ run_daily_check.sh 存在且可执行"
else
    echo "❌ run_daily_check.sh 不存在或不可执行"
fi
echo ""

# 3. 检查环境变量
echo "🔑 检查环境变量:"
cd /root/.openclaw/workspace/PERShtml-project
if [ -f .env ]; then
    echo "✅ .env 文件存在"
    source .env
    [ -n "$AWS_ACCESS_KEY_ID" ] && echo "  ✅ AWS_ACCESS_KEY_ID" || echo "  ❌ AWS_ACCESS_KEY_ID"
    [ -n "$AWS_SECRET_ACCESS_KEY" ] && echo "  ✅ AWS_SECRET_ACCESS_KEY" || echo "  ❌ AWS_SECRET_ACCESS_KEY"
    [ -n "$SCOPUS_API_KEY" ] && echo "  ✅ SCOPUS_API_KEY" || echo "  ❌ SCOPUS_API_KEY"
    [ -n "$GITHUB_TOKEN" ] && echo "  ✅ GITHUB_TOKEN" || echo "  ❌ GITHUB_TOKEN"
else
    echo "❌ .env 文件不存在"
fi
echo ""

# 4. 下次运行时间
echo "⏰ 下次运行时间:"
echo "   每天早上 10:00 (Asia/Shanghai)"
echo ""

# 5. 查看最近的日志
echo "📄 最近的日志:"
if [ -d logs ]; then
    ls -lth logs/daily-check-*.log 2>/dev/null | head -3
else
    echo "   (还没有日志)"
fi
echo ""

echo "✅ 测试完成"
echo ""
echo "💡 提示:"
echo "   - 脚本将在每天 10:00 自动运行"
echo "   - 检查 S3 是否有新文件"
echo "   - 如果有新文件，自动处理并推送到 GitHub"
echo "   - 日志保存在 logs/ 目录"
