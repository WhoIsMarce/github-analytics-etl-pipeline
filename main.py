import logging
import os
from dotenv import load_dotenv

from extract import fetch_issues
from transform import normalize_issue, time_to_close_hours
from load import get_connection, ensure_schema, load_rows

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("etl")


def run():
    repo = os.environ["GITHUB_REPO"]
    db_config = {
        "host": os.environ.get("DB_HOST", "localhost"),
        "port": os.environ.get("DB_PORT", "5432"),
        "dbname": os.environ.get("DB_NAME"),
        "user": os.environ.get("DB_USER"),
        "password": os.environ.get("DB_PASSWORD"),
    }

    logger.info("Starting ETL run for %s", repo)

    rows = []
    for raw in fetch_issues(repo, max_pages=5):
        row = normalize_issue(raw)
        row["time_to_close_hours"] = time_to_close_hours(row)
        rows.append(row)

    logger.info("Extracted and transformed %d issues.", len(rows))

    conn = get_connection(db_config)
    try:
        ensure_schema(conn)
        load_rows(conn, rows)
    finally:
        conn.close()

    logger.info("ETL run complete.")


if __name__ == "__main__":
    run()    