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

api_key = "a0jhwKgR7kEGuYBX0K0PfrnmA"
api_secret = "F88MspacnhB6STqjSgRR297H5hF2qL6EDr0dJ5mvMLy6CKLFrD"
client_id = "QkVQU0pKcUU0WjUxelZZMldtVHo6MTpjaQ"
client_secret = "h8Xuy5MLYY4_OD3fKbjrOFYH7AMEv-U2z05fpNy_b1WSIMdKWY"
access_token = "1800886833653411840-crC1iLTxGrK5s7xBoiIJmenJeV33Py"
access_secret = "J7AsKAI5dzo9HSjVLrnSInieEihy8VCG7MxyYN3ORRbsT"
bearer_token = "AAAAAAAAAAAAAAAAAAAAAKIUuQEAAAAAlfvLygGRTfT3EEjRHmNfld46lqo%3DeJQgBYHv5ik4hriGBeld9N0bdnAPQ3p8DspFpKflTd8f1k2NoM"

bad_categories = ["All Wikipedia articles in need of updating",
                  "Articles with short description",
                  "All stub articles"]

# Authenticate to Twitter
authv1 = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_secret)
authv1.set_access_token(access_token, access_secret)
apiv1 = tweepy.API(authv1)
authv2 = tweepy.Client(bearer_token, api_key, api_secret, access_token, access_secret)
apiv2 = tweepy.API(authv2)

# test if page is suitable for posting
def check_page(random_page):
    print(f"article is in {len(random_page.langlinks) + 1} languages.")
    categories = random_page.categories
    rotten_article = False
    for category in categories:
        if category in bad_categories:
            rotten_article = True
    # Print the categories
    if (len(random_page.langlinks) + 1) < 10 and rotten_article == False:
        run()
        return False
    return True


# main program loop
def run():
    while True:

        message = ""
        post_chars_left = 274 # stay within twitter char limit

        random_link = requests.get("https://en.wikipedia.org/wiki/special:Random")

        random_title = bs4.BeautifulSoup(random_link.text, features="html.parser")
        print(f"attempting: {random_title.title.text[:-12]}")

        wiki_wiki = wikipediaapi.Wikipedia("wiki idk example (example@gmail.com)", 'en')
        random_wiki = wiki_wiki.page(random_title.title.text[:-12])

        #checks suitability of page

        if not check_page(random_wiki):
            break
        random_url = (f"https://en.wikipedia.org/wiki/{random_title.title.text[:-12].replace(' ', '_')}")

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

        url = "https://en.wikipedia.org/w/api.php"
        response = requests.get(url, {
        'action': 'query',
        'prop': 'images',
        'titles': random_wiki.title,
        'format': 'json',
        'formatversion': 2
        }).json()
        images = response['query']['pages'][0]['images']
        image_link = None
        for image in images:
            _, ext = os.path.splitext(image['title'])
            if ext == ".jpeg" or ext == ".jpg" or ext == ".JPEG" or ext == ".JPG":
                image_link = image['title']
                break
        if image_link == None:
            print("using .svg!!")
            image_link = images[0]['title']
        pyWikiCommons.download_commons_image(image_link)
        image_path = os.path.join("wikiCommonsOutput", image_link)
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
        os.remove(image_path)
        summary_message = random_wiki.summary[:post_chars_left]
        final_period_pos = summary_message.rfind('.')
        if not final_period_pos == -1:
            summary_message = summary_message[:final_period_pos + 1]
        message += f" {summary_message} {emoji}\n\n"
        message += shortened_wiki_url
        print(f"posting: {message}\n")
        tweet(authv2, message=str(message), image_path=images[0]['title'])

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