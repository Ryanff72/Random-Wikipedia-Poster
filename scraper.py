import argparse
import logging
import os
import random
import time
from io import BytesIO

import bs4
import cairosvg
import requests
import tweepy
import wikipediaapi
from PIL import Image

logging.basicConfig(filename='wiki_poster.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

#parse args
parser = argparse.ArgumentParser(prog="random wikipedia poster",
                               description="Posts random Wikipedia articles with images")
parser.add_argument("--keyloc", required=True, 
                    help="Path to file containing X API credentials")
args = parser.parse_args()

#read keys
try:
    with open(args.keyloc, 'r') as keys:
        api_key = keys.readline().strip()
        api_secret = keys.readline().strip()
        access_token = keys.readline().strip()
        access_secret = keys.readline().strip()
        bearer_token = keys.readline().strip()
except Exception as e:
    logging.error(f"Failed to read credentials: {e}")
    raise

#auth
try:
    client = tweepy.Client(
        bearer_token=bearer_token,
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_secret
    )
except Exception as e:
    logging.error(f"X API authentication failed: {e}")
    raise
  
bad_categories = [
    "All Wikipedia articles in need of updating",
    "Articles with short description",
    "All stub articles",
    "People",
    "Rights",
    "Musicians"
]

#check viability
def check_page(random_page, data):
    thumb_ok = 'thumbnail' in data and 'source' in data['thumbnail']
    num_languages = len(random_page.langlinks) + 1
    logging.info(f"Article '{random_page.title}' is in {num_languages} languages")
    
    categories = random_page.categories
    rotten_article = any(category in bad_categories for category in categories)
    
    return num_languages > 2 and not rotten_article and thumb_ok

#shorten url for text limit
def shorten_url(long_url):
    try:
        api_url = "http://tinyurl.com/api-create.php"
        params = {'url': long_url}
        response = requests.get(api_url, params=params, timeout=10)
        if response.status_code == 200:
            return response.text
        logging.error(f"TinyURL API failed: {response.status_code}")
        return None
    except Exception as e:
        logging.error(f"Failed to shorten URL: {e}")
        return None

#upload
def upload_media_v2(file_path, oauth_token, oauth_token_secret):
    try:
        url = "https://upload.twitter.com/2/media"
        auth = tweepy.OAuth1UserHandler(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=oauth_token,
            access_token_secret=oauth_token_secret
        )
        files = {'media': open(file_path, 'rb')}
        response = requests.post(url, files=files, auth=auth, timeout=10)
        if response.status_code == 201:
            media_id = response.json()['media_id_string']
            logging.info(f"Media uploaded successfully: {media_id}")
            return media_id
        logging.error(f"Media upload failed: {response.status_code} - {response.text}")
        return None
    except Exception as e:
        logging.error(f"Media upload error: {e}")
        return None

def tweet(client, message, image_path=None):
    try:
        if image_path:
            media_id = upload_media_v2(image_path, access_token, access_secret)
            if media_id:
                client.create_tweet(text=message, media_ids=[media_id])
            else:
                logging.warning("Media upload failed, posting without image")
                client.create_tweet(text=message)
        else:
            client.create_tweet(text=message)
        logging.info(f"Posted tweet: {message}")
    except Exception as e:
        logging.error(f"Failed to post tweet: {e}")

def random_emoji():
    emojis = [
        '💠', '⚜️', '👑', '🏰', '🌍', '🌐', '🗺️', '🧭', '🔭', '🌌', 
        '🌝', '👀', '👁️‍🗨️', '🪬', '🃏', '🎲', '🍻', '🥳', '🪩', '🎰', 
        '⭐', '🪐', '🌃', '🌇', '🌞', '😈', '😏', '🔎', '📷', '✨', 
        '❤️‍🔥', '🐢', '🍄', '🧐', '🤯', '🧬', '🍋', '🍎', '🍑', '🦪', 
        '🦑', '💤', '‼️', '😱', '🙀', '🛡️', '🫧', '♨️', '💢', '🚀', 
        '🦄', '🔥', '🎮', '💎', '🪄', '⚡️', '🦁', '🌈', '💥', '🕹️', 
        '🎉', '🦋', '🌪️', '🪶', '💡', '🎸', '🛸', '🖼️', '🧙', '🍉', 
        '🦖', '🦒', '🌴', '🎨', '🗿', '🦹', '🦸', '🎥', '🪅'
    ]
    return random.choice(emojis)

def run():
    wiki_wiki = wikipediaapi.Wikipedia(
        user_agent="wiki_poster (example@gmail.com)", language='en'
    )
    
    while True:
        try:
            message = ""
            post_chars_left = 271  # Stay within X character limit

            # Fetch random Wikipedia page
            random_link = requests.get(
                "https://en.wikipedia.org/wiki/special:Random", timeout=10
            )
            random_title = bs4.BeautifulSoup(random_link.text, features="html.parser")
            page_title = random_title.title.text[:-12]  # Remove " - Wikipedia"
            logging.info(f"Attempting article: {page_title}")

            # Fetch page summary
            api_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{page_title}"
            response = requests.get(api_url, timeout=10)
            if response.status_code != 200:
                logging.error(f"Failed to fetch summary: {response.status_code}")
                continue
            data = response.json()

            # Fetch Wikipedia page details
            random_wiki = wiki_wiki.page(page_title)

            # Check suitability
            if not check_page(random_wiki, data):
                continue

            # Get Wikipedia URL and shorten it
            random_url = f"https://en.wikipedia.org/wiki/{page_title.replace(' ', '_')}"
            shortened_url = shorten_url(random_url)
            if not shortened_url:
                logging.warning("URL shortening failed, using full URL")
                shortened_url = random_url
            post_chars_left -= len(shortened_url)

            # Prepare tweet message
            emoji = random_emoji()
            message = emoji
            post_chars_left -= len(emoji)

            # Handle image
            image_path = None
            if 'thumbnail' in data and 'source' in data['thumbnail']:
                image_link = data['thumbnail']['source']
                logging.info(f"Image link: {image_link}")
                
                # Download image
                headers = {
                    "User-Agent": (
                        "Mozilla/5.0 (X11; Linux armv7l) AppleWebKit/537.36 "
                        "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                    )
                }
                response = requests.get(image_link, headers=headers, stream=True, timeout=10)
                if response.status_code == 200:
                    base, extension = os.path.splitext(image_link)
                    image_path = f"downloaded_image{extension}"
                    with open(image_path, "wb") as file:
                        file.write(response.content)
                    
                    # Convert SVG to PNG if needed
                    if extension.lower() == ".svg":
                        new_png_path = "downloaded_image.png"
                        cairosvg.svg2png(url=image_link, write_to=new_png_path)
                        if os.path.exists(image_path):
                            os.remove(image_path)
                        image_path = new_png_path
                else:
                    logging.error(f"Failed to download image: {response.status_code}")
                    image_path = None

            #create message
            summary_message = random_wiki.summary[:post.chars_left]
            final_period_pos = summary_message.rfind('.')
            if final_period_pos != -1:
                summary_message = summary_message[:final_period_pos + 1]
            else:
                summary_message += "..."
            message += f" {summary_message} {emoji}\n\n{shortened_url}"
            logging.info(f"Posting: {message}")
            #post
            tweet(client, message, image_path)
            #clean
            if image_path and os.path.exists(image_path):
                os.remove(image_path)
            #wait an hour before posting again
            logging.info("Waiting 1 hour until next post")
            time.sleep(3600)

        except Exception as e:
            logging.error(f"Error in main loop: {e}")
            logging.info("Retrying in 1 minute")
            time.sleep(60)

if __name__ == "__main__":
    run()
