#!/bin/bash
# PERShtml 自动更新脚本 - 加载环境变量并运行

set -e  # 遇到错误立即退出

# 检查参数
if [ $# -eq 0 ]; then
    echo "用法: ./run_update.sh <Excel文件名>"
    echo "示例: ./run_update.sh 26-05_May_metadata.xlsx"
    exit 1
fi

EXCEL_FILE=$1

# 加载 .env 文件（如果存在）
if [ -f .env ]; then
    echo "📋 加载环境变量 (.env)"
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "⚠️  未找到 .env 文件，使用环境变量或默认配置"
fi

# 显示配置状态
echo ""
echo "📊 配置状态:"
if [ -n "$AWS_ACCESS_KEY_ID" ]; then
    echo "  ✅ AWS 凭证已配置"
else
    echo "  ⚠️  AWS 凭证未配置"
fi

if [ -n "$SCOPUS_API_KEY" ]; then
    echo "  ✅ Scopus API Key 已配置"
else
    echo "  ⚠️  Scopus API Key 未配置（Most Cited 将跳过引用数获取）"
fi

echo ""
echo "🚀 运行更新: $EXCEL_FILE"
echo ""

# 运行 Python 脚本
python3 update_from_s3.py "$EXCEL_FILE"

echo ""
echo "✅ 完成！"
