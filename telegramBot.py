import sys
import time
import telepot
import datetime
import requests
import googlemaps
import uber
import grab
import comfort
import distance
import config as cfg

from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, ForceReply

gmaps_key = cfg.google['places_key']
gmaps = googlemaps.Client(key=gmaps_key)

chat_assigned = 0
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

def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    global chat_assigned
    chat_assigned = chat_id
    user_message = msg['text']

    if content_type == 'text':
        if '/start' in user_message:
            welcome_message = "Ola! Dora at your service! :) With me around you can easily compare prices across taxi companies - no more spending time opening all those applications before coming to a decision!"
            help_message = 'Here\'s a list of my commands!\n/taxi - Compare prices across taxi companies by inputting your pick up and drop off location\n/cancel - Cancel the current action\n/help - Show a list of available commands'
            bot.sendMessage(chat_id, welcome_message)
            bot.sendMessage(chat_id, help_message)

        elif '/help' in user_message:
            help_message = 'Here\'s a list of my commands!\n/taxi - Compare prices across taxi companies by inputting your pick up and drop off location\n/cancel - Cancel the current action\n/help - Show a list of available commands'
            bot.sendMessage(chat_id, help_message)

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
            error_message = 'Ah sorry, but I couldn\'t find any search results for your location. Perhaps try a different one?'
            reply_message = 'Sweet! I found these locations! Which would you like your <b>pick up</b> point to be?'
            global autocomplete_data
            autocomplete_data = gmaps.places_autocomplete(
                input_text = user_message,
                offset = 3,
                language = 'en',
                components = { 'country': 'sg' }
            )

            for place in autocomplete_data:
                id = autocomplete_data.index(place)
                callback_id = 'location_pickup_' + str(id)
                init_loc_data.append([InlineKeyboardButton(text=place['description'], callback_data=callback_id)])

            loc_keyboard = InlineKeyboardMarkup(inline_keyboard=init_loc_data)

            if len(autocomplete_data) == 0:
                bot.sendMessage(chat_id, error_message)
            else:
                bot.sendMessage(chat_id, reply_message, parse_mode='HTML', reply_markup=loc_keyboard)

        elif chat_context == 'location_dropoff':
            init_loc_data = []
            error_message = 'Ah sorry! I couldn\'t find any results that match with that location! Perhaps try a different one?'
            reply_message = 'Gotcha! I found these locations! Which would you like your <b>drop off</b> point to be?'
            autocomplete_data = gmaps.places_autocomplete(
                input_text = user_message,
                offset = 3,
                language = 'en',
                components = { 'country': 'sg' }
            )

            for place in autocomplete_data:
                id = autocomplete_data.index(place)
                callback_id = 'location_dropoff_' + str(id)
                init_loc_data.append([InlineKeyboardButton(text=place['description'], callback_data=callback_id)])

            loc_keyboard = InlineKeyboardMarkup(inline_keyboard=init_loc_data)

            if len(autocomplete_data) == 0:
                bot.sendMessage(chat_id, error_message)
            else:
                bot.sendMessage(chat_id, reply_message, parse_mode='HTML', reply_markup=loc_keyboard)

        else :
            reply_msg = 'I\'m sorry but I don\'t quite understand what you\'re saying. Perhaps try \'/help\' if you\'re looking for commands!'
            bot.sendMessage(chat_id, reply_msg)

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
        global chat_context
        pickup_lat = place_result['result']['geometry']['location']['lat']
        pickup_lng = place_result['result']['geometry']['location']['lng']
        pickup_location = place_result['result']['name']
        pickup_placeid = place_result['result']['place_id']

        notif_msg = 'Pick up location set at ' + place_result['result']['name']
        bot.answerCallbackQuery(query_id, text=notif_msg)
        chat_context = 'location_dropoff'
        bot.sendMessage(chat_assigned, 'Now where would you like to be dropped off at?')

    elif 'location_dropoff' in query_data:
        selected_query_id = int(query_data[-1])
        selected_pickup_location = autocomplete_data[selected_query_id]
        selected_place_id = selected_pickup_location['place_id']

        place_result = gmaps.place(selected_place_id, 'en')

        print(place_result)

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

        distance_estimate = distance.estimate(pickup_placeid, dropoff_placeid)

        if (distance_estimate != 0):
            bot.sendMessage(chat_assigned, 'Gotcha! Retrieving prices...')

            grab_estimate = "Grab: SGD " + grab.estimate(distance_estimate)

            comfort_estimate = "ComfortDelGro: SGD " + comfort.estimate(
                start_lat=pickup_lat,
                start_lng=pickup_lng,
                end_lat=dropoff_lat,
                end_lng=dropoff_lng
            )

            uber_estimate = "Uber: " + uber.get_price_estimate(
                start_lat=pickup_lat,
                start_lng=pickup_lng,
                end_lat=dropoff_lat,
                end_lng=dropoff_lng
            )

            price_collation = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=uber_estimate, callback_data='no')],
                [InlineKeyboardButton(text=grab_estimate, callback_data='no')],
                [InlineKeyboardButton(text=comfort_estimate, callback_data='no')],
            ])

            price_estimate_msg = "Here are the estimated prices to travel from " + pickup_location + " to " + dropoff_location + " from the various taxi companies!"
            finish_msg = "Feel free to type \'/taxi\' again to retrieve more fare comparisons! :)"

            bot.sendMessage(chat_assigned, price_estimate_msg, reply_markup=price_collation)
            bot.sendMessage(chat_assigned, finish_msg)
        else:
            error_msg = "I'm sorry but you've inserted an invalid pick up and drop off point! Please type '/taxi' to try again with a different set of locations"
            bot.sendMessage(chat_assigned, error_msg)


print('Listening...')

# Listen to user actions on Telegram
MessageLoop(bot, {
    'chat': on_chat_message,
    'callback_query': on_callback_query,
}).run_as_thread()

# Keep the program running
while 1:
    time.sleep(1)
