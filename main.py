import os
import requests

# 認証トークンと監視対象ユーザー
BEARER_TOKEN = os.getenv("A_BEARER_TOKEN")
USERS = [
    os.getenv("B_USER"),
    os.getenv("C_USER"),
    os.getenv("D_USER"),
]
HEADERS = {
    "Authorization": f"Bearer {BEARER_TOKEN}",
    "Content-Type": "application/json"
}
API_BASE = "https://api.twitter.com/2"

def get_user_id(username):
    url = f"{API_BASE}/users/by/username/{username}"
    res = requests.get(url, headers=HEADERS)
    if res.status_code != 200:
        raise Exception(f"Failed to get user ID for {username}: {res.text}")
    return res.json()["data"]["id"]

def get_latest_image_tweet(user_id):
    url = f"{API_BASE}/users/{user_id}/tweets?max_results=5&expansions=attachments.media_keys&media.fields=type"
    res = requests.get(url, headers=HEADERS)
    if res.status_code != 200:
        print(f"Failed to get tweets for {user_id}")
        return None
    tweets = res.json()
    media = {m["media_key"]: m for m in tweets.get("includes", {}).get("media", [])}

    for tweet in tweets.get("data", []):
        if "attachments" in tweet and any(media[mk]["type"] == "photo" for mk in tweet["attachments"].get("media_keys", [])):
            return tweet
    return None

def react_to_tweet(tweet_id, user_id):
    # リツイート
    rt_url = f"{API_BASE}/users/{user_id}/retweets"
    rt_res = requests.post(rt_url, json={"tweet_id": tweet_id}, headers=HEADERS)
    if rt_res.status_code == 200:
        print(f"Retweeted: {tweet_id}")
    else:
        print(f"RT failed: {rt_res.text}")

    # いいね
    like_url = f"{API_BASE}/users/{user_id}/likes"
    like_res = requests.post(like_url, json={"tweet_id": tweet_id}, headers=HEADERS)
    if like_res.status_code == 200:
        print(f"Liked: {tweet_id}")
    else:
        print(f"Like failed: {like_res.text}")

def main():
    my_id = get_user_id("me")
    for username in USERS:
        try:
            uid = get_user_id(username)
            tweet = get_latest_image_tweet(uid)
            if tweet:
                react_to_tweet(tweet["id"], my_id)
        except Exception as e:
            print(f"Error processing {username}: {e}")

if __name__ == "__main__":
    main()
