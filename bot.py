
import logging
import requests
import os
from reddit import Reddit, Subreddit
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def post(update: Update, _: CallbackContext) -> None:
    buttons = [InlineKeyboardButton(text=sub, callback_data=sub)
               for sub in reddit.config['subreddits']]

    keyboard = []
    n = 0
    
    # Seperates buttons in rows of 2 
    for _ in buttons:
        if n + 1 < len(buttons):
            keyboard.append([buttons[n], buttons[n + 1]])
            n += 2

    update.message.reply_text('select a subreddit',
                              reply_markup=InlineKeyboardMarkup(keyboard))


def add(update: Update, _: CallbackContext) -> None:
    subreddit = Subreddit(update.message.text.split('/add ')[1])

    message = f'{subreddit.name} was added' if reddit.add_subreddit(
        subreddit) else f'{subreddit.name} wasn\'t added for some reason'
    update.message.reply_text(message)


def remove(update: Update, _: CallbackContext) -> None:
    subreddit = Subreddit(update.message.text.split('/remove ')[1])

    message = f'{subreddit.name} was removed' if reddit.remove_subreddit(
        subreddit) else f'{subreddit.name} wasn\'t removed for some reason'
    update.message.reply_text(message)


def button(update: Update, _: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    post = reddit.get_post(
        Subreddit(query.data)
    )

    if post.is_photo:
        query.bot.send_photo(chat_id=query.message.chat_id,
                             photo=post.image_url, caption=post.title)
        query.delete_message()
    else:
        query.edit_message_text(
            text=f'<b>{post.title}</b>\n\n{post.text}', parse_mode=ParseMode.HTML)

def main() -> None:
    updater = Updater(TOKEN)

    updater.dispatcher.add_handler(CommandHandler('post', post))
    updater.dispatcher.add_handler(CommandHandler('add', add))
    updater.dispatcher.add_handler(CommandHandler('remove', remove))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    TOKEN = ''
    reddit = Reddit()
    main()
