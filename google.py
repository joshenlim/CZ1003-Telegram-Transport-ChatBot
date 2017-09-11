import sys
import time
import telepot
import googlemaps
import config as cfg
from telepot.loop import MessageLoop
from datetime import datetime
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, ForceReply

api_key = cfg.google['places_key']
gmaps = googlemaps.Client(key=api_key)

chat_context = 'none'

def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                   [InlineKeyboardButton(text='Press me', callback_data='press')],
               ])

    if content_type == 'text':
        if '/taxi' in msg['text']:
            bot.sendMessage(chat_id, 'Please input your pick up location')
            # bot.sendMessage(chat_id, 'Please input your pick up location', reply_markup=keyboard)
            global chat_context
            chat_context = 'location_pickup'

        elif '/cancel' in msg['text']:
            bot.sendMessage(chat_id, 'Gotcha, cancelled the current action')
            chat_context = 'none'

        elif chat_context == 'location_pickup' :
            place_autocomplete = gmaps.places_autocomplete(
                input_text = msg['text'],
                offset = 3,
                language = 'en',
                components = {
                    'country': 'sg'
                }
            )
            # print(place_autocomplete)
            bot.sendMessage(chat_id, 'Your search returned ' + str(len(place_autocomplete)) + ' results')

            init_loc_data = []

            for place in place_autocomplete:
                init_loc_data.append([InlineKeyboardButton(text=place['description'], callback_data='press')])

            loc_keyboard = InlineKeyboardMarkup(inline_keyboard=init_loc_data)
            bot.sendMessage(chat_id, 'Select location', reply_markup=loc_keyboard)


            # bot.sendMessage(chat_id, 'Please input your drop off location')
            # global chat_context
            chat_context = 'location_dropoff'

        elif chat_context == 'location_dropoff' :
            bot.sendMessage(chat_id, 'Your drop off location is ' + msg['text'])
            bot.sendMessage(chat_id, 'Thank you!')
            chat_context = 'none'

        else :
            bot.sendMessage(chat_id, 'Hey there ' + msg['from']['username'] + '!')
            bot.sendMessage(chat_id, 'You sent me this message: ' + msg['text'])

def on_callback_query(msg):
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    print('Callback Query:', query_id, from_id, query_data)

    bot.answerCallbackQuery(query_id, text='Got it')


bot = telepot.Bot('445426933:AAEFuo2S03hYfphhXWWCGNJemEkRZScF-Ho')

MessageLoop(bot, {
    'chat': on_chat_message,
    'callback_query': on_callback_query
}).run_as_thread()

print('Listening...')

# Keep the program running
while 1:
    time.sleep(10)
