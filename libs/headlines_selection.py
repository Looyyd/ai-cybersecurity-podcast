import feedparser
import openai
import os
import json
from datetime import datetime, timedelta, timezone

openai.api_key = os.getenv("OPENAI_API_KEY")

def gpt35_complete(prompt):
    conversation = [
        {"role": "system", "content": "You are a helpful assistant that creates podcast scripts."},
        {"role": "user", "content": prompt},
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation,
    )
    return response.choices[0].message.content

rss_feed_urls = ['https://feeds.feedburner.com/TheHackersNews',
                 'https://www.cisa.gov/news.xml',
                 #'http://www.reddit.com/r/netsec/.rss',
                 'https://www.darkreading.com/rss.xml',
                 ] 

def parse_date(date_string):
    formats = [
        '%a, %d %b %Y %H:%M:%S %z', 
        '%a, %d %b %y %H:%M:%S %z',
        '%Y-%m-%dT%H:%M:%S%z'
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue

    raise ValueError(f"Date string '{date_string}' does not match any of the expected formats")




# function that selects the most interesting headlines from the rss feeds
def select_headlines(n_headline):
    one_day_ago = datetime.now(timezone.utc) - timedelta(days=2)
    headlines = []

    for  rss_feed_url in rss_feed_urls:
        # Parse the RSS feed
        feed = feedparser.parse(rss_feed_url)
        # Extract and print titles of articles from the last week
        headlines.append("Source: " + rss_feed_url + "\n")
        for entry in feed.entries:
            entry_date = parse_date(entry.published)
            if entry_date > one_day_ago:
                headlines.append("Article:" + entry.title + ", Article link: " + entry.link + "\n")


    headline_string = "\n".join(headlines)

    # generate example output with correct number of headlines
    example_output = ""
    for i in range(n_headline):
        example_output += "{ \"title\": \"Article" + str(i) + "\", \"link\": \"link" + str(i) + "\" }"
        example_output += "\n"


    # Base prompt
    prompt="You will be given headlines of cybersecurity news articles from different sources(the sources will be given before each headline list).\
            Determine what were the"+ str(n_headline) + " most interesting news stories out of these headlines.\
            Under each story, add links to the relevant articles.\
            Put the output into json. You MUST send 1 line per json object. Example output:\n" \
            + example_output \
            + "Headlines:\n"  \
            + headline_string  \
            + "\n{} biggest stories:".format(n_headline)
    print(prompt)

    response = gpt35_complete(prompt)

    response_text = response

    selected_headlines = []
    for line in response_text.splitlines():
        if line.startswith("{"):
            # headline string is in json format, change string to json
            selected_headlines.append(json.loads(line))
    return(selected_headlines)
