# PERS HTML Pipeline — Requirements & Data-Handling Rules (2026-03-26)

> 整理虾总→老汤关于 PERS 自动化的一致要求，方便后续维护不跑偏。

## 1. 数据来源 & 调度
- **元数据来源**：`s3://persearlyaccess/Metadata/YY-XX_Xxx_metadata.xlsx`
- **每日调度**：Cron `0 10 * * * /root/.openclaw/workspace/PERShtml-project/run_daily_check.sh`
- **运行流程**：`run_daily_check.sh → auto_update.py → update_from_s3.py → git commit → run_daily_check 推送 → send_telegram.py 通知`

## 2. Excel 字段 → 标准结构
| Excel 字段             | 处理规则 / 目标字段 |
|------------------------|---------------------|
| `Title`                | 原样写入 `Title` |
| `Authors`              | `clean_authors()` 去除脚注数字/多余分隔符 |
| `Article Category`     | 判定 In-Press vs Research (`in[\s-]?press` 兼容 InPress / In-Press / In Press)。落入 `Category` 字段 |
| `Date MMDDYY`          | - In-Press：`Pages = "Month d, YYYY"`<br>- Research：`Pages = "pp. start–end"`<br>- `PubDate = Month YYYY`<br>- `Year`、`IssueKey = Year + IssueNumber`|
| `Issue Number`, `Volume` | `Issue` 2 位字符串，组成 `IssueKey`、`IssuesArticles` 路径 |
| `Page Numbers`         | 仅 Research 使用（自动加 `pp.` 前缀） |
| `Access Status` (`OA` / `SUB`) | 映射到 HTML 描述：`Open Access content` / `Subscribed content` |
| `DOI`                  | 构造 `URL = https://doi.org/<DOI>` |
| `Abstract`             | 原样写入 `Abstract` |
| `Graphical Abstract`   | Google Drive 链接 → `download_ga_images()` 下载，使用 file_id 作为文件名，生成 `GA_Path` 指向 GitHub raw URL |

## 3. 模块输出（更新_from_s3.py 对应）
1. **Module 1 – InPress**
   - `1_InPress/filtered_InPress_articles_info_abs.csv`
   - `in_press_articles.html`
   - 若 Excel 中有 In-Press 文章，必须列出全部，不得空缺；若没有则生成空模板。
2. **Module 2 – Issues**
   - 重新生成 `issues.html`，更新当月期刊条目与 `NEW` 标签。
3. **Module 5 – Recent Articles**
   - 读取 `6_IssuesArticles/ALL_articles_Update_cleaned.csv`，提取最近 6 个月 → `5_RecentArticles/filtered_articles_info_abs.csv`
   - 生成 `open_access_articles.html`、`member_only_articles.html`。
4. **Module 6 – IssuesArticles**
   - 维护总库 `6_IssuesArticles/ALL_articles_Update_cleaned.csv`（去重、备份、按 IssueKey 覆盖）。
   - 生成 `IssuesArticles/html/<IssueKey>.html` 和对应 GA 图片目录。
5. **Module 7 – Most Cited (Recent 2 years)**
   - `7_MostCited/most_cited_articles.csv`
   - `top_6_articles.html`
   - 调用 Scopus API 获取引用数，输出 Top10/Top6。
6. **Other HTML**
   - `articles.html`, `issues.html`, `member_only_articles.html`, `open_access_articles.html`, `top_6_articles.html`, `IssuesArticles/html/YYYYMM.html` 均需同步。

## 4. Git & 通知要求
- `auto_update.py` 成功处理后 **必须** `git add . && git commit -m "Auto update: <file list>"`。
- `run_daily_check.sh` 只要 `git status -sb` 出现 `[ahead X]` 就自动用 `.env` 中的 `GITHUB_TOKEN` 推送。
- `send_telegram.py` 从最新日志区块解析：
  - S3 文件列表（显示当前大小）
  - 处理状态：`已处理 N 个文件` / `无新文件`
  - 处理详情：`<filename> (新大小): 大小变化: OLD → NEW`
  - HTML 更新列表
  - Git 状态（commit/push 成功/失败）

## 5. 质量控制
- `processed.log` 保存每次文件大小和时间戳，方便回溯；删除该文件可强制全量重算。
- 日志中必须出现 `大小变化: <old> → <new>`，以便 Telegram 报告引用。
- GA 下载失败、缺少 DOI、缺少 Access 时要打印 ⚠️ 以便排查。
- In-Press 检测需兼容 `In-Press`、`InPress`、`In Press`（新代码 `INPRESS_PATTERN`）。
- 任何失败（S3、Scopus、Git、GA）要在日志中标注，以便 `send_telegram.py` 捕捉并提示。

## 6. 期望行为（来自老汤）
- **零人工操作**：每天 10:00 自动跑完、自动 Git push、自动 Telegram。
- **实时/透明**：报告里能看到最新的 S3 大小、处理原因、更新的 HTML 列表、Git 状态。
- **In-Press 不缺失**：Excel 里只要有 In-Press entries，就必须展示在 `in_press_articles.html`，不能静默丢失。
- **Excel 兼容性**：Python 逻辑掌握 Excel 每个 column 的含义；任何格式变化（比如 InPress 写法）要在脚本里兼容，不依赖人工手动修改。
- **可追溯**：`logs/daily-check-YYYY-MM-DD.log` 永久保留 7 天滚动，`processed.log` 纪录每次处理，用于回溯历史。

> 如有新增要求或 Excel 结构变动，更新此文档并同步代码。这样以后任何人都能按同一套规则维护 PERS 自动化。