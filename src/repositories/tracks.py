from typing import Optional
from src.db import get_cursor


def create(
    subject_id: int,
    course_name: Optional[str] = None,
    course_url: Optional[str] = None,
    goal: Optional[str] = None,
) -> dict:
    with get_cursor() as cur:
        cur.execute(
            """
            insert into learning_tracks (subject_id, course_name, course_url, goal)
            values (%s, %s, %s, %s)
            returning id, subject_id, course_name, course_url, goal,
                      started_at, is_active, created_at
            """,
            (subject_id, course_name, course_url, goal),
        )
        return cur.fetchone()


def list_active() -> list[dict]:
    with get_cursor() as cur:
        cur.execute(
            """
            select 
                t.id, t.course_name, t.course_url, t.goal,
                t.started_at, t.is_active,
                subj.id as subject_id,
                subj.name as subject_name
            from learning_tracks t
            join subjects subj on subj.id = t.subject_id
            where t.is_active = true
            order by t.started_at desc
            """
        )
        return cur.fetchall()


def get_by_subject(subject_id: int) -> Optional[dict]:
    with get_cursor() as cur:
        cur.execute(
            """
            select id, subject_id, course_name, course_url, goal,
                   started_at, is_active
            from learning_tracks
            where subject_id = %s
            order by created_at desc
            limit 1
            """,
            (subject_id,),
        )
        return cur.fetchone()


def deactivate(track_id: int) -> bool:
    with get_cursor() as cur:
        cur.execute(
            "update learning_tracks set is_active = false where id = %s",
            (track_id,),
        )
        return cur.rowcount > 0


def reactivate(track_id: int) -> bool:
    with get_cursor() as cur:
        cur.execute(
            "update learning_tracks set is_active = true where id = %s",
            (track_id,),
        )
        return cur.rowcount > 0