from datetime import datetime
from typing import Optional
from src.db import get_cursor


def create(
    kind: str,
    message: str,
    topic: Optional[str] = None,
    subject_id: Optional[int] = None,
) -> dict:
    with get_cursor() as cur:
        cur.execute(
            """
            insert into notifications_log (kind, topic, subject_id, message)
            values (%s, %s, %s, %s)
            returning id, kind, topic, subject_id, message, sent_at
            """,
            (kind, topic, subject_id, message),
        )
        return cur.fetchone()


def list_since(cutoff: datetime) -> list[dict]:
    with get_cursor() as cur:
        cur.execute(
            """
            select 
                n.id, n.kind, n.topic, n.message, n.sent_at,
                subj.name as subject_name
            from notifications_log n
            left join subjects subj on subj.id = n.subject_id
            where n.sent_at >= %s
            order by n.sent_at desc
            """,
            (cutoff,),
        )
        return cur.fetchall()


def count_since(cutoff: datetime) -> int:
    with get_cursor() as cur:
        cur.execute(
            "select count(*) as c from notifications_log where sent_at >= %s",
            (cutoff,),
        )
        return cur.fetchone()["c"]