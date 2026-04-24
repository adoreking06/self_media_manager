from dataclasses import dataclass
from typing import Dict, List

from .config import METRICS_FIELDS, PLATFORMS, TOPIC_FIELDS


def normalize_platforms(value: str) -> str:
    raw_platforms = value.replace(",", "|").replace("，", "|").replace("/", "|")
    platforms = [item.strip() for item in raw_platforms.split("|") if item.strip()]

    if not platforms:
        return "|".join(PLATFORMS)

    normalized = []
    for platform in platforms:
        if platform not in PLATFORMS:
            raise ValueError(f"不支持的平台：{platform}。可选：{'、'.join(PLATFORMS)}")
        if platform not in normalized:
            normalized.append(platform)

    return "|".join(normalized)


def validate_platform(platform: str) -> str:
    platform = platform.strip()
    if platform not in PLATFORMS:
        raise ValueError(f"不支持的平台：{platform}。可选：{'、'.join(PLATFORMS)}")
    return platform


def to_non_negative_int(value: str, field_name: str) -> int:
    try:
        number = int(str(value).strip() or 0)
    except ValueError as error:
        raise ValueError(f"{field_name} 必须是非负整数") from error

    if number < 0:
        raise ValueError(f"{field_name} 必须是非负整数")
    return number


@dataclass
class Topic:
    topic_id: str
    theme: str
    content_line: str
    target_platforms: str
    title: str
    status: str
    publish_date: str
    data_performance: str

    @classmethod
    def from_row(cls, row: Dict[str, str]) -> "Topic":
        values = {field: row.get(field, "").strip() for field in TOPIC_FIELDS}
        values["target_platforms"] = normalize_platforms(values["target_platforms"])
        return cls(**values)

    def to_row(self) -> Dict[str, str]:
        return {field: getattr(self, field) for field in TOPIC_FIELDS}

    def platform_list(self) -> List[str]:
        return [item.strip() for item in self.target_platforms.split("|") if item.strip()]


@dataclass
class MetricsRecord:
    topic_id: str
    platform: str
    publish_date: str
    views: int
    likes: int
    favorites: int
    comments: int
    shares: int
    new_followers: int

    def __post_init__(self) -> None:
        self.topic_id = self.topic_id.strip().upper()
        self.platform = validate_platform(self.platform)
        self.publish_date = self.publish_date.strip()
        self.views = to_non_negative_int(self.views, "views")
        self.likes = to_non_negative_int(self.likes, "likes")
        self.favorites = to_non_negative_int(self.favorites, "favorites")
        self.comments = to_non_negative_int(self.comments, "comments")
        self.shares = to_non_negative_int(self.shares, "shares")
        self.new_followers = to_non_negative_int(self.new_followers, "new_followers")

    @classmethod
    def from_row(cls, row: Dict[str, str]) -> "MetricsRecord":
        values = {field: row.get(field, "").strip() for field in METRICS_FIELDS}
        return cls(
            topic_id=values["topic_id"].upper(),
            platform=validate_platform(values["platform"]),
            publish_date=values["publish_date"],
            views=to_non_negative_int(values["views"], "views"),
            likes=to_non_negative_int(values["likes"], "likes"),
            favorites=to_non_negative_int(values["favorites"], "favorites"),
            comments=to_non_negative_int(values["comments"], "comments"),
            shares=to_non_negative_int(values["shares"], "shares"),
            new_followers=to_non_negative_int(values["new_followers"], "new_followers"),
        )

    def to_row(self) -> Dict[str, str]:
        return {field: str(getattr(self, field)) for field in METRICS_FIELDS}

    def total_engagement(self) -> int:
        return self.likes + self.favorites + self.comments + self.shares

    def engagement_rate(self) -> float:
        if self.views == 0:
            return 0.0
        return self.total_engagement() / self.views

    def favorite_rate(self) -> float:
        if self.views == 0:
            return 0.0
        return self.favorites / self.views

    def comment_rate(self) -> float:
        if self.views == 0:
            return 0.0
        return self.comments / self.views

    def follower_rate(self) -> float:
        if self.views == 0:
            return 0.0
        return self.new_followers / self.views
