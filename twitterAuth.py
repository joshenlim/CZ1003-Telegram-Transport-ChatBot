import tweepy
import twitterConfig as cfg
import schedule
import time

consumer_key = cfg.twitter['consumer']
consumer_secret = cfg.twitter['consumerSecret']
access_token = cfg.twitter['token']
access_token_secret = cfg.twitter['tokenSecret']

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

# Compare timestamps to only sendMsg when there's a new tweet
previous_timestamp = 0

def twitter_pull():
    api = tweepy.API(auth)
    # user = "smrt_singapore"

    global previous_timestamp
    user = "joshenlimek"
    results = api.user_timeline(screen_name = user)
    latest_tweet = results[0]
    latest_tweet_timestamp = time.mktime(time.strptime(str(latest_tweet.created_at), '%Y-%m-%d %H:%M:%S'))

    if latest_tweet_timestamp > previous_timestamp:
        print(latest_tweet.text)
        print(latest_tweet.created_at)
        previous_timestamp = latest_tweet_timestamp
    else:
        print("No updates")