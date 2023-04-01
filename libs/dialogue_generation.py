import json
import openai
import os
from newspaper import Article

openai.api_key = os.getenv("OPENAI_API_KEY")

DEBUG = True

def create_directory_if_not_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

# function that uses gpt4 to complete a prompt
def gpt4_complete(prompt):
    conversation = [
        {"role": "system", "content": "You are a helpful assistant that creates podcast scripts."},
        {"role": "user", "content": prompt},
    ]
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=conversation,
    )
    return response.choices[0].message.content

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

def extract_text_from_url(url):
    article = Article(url)
    article.download()
    article.parse()
    return article.text

# debug logging function
def log(text):
    if(DEBUG):
        print(text)

podcast_number = 1
podcast_name = "The name of the podcast is The Cyber AI Daily"
podcast_number_prompt = "This is episode {} of the podcast.".format(podcast_number)
podcast_characters =" The characters in the podcast are:\
    1. The host\n\
        The host of the podcast is John. Here are John's characteristics, his characteristics should be taken into account when creating the dialogue but never mentionned outloud:\
    John is a CISO at a large company. He has good foundational cybersecurity and computerscience knowledge, and great a understanding of businesses\n\
    2. The co-host\n\
        The co-host of the podcast is Jane. Here are Jane's characteristics,his characteristics should be taken into account when creating the dialogue but never mentionned outloud:\
    Jane is security auditor at a smaller cybersecurity consulting firm. She has exceptionnal cybersecurity technical knowledge, but more limited business understanding.\n"
#TODO: add podcast dynamic between characters
podcast_goal= "The goal of the podcast is to provide cybersecurity news to the listeners. The podcast is to be informative and factual but with a light tone."

podcast_context = podcast_name \
    + podcast_goal \
    + podcast_number_prompt \
    + podcast_characters

# function that takes headlines and creates a podcast introduction
def headlines_to_podcast_introduction(headlines):
    prompt="You will be given a list of headlines. Write a podcast introduction for the podcast.\
            Note that since it's an introduction you must introduce the podcast.\
                Include the name of the speaker before each dialogue line. For exemple John:..." \
            + podcast_context \
            + "\n\nHeadlines: " + headlines
    #log("DEBUG: headlines_to_podcast_introduction prompt:"+ prompt)
    response = gpt35_complete(prompt)
    #TODO add error handling
    return response

# function that takes a article text and returns a podcast segments for it
def text_to_podcast_segment(article_headline, article_text):
    prompt="You will be given the content of an article and a headline for it.\
            Write a podcast segment using the article.\
            Note that since it's a segment you must not introduce the podcast.Jump straight to the subject.\n \
            Include the name of the speaker before each dialogue line. For exemple John:...\n" \
            + podcast_context \
            + "\n\nHeadline: " + article_headline \
            + "\n\nArticle: " + article_text 
    #log("DEBUG: text_to_podcast_segment prompt:"+ prompt)
    response = gpt35_complete(prompt)
    #TODO add error handling
    return response

# function that takes a string of headlines and returns an array of json objects
def headlines_string_to_json_array(headlines_string):
    selected_headlines = []
    for line in response_text.splitlines():
        if line.startswith("{"):
            # headline string is in json format, change string to json
            selected_headlines.append(json.loads(line))
    return selected_headlines

# fuction that takes an array of json headlines and returns a string that can be given to gpt4
def json_headlines_to_prompt(headlines):
    titles_string = ""
    i=1
    for headline in headlines:
        titles_string += "Headline {}".format(i) + headline["title"] + "\n"
        i+=1
    return titles_string


# function that takes interesting headlines in json format and returns a podcast script
def headlines_to_podcast_script(selected_headlines):
    # create string with all the headlines titles
    titles_string = json_headlines_to_prompt(selected_headlines)
    # create podcast introduction
    podcast_introduction = headlines_to_podcast_introduction(titles_string)
    # add jingle to podcast introduction
    podcast_introduction = podcast_introduction + "\n\n#jingle:\n"
    print(podcast_introduction)


    podcast_segments = []
    # for each element in selected_headlines, get the text of the article and add it to the prompt
    i = 1
    segments_prompt = ""
    for headline in selected_headlines:
        article_text = extract_text_from_url(headline["link"])
        podcast_segment = text_to_podcast_segment(headline["title"], article_text)
        #add transition between segmentsn if not last segment
        if(i!=len(selected_headlines)):
            podcast_segment = podcast_segment + "\n\n#transition:\n"
        print(podcast_segment)
        podcast_segments.append(podcast_segment)
        # TODO: test removing the SEGMENT {}:\n
        #segments_prompt+="\nSegment {}:\n".format(i) + podcast_segment
        segments_prompt+=podcast_segment
        i+=1


    #print(podcast_segments)

    bad_podcast = podcast_introduction + segments_prompt


    # for debugging purposes, write the bad podcast to a file in "./archives/podcast.txt"
    create_directory_if_not_exists("archives")
    create_directory_if_not_exists("archives/" + str(podcast_number))
    with open("archives/" + str(podcast_number) + "/firstdraft.txt", "w") as text_file:
        text_file.write(bad_podcast)

    # take the segments and make a cohesive podcast out of it
    prompt = "You will be given a podcast script made by AI. Rewrite it without changing the facts.\n\
            You MUST write the script for a single episode, therefore only include \
            1 introduction and 1 conclusion and remove any seperation between segments.\n\
            You MUST NOT shorten the script, it must be about the same length as the original script.\n\
            You MUST keep the name of the person speaking before each dialogue line.\
            You MUST add the name of the person speaking if is not already there. For exemple John:...\n\
            You MUST remove all text that's isn't a dialogue line.\n\
            You MUST keep the lines that start with an #, because they signal when music should be added. For exemple do NOT delete #jingle or #transition" \
    + podcast_context \
    + bad_podcast

    conversation = [
        {"role": "system", "content": "You are a helpful assistant that creates podcast scripts."},
        {"role": "user", "content": prompt},
    ]

    good_podcast = gpt4_complete(prompt)

    # print the final podcast
    print("PODCAST")
    print(good_podcast)
    # for debugging purposes, write the final podcast to a file
    create_directory_if_not_exists("archives")
    create_directory_if_not_exists("archives/" + str(podcast_number))
    #with open("archives/" + str(podcast_number) + "/finaldraft.txt", "w") as text_file:
        #text_file.write(good_podcast)
    return good_podcast

# for debugging

response_text='{ "title": "Microsoft Introduces GPT-4 AI-Powered Security Copilot Tool to Empower Defenders", "link": "https://thehackernews.com/2023/03/microsoft-introduces-gpt-4-ai-powered.html"}\n\
{ "title": "President Biden Signs Executive Order Restricting Use of Commercial Spyware", "link": "https://thehackernews.com/2023/03/president-biden-signs-executive-order.html"}\n\
{ "title": "North Korea\'s Kimsuky Evolves into Full-Fledged, Prolific APT", "link": "https://www.darkreading.com/threat-intelligence/north-korea-kimsuky-evolves-full-fledged-persistent-threat"}'


