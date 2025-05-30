
import requests
import datetime
import os
import time

BEARER_TOKEN = os.environ['BEARER_TOKEN']
HEADERS = {
    "Authorization": f"Bearer {BEARER_TOKEN}"
}

USER_MAP = {
    "1851571508872654848": "Rosemarie656665",
    "1841179171558461447": "rebecca_mi90591"
}

SELF_ID = "1872918797662994436"

now = datetime.datetime.utcnow()
fifteen_minutes_ago = now - datetime.timedelta(minutes=15)
start_time = fifteen_minutes_ago.isoformat("T") + "Z"
end_time = now.isoformat("T") + "Z"

rt_total = 0
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
    return response.status_code, response.json()

def like_and_retweet(tweet_id):
    print(f"→ Liking and retweeting: {tweet_id}")
    like_res = requests.post(
        f"https://api.twitter.com/2/users/{SELF_ID}/likes",
        headers=HEADERS,
        json={"tweet_id": tweet_id}
    )
    rt_res = requests.post(
        f"https://api.twitter.com/2/users/{SELF_ID}/retweets",
        headers=HEADERS,
        json={"tweet_id": tweet_id}
    )
    print(f"   Like status: {like_res.status_code}")
    print(f"   Retweet status: {rt_res.status_code}")
    return like_res.status_code == 200 and rt_res.status_code == 200

for uid, username in USER_MAP.items():
    print(f"=== Checking tweets from user: {uid} ({username}) ===")
    status_code, data = get_recent_tweets(uid)
    tweets = data.get("data", [])
    includes = data.get("includes", {})
    media_dict = {m["media_key"]: m for m in includes.get("media", [])}
    rt_count = 0

    if status_code == 429:
        send_discord_alert("DISCORD_WEBHOOK_ERROR", f"⚠️ @{username}：API制限（429）。投稿取得失敗。")
        continue
    elif status_code >= 400:
        send_discord_alert("DISCORD_WEBHOOK_ERROR", f"❌ @{username}：エラー（{status_code}）で投稿取得失敗。")
        continue

    if not tweets:
        send_discord_alert("DISCORD_WEBHOOK_NO_MATCH", f"ℹ️ @{username}：15分以内に投稿なし。")
        continue

    for tweet in tweets:
        tweet_id = tweet["id"]
        attachments = tweet.get("attachments", {})
        media_keys = attachments.get("media_keys", [])
        if not media_keys:
            continue
        if any(media_dict.get(k, {}).get("type") == "photo" for k in media_keys):
            if like_and_retweet(tweet_id):
                tweet_url = f"https://twitter.com/{username}/status/{tweet_id}"
                send_discord_alert("DISCORD_WEBHOOK_SUCCESS", f"✅ RT成功：@{username} の投稿
{tweet_url}")
                rt_count += 1

    if rt_count == 0:
        send_discord_alert("DISCORD_WEBHOOK_NO_MATCH", f"ℹ️ @{username}：画像付きツイートなし。RTせず。")
    else:
        rt_total += rt_count

# 全体まとめ通知（任意、今回は省略）
if error_flag:
    print("⚠️ Some errors occurred during processing.")
else:
    print(f"✅ All done. Total RTs: {rt_total}")
