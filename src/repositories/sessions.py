from datetime import datetime, timedelta
from typing import Optional
from src.db import get_cursor


def create(
    subject_id: int,
    topic: str,
    duration_min: int,
    difficulty: Optional[int] = None,
    notes: Optional[str] = None,
    studied_at: Optional[datetime] = None,
) -> dict:

    with get_cursor() as cur:
        cur.execute(
             """
            insert into study_sessions 
                (subject_id, topic, duration_min, difficulty, notes, studied_at)
            values 
                (%s, %s, %s, %s, %s, coalesce(%s, now()))
            returning id, subject_id, topic, duration_min, difficulty, 
                      notes, studied_at, created_at
            """,
            (subject_id, topic, duration_min, difficulty, notes, studied_at),
        )
        return cur.fetchone()

def get_recent(days: int = 7) -> list[dict]:
     with get_cursor() as cur:
        cur.execute(
            """
            select 
            s.id, s.topic, s.duration_min, s.difficulty, 
            s.notes, s.studied_at,
            subj.id as subject_id, subj.name as subject_name, 
            subj.category as subject_category
            from study_sessions s
            join subjects subj on subj.id = s.subject_id
            where s.studied_at >= now() - make_interval(days => %s)
            order by s.studied_at desc
            """,
            (days,),
        )
        return cur.fetchall()

def get_topics_last_seen(days_back: int = 30) -> list[dict]:
        with get_cursor() as cur:
            cur.execute(
                """
                select 
                subj.id as subject_id,
                subj.name as subject_name,
                subj.category as subject_category,
                s.topic,
                max(s.studied_at) as last_seen,
                count(*) as times_studied,
                avg(s.difficulty)::float as avg_difficulty
                from study_sessions s
                join subjects subj on subj.id = s.subject_id
                where s.studied_at >= now() - make_interval(days => %s)
                group by subj.id, subj.name, subj.category, s.topic
                order by last_seen asc
                """,
                (days_back,),
            )
            return cur.fetchall()

def total_minutes_by_subject(days: int = 7) -> list[dict]:
    with get_cursor() as cur:
        cur.execute(
                        """
            select 
                subj.id as subject_id,
                subj.name as subject_name,
                subj.category as subject_category,
                coalesce(sum(s.duration_min), 0) as total_min,
                count(s.id) as session_count
            from subjects subj
            left join study_sessions s 
                on s.subject_id = subj.id
                and s.studied_at >= now() - make_interval(days => %s)
            group by subj.id, subj.name, subj.category
            order by total_min desc
            """,
            (days,),
        )
        return cur.fetchall()

def list_by_subject(subject_id: int, limit: int = 50) -> list[dict]:
    with get_cursor() as cur:
        cur.execute(
                        """
            select id, topic, duration_min, difficulty, notes, studied_at
            from study_sessions
            where subject_id = %s
            order by studied_at desc
            limit %s
            """,
            (subject_id, limit),
        )
        return cur.fetchall()