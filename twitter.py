import schedule
import tweepy
import time

twitter = {
    'consumer': 'Cvs4dBBjFg2i75ujgBUVooSgR',
    'consumerSecret': 'WFBhwGHD1WAOlytOTocLO2vPS3CcVdYFX3pDmbFDRWPd387uh0',
    'token': '905338848447627264-6jKrns9OUd58LLaQvmc5dPwFG2zkzAr',
    'tokenSecret': 'SWb5DLc0Uamxl0q4F1Cu9qzyaju2zp77pgxmXlz7eSW7P'
}

consumer_key = twitter['consumer']
consumer_secret = twitter['consumerSecret']
access_token = twitter['token']
access_token_secret = twitter['tokenSecret']

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

train_lines = [ 'NSL', 'EWL', 'BPLRT', 'NSEWL', 'NSEWL', 'CCL', 'NEL', 'DTL' ]
previous_timestamp = 0

def twitter_pull():
    api = tweepy.API(auth)

    global previous_timestamp
    user = "joshenlimek"
    results = api.user_timeline(screen_name = user)
    latest_tweet = results[0]
    latest_tweet_timestamp = time.mktime(time.strptime(str(latest_tweet.created_at), '%Y-%m-%d %H:%M:%S'))
    current_timestamp = time.time()

    is_tweet_relevant_to_train = any(train_line in latest_tweet.text for train_line in train_lines)
    is_new_tweet = latest_tweet_timestamp > previous_timestamp
    is_latest_tweet_old = current_timestamp < (5 * 60) + latest_tweet_timestamp + (8 * 60 * 60)

    if is_new_tweet and is_tweet_relevant_to_train and is_latest_tweet_old:
        message = latest_tweet.text
        bot.sendMessage(chat_assigned, message)
        previous_timestamp = latest_tweet_timestamp

    else:
        print("No updates")

schedule.every(5).seconds.do(twitter_pull)

while 1:
    schedule.run_pending()
    time.sleep(1)
