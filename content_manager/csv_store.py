import csv
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional

from .config import (
    DEFAULT_STATUS,
    METRICS_CSV,
    METRICS_FIELDS,
    TOPIC_FIELDS,
    TOPICS_CSV,
    VALID_STATUSES,
)
from .models import MetricsRecord, Topic, normalize_platforms, validate_platform


def ensure_csv_exists(csv_path: Path = TOPICS_CSV) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    if csv_path.exists():
        return

    with csv_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=TOPIC_FIELDS)
        writer.writeheader()


def ensure_metrics_csv_exists(csv_path: Path = METRICS_CSV) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    if csv_path.exists():
        return

    with csv_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=METRICS_FIELDS)
        writer.writeheader()


def validate_date(value: str) -> str:
    value = value.strip()
    if not value:
        return ""
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError as error:
        raise ValueError("日期格式必须是 YYYY-MM-DD") from error
    return value


def read_topics(csv_path: Path = TOPICS_CSV) -> List[Topic]:
    ensure_csv_exists(csv_path)
    with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        return [Topic.from_row(row) for row in reader]


def write_topics(topics: Iterable[Topic], csv_path: Path = TOPICS_CSV) -> None:
    ensure_csv_exists(csv_path)
    with csv_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=TOPIC_FIELDS)
        writer.writeheader()
        for topic in topics:
            writer.writerow(topic.to_row())


def read_metrics(csv_path: Path = METRICS_CSV) -> List[MetricsRecord]:
    ensure_metrics_csv_exists(csv_path)
    with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        return [MetricsRecord.from_row(row) for row in reader]


def write_metrics(metrics: Iterable[MetricsRecord], csv_path: Path = METRICS_CSV) -> None:
    ensure_metrics_csv_exists(csv_path)
    with csv_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=METRICS_FIELDS)
        writer.writeheader()
        for record in metrics:
            writer.writerow(record.to_row())


def next_topic_id(topics: List[Topic]) -> str:
    max_number = 0
    for topic in topics:
        if topic.topic_id.startswith("T") and topic.topic_id[1:].isdigit():
            max_number = max(max_number, int(topic.topic_id[1:]))
    return f"T{max_number + 1:03d}"


def get_topic(topic_id: str, csv_path: Path = TOPICS_CSV) -> Optional[Topic]:
    topic_id = topic_id.strip().upper()
    for topic in read_topics(csv_path):
        if topic.topic_id.upper() == topic_id:
            return topic
    return None


def update_topic(
    topic_id: str,
    status: Optional[str] = None,
    title: Optional[str] = None,
    publish_date: Optional[str] = None,
    csv_path: Path = TOPICS_CSV,
) -> Optional[Topic]:
    topics = read_topics(csv_path)
    topic_id = topic_id.strip().upper()

    for topic in topics:
        if topic.topic_id.upper() != topic_id:
            continue

        if status is not None:
            if status not in VALID_STATUSES:
                raise ValueError(f"不支持的状态：{status}。可选：{', '.join(VALID_STATUSES)}")
            topic.status = status
        if title is not None:
            topic.title = title.strip()
        if publish_date is not None:
            topic.publish_date = validate_date(publish_date)

        write_topics(topics, csv_path)
        return topic

    return None


def add_topic(
    theme: str,
    content_line: str,
    target_platforms: str,
    title: str,
    status: str = DEFAULT_STATUS,
    publish_date: str = "",
    data_performance: str = "",
    csv_path: Path = TOPICS_CSV,
) -> Topic:
    if status not in VALID_STATUSES:
        raise ValueError(f"不支持的状态：{status}。可选：{', '.join(VALID_STATUSES)}")

    topics = read_topics(csv_path)
    topic = Topic(
        topic_id=next_topic_id(topics),
        theme=theme.strip(),
        content_line=content_line.strip(),
        target_platforms=normalize_platforms(target_platforms),
        title=title.strip(),
        status=status,
        publish_date=validate_date(publish_date),
        data_performance=data_performance.strip(),
    )
    topics.append(topic)
    write_topics(topics, csv_path)
    return topic


def add_or_update_metrics(
    topic_id: str,
    platform: str,
    publish_date: str,
    views: int,
    likes: int,
    favorites: int,
    comments: int,
    shares: int,
    new_followers: int,
    csv_path: Path = METRICS_CSV,
) -> MetricsRecord:
    topic_id = topic_id.strip().upper()
    record = MetricsRecord(
        topic_id=topic_id,
        platform=validate_platform(platform),
        publish_date=validate_date(publish_date),
        views=views,
        likes=likes,
        favorites=favorites,
        comments=comments,
        shares=shares,
        new_followers=new_followers,
    )

    metrics = read_metrics(csv_path)
    for index, existing in enumerate(metrics):
        if existing.topic_id == record.topic_id and existing.platform == record.platform:
            metrics[index] = record
            write_metrics(metrics, csv_path)
            return record

    metrics.append(record)
    write_metrics(metrics, csv_path)
    return record
