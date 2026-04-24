from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Dict, Iterable, List

from .config import ANALYTICS_DIR
from .models import MetricsRecord, Topic


def safe_divide(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def format_number(value: float) -> str:
    return f"{value:.0f}"


def format_percent(value: float) -> str:
    return f"{value * 100:.2f}%"


def average(values: Iterable[float]) -> float:
    values = list(values)
    if not values:
        return 0.0
    return sum(values) / len(values)


def topic_map(topics: List[Topic]) -> Dict[str, Topic]:
    return {topic.topic_id: topic for topic in topics}


def content_line_for(record: MetricsRecord, topics_by_id: Dict[str, Topic]) -> str:
    topic = topics_by_id.get(record.topic_id)
    if topic is None:
        return "未归类"
    return topic.content_line or "未归类"


def title_for(record: MetricsRecord, topics_by_id: Dict[str, Topic]) -> str:
    topic = topics_by_id.get(record.topic_id)
    if topic is None:
        return "未找到选题"
    return topic.title


def render_platform_stats(metrics: List[MetricsRecord]) -> List[str]:
    grouped = defaultdict(list)
    for record in metrics:
        grouped[record.platform].append(record)

    lines = [
        "## 1. 按平台统计",
        "",
        "| 平台 | 内容数 | 平均浏览 | 平均互动率 | 平均收藏率 | 平均评论率 | 平均涨粉率 |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]

    for platform, records in sorted(grouped.items()):
        avg_views = average(record.views for record in records)
        avg_engagement_rate = average(record.engagement_rate() for record in records)
        avg_favorite_rate = average(record.favorite_rate() for record in records)
        avg_comment_rate = average(record.comment_rate() for record in records)
        avg_follower_rate = average(record.follower_rate() for record in records)
        lines.append(
            f"| {platform} | {len(records)} | {format_number(avg_views)} | "
            f"{format_percent(avg_engagement_rate)} | {format_percent(avg_favorite_rate)} | "
            f"{format_percent(avg_comment_rate)} | {format_percent(avg_follower_rate)} |"
        )

    if not grouped:
        lines.append("| - | 0 | 0 | 0.00% | 0.00% | 0.00% | 0.00% |")

    return lines


def render_content_line_stats(
    topics: List[Topic],
    metrics: List[MetricsRecord],
) -> List[str]:
    topics_by_id = topic_map(topics)
    grouped = defaultdict(list)
    for record in metrics:
        grouped[content_line_for(record, topics_by_id)].append(record)

    rows = []
    for content_line, records in grouped.items():
        total_views = sum(record.views for record in records)
        total_favorites = sum(record.favorites for record in records)
        favorite_rate = safe_divide(total_favorites, total_views)
        rows.append((content_line, records, total_views, total_favorites, favorite_rate))

    rows.sort(key=lambda item: (item[4], item[2]), reverse=True)

    lines = [
        "## 2. 按内容线统计收藏率",
        "",
        "| 内容线 | 内容数 | 总浏览 | 总收藏 | 收藏率 |",
        "| --- | --- | --- | --- | --- |",
    ]

    for content_line, records, total_views, total_favorites, favorite_rate in rows:
        lines.append(
            f"| {content_line} | {len(records)} | {total_views} | {total_favorites} | "
            f"{format_percent(favorite_rate)} |"
        )

    if not rows:
        lines.append("| - | 0 | 0 | 0 | 0.00% |")

    return lines


def render_top_contents(
    topics: List[Topic],
    metrics: List[MetricsRecord],
) -> List[str]:
    topics_by_id = topic_map(topics)
    ranked = sorted(
        metrics,
        key=lambda record: (record.total_engagement(), record.views, record.engagement_rate()),
        reverse=True,
    )[:5]

    lines = [
        "## 3. 表现最好的前 5 条内容",
        "",
        "> 排名按互动数排序，浏览量和互动率作为并列参考。",
        "",
        "| 排名 | 选题ID | 标题 | 平台 | 内容线 | 浏览 | 互动数 | 互动率 | 收藏率 | 涨粉率 |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]

    for index, record in enumerate(ranked, start=1):
        lines.append(
            f"| {index} | {record.topic_id} | {title_for(record, topics_by_id)} | "
            f"{record.platform} | {content_line_for(record, topics_by_id)} | "
            f"{record.views} | {record.total_engagement()} | "
            f"{format_percent(record.engagement_rate())} | "
            f"{format_percent(record.favorite_rate())} | "
            f"{format_percent(record.follower_rate())} |"
        )

    if not ranked:
        lines.append("| - | - | 暂无数据 | - | - | - | - | - | - | - |")

    return lines


def render_next_week_suggestions(
    topics: List[Topic],
    metrics: List[MetricsRecord],
) -> List[str]:
    topics_by_id = topic_map(topics)
    grouped = defaultdict(list)
    for record in metrics:
        grouped[content_line_for(record, topics_by_id)].append(record)

    scored_lines = []
    for content_line, records in grouped.items():
        total_views = sum(record.views for record in records)
        total_favorites = sum(record.favorites for record in records)
        favorite_rate = safe_divide(total_favorites, total_views)
        avg_engagement_rate = average(record.engagement_rate() for record in records)
        scored_lines.append(
            (content_line, favorite_rate, avg_engagement_rate, total_views, len(records))
        )

    scored_lines.sort(key=lambda item: (item[1], item[2], item[3]), reverse=True)

    lines = [
        "## 4. 下周建议继续做的内容线",
        "",
    ]

    if not scored_lines:
        lines.append("- 先补充 `metrics.csv` 数据，再判断下周重点。")
        return lines

    for content_line, favorite_rate, engagement_rate, total_views, count in scored_lines[:3]:
        lines.append(
            f"- 继续做「{content_line}」：已有 {count} 条数据，"
            f"收藏率 {format_percent(favorite_rate)}，平均互动率 {format_percent(engagement_rate)}，"
            f"总浏览 {total_views}。"
        )

    return lines


def render_analytics_report(topics: List[Topic], metrics: List[MetricsRecord]) -> str:
    lines = [
        f"# 数据分析报告：{date.today().isoformat()}",
        "",
        "## 数据口径",
        "",
        "- 互动率 = (点赞 + 收藏 + 评论 + 分享) / 浏览量",
        "- 收藏率 = 收藏 / 浏览量",
        "- 评论率 = 评论 / 浏览量",
        "- 涨粉率 = 新增粉丝 / 浏览量",
        "",
    ]

    sections = [
        render_platform_stats(metrics),
        render_content_line_stats(topics, metrics),
        render_top_contents(topics, metrics),
        render_next_week_suggestions(topics, metrics),
    ]

    for section in sections:
        lines.extend(section)
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def generate_analytics_report(
    topics: List[Topic],
    metrics: List[MetricsRecord],
    output_dir: Path = ANALYTICS_DIR,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"analytics_report_{date.today().isoformat()}.md"
    path.write_text(render_analytics_report(topics, metrics), encoding="utf-8")
    return path
