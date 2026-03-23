# 🔔 Telegram 通知设置

## 快速开始

### 1. 创建 Telegram Bot

1. 在 Telegram 搜索 `@BotFather`
2. 发送 `/newbot`
3. 按提示操作：
   - 输入机器人名称（例如：`PERShtml Bot`）
   - 输入机器人用户名（例如：`pershtml_bot`，必须以 `_bot` 或 `Bot` 结尾）
4. 创建成功后，BotFather 会给你一个 **Bot Token**（类似：`123456789:ABCdefGHIjklMNOpqrsTUVwxyz`）

### 2. 获取 Chat ID

你的 Chat ID 已经知道了：`5469433156`

### 3. 配置环境变量

编辑 `.env` 文件，添加：

```bash
# Telegram 通知
TELEGRAM_BOT_TOKEN=你的_bot_token_这里
TELEGRAM_CHAT_ID=5469433156
```

### 4. 测试

```bash
# 方法 1: 直接发送消息
export TELEGRAM_BOT_TOKEN="你的token"
python3 send_telegram.py "测试消息"

# 方法 2: 发送每日报告格式
python3 send_telegram.py
```

---

## 消息格式

每日自动推送的消息格式：

```
🦞 PERShtml 每日检查报告

📅 时间: 2026-03-24 10:00:00
✅ 状态: 已处理 2 个新文件

🔗 查看 GitHub
```

---

## 使用场景

- ✅ 每天 10:00 自动检查后推送
- ✅ 有新文件处理时通知
- ✅ 无新文件时也通知（确认正常运行）
- ✅ 出错时通知（需要人工检查）

---

## 安全性

- Bot Token 保存在 `.env` 文件中（已排除在 Git 外）
- 只有你能收到消息（通过 Chat ID 限制）
- 纯 Python 实现，无第三方库

---

## 常见问题

### Q: 收不到消息？
A: 检查：
1. Bot Token 是否正确
2. 是否先给机器人发送过消息（必须先启动对话）
3. Chat ID 是否正确

### Q: 如何关闭通知？
A: 从 `.env` 中删除 `TELEGRAM_BOT_TOKEN` 行即可

### Q: 能发给多个人吗？
A: 可以。创建一个群组，把机器人加入，然后用群组的 Chat ID

---

## 技术细节

**脚本**: `send_telegram.py`  
**依赖**: 无（只用 Python 标准库）  
**API**: Telegram Bot API  
**发送方式**: HTTP POST  
**超时**: 10 秒  
**重试**: 无（失败不影响主流程）
