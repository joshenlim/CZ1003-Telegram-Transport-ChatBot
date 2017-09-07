import sys
import time
import telepot
import datetime
import requests

from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, ForceReply

# Sample API call to retrieve IP Address using requests lib

# Think in the context of having the bot in a group when building this
# Always need to ____@botName to activate the bot

def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    # print(content_type, chat_type, chat_id)
    command = msg['text']
    print ('Got command: %s' % command)

    if content_type == 'text':
        # Sample API call syntax
        if '/retrieveip' in command:
            bot.sendMessage(chat_id, 'Retrieving IP...')
            url = 'https://api.ipify.org?format=json'
            ipAdd = requests.get(url).text
            print(ipAdd)
            bot.sendMessage(chat_id, 'Your IP is: ' + ipAdd)

        # Show Custom Buttons on the phone's keyboard area
        # Use case, buttons that's always used for the bot, to help UX
        elif '/inline' in command:
            markup = ReplyKeyboardMarkup(keyboard=[
                     ['Plain text', KeyboardButton(text='Text only')],
                     [dict(text='Phone', request_contact=True), KeyboardButton(text='Location', request_location=True)],
                 ])
            bot.sendMessage(chat_id, 'Custom keyboard with various buttons', reply_markup=markup)

        # Hide the Custom Buttons on the phone's keyboard area
        elif '/hide' in command:
            markup = ReplyKeyboardRemove()
            bot.sendMessage(chat_id, 'Hide custom keyboard', reply_markup=markup)

        # Show Custom Buttons in Chat Area
        # Give options to user
        elif '/help' in command:
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

bot = telepot.Bot('445426933:AAEFuo2S03hYfphhXWWCGNJemEkRZScF-Ho')
answerer = telepot.helper.Answerer(bot)

# MessageLoop(bot, handle).run_as_thread()

MessageLoop(bot, {
    'chat': on_chat_message,
    'callback_query': on_callback_query
}).run_as_thread()

print('Listening...')

# Keep the program running
while 1:
    time.sleep(10)
