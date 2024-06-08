import logging
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from dotenv import load_dotenv
import os
import re

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Bitly API token
BITLY_API_TOKEN = os.getenv('BITLY_API_TOKEN')
TELEGRAM_API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')

# Function to shorten URL using Bitly API
def shorten_url(long_url):
    headers = {
        'Authorization': f'Bearer {BITLY_API_TOKEN}',
        'Content-Type': 'application/json',
    }
    data = {
        'long_url': long_url,
    }
    try:
        response = requests.post('https://api-ssl.bitly.com/v4/shorten', json=data, headers=headers)
        response.raise_for_status()
        return response.json().get('link')
    except requests.exceptions.HTTPError as http_err:
        logger.error(f'HTTP error occurred: {http_err}')
        return None
    except Exception as err:
        logger.error(f'Other error occurred: {err}')
        return None

# URL validation function
def is_valid_url(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None

# Command handler for /start
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hi! Send me a URL and I will shorten it for you.')

# Message handler to process incoming URLs
def handle_message(update: Update, context: CallbackContext) -> None:
    long_url = update.message.text
    if is_valid_url(long_url):
        short_url = shorten_url(long_url)
        if short_url:
            update.message.reply_text(f'Shortened URL: {short_url}')
        else:
            update.message.reply_text('Failed to shorten the URL. Please try again.')
    else:
        update.message.reply_text('Invalid URL. Please provide a valid URL.')

def main():
    # Set up the Updater
    updater = Updater(TELEGRAM_API_TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Register command and message handlers
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT
    updater.idle()

if __name__ == '__main__':
    main()
