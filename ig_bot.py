import signal
from time import sleep
from decouple import config

import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

import instagrapi
from instagrapi import Client

chat_id = config('CHAT_ID')

TOKEN = config('TOKEN')
bot = telebot.TeleBot(TOKEN)

client = Client()

EMOJI = {
    'username': '👤',
    'name': '🗣️',
    'bio': '📜',
    'post': '🖼️',
    'follower': '👥',
    'following': '🫂',
    'private': '🔒',
    'public': '🔓',
    'verified': '✅',
    'notverified': '❎',
    'url': '🌐',
    'video': '🎞️',
    'photo': '🖼️',
    'album': '🖼️🎞️',
    'notsupport': '❌',
    'download': '📥',
    'upload': '📤',
    'back': '🔙',
}


def exit_handler(signum, frame):
    res = input("\n Ctrl-c was pressed. Do you really want to exit? y/n ")
    if res == 'y':
        client.logout()
        exit(1)


signal.signal(signal.SIGINT, exit_handler)

is_authenticated = False
while not is_authenticated:
    sleep(5)
    is_authenticated = client.login(config('IG_USERNAME'),  config('IG_PASSWORD'))


bot.send_message(chat_id, f"Hello {config('IG_USERNAME')}")


def user_info_markup(pk):
    username = client.user_info(pk).username
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(InlineKeyboardButton('Story', callback_data='cb_story'),
               InlineKeyboardButton('Post', callback_data='cb_post'),
               InlineKeyboardButton('Open in Instagram', url=f'https://www.instagram.com/{username}'))
    return markup


def user_story_markup(stories):
    markup = InlineKeyboardMarkup()

    count = len(stories)
    c = 0

    for i in range(count//5):
        row = []
        for j in range(5):
            media_type = ''
            if stories[c].media_type == 1:
                media_type = EMOJI['photo']
            elif stories[c].media_type == 2:
                media_type = EMOJI['video']
            else:
                media_type = EMOJI['notsupport']

            row.append(InlineKeyboardButton(f'{c+1} {media_type}', callback_data=f'cb_story_dl_{c}'))
            c += 1

        markup.add(*row, row_width=5)

    if count % 5 != 0:
        last_row = []
        for i in range(count % 5):
            media_type = ''
            if stories[c].media_type == 1:
                media_type = EMOJI['photo']
            elif stories[c].media_type == 2:
                media_type = EMOJI['video']
            else:
                media_type = EMOJI['notsupport']

            last_row.append(InlineKeyboardButton(f'{c+1} {media_type}', callback_data=f'cb_story_dl_{c}'))
            c += 1
        markup.add(*last_row, row_width=count % 5)

    markup.add(InlineKeyboardButton(f"Get all {EMOJI['download']}", callback_data='cb_story_all'))
    markup.add(InlineKeyboardButton(f"Back {EMOJI['back']}", callback_data='cb_back'))

    return markup


def user_post_markup(posts):
    markup = InlineKeyboardMarkup()

    count = len(posts)
    c = 0

    for i in range(count//5):
        row = []
        for j in range(5):
            media_type = ''
            if posts[c].media_type == 1:
                media_type = EMOJI['photo']
            elif posts[c].media_type == 2:
                media_type = EMOJI['video']
            elif posts[c].media_type == 8:
                media_type = EMOJI['album']
            else:
                media_type = EMOJI['notsupport']

            row.append(InlineKeyboardButton(f'{c+1} {media_type}', callback_data=f'cb_post_dl_{c}'))
            c += 1

        markup.add(*row, row_width=5)

    if count % 5 != 0:
        last_row = []
        for i in range(count % 5):
            media_type = ''
            if posts[c].media_type == 1:
                media_type = EMOJI['photo']
            elif posts[c].media_type == 2:
                media_type = EMOJI['video']
            elif posts[c].media_type == 8:
                media_type = EMOJI['album']
            else:
                media_type = EMOJI['notsupport']

            last_row.append(InlineKeyboardButton(f'{c+1} {media_type}', callback_data=f'cb_post_dl_{c}'))
            c += 1
        markup.add(*last_row, row_width=count % 5)

    markup.add(InlineKeyboardButton(f"Get all {EMOJI['download']}", callback_data='cb_post_all'))
    markup.add(InlineKeyboardButton(f"Back {EMOJI['back']}", callback_data='cb_back'))

    return markup


def user_post_markup2(posts):
    markup = InlineKeyboardMarkup()

    c = 0

    for i in range(3):
        row = []
        for j in range(3):
            media_type = ''
            if posts[c].media_type == 1:
                media_type = EMOJI['photo']
            elif posts[c].media_type == 2:
                media_type = EMOJI['video']
            elif posts[c].media_type == 8:
                media_type = EMOJI['album']
            else:
                media_type = EMOJI['notsupport']

            row.append(InlineKeyboardButton(f'{c+1} {media_type}', callback_data=f'cb_post_dl_{c}'))
            c += 1

        markup.add(*row, row_width=3)

    markup.add(InlineKeyboardButton(f"Get all {EMOJI['download']}", callback_data='cb_post_all'))
    markup.add(InlineKeyboardButton(f"Back {EMOJI['back']}", callback_data='cb_back'))

    return markup


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):

    caption = call.message.caption
    user_id = caption[caption.find('#u')+2:]

    if call.data == 'cb_back':
        bot.answer_callback_query(call.id, 'Back to user info!')
        bot.edit_message_reply_markup(chat_id=call.from_user.id, message_id=call.message.id, reply_markup=user_info_markup(user_id))

    elif call.data == 'cb_story':
        stories = client.user_stories(user_id)

        if len(stories) == 0:
            bot.answer_callback_query(call.id, 'User has no story!')
        else:
            bot.answer_callback_query(call.id, 'Select Story')
            bot.edit_message_reply_markup(chat_id=call.from_user.id, message_id=call.message.id, reply_markup=user_story_markup(stories))

    elif call.data.startswith('cb_story_dl_'):
        number = int(call.data.replace('cb_story_dl_', ''))

        bot.answer_callback_query(call.id, f'Get Story {number+1}!')

        stories = client.user_stories(user_id)

        story = stories[number]
        if story.media_type == 1:
            bot.send_photo(call.from_user.id, story.thumbnail_url, caption=f'Story Number: {number+1}\n#u{user_id}')
        elif story.media_type == 2:
            bot.send_video(call.from_user.id, story.video_url, caption=f'Story Number: {number+1}\n#u{user_id}')
        else:
            bot.send_message(call.from_user.id, 'FORMAT NOT FOUND!')

    elif call.data == 'cb_story_all':
        bot.answer_callback_query(call.id, 'Get all Stories!')

        stories = client.user_stories(user_id)

        for number, story in enumerate(stories):
            if story.media_type == 1:
                bot.send_photo(call.from_user.id, story.thumbnail_url, caption=f'Story Number: {number+1}\n#u{user_id}')
            elif story.media_type == 2:
                bot.send_video(call.from_user.id, story.video_url, caption=f'Story Number: {number+1}\n#u{user_id}')
            else:
                bot.send_message(call.from_user.id, 'FORMAT NOT FOUND!')

    elif call.data == 'cb_post':
        posts = client.user_medias(user_id, 9)

        if len(posts) == 0:
            bot.answer_callback_query(call.id, 'User has no post!')
        else:
            bot.answer_callback_query(call.id, 'Select Post')
            bot.edit_message_reply_markup(chat_id=call.from_user.id, message_id=call.message.id, reply_markup=user_post_markup(posts))

    elif call.data.startswith('cb_post_dl_'):
        number = int(call.data.replace('cb_post_dl_', ''))

        bot.answer_callback_query(call.id, f'Get Post {number+1}!')

        posts = client.user_medias(user_id, number+1)

        post = posts[number]
        if post.media_type == 1:
            bot.send_photo(call.from_user.id, post.thumbnail_url, caption=f'Post Number: {number+1}\n#u{user_id}')
        elif post.media_type == 2:
            bot.send_video(call.from_user.id, post.video_url, caption=f'Post Number: {number+1}\n#u{user_id}')
        elif post.media_type == 8:
            for slide_num, post.resource in enumerate(post.resources):
                if resource.media_type == 1:
                    bot.send_photo(call.from_user.id, resource.thumbnail_url, caption=f'Post Number: {number+1}\nSlide: {slide_num+1}\n#u{user_id}')
                elif resource.media_type == 2:
                    bot.send_video(call.from_user.id, resource.video_url, caption=f'Post Number: {number+1}\nSlide: {slide_num+1}\n#u{user_id}')

        else:
            bot.send_message(call.from_user.id, 'FORMAT NOT FOUND!')


@bot.inline_handler(lambda query: len(query.query) != 0)
def inline_query(query):
    try:
        try:
            user_info = client.user_info_by_username(query.query)
            r = types.InlineQueryResultPhoto('1', user_info.profile_pic_url, user_info.profile_pic_url, title=f'{user_info.username}', description=f'{user_info.full_name}',
                                             caption=f'''
                                             {EMOJI['username']} Username: {user_info.username}
                                             {EMOJI['name']} FullName: {user_info.full_name}
                                             {EMOJI['private'] if user_info.is_private else EMOJI['public']}Privacy: {'Private' if user_info.is_private else 'Public'}
                                             {EMOJI['verified'] if user_info.is_verified else EMOJI['notverified']} Verify: {'Verified' if user_info.is_verified else 'Not Verified'}
                                             {EMOJI['bio']} Biography: {user_info.biography}
                                             {EMOJI['post']} Posts: {user_info.media_count}
                                             {EMOJI['follower']} Followers: {user_info.follower_count:,}
                                             {EMOJI['following']} Followings: {user_info.following_count:,}
                                             {EMOJI['url']} URL: {user_info.external_url if user_info.external_url else ''}
                                             #u{user_info.pk}
                                             '''.replace('                                             ', '\n'))

        except instagrapi.exceptions.UserNotFound as e:
            r = types.InlineQueryResultArticle('1', f'Not Found', input_message_content=types.InputTextMessageContent(query.query))

        bot.answer_inline_query(query.id, [r])

    except Exception as e:
        print(e)


@ bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(message.chat.id, 'Hello World')


# @ bot.message_handler(commands=['login'])
# def bot_login(message):
#     is_logged_in = client.login(config('IG_USERNAME'),  config('IG_PASSWORD'))
#     bot.send_message(message.chat.id, f"{'Logged in' if is_logged_in else 'Can not log in'}")


# @ bot.message_handler(commands=['logout'])
# def bot_login(message):
#     is_logged_out = client.logout()
#     bot.send_message(message.chat.id, f"{'Logged out' if is_logged_out else 'Can not log out'}")


@ bot.message_handler(func=lambda message: True)
def answer_message(message):

    try:
        if message.text.startswith('eval '):
            bot.reply_to(message, f'{eval(message.text[5:])}')
        else:
            user_info = client.user_info_by_username(message.text)
            bot.send_photo(message.chat.id, user_info.profile_pic_url,
                           f'''
                        {EMOJI['username']} Username: {user_info.username}
                        {EMOJI['name']} FullName: {user_info.full_name}
                        {EMOJI['private'] if user_info.is_private else EMOJI['public']}Privacy: {'Private' if user_info.is_private else 'Public'}
                        {EMOJI['verified'] if user_info.is_verified else EMOJI['notverified']} Verify: {'Verified' if user_info.is_verified else 'Not Verified'}
                        {EMOJI['bio']} Biography: {user_info.biography}
                        {EMOJI['post']} Posts: {user_info.media_count}
                        {EMOJI['follower']} Followers: {user_info.follower_count:,}
                        {EMOJI['following']} Followings: {user_info.following_count:,}
                        {EMOJI['url']} URL: {user_info.external_url if user_info.external_url else ''}
                        #u{user_info.pk}
                        '''.replace('                       ', '\n'), reply_markup=user_info_markup(user_info.pk))
    except instagrapi.exceptions.UserNotFound as e:
        bot.reply_to(message, 'User not found :(')


bot.infinity_polling(skip_pending=True)
