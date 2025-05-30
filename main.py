
import requests
import datetime
import os
import time

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

rt_count = 0
error_flag = False

def send_discord_alert(webhook_env, message):
    url = os.environ.get(webhook_env)
    if not url:
        print(f"{webhook_env} not set. Skipping alert.")
        return
    payload = {"content": message}
    res = requests.post(url, json=payload)
    print(f"[Webhook:{webhook_env}] status: {res.status_code}")

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
    if response.status_code == 429 or response.status_code >= 500:
        global error_flag
        error_flag = True
    return response.json()

def like_and_retweet(tweet_id):
    global rt_count
    print(f"→ Liking and retweeting: {tweet_id}")
    like_res = requests.post(
        f"https://api.twitter.com/2/users/{SELF_ID}/likes",
        headers=HEADERS,
        json={"tweet_id": tweet_id}
    )
    print(f"   Like status: {like_res.status_code}")
    rt_res = requests.post(
        f"https://api.twitter.com/2/users/{SELF_ID}/retweets",
        headers=HEADERS,
        json={"tweet_id": tweet_id}
    )
    print(f"   Retweet status: {rt_res.status_code}")
    if like_res.status_code == 200 and rt_res.status_code == 200:
        rt_count += 1

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

    time.sleep(2)  # sleep to reduce rate limit issues

# Notification logic
if error_flag:
    send_discord_alert("DISCORD_WEBHOOK_ERROR", "⚠️ APIリクエストが制限されました（429など）。RTできませんでした。")
elif rt_count == 0:
    send_discord_alert("DISCORD_WEBHOOK_NO_MATCH", "ℹ️ 画像付きツイートが見つかりませんでした。RTなし。")
else:
    send_discord_alert("DISCORD_WEBHOOK_SUCCESS", f"✅ RT完了：{rt_count} 件の画像付きツイートをRT・いいねしました。")
