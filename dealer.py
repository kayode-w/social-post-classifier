import requests
from requests.exceptions import RequestException


def fetch_posts(instance: str, hashtag: str) -> list[dict]:
    """
    Fetches posts from a Mastodon instance based on a given hashtag.

    Args:
        instance (str): The Mastodon instance URL (e.g., "mastodon.social").
        hashtag (str): The hashtag to search for (without the '#' symbol).
    """
 
    url = f"https://{instance}/api/v1/timelines/tag/{hashtag}"

    response = requests.get(url, params={"limit": 40}, timeout=10)
    response.raise_for_status()  # Raise an error for bad responses
    data = response.json()

    return data

posts = fetch_posts("mastodon.social", "tech")
print(type(posts))
print(len(posts))

print(posts[0].keys())  # Print the first post for inspection