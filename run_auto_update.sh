#!/bin/bash
# PERShtml 全自动更新脚本
# 自动扫描 S3，处理新文件，跳过已处理的文件

set -e

# 加载 .env 文件（如果存在）
if [ -f .env ]; then
    echo "📋 加载环境变量 (.env)"
    export $(cat .env | grep -v '^#' | xargs)
fi

# 检查 AWS 凭证
if [ -z "$AWS_ACCESS_KEY_ID" ]; then
    echo "❌ 未找到 AWS 凭证"
    echo "   请配置 .env 文件或设置环境变量"
    exit 1
fi

echo ""
echo "🦞 运行全自动更新..."
echo ""

# 运行 Python 脚本
python3 auto_update.py

echo ""
echo "✅ 完成！"
