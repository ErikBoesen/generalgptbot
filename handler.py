import sys
sys.path.insert(0, 'vendor')

import os
import requests
import random
import json
import time

PREFIX = '+'
OPENAI_ENDPOINT = 'https://api.openai.com/v1/chat/completions'
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
MAX_MESSAGE_LENGTH = 1000

def receive(event, context):
    message = json.loads(event['body'])

    bot_id = message['bot_id']
    response = process_message(message)
    if response:
        send(response, bot_id)

    return {
        'statusCode': 200,
        'body': 'ok'
    }

def process_message(message):
    # Prevent self-reply
    if message['sender_type'] != 'bot':
        text = message['text']
        if text.startswith(PREFIX):
            return process_text(text.lstrip(PREFIX))

def get_pretraining_content():
    return 'Your purpose is to help people with creative writing tasks. Please respond in a positive and constructive manner giving detailed critique of the user\'s writing and advice for improvement.\n\nHere is the message:\n'

def process_text(text):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + OPENAI_API_KEY
    }

    data = {
        'model': 'gpt-3.5-turbo',
        'messages': [{'role': 'user', 'content': get_pretraining_content() + text}],
        'temperature': 0.5,
    }

    response = requests.post(OPENAI_ENDPOINT, headers=headers, json=data)

    if response.status_code == 200:
        print(response.json())
        return response.json()['choices'][0]['message']['content']
    return 'Error: ' + response.text.strip()


def send(text, bot_id):
    url = 'https://api.groupme.com/v3/bots/post'

    if len(text) > MAX_MESSAGE_LENGTH:
        # If text is too long for one message, split it up over several
        for block in [text[i:i + MAX_MESSAGE_LENGTH] for i in range(0, len(text), MAX_MESSAGE_LENGTH)]:
            send(block, bot_id)
            time.sleep(0.3)
        return

    message = {
        'bot_id': bot_id,
        'text': text,
    }
    r = requests.post(url, json=message)

#print(process_text('Can you tell me how to get into Yale?'))
