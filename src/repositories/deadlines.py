from datetime import datetime
from typing import Literal, Optional
from src.db import get_cursor


DeadlineKind = Literal["prova", "entrega", "trabalho", "outro"]


def create(
    subject_id: int,
    title: str,
    kind: DeadlineKind,
    due_at: datetime,
) -> dict:
    with get_cursor() as cur:
        cur.execute(
            """
            insert into deadlines (subject_id, title, kind, due_at)
            values (%s, %s, %s, %s)
            returning id, subject_id, title, kind, due_at, completed, created_at
            """,
            (subject_id, title, kind, due_at),
        )
        return cur.fetchone()


def get_upcoming(days: int = 14) -> list[dict]:
    with get_cursor() as cur:
        cur.execute(
            """
            select 
                d.id, d.title, d.kind, d.due_at, d.completed,
                subj.id as subject_id,
                subj.name as subject_name,
                subj.category as subject_category,
                extract(epoch from (d.due_at - now())) / 86400 as days_until
            from deadlines d
            join subjects subj on subj.id = d.subject_id
            where d.completed = false
              and d.due_at >= now()
              and d.due_at <= now() + make_interval(days => %s)
            order by d.due_at asc
            """,
            (days,),
        )
        return cur.fetchall()


def get_overdue() -> list[dict]:
    with get_cursor() as cur:
        cur.execute(
            """
            select 
                d.id, d.title, d.kind, d.due_at,
                subj.name as subject_name,
                subj.category as subject_category
            from deadlines d
            join subjects subj on subj.id = d.subject_id
            where d.completed = false
              and d.due_at < now()
            order by d.due_at asc
            """
        )
        return cur.fetchall()


def mark_completed(deadline_id: int) -> bool:
    with get_cursor() as cur:
        cur.execute(
            "update deadlines set completed = true where id = %s",
            (deadline_id,),
        )
        return cur.rowcount > 0


def list_all(include_completed: bool = False) -> list[dict]:
    with get_cursor() as cur:
        if include_completed:
            cur.execute(
                """
                select d.id, d.title, d.kind, d.due_at, d.completed,
                       subj.name as subject_name, subj.category as subject_category
                from deadlines d
                join subjects subj on subj.id = d.subject_id
                order by d.due_at asc
                """
            )
        else:
            cur.execute(
                """
                select d.id, d.title, d.kind, d.due_at, d.completed,
                       subj.name as subject_name, subj.category as subject_category
                from deadlines d
                join subjects subj on subj.id = d.subject_id
                where d.completed = false
                order by d.due_at asc
                """
            )
        return cur.fetchall()