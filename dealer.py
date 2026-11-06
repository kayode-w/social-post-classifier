import requests
import json
from datetime import datetime, timedelta, timezone

# created this because i needed a way to pass the elements into the two functions
INSTANCE = "mastodon.social"
HASHTAG = "tech"
CURRENT_TIME = datetime.now(timezone.utc).isoformat() #converts the time to a string that can be read by json dumps
MAX_PAGES = 3

# # step 1: grab the posts
# def fetch_posts(instance: str, hashtag: str) -> list[dict]: #returns a list of dictionaries, each representing a post
#     """
#     Fetches posts from a Mastodon instance based on a given hashtag.

#     Args:
#         instance (str): The Mastodon instance URL (e.g., "mastodon.social").
#         hashtag (str): The hashtag to search for (without the '#' symbol).
#     Returns:
#         list of dicts: A list of dictionaries containing the extracted information.
#     """
 
#     url = f"https://{instance}/api/v1/timelines/tag/{hashtag}"

#     response = requests.get(url, params={"limit": 40}, timeout=10) #limit to 40 posts and timeout after 10 seconds
#     response.raise_for_status()  #raise an error for bad responses
#     data = response.json()

#     return data
# # print(posts[0].keys())  # Print the first post for inspection

# step 1: since we have multiple pages of posts, we need to loop through the pages and grab all the posts. This function will return a list of all the posts.
def fetch_posts(instance: str, hashtag: str, max_pages: int = MAX_PAGES) -> list[dict]: #returns a list of dictionaries, each representing a post
    """
    Fetches posts from a Mastodon instance for a given hashtag, following
    the next page links until there are no more pages or max_pages is reached.

    Args:
        instance (str): The Mastodon server name (e.g., "mastodon.social").
        hashtag (str): The hashtag to search for (without the '#' symbol).
        max_pages (int): The most pages to fetch. Each page holds up to 40 posts.

    Returns:
        list[dict]: The raw posts, one dictionary per post, exactly as Mastodon sent them.
    """
 
    url = f"https://{instance}/api/v1/timelines/tag/{hashtag}?limit=40"
    posts = []

    for page in range(max_pages):

        response = requests.get(url, timeout=10) #limit to 40 posts and timeout after 10 seconds
        response.raise_for_status()  #raise an error for bad responses
        data = response.json()
        posts.extend(data)

        # now we loop through the other pages, response.links contains the info for the next page. 

        # {
        #     "next": {"url": "https://...max_id=123", "rel": "next"},
        #     "prev": {"url": "https://...min_id=456", "rel": "prev"}
        # }
        next_url = response.links.get('next', {}).get('url')
        if not next_url:
            break
        url = next_url

    return posts


# step 2: extract only the fields we need (this function assumes that what is past in is a single post, not the list of posts)
def extract_fields(post: dict, instance: str, hashtag: str, loaded_at: str = CURRENT_TIME) -> dict: #need to give it one post, not the list of posts
    """
    Extracts relevant fields from a single post.

    Args:
        post (dict): A dictionary representing a single post.
        instance (str): Server instance where post is fetched from.
        hashtag (str): Hashtag of post that has been fetched.
        loaded_at (str): When this batch was loaded, in UTC
    Returns:
        dict: A dictionary containing the extracted information.
    """

    #the tags are nested within the post and contain multiple tags, so i'll run a loop to extract the tag name so it can be appended into the dict below
    tag_names = []
    for tag in post['tags']:
        name = tag['name']
        tag_names.append(name)

    #here, i'd extract the server used for this post, useful field in analytics to help filter the origin of the posts.
    acc = post['account']['acct']
    author_server = acc.split('@')[1] if '@' in acc else instance

    row = {
        "post_id": post["id"],
        "content_html": post["content"],
        "created_at": post["created_at"],
        "language": post["language"],
        "instance": instance,
        "is_reblog": False if post["reblog"] is None else True,
        # "post_type": "repost" if post["reblog"] is not None else "original",
        "source_hashtag": hashtag,
        "tags": tag_names,
        "author_server": author_server,
        "loaded_at": loaded_at
        }
    return row
    
# calls
posts = fetch_posts(INSTANCE, HASHTAG, MAX_PAGES) #list of posts, each post is a dictionary
# row = extract_fields(posts[0])

#step 3: re arrange all posts into list with the relevant data we extracted
all_posts = []

# at this point, we feed the fxn one post at a time
for post in posts:

    tbl_row = extract_fields(post, INSTANCE, HASHTAG) #extract the relevant fields one post at a time.
    all_posts.append(tbl_row)

print(type(all_posts))
print(len(all_posts))
print(json.dumps(all_posts, indent = 2,ensure_ascii=False ))