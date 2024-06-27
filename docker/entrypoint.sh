#!/bin/sh

set -e

echo "Waiting for database to be ready..."

until python << END
import sys
import psycopg2
import os

def check_database():
    try:
        conn_url = os.environ['DATABASE_URL']
        conn = psycopg2.connect(conn_url)
        conn.close()
        return True
    except psycopg2.OperationalError:
        return False

if check_database():
    sys.exit(0)
else:
    sys.exit(-1)
END
do
  echo "Waiting for PostgreSQL to become available..."
  sleep 1
done

echo "Database is ready, starting the application..."

fastapi dev com_agent/api/app.py --reload --host 0.0.0.0 --port 8000
