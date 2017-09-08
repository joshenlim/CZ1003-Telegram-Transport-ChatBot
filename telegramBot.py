import sys
import time
import telepot
import datetime
import requests
import schedule

import tweepy
import config as cfg

from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, ForceReply

consumer_key = cfg.twitter['consumer']
consumer_secret = cfg.twitter['consumerSecret']
access_token = cfg.twitter['token']
access_token_secret = cfg.twitter['tokenSecret']

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

previous_timestamp = 0
chat_assigned = 0
train_lines = [ 'NSL', 'EWL', 'BPLRT', 'NSEWL', 'NSEWL', 'CCL', 'NEL', 'DTL' ]

bot = telepot.Bot('445426933:AAEFuo2S03hYfphhXWWCGNJemEkRZScF-Ho')

def twitter_pull():
    api = tweepy.API(auth)

    global previous_timestamp
    user = "joshenlimek"
    # user = "smrt_singapore"
    results = api.user_timeline(screen_name = user)
    latest_tweet = results[0]
    latest_tweet_timestamp = time.mktime(time.strptime(str(latest_tweet.created_at), '%Y-%m-%d %H:%M:%S'))
    current_timestamp = time.time()

    # Conditions for posting a message
    is_tweet_relevant_to_train = any(train_line in latest_tweet.text for train_line in train_lines)
    is_new_tweet = latest_tweet_timestamp > previous_timestamp
    # Check for relevancy, if tweet within 5 minutes from current time, send message - is 5 minutes a good gauge?
    # Add 8 hours because Twitter timezone is GMT-8
    is_latest_tweet_old = current_timestamp < (5 * 60) + latest_tweet_timestamp + (8 * 60 * 60)

    if is_new_tweet and is_tweet_relevant_to_train and is_latest_tweet_old:
        message = latest_tweet.text
        bot.sendMessage(chat_assigned, message)
        previous_timestamp = latest_tweet_timestamp

    else:
        print("No updates")

def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    global chat_assigned
    chat_assigned = chat_id
    user_message = msg['text']

    if content_type == 'text':
        if '/start' in user_message:
            # Start command required to retrieve chat_id of the current chat that bot is in
            print("Initialize Twitter Pull Cron")
            welcome_message = "Hey there! Phew, finally woken up. I'll be giving updates if any of the train services are down so stay tuned!"
            bot.sendMessage(chat_assigned, welcome_message)
            schedule.every(3).seconds.do(twitter_pull)

        # Sample API call syntax
        elif '/retrieveip' in user_message:
            bot.sendMessage(chat_id, 'Retrieving IP...')
            url = 'https://api.ipify.org?format=json'
            ipAdd = requests.get(url).text
            print(ipAdd)
            bot.sendMessage(chat_id, 'Your IP is: ' + ipAdd)

        # Show Custom Buttons on the phone's keyboard area
        # Use case, buttons that's always used for the bot, to help UX
        elif '/inline' in user_message:
            markup = ReplyKeyboardMarkup(keyboard=[
                     ['Plain text', KeyboardButton(text='Text only')],
                     [dict(text='Phone', request_contact=True), KeyboardButton(text='Location', request_location=True)],
                 ])
            bot.sendMessage(chat_id, 'Custom keyboard with various buttons', reply_markup=markup)

        # Hide the Custom Buttons on the phone's keyboard area
        elif '/hide' in user_message:
            markup = ReplyKeyboardRemove()
            bot.sendMessage(chat_id, 'Hide custom keyboard', reply_markup=markup)

        # Show Custom Buttons in Chat Area
        # Give options to user
        elif '/help' in user_message:
            bot.sendMessage(chat_id, 'Gimme a second, retrieving prices from the various taxi companies...')
            markup = InlineKeyboardMarkup(inline_keyboard=[
                     [dict(text='Uber - $5.80', url='http://www.google.com/')],
                     [dict(text='Grab - $6.00', url='http://www.google.com/')],
                     [dict(text='ComfortDelGro - $5.00', url='http://www.google.com/')],
                    #  [InlineKeyboardButton(text='Callback - show notification', callback_data='notification')],
                    #  [dict(text='Callback - show alert', callback_data='alert')],
                    #  [InlineKeyboardButton(text='Callback - edit message', callback_data='edit')],
                    #  [dict(text='Switch to using bot inline', switch_inline_query='initial query')],
                 ])

            global message_with_inline_keyboard
            message_with_inline_keyboard = bot.sendMessage(chat_id, 'These are the prices to travel from Boon Lay MRT to NTU Tanjong Hall of Residence', reply_markup=markup)

        # Return string which user sent, and message sent timestamp
        else :
            bot.sendMessage(chat_id, 'Hey there ' + msg['from']['username'] + '! You sent me this message: ' + msg['text'])
            bot.sendMessage(chat_id, 'Sent at: ' + datetime.datetime.fromtimestamp(int(msg['date'])).strftime('%Y-%m-%d %H:%M:%S'))

# For Inline Keyboard Markup, respond accordingly for callbacks
def on_callback_query(msg):
    query_id, from_id, data = telepot.glance(msg, flavor='callback_query')
    print('Callback query:', query_id, from_id, data)

    if data == 'notification':
        print("Notification")
        # await bot.answerCallbackQuery(query_id, text='Notification at top of screen')
    elif data == 'alert':
        print("Alert")
        # await bot.answerCallbackQuery(query_id, text='Alert!', show_alert=True)
    elif data == 'edit':
        print("Edit")
        # global message_with_inline_keyboard
        #
        # if message_with_inline_keyboard:
        #     msg_idf = telepot.message_identifier(message_with_inline_keyboard)
        #     await bot.editMessageText(msg_idf, 'NEW MESSAGE HERE!!!!!')
        # else:
        #     await bot.answerCallbackQuery(query_id, text='No previous message to edit')

print('Listening...')

# Listen to user actions on Telegram
MessageLoop(bot, {
    'chat': on_chat_message,
    'callback_query': on_callback_query
}).run_as_thread()

# Keep the program running
while 1:
    schedule.run_pending()
    time.sleep(1)
