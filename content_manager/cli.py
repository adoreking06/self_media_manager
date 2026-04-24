import argparse
from datetime import date
from pathlib import Path
from typing import List

from .analytics import generate_analytics_report
from .config import METRICS_CSV, PLATFORMS, TOPICS_CSV, VALID_STATUSES
from .csv_store import (
    add_or_update_metrics,
    add_topic,
    ensure_csv_exists,
    ensure_metrics_csv_exists,
    get_topic,
    read_metrics,
    read_topics,
    update_topic,
)
from .markdown_templates import generate_templates
from .models import Topic
from .weekly_plan import generate_weekly_plan, monday_of_week, parse_date
from .weekly_review import generate_weekly_review


def print_paths(paths: List[Path]) -> None:
    for path in paths:
        print(f"- {path}")


def list_topics(topics: List[Topic]) -> None:
    if not topics:
        print("选题库为空。可以用 `python main.py add ...` 添加第一条。")
        return

    print("当前选题库：")
    for topic in topics:
        print(
            f"- {topic.topic_id} | {topic.status} | {topic.target_platforms} | "
            f"{topic.title} | 发布时间：{topic.publish_date or '待定'}"
        )


def add_sample_data() -> None:
    ensure_csv_exists()
    ensure_metrics_csv_exists()

    if not read_topics():
        samples = [
            {
                "theme": "CS231n 自学记录",
                "content_line": "科研入门/课程学习",
                "target_platforms": "小红书|B站|抖音",
                "title": "吉大AI本科生从零开始刷 CS231n：第一周学了什么",
            },
            {
                "theme": "CS336 自学",
                "content_line": "大模型基础",
                "target_platforms": "小红书|B站|抖音",
                "title": "CS336 该怎么入门：我给自己设计的学习路线",
            },
            {
                "theme": "多模态论文阅读",
                "content_line": "论文精读",
                "target_platforms": "小红书|B站",
                "title": "读 BLIP-2 前我先补了这些背景",
                "status": "published",
                "publish_date": "2026-04-22",
                "data_performance": "B站播放 320；小红书收藏 18",
            },
            {
                "theme": "港校申请准备",
                "content_line": "MPhil/PhD申请",
                "target_platforms": "小红书|B站|抖音",
                "title": "港校 MPhil/PhD 申请时间线：本科生现在能做什么",
            },
            {
                "theme": "健身记录",
                "content_line": "生活/长期主义",
                "target_platforms": "小红书|抖音",
                "title": "科研入门期怎么安排训练：我的一周健身计划",
            },
        ]

        for sample in samples:
            add_topic(**sample)

    if not read_metrics() and get_topic("T003") is not None:
        add_or_update_metrics("T003", "小红书", "2026-04-22", 980, 65, 18, 7, 6, 4)
        add_or_update_metrics("T003", "B站", "2026-04-22", 320, 25, 10, 3, 2, 2)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="面向小红书、B站、抖音的个人自媒体内容管理系统。"
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("init-data", help="创建 CSV 并写入示例选题。")
    subparsers.add_parser("list", help="查看当前选题库。")

    add_parser = subparsers.add_parser("add", help="新增一个选题。")
    add_parser.add_argument("--theme", required=True, help="主题，例如：CS231n 自学记录")
    add_parser.add_argument("--content-line", required=True, help="内容线，例如：科研入门/课程学习")
    add_parser.add_argument(
        "--target-platforms",
        default="|".join(PLATFORMS),
        help="目标平台，用 | 分隔，例如：小红书|B站|抖音",
    )
    add_parser.add_argument("--title", required=True, help="标题")
    add_parser.add_argument(
        "--status",
        default="idea",
        choices=VALID_STATUSES,
        help="状态：idea/drafting/scheduled/published",
    )
    add_parser.add_argument("--publish-date", default="", help="发布时间，格式：YYYY-MM-DD")
    add_parser.add_argument("--data-performance", default="", help="数据表现，例如：播放 1000，收藏 50")

    template_parser = subparsers.add_parser("generate-templates", help="为一个选题生成目标平台 Markdown 模板。")
    template_parser.add_argument("--topic-id", required=True, help="选题ID，例如：T001")

    update_parser = subparsers.add_parser("update-topic", help="更新选题状态、标题或发布时间。")
    update_parser.add_argument("--topic-id", required=True, help="选题ID，例如：T001")
    update_parser.add_argument(
        "--status",
        choices=VALID_STATUSES,
        help="状态：idea/drafting/scheduled/published",
    )
    update_parser.add_argument("--title", help="新的标题")
    update_parser.add_argument("--publish-date", help="发布时间，格式：YYYY-MM-DD")

    metrics_parser = subparsers.add_parser("add-metrics", help="录入或更新某条内容在某个平台的数据。")
    metrics_parser.add_argument("--topic-id", required=True, help="选题ID，例如：T003")
    metrics_parser.add_argument("--platform", required=True, choices=PLATFORMS, help="平台")
    metrics_parser.add_argument("--publish-date", default="", help="发布时间，格式：YYYY-MM-DD；不填则使用选题发布时间")
    metrics_parser.add_argument("--views", required=True, type=int, help="浏览量/播放量")
    metrics_parser.add_argument("--likes", default=0, type=int, help="点赞数")
    metrics_parser.add_argument("--favorites", default=0, type=int, help="收藏数")
    metrics_parser.add_argument("--comments", default=0, type=int, help="评论数")
    metrics_parser.add_argument("--shares", default=0, type=int, help="分享数")
    metrics_parser.add_argument("--new-followers", default=0, type=int, help="新增粉丝数")

    plan_parser = subparsers.add_parser("weekly-plan", help="生成每周发布计划。")
    plan_parser.add_argument("--start-date", default="", help="周一日期，格式：YYYY-MM-DD；不填则使用本周一。")

    review_parser = subparsers.add_parser("weekly-review", help="生成 weekly_review_YYYY-MM-DD.md。")
    review_parser.add_argument("--start-date", default="", help="周一日期，格式：YYYY-MM-DD；不填则使用本周一。")

    subparsers.add_parser("analytics", help="生成数据分析报告。")

    all_parser = subparsers.add_parser("all", help="初始化数据，并生成模板、周计划、复盘和分析报告。")
    all_parser.add_argument("--start-date", default="", help="周一日期，格式：YYYY-MM-DD；不填则使用本周一。")

    return parser


def get_start_date(value: str) -> date:
    if value:
        return parse_date(value)
    return monday_of_week(date.today())


def run_all(start_date: date) -> None:
    add_sample_data()
    topics = read_topics()
    metrics = read_metrics()
    all_paths = []
    for topic in topics:
        all_paths.extend(generate_templates(topic))

    plan_path = generate_weekly_plan(topics, start_date)
    review_path = generate_weekly_review(topics, start_date, metrics)
    analytics_path = generate_analytics_report(topics, metrics)

    print("已生成目标平台模板：")
    print_paths(all_paths)
    print("\n已生成周计划：")
    print(f"- {plan_path}")
    print("\n已生成周复盘：")
    print(f"- {review_path}")
    print("\n已生成数据分析报告：")
    print(f"- {analytics_path}")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == "init-data":
        add_sample_data()
        print(f"已初始化选题库：{TOPICS_CSV}")
        print(f"已初始化数据表：{METRICS_CSV}")
        return

    if args.command == "list":
        list_topics(read_topics())
        return

    if args.command == "add":
        topic = add_topic(
            theme=args.theme,
            content_line=args.content_line,
            target_platforms=args.target_platforms,
            title=args.title,
            status=args.status,
            publish_date=args.publish_date,
            data_performance=args.data_performance,
        )
        print(f"已新增选题：{topic.topic_id} - {topic.title}")
        return

    if args.command == "update-topic":
        if args.status is None and args.title is None and args.publish_date is None:
            raise SystemExit("请至少提供 --status、--title 或 --publish-date 中的一项。")
        topic = update_topic(
            topic_id=args.topic_id,
            status=args.status,
            title=args.title,
            publish_date=args.publish_date,
        )
        if topic is None:
            raise SystemExit(f"找不到选题：{args.topic_id}")
        print(f"已更新选题：{topic.topic_id} | {topic.status} | {topic.title} | 发布时间：{topic.publish_date or '待定'}")
        return

    if args.command == "add-metrics":
        topic = get_topic(args.topic_id)
        if topic is None:
            raise SystemExit(f"找不到选题：{args.topic_id}")
        if args.platform not in topic.platform_list():
            raise SystemExit(f"{topic.topic_id} 的目标平台不包含：{args.platform}")

        publish_date = args.publish_date or topic.publish_date
        record = add_or_update_metrics(
            topic_id=topic.topic_id,
            platform=args.platform,
            publish_date=publish_date,
            views=args.views,
            likes=args.likes,
            favorites=args.favorites,
            comments=args.comments,
            shares=args.shares,
            new_followers=args.new_followers,
        )
        print(
            f"已录入数据：{record.topic_id} | {record.platform} | "
            f"浏览 {record.views} | 互动 {record.total_engagement()}"
        )
        return

    if args.command == "generate-templates":
        topic = get_topic(args.topic_id)
        if topic is None:
            raise SystemExit(f"找不到选题：{args.topic_id}")
        paths = generate_templates(topic)
        print("已生成模板：")
        print_paths(paths)
        return

    if args.command == "weekly-plan":
        path = generate_weekly_plan(read_topics(), get_start_date(args.start_date))
        print(f"已生成周计划：{path}")
        return

    if args.command == "weekly-review":
        path = generate_weekly_review(read_topics(), get_start_date(args.start_date), read_metrics())
        print(f"已生成 weekly_review：{path}")
        return

    if args.command == "analytics":
        path = generate_analytics_report(read_topics(), read_metrics())
        print(f"已生成数据分析报告：{path}")
        return

    if args.command == "all":
        run_all(get_start_date(args.start_date))
        return
