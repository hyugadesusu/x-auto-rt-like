import os
import requests
from datetime import datetime, timezone, timedelta

# 環境変数から取得
BEARER_TOKEN = os.environ["BEARER_TOKEN"]
USERS = [
    os.environ["B_USER"],
    os.environ["C_USER"],
    os.environ["D_USER"]
]

HEADERS = {
    "Authorization": f"Bearer {BEARER_TOKEN}"
}

API_URL = "https://api.twitter.com/2"


def get_user_id(username):
    url = f"{API_URL}/users/by/username/{username}"
    res = requests.get(url, headers=HEADERS)
    return res.json().get("data", {}).get("id")


def get_latest_tweets(user_id):
    url = f"{API_URL}/users/{user_id}/tweets"
    params = {
        "max_results": 5,
        "tweet.fields": "created_at,attachments",
        "expansions": "attachments.media_keys",
        "media.fields": "type,url"
    }
    res = requests.get(url, headers=HEADERS, params=params)
    return res.json()


def get_my_user_id():
    url = f"{API_URL}/users/me"
    res = requests.get(url, headers=HEADERS)
    return res.json()["data"]["id"]


def retweet(my_id, tweet_id):
    url = f"{API_URL}/users/{my_id}/retweets"
    res = requests.post(url, headers=HEADERS, json={"tweet_id": tweet_id})
    print(f"Retweet {tweet_id}: {res.status_code}")


def like(my_id, tweet_id):
    url = f"{API_URL}/users/{my_id}/likes"
    res = requests.post(url, headers=HEADERS, json={"tweet_id": tweet_id})
    print(f"Like {tweet_id}: {res.status_code}")


# メイン処理
my_user_id = get_my_user_id()

for username in USERS:
    user_id = get_user_id(username)
    tweets_data = get_latest_tweets(user_id)

    tweets = tweets_data.get("data", [])
    media_keys = set()
    if "includes" in tweets_data and "media" in tweets_data["includes"]:
        media_keys = {media["media_key"] for media in tweets_data["includes"]["media"]}

    for tweet in tweets:
        # 投稿日時チェック
        created_at = datetime.strptime(tweet["created_at"], "%Y-%m-%dT%H:%M:%S.%fZ")
        created_at = created_at.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        if now - created_at > timedelta(minutes=15):
            continue

        # メディア付きチェック
        has_media = False
        if "attachments" in tweet and "media_keys" in tweet["attachments"]:
            if any(key in media_keys for key in tweet["attachments"]["media_keys"]):
                has_media = True

        if has_media:
            tweet_id = tweet["id"]
            retweet(my_user_id, tweet_id)
            like(my_user_id, tweet_id)
