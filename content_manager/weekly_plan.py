from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

from .config import PLANS_DIR
from .models import Topic

WEEKDAY_NAMES = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
PLATFORM_RHYTHM = {
    0: "小红书",
    1: "B站",
    2: "抖音",
    3: "小红书",
    4: "B站",
    5: "抖音",
    6: "复盘",
}


def parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def monday_of_week(day: date) -> date:
    return day - timedelta(days=day.weekday())


def topic_platform_pairs(topics: List[Topic]) -> List[Tuple[Topic, str]]:
    pairs: List[Tuple[Topic, str]] = []
    for topic in topics:
        if topic.status == "published":
            continue
        for platform in topic.platform_list():
            pairs.append((topic, platform))
    return pairs


def build_schedule(topics: List[Topic], start_day: date) -> Dict[date, List[Tuple[Topic, str]]]:
    days = [start_day + timedelta(days=offset) for offset in range(7)]
    schedule: Dict[date, List[Tuple[Topic, str]]] = {day: [] for day in days}

    pairs = topic_platform_pairs(topics)
    dated_pairs = []
    undated_pairs = []
    for topic, platform in pairs:
        if topic.publish_date:
            try:
                publish_day = parse_date(topic.publish_date)
            except ValueError:
                undated_pairs.append((topic, platform))
                continue
            if start_day <= publish_day <= start_day + timedelta(days=6):
                dated_pairs.append((publish_day, topic, platform))
            else:
                undated_pairs.append((topic, platform))
        else:
            undated_pairs.append((topic, platform))

    for publish_day, topic, platform in dated_pairs:
        schedule[publish_day].append((topic, platform))

    for topic, platform in undated_pairs:
        target_days = [day for day in days if PLATFORM_RHYTHM[day.weekday()] == platform]
        if not target_days:
            target_days = days[:6]
        target_day = min(target_days, key=lambda item: len(schedule[item]))
        schedule[target_day].append((topic, platform))

    return schedule


def render_weekly_plan(topics: List[Topic], start_day: date) -> str:
    end_day = start_day + timedelta(days=6)
    schedule = build_schedule(topics, start_day)

    lines = [
        f"# 每周发布计划：{start_day.isoformat()} - {end_day.isoformat()}",
        "",
        "## 本周主线",
        "",
        "- 科研入门：记录课程、论文和实验环境搭建。",
        "- CS 自学：CS231n / CS336 的阶段性输出。",
        "- 申请准备：港校 MPhil / PhD 材料、时间线和信息差。",
        "- 生活支撑：健身、作息和长期主义。",
        "",
        "## 发布安排",
        "",
        "| 日期 | 星期 | 平台节奏 | 选题ID | 标题 | 状态 |",
        "| --- | --- | --- | --- | --- | --- |",
    ]

    for day in schedule:
        weekday = WEEKDAY_NAMES[day.weekday()]
        rhythm = PLATFORM_RHYTHM[day.weekday()]
        items = schedule[day]
        if not items:
            lines.append(f"| {day.isoformat()} | {weekday} | {rhythm} | - | 机动/素材整理 | - |")
            continue
        for topic, platform in items:
            lines.append(
                f"| {day.isoformat()} | {weekday} | {platform} | {topic.topic_id} | {topic.title} | {topic.status} |"
            )

    lines.extend(
        [
            "",
            "## 每日执行清单",
            "",
            "- [ ] 写标题：同一选题至少写 5 个备选标题。",
            "- [ ] 整理素材：截图、笔记、训练记录或申请材料进展。",
            "- [ ] 完成平台改写：小红书偏图文，B站偏结构，抖音偏钩子。",
            "- [ ] 发布后 24 小时记录数据表现。",
            "",
            "## 本周最低完成标准",
            "",
            "- 至少发布 3 条短内容。",
            "- 至少完成 1 条 B站长内容或长内容脚本。",
            "- 每条内容都沉淀一个可复用模板、资料清单或复盘结论。",
        ]
    )
    return "\n".join(lines) + "\n"


def generate_weekly_plan(
    topics: List[Topic],
    start_day: date,
    output_dir: Path = PLANS_DIR,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"weekly_plan_{start_day.isoformat()}.md"
    path.write_text(render_weekly_plan(topics, start_day), encoding="utf-8")
    return path
