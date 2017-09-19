import sys
import time
import telepot
import datetime
import requests
import schedule
import googlemaps
import tweepy
import uber
import comfort
import distance
import config as cfg

from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, ForceReply

consumer_key = cfg.twitter['consumer']
consumer_secret = cfg.twitter['consumerSecret']
access_token = cfg.twitter['token']
access_token_secret = cfg.twitter['tokenSecret']

gmaps_key = cfg.google['places_key']
gmaps = googlemaps.Client(key=gmaps_key)

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

previous_timestamp = 0
chat_assigned = 0
train_lines = [ 'NSL', 'EWL', 'BPLRT', 'NSEWL', 'NSEWL', 'CCL', 'NEL', 'DTL' ]
chat_context = 'none'

autocomplete_data = []
pickup_location = ''
pickup_placeid = ''
pickup_lat = 0
pickup_lng = 0
dropoff_location = ''
dropoff_placeid = ''
dropoff_lat = 0
dropoff_lng = 0

bot = telepot.Bot(cfg.telegram['bot_id'])

# This function runs indefinitely
def twitter_pull():
    api = tweepy.API(auth)

    global previous_timestamp
    # user = "joshenlimek"
    user = "joshenlimek"
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
        # Start command required to retrieve chat_id of the current chat that bot is in
        if '/start' in user_message:
            print("Initialize Twitter Pull Cron")
            welcome_message = "Hey there! Phew, finally woken up. I'll be giving updates if any of the train services are down so stay tuned!"
            bot.sendMessage(chat_assigned, welcome_message)
            schedule.every(5).seconds.do(twitter_pull)

        # Sample API call syntax
        elif '/retrieveip' in user_message:
            bot.sendMessage(chat_id, 'Retrieving IP...')
            url = 'https://api.ipify.org?format=json'
            ipAdd = requests.get(url).text
            print(ipAdd)
            bot.sendMessage(chat_id, 'Your IP is: ' + ipAdd)

        # Start taxi price check program
        elif '/taxi' in user_message:
            bot.sendMessage(chat_id, 'Gotcha! Where would you like to be picked up from?')
            global chat_context
            chat_context = 'location_pickup'

        # Cancel taxi price check program
        elif '/cancel' in user_message:
            bot.sendMessage(chat_id, 'Gotcha, cancelled the current action')
            chat_context = 'none'

        elif chat_context == 'location_pickup' :
            init_loc_data = []
            chat_context = 'location_dropoff'
            reply_message = 'Sweet! I found these locations! Which would you like your pick up point to be?'
            global autocomplete_data
            autocomplete_data = gmaps.places_autocomplete(
                input_text = msg['text'],
                offset = 3,
                language = 'en',
                components = { 'country': 'sg' }
            )

            for place in autocomplete_data:
                id = autocomplete_data.index(place)
                callback_id = 'location_pickup_' + str(id)
                init_loc_data.append([InlineKeyboardButton(text=place['description'], callback_data=callback_id)])

            loc_keyboard = InlineKeyboardMarkup(inline_keyboard=init_loc_data)
            bot.sendMessage(chat_id, reply_message, reply_markup=loc_keyboard)

        elif chat_context == 'location_dropoff':
            init_loc_data = []
            reply_message = 'Gotcha! I found these locations! Which would you like your drop off point to be?'
            autocomplete_data = gmaps.places_autocomplete(
                input_text = msg['text'],
                offset = 3,
                language = 'en',
                components = { 'country': 'sg' }
            )

            for place in autocomplete_data:
                id = autocomplete_data.index(place)
                callback_id = 'location_dropoff_' + str(id)
                init_loc_data.append([InlineKeyboardButton(text=place['description'], callback_data=callback_id)])

            loc_keyboard = InlineKeyboardMarkup(inline_keyboard=init_loc_data)
            bot.sendMessage(chat_id, reply_message, reply_markup=loc_keyboard)

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
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')

    if 'location_pickup' in query_data:
        selected_query_id = int(query_data[-1])
        selected_pickup_location = autocomplete_data[selected_query_id]
        selected_place_id = selected_pickup_location['place_id']

        place_result = gmaps.place(selected_place_id, 'en')

        global pickup_lat
        global pickup_lng
        global pickup_location
        global pickup_placeid
        pickup_lat = place_result['result']['geometry']['location']['lat']
        pickup_lng = place_result['result']['geometry']['location']['lng']
        pickup_location = place_result['result']['name']
        pickup_placeid = place_result['result']['place_id']

        notif_msg = 'Pick up location set at ' + place_result['result']['name']
        bot.answerCallbackQuery(query_id, text=notif_msg)
        bot.sendMessage(chat_assigned, 'Now where would you like to be dropped off at?')

    elif 'location_dropoff' in query_data:
        selected_query_id = int(query_data[-1])
        selected_pickup_location = autocomplete_data[selected_query_id]
        selected_place_id = selected_pickup_location['place_id']

        place_result = gmaps.place(selected_place_id, 'en')

        global dropoff_lat
        global dropoff_lng
        global dropoff_location
        global dropoff_placeid
        dropoff_lat = place_result['result']['geometry']['location']['lat']
        dropoff_lng = place_result['result']['geometry']['location']['lng']
        dropoff_location = place_result['result']['name']
        dropoff_placeid = place_result['result']['place_id']

        notif_msg = 'Drop off location set at ' + place_result['result']['name']
        bot.answerCallbackQuery(query_id, text=notif_msg)
        bot.sendMessage(chat_assigned, 'Gotcha! Retrieving prices...')

        distance_estimate = distance.estimate(pickup_placeid, dropoff_placeid)

        # Calculate Grab Fare estimate
        # Calculate CityCab Fare estimate

        comfort_estimate = "Comfort: SGD " + comfort.estimate(distance_estimate)

        uber_estimate = "Uber: " + uber.get_price_estimate(
            start_lat=pickup_lat,
            start_lng=pickup_lng,
            end_lat=dropoff_lat,
            end_lng=dropoff_lng
        )

        price_collation = InlineKeyboardMarkup(inline_keyboard=[
            [dict(text=uber_estimate, url='http://www.google.com/')],
            [dict(text=comfort_estimate, url='http://www.google.com/')]
        ])

        price_estimate_msg = "Here are the estimated prices to travel from " + pickup_location + " to " + dropoff_location + " from the various taxi companies!"

        bot.sendMessage(chat_assigned, price_estimate_msg, reply_markup=price_collation)


print('Listening...')

# Listen to user actions on Telegram
MessageLoop(bot, {
    'chat': on_chat_message,
    'callback_query': on_callback_query,
}).run_as_thread()

# Keep the program running
while 1:
    schedule.run_pending()
    time.sleep(1)
