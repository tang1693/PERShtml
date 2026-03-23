# 🤖 PERShtml 自动化系统

## 概述

**完全自动化的期刊网站维护系统**（无需 AI 参与运行）

每天自动检测 S3 新数据 → 处理 → 生成 HTML → 推送 GitHub → Telegram 通知

---

## 🎯 核心功能

### 1️⃣ 自动扫描 S3
- 每天 10:00 扫描 `s3://persearlyaccess/Metadata/`
- 列出所有 Excel 文件 + 大小

### 2️⃣ 智能检测变化
- 新文件 → 自动处理
- 文件大小变了 → 重新处理
- 无变化 → 跳过

### 3️⃣ 自动处理数据
- 下载 Excel
- 提取文章信息
- 下载 GA 图片
- 调用 Scopus API 获取引用数
- 生成所有 HTML

### 4️⃣ 自动推送 GitHub
- Git commit
- Git push
- 网站自动更新（GitHub Pages）

### 5️⃣ Telegram 实时通知
- S3 文件列表
- 处理详情
- HTML 更新列表
- GitHub 状态

---

## 📱 Telegram 通知示例

```
🦞 PERShtml 每日检查报告
程序自动生成

📅 时间: 2026-03-24 10:00:00

📦 S3 文件:
  • 26-04_April_metadata.xlsx: 17.6 KB

✅ 状态: 已处理 1 个文件

📝 处理详情:
  • 26-04_April_metadata.xlsx (17.6 KB): 新文件

📄 更新的 HTML:
  • in_press_articles.html
  • issues.html
  • open_access_articles.html
  • member_only_articles.html
  • IssuesArticles/html/202604.html
  • top_6_articles.html

✅ 已推送到 GitHub

🔗 查看 GitHub
```

---

## 🔧 技术架构

### 脚本组成
```
auto_update.py          # 主逻辑（S3 扫描 + 变化检测）
send_telegram.py        # Telegram 通知生成
run_daily_check.sh      # Cron 定时任务
update_from_s3.py       # 数据处理核心
processed.log           # 状态追踪
```

### 定时任务
```bash
# Cron 配置
0 10 * * * /root/.openclaw/workspace/PERShtml-project/run_daily_check.sh
```

### 环境变量（.env）
```bash
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
SCOPUS_API_KEY=...
GITHUB_TOKEN=...
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=5469433156
```

---

## 📊 数据流

```
S3 Excel 文件
  ↓
扫描 + 大小检测
  ↓
下载 + 解析
  ↓
清理数据
  ↓
下载 GA 图片
  ↓
调用 Scopus API（引用数）
  ↓
生成 CSV
  ↓
生成 HTML
  ├─ InPress
  ├─ Issues
  ├─ Recent Articles
  ├─ Articles (专题页)
  └─ Most Cited (Top 6)
  ↓
Git commit + push
  ↓
Telegram 通知
```

---

## 🚀 快速开始

### 1. 配置环境变量
```bash
cp .env.example .env
vim .env  # 填入真实凭证
```

### 2. 测试手动运行
```bash
./run_daily_check.sh
```

### 3. 验证 Cron
```bash
crontab -l | grep PERShtml
```

### 4. 查看日志
```bash
tail -f logs/daily-check-$(date +%Y-%m-%d).log
```

---

## 📖 文档

| 文档 | 说明 |
|------|------|
| `AUTOMATION.md` | 自动化系统详细说明 |
| `SIZE_TRACKING.md` | 文件大小监控机制 |
| `TELEGRAM_SETUP.md` | Telegram 通知设置 |
| `test_telegram_format.py` | 通知格式测试 |
| `test_cron.sh` | Cron 配置测试 |

---

## ✅ 状态监控

### 检查 Cron
```bash
./test_cron.sh
```

### 测试 Telegram
```bash
python3 send_telegram.py "测试消息"
```

### 测试 S3 扫描
```bash
python3 auto_update.py
```

### 查看处理记录
```bash
cat processed.log
```

---

## 🛠️ 故障排查

### Telegram 不发送？
```bash
# 1. 检查 token
grep TELEGRAM_BOT_TOKEN .env

# 2. 测试
python3 send_telegram.py "测试"

# 3. 查看日志
tail logs/daily-check-*.log
```

### S3 扫描失败？
```bash
# 1. 检查 AWS 凭证
aws s3 ls s3://persearlyaccess/Metadata/

# 2. 检查 .env
grep AWS .env
```

### GitHub 推送失败？
```bash
# 1. 检查 token
grep GITHUB_TOKEN .env

# 2. 手动推送
git push origin main
```

---

## 🎯 关键特性

✅ **完全自动化** - 无人工干预  
✅ **智能检测** - 大小变化自动重新处理  
✅ **实时通知** - Telegram 推送所有状态  
✅ **可追溯** - 所有操作记录日志  
✅ **无 AI 运行时** - 纯程序执行  
✅ **零停机** - Cron 自动重试  
✅ **安全** - 凭证环境变量，不提交 Git  

---

## 📈 数据统计

- **总库**: 1,600+ 篇文章
- **最近6个月**: Recent Articles
- **最近2年**: Most Cited (Top 6)
- **每日检查**: S3 所有文件
- **自动通知**: Telegram 实时推送

---

## 🔐 安全性

- ✅ 所有凭证保存在 `.env`（不提交 Git）
- ✅ GitHub Token 用于自动推送
- ✅ Telegram Bot 只发给指定 Chat ID
- ✅ AWS 凭证只读 S3
- ✅ Scopus API 只调用引用数

---

## 📞 联系方式

- GitHub: https://github.com/tang1693/PERShtml
- Telegram: 自动通知（Chat ID: 5469433156）

---

**AI 只写代码，运行时 100% 程序自动化！** 🤖🚀
