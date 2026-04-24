from datetime import date, timedelta
from pathlib import Path
from typing import List, Optional

from .config import REVIEWS_DIR
from .models import MetricsRecord, Topic
from .weekly_plan import parse_date


def format_percent(value: float) -> str:
    return f"{value * 100:.2f}%"


def topic_in_week(topic: Topic, start_day: date) -> bool:
    if not topic.publish_date:
        return False
    try:
        publish_day = parse_date(topic.publish_date)
    except ValueError:
        return False
    return start_day <= publish_day <= start_day + timedelta(days=6)


def metric_in_week(record: MetricsRecord, start_day: date) -> bool:
    if not record.publish_date:
        return False
    try:
        publish_day = parse_date(record.publish_date)
    except ValueError:
        return False
    return start_day <= publish_day <= start_day + timedelta(days=6)


def render_weekly_review(
    topics: List[Topic],
    start_day: date,
    metrics: Optional[List[MetricsRecord]] = None,
) -> str:
    end_day = start_day + timedelta(days=6)
    weekly_topics = [topic for topic in topics if topic_in_week(topic, start_day)]
    weekly_metrics = [record for record in metrics or [] if metric_in_week(record, start_day)]
    topics_by_id = {topic.topic_id: topic for topic in topics}

    lines = [
        f"# Weekly Review：{start_day.isoformat()} - {end_day.isoformat()}",
        "",
        "## 1. 本周发布数据",
        "",
        "| 选题ID | 标题 | 内容线 | 平台 | 发布时间 | 浏览 | 点赞 | 收藏 | 评论 | 分享 | 涨粉 | 互动率 |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]

    if weekly_metrics:
        for record in weekly_metrics:
            topic = topics_by_id.get(record.topic_id)
            title = topic.title if topic else "未找到选题"
            content_line = topic.content_line if topic else "未归类"
            lines.append(
                f"| {record.topic_id} | {title} | {content_line} | {record.platform} | "
                f"{record.publish_date} | {record.views} | {record.likes} | "
                f"{record.favorites} | {record.comments} | {record.shares} | "
                f"{record.new_followers} | {format_percent(record.engagement_rate())} |"
            )
    elif weekly_topics:
        for topic in weekly_topics:
            for platform in topic.platform_list():
                lines.append(
                    f"| {topic.topic_id} | {topic.title} | {topic.content_line} | {platform} | "
                    f"{topic.publish_date} | 待记录 | 待记录 | 待记录 | 待记录 | 待记录 | 待记录 | 待记录 |"
                )
    else:
        lines.append("| - | 本周暂无带发布时间或数据记录的选题 | - | - | - | - | - | - | - | - | - | - |")

    lines.extend(
        [
            "",
            "## 2. 单条内容复盘",
            "",
            "| 选题ID | 做对了什么 | 没做好的地方 | 下一次怎么改 |",
            "| --- | --- | --- | --- |",
            "|  |  |  |  |",
            "",
            "## 3. 平台观察",
            "",
            "### 小红书",
            "",
            "- 爆点/收藏点：",
            "- 评论区问题：",
            "- 下一条改进：",
            "",
            "### B站",
            "",
            "- 完播/互动反馈：",
            "- 标题封面问题：",
            "- 下一条改进：",
            "",
            "### 抖音",
            "",
            "- 前 3 秒留存判断：",
            "- 评论区高频词：",
            "- 下一条改进：",
            "",
            "## 4. 下周选题池",
            "",
            "- 最值得继续做的选题：",
            "- 可以系列化的选题：",
            "- 需要暂停的选题：",
            "",
            "## 5. 对账号定位的修正",
            "",
            "- 我现在最像谁？",
            "- 读者为什么愿意关注我？",
            "- 下周要更明确表达的身份标签：",
        ]
    )

    return "\n".join(lines) + "\n"


def generate_weekly_review(
    topics: List[Topic],
    start_day: date,
    metrics: Optional[List[MetricsRecord]] = None,
    output_dir: Path = REVIEWS_DIR,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"weekly_review_{start_day.isoformat()}.md"
    path.write_text(render_weekly_review(topics, start_day, metrics), encoding="utf-8")
    return path
