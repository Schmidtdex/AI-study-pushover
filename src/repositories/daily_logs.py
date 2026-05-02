from datetime import date, timedelta
from typing import Optional
from src.db import get_cursor


def upsert(
    log_date: Optional[date] = None,
    energy: Optional[int] = None,
    mood: Optional[str] = None,
    note: Optional[str] = None,
) -> dict:
    target_date = log_date or date.today()
    
    with get_cursor() as cur:
        cur.execute(
            """
            insert into daily_logs (log_date, energy, mood, note)
            values (%s, %s, %s, %s)
            on conflict (log_date) do update set
                energy = coalesce(excluded.energy, daily_logs.energy),
                mood   = coalesce(excluded.mood,   daily_logs.mood),
                note   = coalesce(excluded.note,   daily_logs.note)
            returning id, log_date, energy, mood, note, created_at
            """,
            (target_date, energy, mood, note),
        )
        return cur.fetchone()


def get_by_date(log_date: date) -> Optional[dict]:
    with get_cursor() as cur:
        cur.execute(
            """
            select id, log_date, energy, mood, note, created_at
            from daily_logs
            where log_date = %s
            """,
            (log_date,),
        )
        return cur.fetchone()


def get_recent(days: int = 7) -> list[dict]:
    with get_cursor() as cur:
        cur.execute(
            """
            select id, log_date, energy, mood, note, created_at
            from daily_logs
            where log_date >= current_date - make_interval(days => %s)
            order by log_date desc
            """,
            (days,),
        )
        return cur.fetchall()


def average_energy(days: int = 7) -> Optional[float]:
    with get_cursor() as cur:
        cur.execute(
            """
            select avg(energy)::float as avg_energy
            from daily_logs
            where log_date >= current_date - make_interval(days => %s)
              and energy is not null
            """,
            (days,),
        )
        row = cur.fetchone()
        return row["avg_energy"] if row else None