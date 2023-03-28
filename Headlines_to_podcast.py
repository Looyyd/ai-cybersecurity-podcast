import json
import openai
from newspaper import Article

DEBUG = True

def extract_text_from_url(url):
    article = Article(url)
    article.download()
    article.parse()
    return article.text

# debug logging function
def log(text):
    if(DEBUG):
        print(text)

podcast_name = "The name of the podcast is Cybersecurity cybernews podcast"
podcast_number = "This is episode {} of the podcast.".format(1)
podcast_characters =" The characters in the podcast are:\
    1. The host\
        The host of the podcast is John. John is a CISO at a large company.\
    2. The co-host\
        The co-host of the podcast is Jane. Jane is security auditor at a smaller cybersecurity consulting firm."
podcast_goal= "The goal of the podcast is to provide cybersecurity news to the listeners. The goal of the podcast is to be informative and factual but with a light tone."

podcast_context = podcast_name \
    + podcast_goal \
    + podcast_number \
    + podcast_characters

# function that takes a article text and returns a podcast segments for it
def text_to_podcast_segment(article_headline, article_text):
    prompt="You will be given the content of an article and a headline for it.\
            Write a podcast segment for the article." \
            + podcast_context \
            + "\n\nHeadline: " + article_headline \
            + "\n\nArticle: " + article_text 
    log("DEBUG: text_to_podcast_segment prompt:"+ prompt)
    response = openai.Completion.create(
    model="text-davinci-003",
        prompt=prompt,
    temperature=0.4,
    max_tokens=1000,
    top_p=1.0,
    frequency_penalty=0.5,
    presence_penalty=0.0
    )
    return response.choices[0].text

# for debugging
response_text='{ "title": "Microsoft Introduces GPT-4 AI-Powered Security Copilot Tool to Empower Defenders", "link": "https://thehackernews.com/2023/03/microsoft-introduces-gpt-4-ai-powered.html"}\n\
{ "title": "President Biden Signs Executive Order Restricting Use of Commercial Spyware", "link": "https://thehackernews.com/2023/03/president-biden-signs-executive-order.html"}\n\
{ "title": "North Korea\'s Kimsuky Evolves into Full-Fledged, Prolific APT", "link": "https://www.darkreading.com/threat-intelligence/north-korea-kimsuky-evolves-full-fledged-persistent-threat"}'


selected_headlines = []
for line in response_text.splitlines():
    if line.startswith("{"):
        # headline string is in json format, change string to json
        selected_headlines.append(json.loads(line))

print(selected_headlines)


podcast_segments = []
# for each element in selected_headlines, get the text of the article and add it to the prompt
i = 1
segments_prompt = ""
print("DEBUG: entering segment creation loop")
for headline in selected_headlines:
    article_text = extract_text_from_url(headline["link"])
    podcast_segment = text_to_podcast_segment(headline["title"], article_text)
    print(podcast_segment)
    podcast_segments.append(podcast_segment)
    segments_prompt+="\nSegment {}:\n".format(i) + podcast_segment
    i+=1


#print(podcast_segments)

print("Segments prompt")
print(segments_prompt)

# take the segments and make a cohesive podcast out of it
prompt = "You will be given a list of podcast segments. Use these segments to create a cohesive podcast episode" \
+ podcast_context \
+ segments_prompt

conversation = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": prompt},
]


response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=conversation,
)
print(response)

# print the final podcast
print("PODCAST")
print(response.choices[0].text)
