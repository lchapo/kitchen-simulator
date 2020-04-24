#! /usr/bin python

import sys

from common import (
    execute_sql,
    css_cursor,
)

UP_SQL = """
CREATE TABLE orders (
  id               INTEGER  PRIMARY KEY
, status           TEXT  --one of {received, being prepared, completed}
, received_at      DATETIME
, started_at       DATETIME
, completed_at     DATETIME
, customer_name    TEXT
, service          TEXT
, total_price      TEXT
, items            TEXT --json
);
"""

DOWN_SQL = """
DROP TABLE IF EXISTS orders;
"""

def run_migration():
    """Execute and commit SQL

    Examples:
      Run UP SQL: ipython {migration_filepath}
      Run UP SQL: ipython {migration_filepath} upgrade
      Run DOWN SQL: ipython {migration_filepath} downgrade
    """
    arg = sys.argv[1] if len(sys.argv) > 1 else 'upgrade'
    with css_cursor() as cur:
        if arg == 'upgrade':
            execute_sql(UP_SQL, cur)
        elif arg == 'downgrade':
            execute_sql(DOWN_SQL, cur)

if __name__ == '__main__':
    run_migration()
