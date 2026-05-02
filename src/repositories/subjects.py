from email import generator
from typing import Literal, Optional
from src.db import get_cursor


Category = Literal["faculdade", "pessoal"]


def create(name: str, category: Category = "faculdade") -> dict:
    with get_cursor() as cur:
        cur.execute(
            """
            insert into subjects (name, category)
            values (%s, %s)
            returning id, name, category, created_at
            """,
            (name, category),
        )
        return cur.fetchone()

def get_by_id(subject_id: int) -> Optional[dict]:
    with get_cursor() as cur:
        cur.execute(
            "select id, name, category, created_at from subjects where id =%s",
            (subject_id,)
        )
        return cur.fetchone()

def get_by_name(name: str) -> Optional[dict]:
    with get_cursor() as cur:
        cur.execute(
            "select id, name, category, created_at from subjects where name =%s",
            (name,)
        )
        return cur.fetchone()

def get_or_create(name: str, category: Category = "faculdade") -> dict:
    existing = get_by_name(name)
    if existing:
        return existing
    return create(name, category)

def list_all(category: Optional[Category] = None) -> list[dict]:
    with get_cursor() as cur:
        if category:
            cur.execute(
                """
                select id, name, category, created_at 
                from subjects 
                where category = %s
                order by name
                """,
                (category,),
            )
        else:
            cur.execute(
                "select id, name, category, created_at from subjects order by name"
            )
        return cur.fetchall()


def delete(subject_id: int) -> bool:
    with get_cursor() as cur:
        cur.execute("delete from subjects where id = %s", (subject_id,))
        return cur.rowcount > 0