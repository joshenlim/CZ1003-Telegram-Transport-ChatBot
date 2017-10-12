# Python Libraries
import time
import telepot
import requests
import googlemaps
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

# User created files
import uber
import grab
import comfort
import distance
import config as cfg

gmaps_key = cfg.google['places_key']
gmaps = googlemaps.Client(key=gmaps_key)

database_url = (f'https://api.airtable.com/v0/appK4VpMGwbvfp5q0/chatData')
database_key = cfg.airtable['api_key']
database_params = { "api_key": database_key }

bot = telepot.Bot(cfg.telegram['bot_id'])

def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    user_message = msg['text']

    user_data = {}

    data = requests.get(database_url, params=database_params).json()['records']
    search_user = list(filter(lambda x: x['fields']['chatId'] == str(chat_id), data))

    if (len(search_user) == 0):
        # print('User cannot be found, creating user...')
        payload = {
        	"fields": {
            	"chatId": str(chat_id),
                "chat_context": 'none',
                "pickup_location": '',
                "pickup_placeid": '',
                "pickup_lat": 0,
                "pickup_lng": 0,
                "dropoff_location": '',
                "dropoff_placeid": '',
                "dropoff_lat": 0,
                "dropoff_lng": 0,
                "autocomplete_data": '',
        	}
        }
        create_user = requests.post(database_url, json=payload, params=database_params)
        # print(create_user.text)
        user_data = create_user.json()
    else:
        # print('User found')
        user_data = search_user[0]

    user_id =  user_data['id']
    user_saved_information =  user_data['fields']

    print(user_id)
    print(user_saved_information)
    # print("User message: ", user_message)

    if content_type == 'text':
        if '/start' in user_message:
            welcome_message = "Ola! Dora at your service! :) With me around you can easily compare prices across taxi companies - no more spending time opening all those applications before coming to a decision!"
            help_message = 'Here\'s a list of my commands!\n/taxi - Compare prices across taxi companies by inputting your pick up and drop off location\n/cancel - Cancel the current action\n/help - Show a list of available commands'
            bot.sendMessage(chat_id, welcome_message)
            bot.sendMessage(chat_id, help_message)

        # Display available commands
        elif '/help' in user_message:
            help_message = 'Here\'s a list of my commands!\n/taxi - Compare prices across taxi companies by inputting your pick up and drop off location\n/cancel - Cancel the current action\n/help - Show a list of available commands'
            bot.sendMessage(chat_id, help_message)

        # Start taxi price check program
        elif '/taxi' in user_message:
            bot.sendMessage(chat_id, 'Gotcha! Where would you like to be picked up from?')
            payload = {
            	"fields": {
                	"chat_context": "location_pickup"
            	}
            }
            update_user = requests.patch(database_url + '/' + user_id, json=payload, params=database_params)

        # Cancel taxi price check program at any point
        elif '/cancel' in user_message:
            bot.sendMessage(chat_id, 'Gotcha, cancelled the current action')
            payload = {
            	"fields": {
                	"chat_context": "none"
            	}
            }
            update_user = requests.patch(database_url + '/' + user_id, json=payload, params=database_params)

        elif user_saved_information['chat_context'] == 'location_pickup':
            init_loc_data = []
            error_message = 'Ah sorry, but I couldn\'t find any search results for your location. Perhaps try a different one?'
            reply_message = 'Sweet! I found these locations! Which would you like your <b>pick up</b> point to be?'

            autocomplete_data = gmaps.places_autocomplete(
                input_text = user_message,
                offset = 3,
                language = 'en',
                components = { 'country': 'sg' }
            )

            payload = {
            	"fields": {
                	"autocomplete_data": str(autocomplete_data)
            	}
            }
            update_user = requests.patch(database_url + '/' + user_id, json=payload, params=database_params)
            user_saved_information = update_user.json()['fields']

            # print(autocomplete_data)

            for place in eval(user_saved_information['autocomplete_data']):
                # print(place)
                id = eval(user_saved_information['autocomplete_data']).index(place)
                # Generate unique id for each button to retrieve place data by index
                # from autocomplete_data list fter user selects a button
                callback_id = 'location_pickup_' + str(id)
                init_loc_data.append([InlineKeyboardButton(text=place['description'], callback_data=callback_id)])

            loc_keyboard = InlineKeyboardMarkup(inline_keyboard=init_loc_data)

            if len(autocomplete_data) == 0:
                bot.sendMessage(chat_id, error_message)
            else:
                bot.sendMessage(chat_id, reply_message, parse_mode='HTML', reply_markup=loc_keyboard)

        elif user_saved_information['chat_context'] == 'location_dropoff':
            init_loc_data = []
            error_message = 'Ah sorry! I couldn\'t find any results that match with that location! Perhaps try a different one?'
            reply_message = 'Gotcha! I found these locations! Which would you like your <b>drop off</b> point to be?'
            autocomplete_data = gmaps.places_autocomplete(
                input_text = user_message,
                offset = 3,
                language = 'en',
                components = { 'country': 'sg' }
            )

            # print(autocomplete_data)

            payload = {
            	"fields": {
                	"autocomplete_data": str(autocomplete_data)
            	}
            }
            update_user = requests.patch(database_url + '/' + user_id, json=payload, params=database_params)
            user_saved_information = update_user.json()['fields']

            for place in eval(user_saved_information['autocomplete_data']):
                # print(place)
                id = eval(user_saved_information['autocomplete_data']).index(place)
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

# Respond accordingly for callbacks for Inline Keyboard Markup
def on_callback_query(msg):
    query_id, chat_id, callback_data = telepot.glance(msg, flavor='callback_query')

    user_data = {}

    params = { "api_key": database_key }
    data = requests.get(database_url, params=database_params).json()['records']
    user_data = list(filter(lambda x: x['fields']['chatId'] == str(chat_id), data))[0]

    user_id =  user_data['id']
    user_saved_information =  user_data['fields']

    print(user_id)
    print(user_saved_information)

    if 'location_pickup' in callback_data:
        selected_query_id = int(callback_data[-1])
        selected_pickup_location = eval(user_saved_information['autocomplete_data'])[selected_query_id]
        selected_place_id = selected_pickup_location['place_id']

        place_result = gmaps.place(selected_place_id, 'en')
        # print(place_result)

        pickup_lat = place_result['result']['geometry']['location']['lat']
        pickup_lng = place_result['result']['geometry']['location']['lng']
        pickup_location = place_result['result']['name']
        pickup_placeid = place_result['result']['place_id']

        # print("Pick up latitude:", pickup_lat)
        # print("Pick up longitude:", pickup_lng)
        # print("Pick up location:", pickup_location)
        # print("Pick up Place ID:", pickup_placeid)

        notif_msg = 'Pick up location set at {}'.format(place_result['result']['name'])
        bot.answerCallbackQuery(query_id, text=notif_msg)

        payload = {
            "fields": {
                "pickup_location": pickup_location,
                "pickup_placeid": pickup_placeid,
                "pickup_lat": pickup_lat,
                "pickup_lng": pickup_lng,
                "chat_context": "location_dropoff"
            }
        }
        update_user = requests.patch(database_url + '/' + user_id, json=payload, params=database_params)

        bot.sendMessage(chat_id, 'Now where would you like to be dropped off at?')

    elif 'location_dropoff' in callback_data:
        selected_query_id = int(callback_data[-1])
        selected_pickup_location = eval(user_saved_information['autocomplete_data'])[selected_query_id]
        selected_place_id = selected_pickup_location['place_id']

        place_result = gmaps.place(selected_place_id, 'en')

        # print(place_result)

        dropoff_lat = place_result['result']['geometry']['location']['lat']
        dropoff_lng = place_result['result']['geometry']['location']['lng']
        dropoff_location = place_result['result']['name']
        dropoff_placeid = place_result['result']['place_id']

        payload = {
            "fields": {
                "dropoff_location": dropoff_location,
                "dropoff_placeid": dropoff_placeid,
                "dropoff_lat": dropoff_lat,
                "dropoff_lng": dropoff_lng,
                "chat_context": "none"
            }
        }
        update_user = requests.patch(database_url + '/' + user_id, json=payload, params=database_params)
        user_saved_information = update_user.json()['fields']

        # print("Drop off latitude:", dropoff_lat)
        # print("Drop off longitude:", dropoff_lng)
        # print("Drop off location:", dropoff_location)
        # print("Drop off Place ID:", dropoff_placeid)

        notif_msg = 'Drop off location set at {}'.format(place_result['result']['name'])
        bot.answerCallbackQuery(query_id, text=notif_msg)

        distance_matrix = distance.estimate(user_saved_information['pickup_placeid'], user_saved_information['dropoff_placeid'])
        # print("Distance Matrix:", distance_matrix)
        distance_estimate = distance_matrix['distance']['value'] if distance_matrix != 0 else 0
        duration_estimate = distance_matrix['duration']['value'] if distance_matrix != 0 else 0

        # print("Distance Matrix Estimate:", distance_matrix)

        if (distance_estimate != 0):
            bot.sendMessage(chat_id, 'Gotcha! Retrieving prices...')

            grab_estimate = "Grab: SGD " + grab.estimate(distance_estimate, duration_estimate)

            comfort_estimate = "ComfortDelGro: SGD " + comfort.estimate(
                start_lat=user_saved_information['pickup_lat'],
                start_lng=user_saved_information['pickup_lng'],
                end_lat=user_saved_information['dropoff_lat'],
                end_lng=user_saved_information['dropoff_lng']
            )

            uber_estimate = "Uber: " + uber.get_price_estimate(
                start_lat=user_saved_information['pickup_lat'],
                start_lng=user_saved_information['pickup_lng'],
                end_lat=user_saved_information['dropoff_lat'],
                end_lng=user_saved_information['dropoff_lng']
            )

            # print("Grab estimate:", grab_estimate)
            # print("Comfort estimate:", comfort_estimate)
            # print("Uber estimate:", uber_estimate)

            price_collation = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=uber_estimate, callback_data='no')],
                [InlineKeyboardButton(text=grab_estimate, callback_data='no')],
                [InlineKeyboardButton(text=comfort_estimate, callback_data='no')],
            ])

            price_estimate_msg = "Here are the estimated prices to travel from  {} to {} from the various taxi companies!".format(user_saved_information['pickup_location'], user_saved_information['dropoff_location'])
            finish_msg = "Feel free to type \'/taxi\' again to retrieve more fare comparisons! :)"

            bot.sendMessage(chat_id, price_estimate_msg, reply_markup=price_collation)
            bot.sendMessage(chat_id, finish_msg)
        else:
            error_msg = "I'm sorry but you've inserted an invalid pick up and drop off point! Please type '/taxi' to try again with a different set of locations"

            bot.sendMessage(chat_id, error_msg)


print('Listening...')

MessageLoop(bot, {
    'chat': on_chat_message,
    'callback_query': on_callback_query,
}).run_as_thread()

while 1:
    time.sleep(1)
