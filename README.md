# Self Media Manager

面向小红书、B站、抖音的个人自媒体内容管理系统。

账号定位：

- 吉大 AI 本科生
- 记录科研入门、CS231n / CS336 自学、多模态论文阅读
- 记录健身和港校 MPhil / PhD 申请准备

## 项目结构

```text
self_media_manager/
├── main.py
├── requirements.txt
├── data/
│   ├── topics.csv
│   └── metrics.csv
├── content_manager/
│   ├── analytics.py
│   ├── cli.py
│   ├── config.py
│   ├── csv_store.py
│   ├── markdown_templates.py
│   ├── models.py
│   ├── weekly_plan.py
│   └── weekly_review.py
└── output/
    ├── analytics/
    ├── templates/
    ├── plans/
    └── reviews/
```

## CSV 字段

`data/topics.csv` 是选题库，包含这些字段：

| 字段 | 含义 |
| --- | --- |
| topic_id | 选题 ID，例如 T001 |
| theme | 主题，例如 CS231n 自学记录 |
| content_line | 内容线，例如 科研入门/课程学习 |
| target_platforms | 目标平台，用 `|` 分隔 |
| title | 标题 |
| status | 状态：idea / drafting / scheduled / published |
| publish_date | 发布时间，格式为 YYYY-MM-DD |
| data_performance | 旧版文本数据备注，正式分析请使用 `metrics.csv` |

`data/metrics.csv` 是结构化数据表，包含这些字段：

| 字段 | 含义 |
| --- | --- |
| topic_id | 选题 ID，例如 T003 |
| platform | 平台：小红书 / B站 / 抖音 |
| publish_date | 平台发布时间，格式为 YYYY-MM-DD |
| views | 浏览量/播放量 |
| likes | 点赞数 |
| favorites | 收藏数 |
| comments | 评论数 |
| shares | 分享数 |
| new_followers | 新增粉丝数 |

## 快速开始

```bash
cd /Users/macbook/Documents/self_media_manager
python3 main.py all
```

这会基于 `data/topics.csv`：

- 为每个选题的目标平台生成 Markdown 模板；
- 生成每周发布计划；
- 生成 `output/reviews/weekly_review_YYYY-MM-DD.md`；
- 生成 `output/analytics/analytics_report_YYYY-MM-DD.md`。

## 常用命令

查看选题库：

```bash
python3 main.py list
```

新增选题：

```bash
python3 main.py add \
  --theme "港校申请准备" \
  --content-line "MPhil/PhD申请" \
  --target-platforms "小红书|B站|抖音" \
  --title "港校 MPhil 申请前，我在本科阶段补哪些经历"
```

为某个选题生成目标平台模板：

```bash
python3 main.py generate-templates --topic-id T001
```

更新选题状态、标题或发布时间：

```bash
python3 main.py update-topic \
  --topic-id T001 \
  --status scheduled \
  --publish-date 2026-04-27
```

录入某条内容在某个平台的数据：

```bash
python3 main.py add-metrics \
  --topic-id T003 \
  --platform 小红书 \
  --publish-date 2026-04-22 \
  --views 980 \
  --likes 65 \
  --favorites 18 \
  --comments 7 \
  --shares 6 \
  --new-followers 4
```

生成本周发布计划：

```bash
python3 main.py weekly-plan
```

生成指定周的发布计划：

```bash
python3 main.py weekly-plan --start-date 2026-04-20
```

生成周复盘：

```bash
python3 main.py weekly-review
```

生成数据分析报告：

```bash
python3 main.py analytics
```

分析报告会输出：

- 按平台统计平均浏览、平均互动率、平均收藏率、平均评论率、平均涨粉率；
- 按内容线统计收藏率；
- 找出表现最好的前 5 条内容；
- 给出下周建议继续做的内容线。

## 内容工作流建议

1. 每周先把想法写进 `data/topics.csv`。
2. 用 `generate-templates` 生成目标平台模板。
3. 按模板写成平台版本。
4. 发布后用 `add-metrics` 把浏览、点赞、收藏、评论、分享、涨粉写进 `metrics.csv`。
5. 每周用 `weekly-review` 生成复盘文件，再用 `analytics` 看内容方向。
