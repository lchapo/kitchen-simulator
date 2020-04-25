from contextlib import contextmanager
import sqlite3

CSS_DATABASE = 'db/css.db'

@contextmanager
def css_connection():
    """Callable connection to the CSS database"""
    conn = sqlite3.connect(CSS_DATABASE)
    try:
        yield conn
    finally:
        conn.close()
