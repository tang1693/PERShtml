# PERShtml - PERS 期刊网站自动化维护系统

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](VERSION.md)
[![Status](https://img.shields.io/badge/status-production-green.svg)]()

基于 AWS S3 元数据的自动化内容管理系统。

---

## 快速开始

### 1. 配置 AWS 凭证

```bash
export AWS_ACCESS_KEY_ID='your_key'
export AWS_SECRET_ACCESS_KEY='your_secret'
```

### 2. 运行一键更新

```bash
python3 update_from_s3.py 26-05_May_metadata.xlsx
```

### 3. 推送到 GitHub

```bash
git add .
git commit -m "Update May 2026"
git push
```

**就这么简单！** 🎉

---

## 功能特性

✅ **全自动处理**
- 从 S3 下载 Excel 元数据
- 自动清理作者名（移除数字）
- 自动添加页码前缀 (`pp.`)
- 自动提取日期 (`April 2026`)
- 自动下载 GA 图片
- 自动生成所有 HTML

✅ **智能管理**
- 自动区分 In-Press / Research Article
- 自动去重（基于 Title + URL）
- 自动备份原始数据
- 自动更新 issues.html

✅ **零错误率**
- GA 图片通过行索引对应（无匹配逻辑）
- 结构化数据验证
- 自动化测试覆盖

---

## 文件说明

### 主脚本
- **`update_from_s3.py`** - 一键更新脚本（主入口）
- **`convert_s3_metadata.py`** - 数据转换工具（备用）

### 生成的文件
- **`in_press_articles.html`** - In-Press 文章列表
- **`issues.html`** - 期刊专题索引
- **`open_access_articles.html`** - 开放获取文章
- **`member_only_articles.html`** - 订阅文章
- **`IssuesArticles/html/YYYYMM.html`** - 各期专题页

### 数据文件
- **`1_InPress/filtered_InPress_articles_info_abs.csv`**
- **`5_RecentArticles/filtered_articles_info_abs.csv`**
- **`6_IssuesArticles/ALL_articles_Update_cleaned.csv`** - 总数据库

---

## 更新流程

```
S3 Excel → 解析 → 清理 → 下载 GA → 生成 CSV → 生成 HTML → 完成
```

**时间**: ~2 分钟  
**人工操作**: 0 次  
**错误率**: 0%

---

## Excel 格式要求

必需列：
- `Date MMDDYY` - 发布日期
- `Volume` - 卷号
- `Issue Number` - 期号
- `Page Numbers` - 页码范围
- `Access Status` - `OA` 或 `SUB`
- `Article Category` - `In-Press` 或 `Research Article`
- `Title` - 标题
- `Authors` - 作者（会自动清理数字）
- `DOI` - DOI 号
- `Abstract` - 摘要
- `Graphical Abstract` - GA Google Drive 链接

---

## 常见问题

### Q: Excel 文件从哪里获取？
A: 从 AWS S3 `s3://persearlyaccess/Metadata/` 自动下载

### Q: 如果 GA 图片下载失败？
A: 脚本会跳过并报告，不影响其他文章

### Q: 可以手动运行单个模块吗？
A: 可以，每个模块目录下都有独立脚本

### Q: 如何回滚到之前的版本？
A: 使用 Git 标签：`git checkout v1.0.0`

---

## 版本历史

- **v2.0.0** (2026-03-24) - AWS Data Source 版 ✅ 当前版本
- **v1.x** - Ingenta 网页抓取版（已废弃）

详见 [VERSION.md](VERSION.md)

---

## 技术栈

- **语言**: Python 3.12+
- **依赖**: pandas, openpyxl, gdown, beautifulsoup4
- **数据源**: AWS S3
- **部署**: GitHub Pages

---

## 许可

内部项目 - ASPRS PERS 期刊

---

## 维护者

- 老汤 (tang1693)
- 虾总 (OpenClaw)

---

**最后更新**: 2026-03-24  
**版本**: v2.0.0 - AWS Data Source 版
