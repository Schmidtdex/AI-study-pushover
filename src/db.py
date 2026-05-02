from contextlib import contextmanager
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row

from src.config import config

pool = ConnectionPool(config.database_url, min_size=1, max_size=5, open=True)


@contextmanager
def get_cursor():
    with pool.connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            yield cur

def close_pool() -> None:
    pool.close()