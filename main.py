
import os
import requests
from requests_oauthlib import OAuth1
import datetime

# OAuth1 認証
auth = OAuth1(
    os.environ['API_KEY'],
    os.environ['API_SECRET_KEY'],
    os.environ['ACCESS_TOKEN'],
    os.environ['ACCESS_TOKEN_SECRET']
)

# 対象ユーザーIDと名前のマップ
USER_MAP = {
    "1851571508872654848": "Rosemarie656665",
    "1841179171558461447": "rebecca_mi90591",
    "1741266863477825536": "natalina98207"
}

SELF_ID = "1872918797662994436"

now = datetime.datetime.utcnow()
fifteen_minutes_ago = now - datetime.timedelta(minutes=15)
start_time = fifteen_minutes_ago.isoformat("T") + "Z"
end_time = now.isoformat("T") + "Z"

def get_recent_tweets(user_id):
    url = f"https://api.twitter.com/2/users/{user_id}/tweets"
    params = {
        "max_results": 5,
        "start_time": start_time,
        "end_time": end_time,
        "tweet.fields": "created_at,attachments",
        "expansions": "attachments.media_keys",
        "media.fields": "type,url"
    }
    response = requests.get(url, params=params, auth=auth)
    print(f"[{user_id}] status: {response.status_code}")
    if response.status_code != 200:
        return []
    data = response.json()
    tweets = data.get("data", [])
    media_dict = {}
    includes = data.get("includes", {})
    for m in includes.get("media", []):
        media_dict[m["media_key"]] = m
    results = []
    for tweet in tweets:
        keys = tweet.get("attachments", {}).get("media_keys", [])
        if any(media_dict.get(k, {}).get("type") == "photo" for k in keys):
            results.append(tweet["id"])
    return results

def like_and_retweet(tweet_id):
    like_url = f"https://api.twitter.com/2/users/{SELF_ID}/likes"
    rt_url = f"https://api.twitter.com/2/users/{SELF_ID}/retweets"
    like_res = requests.post(like_url, auth=auth, json={"tweet_id": tweet_id})
    rt_res = requests.post(rt_url, auth=auth, json={"tweet_id": tweet_id})
    print(f"Liked: {like_res.status_code}, Retweeted: {rt_res.status_code}")

for uid, username in USER_MAP.items():
    print(f"=== Checking tweets from user: {uid} ({username}) ===")
    tweet_ids = get_recent_tweets(uid)
    for tid in tweet_ids:
        print(f"→ @{username} posted tweet with image: {tid}")
        like_and_retweet(tid)
