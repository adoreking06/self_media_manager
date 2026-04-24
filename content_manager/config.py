from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"
TEMPLATES_DIR = OUTPUT_DIR / "templates"
PLANS_DIR = OUTPUT_DIR / "plans"
REVIEWS_DIR = OUTPUT_DIR / "reviews"
ANALYTICS_DIR = OUTPUT_DIR / "analytics"
TOPICS_CSV = DATA_DIR / "topics.csv"
METRICS_CSV = DATA_DIR / "metrics.csv"

PLATFORMS = ["小红书", "B站", "抖音"]

TOPIC_FIELDS = [
    "topic_id",
    "theme",
    "content_line",
    "target_platforms",
    "title",
    "status",
    "publish_date",
    "data_performance",
]

METRICS_FIELDS = [
    "topic_id",
    "platform",
    "publish_date",
    "views",
    "likes",
    "favorites",
    "comments",
    "shares",
    "new_followers",
]

DEFAULT_STATUS = "idea"
VALID_STATUSES = ["idea", "drafting", "scheduled", "published"]
