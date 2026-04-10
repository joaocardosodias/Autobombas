import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

from backend.config import settings

# Pool de conexoes: min 2, max 10
_pool = pool.SimpleConnectionPool(2, 10, settings.DATABASE_URL)


@contextmanager
def get_db():
    """Context manager que fornece cursor com dict rows e faz commit/rollback."""
    conn = _pool.getconn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        _pool.putconn(conn)
