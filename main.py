
import requests
import datetime
import os

BEARER_TOKEN = os.environ['BEARER_TOKEN']
HEADERS = {
    "Authorization": f"Bearer {BEARER_TOKEN}"
}

USER_IDS = [
    "1851571508872654848",  # Rosemarie656665
    "1841179171558461447"   # rebecca_mi90591
]

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
    response = requests.get(url, headers=HEADERS, params=params)
    print(f"[{user_id}] status: {response.status_code}")
    return response.json()

def like_and_retweet(tweet_id):
    print(f"→ Liking and retweeting: {tweet_id}")
    # Like
    like_res = requests.post(
        f"https://api.twitter.com/2/users/{SELF_ID}/likes",
        headers=HEADERS,
        json={"tweet_id": tweet_id}
    )
    print(f"   Like status: {like_res.status_code}")
    # Retweet
    rt_res = requests.post(
        f"https://api.twitter.com/2/users/{SELF_ID}/retweets",
        headers=HEADERS,
        json={"tweet_id": tweet_id}
    )
    print(f"   Retweet status: {rt_res.status_code}")

for uid in USER_IDS:
    print(f"=== Checking tweets from user: {uid} ===")
    data = get_recent_tweets(uid)
    tweets = data.get("data", [])
    includes = data.get("includes", {})
    media_dict = {m["media_key"]: m for m in includes.get("media", [])}
    print(f"→ {len(tweets)} tweets found")

    for tweet in tweets:
        tweet_id = tweet["id"]
        attachments = tweet.get("attachments", {})
        media_keys = attachments.get("media_keys", [])

        if not media_keys:
            print(f"   Tweet {tweet_id} has no media, skipping.")
            continue

        if any(media_dict.get(k, {}).get("type") == "photo" for k in media_keys):
            print(f"   Tweet {tweet_id} has photo(s), processing.")
            like_and_retweet(tweet_id)
        else:
            print(f"   Tweet {tweet_id} has media, but not photo, skipping.")
