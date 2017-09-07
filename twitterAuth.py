import tweepy
import twitterConfig as cfg

consumer_key = cfg.twitter['consumer']
consumer_secret = cfg.twitter['consumerSecret']
access_token = cfg.twitter['token']
access_token_secret = cfg.twitter['tokenSecret']

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

user = "smrt_singapore"
results = api.user_timeline(screen_name = user)

for status in results:
    print(status.text)
    print(status.created_at)
