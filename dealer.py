import requests
import json
from requests.exceptions import RequestException

# step 1: grab the posts
def fetch_posts(instance: str, hashtag: str) -> list[dict]: #returns a list of dictionaries, each representing a post
    """
    Fetches posts from a Mastodon instance based on a given hashtag.

    Args:
        instance (str): The Mastodon instance URL (e.g., "mastodon.social").
        hashtag (str): The hashtag to search for (without the '#' symbol).
    """
 
    url = f"https://{instance}/api/v1/timelines/tag/{hashtag}"

    response = requests.get(url, params={"limit": 40}, timeout=10) #limit to 40 posts and timeout after 10 seconds
    response.raise_for_status()  #raise an error for bad responses
    data = response.json()

    return data
# print(posts[0].keys())  # Print the first post for inspection


# step 2: extract only the fields we need
def extract_fields(post: dict) -> dict: #need to give it one post, not the list of posts
    """
    Extracts relevant information from a list of posts.

    Args:
        post (dict): A dictionary representing a single post.
    Returns:
        dict: A dictionary containing the extracted information.
    """

    row = {
        "post_id": post["id"],
        "content_html": post["content"],
        "created_at": post["created_at"],
        "language": post["language"]
        }
    return row
    

posts = fetch_posts("mastodon.social", "tech") #list of posts, each post is a dictionary
# row = extract_fields(posts[0])


#step 3: re arrange all posts into list with the relevant data we extracted
all_posts = []

for post in posts:
    tbl_row = extract_fields(post)
    all_posts.append(tbl_row)

print(type(all_posts))
print(len(all_posts))
print(json.dumps(all_posts, indent = 2,ensure_ascii=False ))