from src.agents.collector import collect
from src.agents.analyst import analyze
from src.agents.decision import decide
from src.agents.comunicator import compose_message
from src.notifications.pushover import send_push
from src.repositories import notifications as notif_repo


def run_cycle(dry_run: bool = False) -> dict:
    result = {
        "collected": False,
        "insights_count": 0,
        "decided": False,
        "message": None,
        "pushed": False,
    }

    bundle = collect()
    result["collected"] = True

    insights = analyze(bundle)
    result["insights_count"] = len(insights)

    if not insights:
        result["reason"] = "Nenhum insight gerado"
        return result

    chosen = decide(insights)
    if chosen is None:
        result["reason"] = "Nenhum insight passou pelas regras"
        return result

    result["decided"] = True
    result["chosen_kind"] = chosen.kind
    result["chosen_severity"] = chosen.severity

    message = compose_message(chosen)
    result["message"] = message

    if dry_run:
        result["reason"] = "dry_run=True, push não enviado"
        return result

    send_push(message)
    result["pushed"] = True

    subject_id = _resolve_subject_id(chosen.subject)

    notif_repo.create(
        kind=chosen.kind,
        message=message,
        topic=chosen.topic,
        subject_id=subject_id,
    )

    return result


def _resolve_subject_id(subject_name: str | None) -> int | None:
    if not subject_name:
        return None
    from src.repositories import subjects as subj_repo
    found = subj_repo.get_by_name(subject_name)
    return found["id"] if found else None