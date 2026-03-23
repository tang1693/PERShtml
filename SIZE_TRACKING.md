# 📊 文件大小监控说明

## 功能

自动检测 S3 文件的大小变化，如果 Excel 文件被更新（大小变了），自动重新处理。

---

## 工作原理

### 1. 记录文件信息

`processed.log` 格式：
```
filename size_bytes # Processed at timestamp
```

示例：
```
26-04_April_metadata.xlsx 17998 # Processed at 2026-03-24 04:35:09
```

### 2. 检测逻辑

每次运行时：
1. 列出 S3 文件 + 大小
2. 对比 `processed.log`
3. 决定是否处理：

| 情况 | 操作 |
|------|------|
| S3 有新文件 | ✅ 处理 |
| 文件大小变了 | ✅ 重新处理 |
| 文件大小未变 | ⏭️ 跳过 |

### 3. Telegram 通知

通知内容包含：

**S3 文件列表**：
```
📦 S3 文件:
  • 26-04_April_metadata.xlsx: 17.6 KB
```

**处理详情**：
```
📝 处理详情:
  • 26-04_April_metadata.xlsx (17.6 KB): 大小变化: 14.6KB → 17.6KB
```

---

## 使用场景

### 场景 1: 新月份数据

S3 新增文件 `26-05_May_metadata.xlsx`

**结果**：
- ✅ 自动检测到新文件
- ✅ 下载并处理
- ✅ 记录到 log
- 📱 发送通知

### 场景 2: 数据更新

4月数据修正，Excel 文件重新上传到 S3（文件名相同，大小变了）

**结果**：
- ✅ 检测到大小变化（14.6KB → 17.6KB）
- ✅ 重新处理最新数据
- ✅ 更新 log
- 📱 发送通知（说明原因）

### 场景 3: 无变化

重复运行，S3 文件未变

**结果**：
- ⏭️ 跳过处理
- 📱 发送通知："无新文件或变化"

---

## 示例输出

### 控制台输出

```
📡 扫描 S3 bucket: s3://persearlyaccess/Metadata/
   找到 1 个 Excel 文件

📊 S3 文件列表:
   - 26-04_April_metadata.xlsx: 17.6 KB

📌 发现 1 个文件需要处理:
   - 26-04_April_metadata.xlsx: 大小变化: 14.6KB → 17.6KB
```

### Telegram 通知

```
🦞 PERShtml 每日检查报告

📅 时间: 2026-03-24 10:00:00

📦 S3 文件:
  • 26-04_April_metadata.xlsx: 17.6 KB

✅ 状态: 已处理 1 个文件

📝 处理详情:
  • 26-04_April_metadata.xlsx (17.6 KB): 大小变化: 14.6KB → 17.6KB

🔗 查看 GitHub
```

---

## 技术细节

### processed.log 格式

```
# 旧格式（仅文件名）
26-04_April_metadata.xlsx # Processed at 2026-03-24 04:08:00

# 新格式（文件名 + 大小）
26-04_April_metadata.xlsx 17998 # Processed at 2026-03-24 04:35:09
```

**兼容性**：
- 脚本兼容旧格式（无大小信息）
- 旧格式记录会在下次处理时升级

### AWS CLI 输出解析

```bash
$ aws s3 ls s3://persearlyaccess/Metadata/
2026-03-21 00:21:45      17998 26-04_April_metadata.xlsx
                         ↑↑↑↑↑
                      提取这个值
```

### 大小比对

```python
if processed[filename] and processed[filename] != size_bytes:
    # 文件大小变化，重新处理
    old_kb = processed[filename] / 1024
    new_kb = size_bytes / 1024
    print(f"大小变化: {old_kb:.1f}KB → {new_kb:.1f}KB")
```

---

## 常见问题

### Q: 如何强制重新处理所有文件？
A: 删除 `processed.log`

```bash
rm processed.log
./run_auto_update.sh
```

### Q: 如果 Excel 内容变了但大小没变怎么办？
A: 极少发生。如需强制重新处理特定文件，从 `processed.log` 中删除那一行。

### Q: 大小差异多少才算变化？
A: 任何差异（1 byte）都算变化。Excel 文件内容改变通常会导致大小变化。

### Q: 通知中的 KB 是精确值吗？
A: 显示小数点后 1 位（如 17.6 KB），实际存储的是精确字节数（17998 bytes）。

---

## 文件位置

- `auto_update.py` - 主逻辑（检测 + 处理）
- `send_telegram.py` - 通知格式化
- `processed.log` - 记录文件（在 GitHub 上可见）

---

**自动监控，自动处理，自动通知！** 🚀
