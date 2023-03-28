import feedparser
import openai
import os
import json
from datetime import datetime, timedelta, timezone

openai.api_key = os.getenv("OPENAI_API_KEY")


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


# time Mon, 20 Mar 2023 11:21:00 +0530
# tim2 Wed, 14 Dec 22 12:00:00 +0000
# Get the date one week ago as an offset-aware datetime
# TODO: change delta to 1 week
one_week_ago = datetime.now(timezone.utc) - timedelta(days=1)
headlines = []

for  rss_feed_url in rss_feed_urls:
    # Parse the RSS feed
    feed = feedparser.parse(rss_feed_url)
    # Extract and print titles of articles from the last week
    headlines.append("Source: " + rss_feed_url + "\n")
    for entry in feed.entries:
        entry_date = parse_date(entry.published)
        if entry_date > one_week_ago:
            #print(entry.published, entry.title)
            headlines.append("Article:" + entry.title + " ,Article link: " + entry.link + "\n")
            #print(entry)


headline_string = "\n".join(headlines)

print(headline_string)

# Base prompt
prompt="You will be given headlines of cybersecurity news articles from different sources(the sources will be given before each headline list).\
        Determine what were the 3 most interesting news stories out of these headlines.\
        Under each story, add links to the relevant articles.\
        Example output:\
            1. Cyberattack targets something.\
                https://thehackernews.com/2023/03/cyberattack-targets-something\
                https://www.darkreading.com/attacks-breaches/cyberattack-at-something\n\n"\
        + "Headlines:\n"  \
        + headline_string  \
        + "\n3 biggest stories:"
prompt="You will be given headlines of cybersecurity news articles from different sources(the sources will be given before each headline list).\
        Determine what were the 3 most interesting news stories out of these headlines.\
        Under each story, add links to the relevant articles.\
                Put the output into json. Example output:\
    { \"title\": \"Article1\", \"link\": \"link1\" } \
    { \"title\": \"Article2\", \"link\": \"link2\" } \
    { \"title\": \"Article3\", \"link\": \"link3\" } \
}\n\n"\
        + "Headlines:\n"  \
        + headline_string  \
        + "\n3 biggest stories:"

response = openai.Completion.create(
  model="text-davinci-003",
    prompt=prompt,
  temperature=0,
  max_tokens=1000,
  top_p=1.0,
  frequency_penalty=0.5,
  presence_penalty=0.0
)


print("GPT response:")
#print(response)
response_text = response.choices[0].text
print(response_text)

selected_headlines = []
for line in response_text.splitlines():
    if line.startswith("{"):
        # headline string is in json format, change string to json
        selected_headlines.append(json.loads(line))

print(selected_headlines)
