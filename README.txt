# Random Wikipedia Poster

Random-Wikipedia-Poster is a Python script that automatically fetches a random Wikipedia article and posts a summary of it, along with a relevant image, to Twitter every hour.

## Features

- Fetches a random Wikipedia article every hour.
- Posts a summary of the article along with a thumbnail image to Twitter.
- Filters out articles based on specified categories to avoid certain types of content.
- Uses TinyURL to shorten the Wikipedia URL for the tweet.
- Adds a random emoji to each tweet for visual appeal.

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/Random-Wikipedia-Poster.git
   cd Random-Wikipedia-Poster
   ```

2. **Install dependencies:**
   ```bash
   pip install requests wikipedia-api beautifulsoup4 tweepy pyWikiCommons cairosvg pillow
   ```

3. **Set up Twitter API keys:**

   Create a text file with your Twitter API keys and tokens in the following order:
   ```
   API_KEY
   API_SECRET_KEY
   CLIENT_ID
   CLIENT_SECRET
   ACCESS_TOKEN
   ACCESS_TOKEN_SECRET
   BEARER_TOKEN
   ```

   Save this file at your desired location (e.g., `keys.txt`).

## Usage

Run the script with the path to your keys file:

```bash
python random_wikipedia_poster.py --keyloc /path/to/your/keys.txt
```

## Script Details

### Arguments

- `--keyloc`: The path to the file containing your Twitter API keys and tokens.

### Main Components

- **Authentication**: Uses `tweepy` for Twitter API authentication.
- **Fetching Random Wikipedia Article**: Uses Wikipedia API to fetch a random article.
- **Filtering Articles**: Articles in certain categories (defined in `bad_categories`) are filtered out.
- **Shortening URLs**: Uses TinyURL API to shorten the Wikipedia URL for the tweet.
- **Posting to Twitter**: Posts the article summary and image to Twitter.

### Function Overview

- `check_page(random_page, data)`: Checks if the fetched Wikipedia page is suitable for posting.
- `run()`: Main loop that fetches articles, checks suitability, prepares the tweet, and posts it to Twitter.
- `shorten_url(long_url)`: Shortens the given URL using TinyURL API.
- `random_emoji()`: Returns a random emoji from a predefined list.
- `tweet(api, message, image_path)`: Posts the tweet with or without an image.

### Error Handling

If an error occurs, the script will print the error message and retry after one minute.

## Contributing

If you find any issues or have suggestions for improvements, please open an issue or create a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [Wikipedia API](https://github.com/martin-majlis/Wikipedia-API) for fetching Wikipedia content.
- [Tweepy](https://www.tweepy.org/) for interacting with the Twitter API.
- [CairoSVG](https://cairosvg.org/) for converting SVG images to PNG.

---

Ryan Feller
Last Updated June 16, 2024