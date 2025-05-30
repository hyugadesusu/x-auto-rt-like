
import requests
import datetime
import os

BEARER_TOKEN = os.environ['BEARER_TOKEN']
HEADERS = {
    "Authorization": f"Bearer {BEARER_TOKEN}"
}

# 対象ユーザーID（B・Cのみ。Dは後で追加OK）
USER_IDS = [
    "1851571508872654848",  # Rosemarie656665
    "1841179171558461447"   # rebecca_mi90591
]

# 実行アカウントAのID（固定）
SELF_ID = "1872918797662994436"

# 現在時刻と15分前のUTC時間を取得
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
    return response.json()

def like_and_retweet(tweet_id):
    # Like
    requests.post(
        f"https://api.twitter.com/2/users/{SELF_ID}/likes",
        headers=HEADERS,
        json={"tweet_id": tweet_id}
    )
    # Retweet
    requests.post(
        f"https://api.twitter.com/2/users/{SELF_ID}/retweets",
        headers=HEADERS,
        json={"tweet_id": tweet_id}
    )

for uid in USER_IDS:
    data = get_recent_tweets(uid)
    tweets = data.get("data", [])
    includes = data.get("includes", {})
    media_dict = {m["media_key"]: m for m in includes.get("media", [])}

    for tweet in tweets:
        attachments = tweet.get("attachments", {})
        media_keys = attachments.get("media_keys", [])

        # 画像が含まれているツイートだけを対象にする
        if any(media_dict.get(k, {}).get("type") == "photo" for k in media_keys):
            tweet_id = tweet["id"]
            like_and_retweet(tweet_id)
