import webbrowser
import requests
import wikipediaapi
import bs4
import tweepy
from pyWikiCommons import pyWikiCommons
import os
import cairosvg
import random
import time
from PIL import Image
from io import BytesIO
import argparse

parser = argparse.ArgumentParser(prog="random wikipedia poster",
                                 description="posts random wikipedia articles")
parser.add_argument("--keydir", action='store_true', required=True)
args = parser.parse_args()

with open(args.keydir, 'r') as keys:
    api_key = keys.readline()
    api_secret = keys.readline()
    client_id = keys.readline()
    client_secret = keys.readline()
    access_token = keys.readline()
    access_secret = keys.readline()
    bearer_token = keys.readline()

bad_categories = ["All Wikipedia articles in need of updating",
                  "Articles with short description",
                  "All stub articles",
                  "People",
                  "Rights",
                  ]

# Authenticate to Twitter
authv1 = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_secret)
authv1.set_access_token(access_token, access_secret)
apiv1 = tweepy.API(authv1)
authv2 = tweepy.Client(bearer_token, api_key, api_secret, access_token, access_secret)
apiv2 = tweepy.API(authv2)

# test if page is suitable for posting
def check_page(random_page, data):
    thumb_ok = False
    if 'thumbnail' in data and 'source' in data['thumbnail']:
       thumb_ok = True 
    print(f"article is in {len(random_page.langlinks) + 1} languages.")
    categories = random_page.categories
    rotten_article = False
    for category in categories:
        if category in bad_categories:
            rotten_article = True
    if (len(random_page.langlinks) + 1) > 2 and rotten_article == False and thumb_ok == True:
        return True
    run()
    return False

# main program loop
def run():
    while True:

        message = ""
        post_chars_left = 271 # stay within twitter char limit

        random_link = requests.get("https://en.wikipedia.org/wiki/special:Random")

        random_title = bs4.BeautifulSoup(random_link.text, features="html.parser")
        api_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{random_title.title.text[:-12]}"
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
        else :
            print("could not fetch.")
            exit()

        print(f"attempting: {random_title.title.text[:-12]}")

        wiki_wiki = wikipediaapi.Wikipedia("wiki idk example (example@gmail.com)", 'en')
        random_wiki = wiki_wiki.page(random_title.title.text[:-12])

        #checks suitability of page

        if not check_page(random_wiki, data):
            break
        image_link = None
        random_url = (f"https://en.wikipedia.org/wiki/{random_title.title.text[:-12].replace(' ', '_')}")
        print("---------------------")
        if 'thumbnail' in data and 'source' in data['thumbnail']:
            print(f"Image link:")
            print(data['thumbnail']['source'])
            image_link = data['thumbnail']['source']
        print("-----------------------")

        # shortens url so that it can be used in the post.

        def shorten_url(long_url):
            api_url = "http://tinyurl.com/api-create.php"
            params = {'url': long_url}
            
            response = requests.get(api_url, params=params)
            
            if response.status_code == 200:
                return response.text
            else:
                return None

        shortened_wiki_url = shorten_url(random_url)
        post_chars_left -= len(shortened_wiki_url)

        def random_emoji():
            emojis = ['💠', '⚜️', '👑', '🏰', '🌍', '🌐', '🗺️', '🧭', '✅', '🆗', '🔭',
                    '🌌', '🌝', '👀', '👁️‍🗨️', '👁️', '🪬', '🃏', '🎲', '🍻', '🥳', '🪩',
                    'ℹ️', '🎰', '⭐', '🪐', '🌃', '🌇', '🌞', '🥵', '😈', '😏', '🔎',
                    '📷', '✨', '❤️‍🔥', '🐢', '🍄', '🧐', '🧐', '🤯', '🤯', '🧬',
                    '📇', '🍋', '🍎', '🍑', '🦪', '🦑', '💤', '🥱', '‼️', '😱', '🙀',
                    '🛡️', '🫧', '♨️', '💢']
            return random.choice(emojis)
        emoji = random_emoji()
        message = emoji
        post_chars_left -= len(message)

        image_to_post = None
        #fix image link

        print(image_link)
        last_slash_pos = image_link.rfind('/')
        #image_link = image_link[:last_slash_pos]

        # Headers to mimic a request from a web browser
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

        # Send a GET request to the image URL with headers
        response = requests.get(image_link, headers=headers, stream=True)
        base, extension = os.path.splitext(image_link)
        image_path = f"downloaded_image{extension}"
        os.system(f"touch {image_path}")
        if response.status_code == 200:
            with open(image_path, "wb") as file:
                file.write(response.content)
        base, extension = os.path.splitext(image_path)
        if extension == ".svg":
            new_png_path = base + ".png"
            os.remove(image_path)
            cairosvg.svg2png(url=image_path, write_to=new_png_path)
            image_path = new_png_path
        media_to_upload = apiv1.media_upload(filename=image_path)
        media_id = media_to_upload.media_id
        def tweet(api: tweepy.API, message: str, image_path=None):
            if image_path:
                authv2.create_tweet(text=message, media_ids=[media_id])
            else:
                authv2.create_tweet(text=message)
        summary_message = random_wiki.summary[:post_chars_left]
        final_period_pos = summary_message.rfind('.')
        if not final_period_pos == -1:
            summary_message = summary_message[:final_period_pos + 1]
        else:
            summary_message += "..."
        message += f" {summary_message} {emoji}\n\n"
        message += shortened_wiki_url
        print(f"posting: {message}\n")
        tweet(authv2, message=str(message), image_path=image_path)
        os.remove(image_path)

        print("One hour until the next post...")
        time.sleep(3600)

# Verify the authentication
while True:
    try:
        run()
    except Exception as e:
        print(e)
        print("Trying again in 1 minute...")
        time.sleep(60)