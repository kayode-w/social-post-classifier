import requests
import json

url = "https://mastodon.social/api/v1/instance"

response = requests.get(url, timeout=10)
response.raise_for_status()  # Raise an error for bad responses

data = response.json()

print(response.status_code)
print(type(data))
print(data["title"])

print(json.dumps(data, indent=2))

