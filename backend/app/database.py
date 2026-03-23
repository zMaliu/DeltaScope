from contextlib import contextmanager

import pymysql

from app.config import DB_CONFIG


def _db_config() -> dict:
    return {**DB_CONFIG, "cursorclass": pymysql.cursors.DictCursor}


def get_connection():
    return pymysql.connect(**_db_config())


@contextmanager
def transaction():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
