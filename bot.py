"""
Vk.com to Telegram messages retranslator demo

"""

import config
import time
import eventlet
import requests
import logging
import telebot
from time import sleep

queryURL = "https://api.vk.com/method/messages.get?access_token=" + config.vToken+"&v=5.1&out=1"
FILENAME_VK = 'last_known_id.txt'

bot = telebot.TeleBot(config.teleToken)


def get_data():
    timeout = eventlet.Timeout(10)
    try:
        msgs = requests.get(queryURL)
        return msgs.json()
    except eventlet.timeout.Timeout:
        logging.warning('Got Timeout while retrieving VK JSON data. Cancelling...')
        return None
    finally:
        timeout.cancel()


def get_last_msg_id():
    with open(FILENAME_VK, 'rt') as file:
        last_id = int(file.read())
        if last_id is None:
            logging.error('Could not read from storage. Skipped iteration.')
            return
        logging.info('Last ID (VK) = {!s}'.format(last_id))
    return last_id


def send_new_msg(items, last_id):
    for item in items:
        new_last_msg_id = int(item['id'])
        #if new_last_msg_id <= last_id:
            #break
        if 'chat_id' not in item:
            continue
        if item['chat_id'] != config.vkChatID:
            continue
        print(item)
        sending_msg = "from: " + str(item['user_id'])+'\n'
        sending_msg += "text: " + item['body']
        bot.send_message(chat_id=config.teleChatID, text=sending_msg)
        # wait second, for avoid block (flood)
        time.sleep(1)
    return new_last_msg_id


last_msg_id = get_last_msg_id()
msgs = get_data()
entries = msgs['response']['items']

last_msg_id = send_new_msg(entries, last_msg_id)


