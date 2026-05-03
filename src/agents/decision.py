from datetime import datetime, timezone, timedelta
from typing import Optional
from src.agents.analyst import Insight
from src.repositories import notifications as notif_repo

MIN_SEVERITY_TO_NOTIFY = 3        # severity < 3 nunca vira push
MAX_PUSHES_PER_DAY = 2            # teto duro de pushes/dia
COOLDOWN_HOURS_SAME_TOPIC = 24    # mesmo tópico só de novo após X horas

def _category_weight(insight: Insight) -> int:
    return 0

def filter_by_severity(insights: list[Insight]) -> list[Insight]:
    return [i for i in insights if i.severity >= MIN_SEVERITY_TO_NOTIFY]

def filter_recently_notified(insights: list[Insight]) -> list[Insight]:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=COOLDOWN_HOURS_SAME_TOPIC)
    recent = notif_repo.list_since(cutoff)

    recent_keys = {
        _insight_key(n["kind"], n["topic"], n.get("subject_name"))
        for n in recent
    }

    return [
        i for i in insights
        if _insight_key(i.kind, i.topic, i.subject) not in recent_keys
    ]

def _insight_key(kind: str, topic: Optional[str], subject: Optional[str]) -> tuple:
    return (kind, topic or "", subject or "")

def daily_quota_remaining() -> int:
    today_start = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    sent_today = notif_repo.count_since(today_start)
    remaining = MAX_PUSHES_PER_DAY - sent_today
    return max(0, remaining)

def pick_best(insights: list[Insight]) -> Optional[Insight]:
    if not insights:
        return None
    return max(insights, key=lambda i: i.severity)

def decide(insights: list[Insight]) -> Optional[Insight]:
    filtered = filter_by_severity(insights)
    if not filtered:
        return None
    filtered = filter_recently_notified(filtered)
    if not filtered:
        return None
    if daily_quota_remaining() <= 0:
        return None
    return pick_best(filtered)