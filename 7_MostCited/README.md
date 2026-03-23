# Most Cited Articles 模块

自动提取最近2年的论文，获取引用数，生成 Most Cited HTML。

## 功能

1. **数据提取**: 从 `ALL_articles_Update_cleaned.csv` 提取最近2年（730天）的论文
2. **引用数获取**: 通过 Scopus API 获取每篇论文的引用数
3. **HTML 生成**: 生成 `most_cited_articles.html`（Top 50，按引用数排序）

## 自动化

每次运行 `update_from_s3.py` 时会自动执行：
- 提取最近2年的论文（104篇）
- 获取引用数（如果配置了 API key）
- 生成 HTML

## Scopus API 配置

### 1. 获取 API Key

访问 [Elsevier Developer Portal](https://dev.elsevier.com/)：
1. 注册并登录
2. 进入 "My API Key" 页面
3. 创建新的 API key（选择 Scopus Search API）
4. 复制 API key

### 2. 配置环境变量

**Linux/Mac**:
```bash
export SCOPUS_API_KEY='your_api_key_here'
```

**永久配置** (添加到 `~/.bashrc` 或 `~/.zshrc`):
```bash
echo 'export SCOPUS_API_KEY="your_api_key_here"' >> ~/.bashrc
source ~/.bashrc
```

### 3. 验证配置

```bash
echo $SCOPUS_API_KEY  # 应该显示你的 API key
```

## 手动运行

如果需要单独更新 Most Cited 模块：

```bash
cd PERShtml-project

# 1. 提取数据 + 获取引用数
python3 7_MostCited/fetch_citations.py

# 2. 生成 HTML
python3 7_MostCited/generate_html.py
```

## 输出文件

- `7_MostCited/most_cited_articles.csv` - 最近2年的论文数据（带引用数）
- `most_cited_articles.html` - 网页（Top 50）

## 数据说明

### 日期范围
- **当前**: 2024-04-01 到 2026-04-01
- **更新频率**: 每次运行 `update_from_s3.py` 时自动更新
- **动态调整**: 日期范围自动跟随当前时间（始终保持最近2年）

### 引用数来源
- **Scopus Search API**: 优先使用 DOI 搜索，fallback 到 Title 搜索
- **更新频率**: 每次运行时重新获取（确保最新数据）
- **无 API key**: 所有引用数为 0（仍然生成 HTML）

### Top 50 限制
- HTML 默认显示 Top 50
- CSV 包含所有文章（104篇）
- 可以修改 `generate_html.py` 中的 `max_articles` 参数

## API 限制

Scopus API 有以下限制：
- **免费账户**: 25,000 次/周
- **速率限制**: 脚本已实现 0.5 秒延迟
- **429 错误**: 自动等待 30 秒后继续

## 故障排查

### 引用数全是 0
1. 检查 SCOPUS_API_KEY 是否设置：`echo $SCOPUS_API_KEY`
2. 检查 API key 是否有效（访问 Elsevier Developer Portal）
3. 查看脚本输出是否有 API 错误信息

### 某些文章没有引用数
- 旧文章（Ingenta URL）没有 DOI：使用 Title 搜索（可能匹配失败）
- Scopus 数据库中不存在：引用数为 0
- API 限流：部分文章跳过，下次运行会重新获取

## 未来改进

可选的改进方向：
1. **缓存引用数**: 避免每次都调用 API
2. **增量更新**: 只获取新文章的引用数
3. **其他数据源**: 支持 Google Scholar, Crossref 等
4. **更多指标**: H-index, Altmetrics 等

---

**维护者**: XIA zong  
**最后更新**: 2026-03-24
