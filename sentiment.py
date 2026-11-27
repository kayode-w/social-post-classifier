from loader import conn
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime, timezone
analyzer = SentimentIntensityAnalyzer()

CURRENT_TIME = datetime.now(timezone.utc)


def get_posts(conn) -> list[tuple]:
    """
    Fetch English posts from stg_posts that don't have a sentiment score yet.

    Args:
        conn: An open psycopg2 connection. Not closed here.

    Returns:
        list[tuple]: One (post_id, content_no_hashtags) pair per unscored post.
        Empty list if every post is already scored.
    """
    cur = conn.cursor()
    posts = """select post_id, content_no_hashtags
               from dbt_dev.stg_posts s
               where s.language = 'en'
               and not exists(    ---exclude posts that already exists
               select 1 from public.post_sentiment p
               where p.post_id = s.post_id
               )
            """
    cur.execute(posts)
    rows = cur.fetchall()

    cur.close()

    return rows

def score_texts(rows: list[tuple]) -> list[tuple]:
    """
    Score each post's text with VADER.

    Args:
        rows (list[tuple]): (post_id, text) pairs, as returned by get_posts.

    Returns:
        list[tuple]: One (post_id, compound) pair per post. compound runs
        from -1 (very negative) to 1 (very positive).
    """
    scored_posts = []

    for pid, col in rows:
        score = analyzer.polarity_scores(col)["compound"]
        scored_posts.append((pid, score)) #append everything as a single item in scored_post

    return scored_posts


sql = """
INSERT INTO public.post_sentiment (post_id, compound, scored_at)
VALUES (%s, %s, %s)
ON CONFLICT (post_id) DO NOTHING 
"""

def load_scores(conn, scored_posts: list[tuple], scored_at=CURRENT_TIME) -> int:
    """
    Insert scores into public.post_sentiment, skipping posts already there.

    Args:
        conn: An open psycopg2 connection. Committed here, not closed.
        scored_posts (list[tuple]): (post_id, compound) pairs, as returned by score_texts.
        scored_at (datetime): When this batch was scored. Defaults to the run's start time.

    Returns:
        int: Number of rows actually inserted (repeats are skipped and not counted).
    """
    cur = conn.cursor()

    inserted_rows = 0

    for pid, post_score in scored_posts:
        values = (pid, post_score, scored_at)
                  
        cur.execute(sql, values)
        inserted_rows += cur.rowcount

    conn.commit()
    cur.close()
    return inserted_rows


def main():
    rows = get_posts(conn)
    scored_posts = score_texts(rows)
    tbl_cnt = load_scores(conn, scored_posts)
    print(f"Scored {len(scored_posts)}, inserted {tbl_cnt}")    

    conn.close()

if __name__ == "__main__":
    main()




