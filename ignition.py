from dealer import fetch_posts, extract_fields, INSTANCE, HASHTAG, MAX_PAGES, json
from loader import conn, load_posts





posts = fetch_posts(INSTANCE, HASHTAG, MAX_PAGES) #list of posts, each post is a dictionary

all_posts = []

# at this point, we feed the fxn one post at a time
for post in posts:

    tbl_row = extract_fields(post, INSTANCE, HASHTAG) #extract the relevant fields one post at a time.
    all_posts.append(tbl_row)

# loading the posts into the database
inserted = load_posts(conn, all_posts)
print(f"Fetched {len(all_posts)}, inserted {inserted}, skipped {len(all_posts) - inserted}")
conn.close()