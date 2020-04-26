#! /usr/bin python

import sys

from db.connection import (
    execute_sql,
    css_cursor,
)

UP_SQL = """
CREATE TABLE orders (
  id               INTEGER  PRIMARY KEY
, status           TEXT  --one of {queued, in progress, completed}
, received_at      INTEGER --epochs
, started_at       INTEGER --epochs
, completed_at     INTEGER --epochs
, customer_name    TEXT
, service          TEXT
, total_price      INTEGER
, items            TEXT --json
);
"""

DOWN_SQL = """
DROP TABLE IF EXISTS orders;
"""

def recreate_orders_table():
    """Drop and recreate orders table"""
    with css_cursor() as cur:
        execute_sql(DOWN_SQL, cur, verbose=True)
        execute_sql(UP_SQL, cur, verbose=True)

if __name__ == '__main__':
    run_migration()
