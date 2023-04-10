import feedparser
import openai
import os
import json
import random
from datetime import datetime, timedelta, timezone
from libs.gpt import gpt35_complete, gpt4_complete



def parse_date(date_string):
    formats = [
        '%a, %d %b %Y %H:%M:%S %z', 
        '%a, %d %b %y %H:%M:%S %z',
        '%Y-%m-%dT%H:%M:%S%z',
        '%d %b %Y %H:%M:%S %z'
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue

    raise ValueError(f"Date string '{date_string}' does not match any of the expected formats")


# function that takes in rss feeds and outputs a prompt for gpt
def rss_to_prompt(rss_feeds_urls, time_delta_in_days):
    headlines = []
    one_day_ago = datetime.now(timezone.utc) - timedelta(days=time_delta_in_days)

    for  rss_feed_url in rss_feeds_urls:
        # Parse the RSS feed
        feed = feedparser.parse(rss_feed_url)
        # Extract and print titles of articles from the last week
        headlines.append("Source: " + rss_feed_url + "\n")
        for entry in feed.entries:
            entry_date = parse_date(entry.published)
            if entry_date > one_day_ago:
                headlines.append("Article:" + entry.title + ", Article link: " + entry.link + "\n")


    headline_string = "\n".join(headlines)
    return headline_string


# function that selects the most interesting headlines from the rss feeds
def select_headlines(n_headline, days):
    rss_feed_urls = ['https://feeds.feedburner.com/TheHackersNews',
                    'https://www.cisa.gov/news.xml',
                    #'http://www.reddit.com/r/netsec/.rss',
                    'https://www.darkreading.com/rss.xml',
                    'https://www.bleepingcomputer.com/feed/',
                    'https://www.csoonline.com/news/index.rss',
                    'https://feeds.feedburner.com/securityweek',
                    'https://cyware.com/allnews/feed',
                    'https://cybersecuritynews.com/feed/' # seems mediocre quality
                    ] 

    # https://nakedsecurity.sophos.com/feed article extraction is not working
    # https://www.scmagazine.com no rss feed
    # https://www.infosecurity-magazine.com/news/ no rss
    # https://www.helpnetsecurity.com/view/news/ no rss feed
    
    headlines_string = rss_to_prompt(rss_feed_urls, days)

    # generate example output with correct number of headlines
    example_output = ""
    for i in range(n_headline):
        n_links = random.randint(1, 3)
        links = ", ".join(["\"link" + str(i) + "_" + str(j) + "\"" for j in range(n_links)])
        
        example_output += "{ \"title\": \"Article" + str(i) + "\", \"links\": [" + links + "] }"
        example_output += "\n"



    # Base prompt
    # TODO: put prompt into a seperate function
    prompt="You will be given headlines of cybersecurity news articles from different sources(the sources will be given before each headline list).\
            Determine what were the"+ str(n_headline) + " most interesting news stories out of these headlines.\
            For each story, add links to the relevant articles.\
            Put the output into json. You MUST send 1 line per json object, with the string title and an array of strings called links. Example output:\n" \
            + example_output \
            + "Headlines:\n"  \
            + headlines_string  \
            + "\n{} biggest stories:".format(n_headline)
    #print(prompt)

    response = gpt4_complete(prompt)

    response_text = response

    selected_headlines = []
    for line in response_text.splitlines():
        if line.startswith("{"):
            # headline string is in json format, change string to json
            selected_headlines.append(json.loads(line))
    return(selected_headlines)


if __name__ == "__main__":
    # Example usage
    selected_headlines = select_headlines(5, 1)
    print(selected_headlines)