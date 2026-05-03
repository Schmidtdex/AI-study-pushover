from datetime import datetime, timezone
from src.repositories import (
    deadlines as deadlines_repo,
    daily_logs as logs_repo,
    sessions as sessions_repo,
    tracks as tracks_repo,
)
from src.agents.context_types import (
    DailyContext,
    DeadlinesContext,
    SessionsContext,
    TracksContext,
    DerivedContext,
    ContextBundle,
)

NEGLECT_THRESHOLD_DAYS = 7     # matéria não estudada há >= N dias = negligenciada
FORGOT_THRESHOLD_DAYS = 5      # tópico não revisado há >= N dias = esquecido
URGENT_DEADLINE_DAYS = 3       # deadline em <= N dias = urgente
URGENT_LOW_STUDY_MIN = 60      # se estudou < N min da matéria, considera "pouco"

def _now_utc() -> datetime:
    return datetime.now(timezone.utc)

def _days_between(past: datetime, ref: datetime) -> int:
    delta = ref - past
    return delta.days

def _calc_days_studied(recent_sessions: list[dict]) -> int:
    distinct_dates = {s["studied_at"].date() for s in recent_sessions}
    return len(distinct_dates)
    
def _calc_neglected_subjects(
    totals_7d: list[dict],
    threshold_min: int = 1,
) -> list[dict]:
    return [
        {
            "subject_id": t["subject_id"], 
            "subject_name": t["subject_name"],
            "total_min_7d": t["total_min"],
            "subject_category": t["subject_category"],
        }
        for t in totals_7d
        if t["total_min"] <= threshold_min
    ]

def _calc_forgotten_topics(
    topics_status: list[dict],
    now: datetime,
    threshold_days: int = FORGOT_THRESHOLD_DAYS,
) -> list[dict]:
    forgotten = []
    for t in topics_status:
        days_since = _days_between(t["last_seen"], now)
        if days_since >= threshold_days:
            forgotten.append({
                "subject_id": t["subject_id"],
                "subject_name": t["subject_name"],
                "subject_category": t["subject_category"],
                "topic": t["topic"],
                "days_since_last_seen": days_since,
                "times_studied": t["times_studied"],
                "avg_difficulty": t["avg_difficulty"],
            })
    forgotten.sort(key=lambda x: x["days_since_last_seen"], reverse=True)
    return forgotten


def _calc_urgent_deadlines(
    upcoming: list[dict],
    totals_7d: list[dict],
    days_threshold: int = URGENT_DEADLINE_DAYS,
    low_study_min: int = URGENT_LOW_STUDY_MIN,
) -> list[dict]:
    totals_by_id = {t["subject_id"]: t["total_min"] for t in totals_7d}
    urgent = []
    for d in upcoming:
        if d["days_until"] > days_threshold:
            continue
        studied_min = totals_by_id.get(d["subject_id"], 0)
        if studied_min >= low_study_min:
            continue   
        urgent.append({
            "deadline_id": d["id"],
            "title": d["title"],
            "kind": d["kind"],
            "subject_id": d["subject_id"],
            "subject_name": d["subject_name"],
            "subject_category": d["subject_category"],
            "due_at": d["due_at"],
            "days_until": d["days_until"],
            "studied_min_7d": studied_min,
        })
    return urgent


def collect() -> ContextBundle:
    now = _now_utc()

    today_log = logs_repo.get_by_date(now.date())
    recent_logs = logs_repo.get_recent(days=7)
    avg_energy = logs_repo.average_energy(days=7)

    upcoming = deadlines_repo.get_upcoming(days=14)
    overdue = deadlines_repo.get_overdue()

    recent_sessions = sessions_repo.get_recent(days=7)
    totals_7d = sessions_repo.total_minutes_by_subject(days=7)
    topics_status = sessions_repo.get_topics_last_seen(days_back=30)

    active_tracks = tracks_repo.list_active()

    derived = DerivedContext(
        days_studied_in_last_7=_calc_days_studied(recent_sessions),
        neglected_subjects=_calc_neglected_subjects(totals_7d),
        forgotten_topics=_calc_forgotten_topics(topics_status, now),
        urgent_deadlines=_calc_urgent_deadlines(upcoming, totals_7d),
    )

    return ContextBundle(
        generated_at=now,
        daily=DailyContext(
            today_log=today_log,
            recent_logs=recent_logs,
            avg_energy_7d=avg_energy,
        ),
        deadlines=DeadlinesContext(
            upcoming=upcoming,
            overdue=overdue,
        ),
        sessions=SessionsContext(
            recent=recent_sessions,
            total_by_subject_7d=totals_7d,
            topics_status=topics_status,
        ),
        tracks=TracksContext(
            active=active_tracks,
        ),
        derived=derived,
    )