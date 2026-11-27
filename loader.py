import os
from dotenv import load_dotenv
import psycopg2
from datetime import datetime

load_dotenv(override=True)

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
)

sql = """
INSERT INTO public.raw_posts
    (post_id, content_html, created_at, language, instance,
     is_reblog, source_hashtag, tags, author_server, loaded_at)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (post_id) DO NOTHING 
"""
#on conflict skips existing rows to prevent dups

#here, the rows we pass is the what is returned from extract_posts
def load_posts(conn, rows: list[dict]) -> int:
    """
    Inserts rows into public.raw_posts, skipping any post_id already stored.

    Args:
        conn: An open psycopg2 connection.
        rows (list[dict]): Rows from extract_fields, one dict per post.

    Returns:
        int: How many rows were actually inserted (new posts).
    """
    cur = conn.cursor()
    inserted = 0

    for row in rows:
        values = (
            row["post_id"],
            row["content_html"],
            row["created_at"],
            row["language"],
            row["instance"],
            row["is_reblog"],
            row["source_hashtag"],
            row["tags"],
            row["author_server"],
            row["loaded_at"]
        )
        cur.execute(sql, values)
        inserted += cur.rowcount

    conn.commit()
    cur.close()
    return inserted