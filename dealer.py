import requests
import json
from datetime import datetime, timedelta, timezone

# created this because i needed a way to pass the elements into the two functions
INSTANCE = "mastodon.social"
HASHTAG = "tech"
CURRENT_TIME = datetime.now(timezone.utc).isoformat() #converts the time to a string that can be read by json dumps


# step 1: grab the posts
def fetch_posts(instance: str, hashtag: str) -> list[dict]: #returns a list of dictionaries, each representing a post
    """
    Fetches posts from a Mastodon instance based on a given hashtag.

    Args:
        instance (str): The Mastodon instance URL (e.g., "mastodon.social").
        hashtag (str): The hashtag to search for (without the '#' symbol).
    Returns:
        list of dicts: A list of dictionaries containing the extracted information.
    """
 
    url = f"https://{instance}/api/v1/timelines/tag/{hashtag}"

    response = requests.get(url, params={"limit": 40}, timeout=10) #limit to 40 posts and timeout after 10 seconds
    response.raise_for_status()  #raise an error for bad responses
    data = response.json()

    return data
# print(posts[0].keys())  # Print the first post for inspection


# step 2: extract only the fields we need
def extract_fields(post: dict, instance: str, hashtag: str, loaded_at: str = CURRENT_TIME) -> dict: #need to give it one post, not the list of posts
    """
    Extracts relevant information from a single post.

    Args:
        post (dict): A dictionary representing a single post.
        instance (str): Server instance where post is fetched from.
        hashtag (str): Hashtag of post that has been fetched.
        loaded_at (str): When this batch was loaded, in UTC
    Returns:
        dict: A dictionary containing the extracted information.
    """

    row = {
        "post_id": post["id"],
        "content_html": post["content"],
        "created_at": post["created_at"],
        "language": post["language"],
        "instance": instance,
        "is_reblog": False if post["reblog"] is None else True,
        "post_type": "repost" if post["reblog"] is not None else "original",
        "source_hashtag": hashtag,
        "loaded_at": loaded_at
        }
    return row
    
# calls
posts = fetch_posts(INSTANCE, HASHTAG) #list of posts, each post is a dictionary
# row = extract_fields(posts[0])

#step 3: re arrange all posts into list with the relevant data we extracted
all_posts = []

# at this point, we feed the fxn one post at a time
for post in posts:

    tbl_row = extract_fields(post, INSTANCE, HASHTAG)

    all_posts.append(tbl_row)

print(type(all_posts))
print(len(all_posts))
print(json.dumps(all_posts, indent = 2,ensure_ascii=False ))