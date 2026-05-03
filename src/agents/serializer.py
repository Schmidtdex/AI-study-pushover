import typing_extensions
import json
from datetime import datetime, date
from decimal import Decimal
from src.agents.context_types import ContextBundle

def _json_default(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, date):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def bundle_to_llm_json(bundle: ContextBundle)-> str:
    payload = {
        "snapshot_at": bundle.generated_at.isoformat(),

        "today":_format_today(bundle),

        "week_summary": {
            "days_studied_in_last_7": bundle.derived.days_studied_in_last_7,
            "avg_energy": bundle.daily.avg_energy_7d,
        },

        "subjects_progress_7d": [
            {
                "subject": t["subject_name"],
                "category": t["subject_category"],
                "minutes_studied": t["total_min"],
                "session_count": t["session_count"],
            }
            for t in bundle.sessions.total_by_subject_7d
        ],

        "topics_status": [
            {
                "subject": t["subject_name"],
                "category": t["subject_category"],
                "topic": t["topic"],
                "last_seen_iso": t["last_seen"].isoformat(),
                "times_studied_recent": t["times_studied"],
                "avg_difficulty": t["avg_difficulty"],
            }
            for t in bundle.sessions.topics_status
        ],

        "upcoming_deadlines": [
            {
                "deadline_id": d["id"],
                "subject": d["subject_name"],
                "category": d["subject_category"],
                "title": d["title"],
                "kind": d["kind"],
                "due_at_iso": d["due_at"].isoformat(),
                "days_until": round(d["days_until"], 1),
            }
            for d in bundle.deadlines.upcoming
        ],

        "active_tracks": [
            {
                "subject": t["subject_name"],
                "course": t["course_name"],
                "goal": t["goal"],
            }
            for t in bundle.tracks.active
        ],

        "facts": {
            "neglected_subjects": [
                n["subject_name"] for n in bundle.derived.neglected_subjects
            ],
            "forgotten_topics": [
                {
                    "subject": f["subject_name"],
                    "topic": f["topic"],
                    "days_since": f["days_since_last_seen"],
                    "difficulty": f["avg_difficulty"],
                }
                for f in bundle.derived.forgotten_topics
            ],
            "urgent_deadlines": [
                {
                    "deadline_id": u["deadline_id"],
                    "subject": u["subject_name"],
                    "title": u["title"],
                    "days_until": round(u["days_until"], 1),
                    "minutes_studied_7d": u["studied_min_7d"],
                }
                for u in bundle.derived.urgent_deadlines
            ],
        },
    }
    return json.dumps(payload, default=_json_default, ensure_ascii=False, indent=2)

def _format_today(bundle: ContextBundle) -> dict:
    log = bundle.daily.today_log
    if log is None:
        return {"logged": False}
    return {
        "logged": True,
        "energy": log["energy"],
        "mood": log["mood"],
        "note": log["note"],
    }
