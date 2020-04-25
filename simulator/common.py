from contextlib import contextmanager
import csv
import logging
import time
import sqlite3
import sys


CSS_DATABASE = 'db/css.db'
ORDERS_TABLE = 'orders'

def setup_logging(module=None, level=logging.INFO):
    """Configure logger"""
    logger = logging.getLogger(module or '')
    logger.setLevel(level)
    logging.Formatter.converter = time.gmtime
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(processName)s - %(levelname)s - %(message)s'
    )
    stream_handler = logging.StreamHandler(sys.stderr)
    stream_handler.setLevel(level)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    return logger

logger = setup_logging(__name__)

@contextmanager
def css_cursor():
    """Callable cursor that connects to the CSS database

    Commits (only) after all statements with the open cursor have been
    successfully executed, then closes the connection
    """
    conn = sqlite3.connect(CSS_DATABASE)
    cur = conn.cursor()
    try:
        yield cur
    finally:
        conn.commit()
        cur.close()
        conn.close()

@contextmanager
def css_connection():
    """Callable connection to the CSS database"""
    conn = sqlite3.connect(CSS_DATABASE)
    try:
        yield conn
    finally:
        conn.close()


def execute_sql(sql, cur, runtime_values=None, verbose=False):
    """Execute SQL statement in sqlite and log

    Args:
      sql (str): sql statment to be executed
      cur (cursor): open cursor
      runtime_values (tuple): values to bind
      verbose (bool): whether to log the SQL or not
    """
    log_msg = f"Executing SQL: {sql}"
    if runtime_values:
        log_msg += f" with bindings {runtime_values}"
    if verbose:
        logger.info(log_msg)
    if runtime_values:
        cur.execute(sql, runtime_values)
    else:
        cur.execute(sql)
    if verbose:
        logger.info("Done")

def truncate_table(table, cur):
    """Delete all values from table
    
    Args:
      table (str): name of table to truncate
      cur (cursor): open cursor
    """
    SQL = f"DELETE FROM {table};"
    execute_sql(SQL, cur)

def execute_many(sql, values, cur):
    """Execute bulk insertion and log statement

    Args:
      sql (str): insert sql statement with binding placeholders
      values (list of tuples): placeholder bindings (one tuple per row)
      cur (cursor): open cursor
    """
    logger.info(f"Executing SQL: {sql} with values {str(values)[:1000]}...")
    cur.executemany(sql, values)
