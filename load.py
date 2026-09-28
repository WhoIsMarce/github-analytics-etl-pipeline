import logging
import psycopg

logger = logging.getLogger(__name__)

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS issues (
    id BIGINT PRIMARY KEY,
    number INT,
    title TEXT,
    state TEXT,
    is_pull_request BOOLEAN,
    created_at TIMESTAMPTZ,
    closed_at TIMESTAMPTZ,
    comments INT,
    author TEXT,
    time_to_close_hours NUMERIC
);
"""


UPSERT = """
INSERT INTO issues (id, number, title, state, is_pull_request, created_at, closed_at, comments, author, time_to_close_hours)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (id) DO UPDATE SET
    state = EXCLUDED.state,
    closed_at = EXCLUDED.closed_at,
    comments = EXCLUDED.comments,
    time_to_close_hours = EXCLUDED.time_to_close_hours;
"""


def get_connection(db_config: dict):
    return psycopg.connect(**db_config)

def ensure_schema(conn):
    with conn.cursor() as cur:
        cur.execute(CREATE_TABLE)
        conn.commit()
        
def load_rows(conn, rows: list[dict]):
    if not rows:
        logger.info("No rows to load.")
        return
    values = [
        (r["id"], r["number"], r["title"], r["state"], r["is_pull_request"],
        r["created_at"], r["closed_at"], r["comments"], r["author"], r["time_to_close_hours"])
        for r in rows 
    ]
    with conn.cursor() as cur:
        cur.executemany(UPSERT, values)
    conn.commit()
    logger.info("Loaded/updated %d rows.", len(rows))