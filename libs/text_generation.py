import json
import openai
import os
from newspaper import Article
from libs.file_manipulation import create_directory_if_not_exists
from libs.gpt import gpt35_complete, gpt4_complete
from datetime import date

openai.api_key = os.getenv("OPENAI_API_KEY")

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


# function that takes headlines and creates a podcast introduction
def headlines_to_podcast_introduction(headlines, podcast_context):
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
def text_to_podcast_segment(article_headline, article_text, podcast_context):
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
def headlines_to_podcast_script(selected_headlines, podcast_number):
    # create string with all the headlines titles
    titles_string = json_headlines_to_prompt(selected_headlines)
    # create podcast introduction
    podcast_introduction = headlines_to_podcast_introduction(titles_string)
    # add jingle to podcast introduction
    podcast_introduction = podcast_introduction + "\n\n#jingle:\n"

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
        podcast_segments.append(podcast_segment)
        # TODO: test removing the SEGMENT {}:\n
        #segments_prompt+="\nSegment {}:\n".format(i) + podcast_segment
        segments_prompt+=podcast_segment
        i+=1


    bad_podcast = podcast_introduction + segments_prompt


    # for debugging purposes, write the bad podcast to a file in "./archives/podcast.txt"
    create_directory_if_not_exists("archives")
    create_directory_if_not_exists("archives/" + str(podcast_number))
    with open("archives/" + str(podcast_number) + "/firstdraft.txt", "w") as text_file:
        text_file.write(bad_podcast)

    podcast_context = create_podcast_context(podcast_number)

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

    # for debugging purposes, write the final podcast to a file
    create_directory_if_not_exists("archives")
    create_directory_if_not_exists("archives/" + str(podcast_number))
    #with open("archives/" + str(podcast_number) + "/finaldraft.txt", "w") as text_file:
        #text_file.write(good_podcast)
    return good_podcast


# create podcast context string from podcast number
def create_podcast_context(podcast_number):
    podcast_name = "The name of the podcast is The Cybersecurity AI Daily"
    podcast_number_prompt = "This is episode {} of the podcast. Today's date is {}".format(podcast_number, date.today().strftime("%B %d, %Y"))
    podcast_characters =" The characters in the podcast are:\
        1. The host\n\
            The host of the podcast is John. Here are John's characteristics, his characteristics should be taken into account when creating the dialogue but never mentionned outloud:\
        John is a CISO at a large company. He has good foundational cybersecurity and computerscience knowledge, and great a understanding of businesses\n\
        2. The co-host\n\
            The co-host of the podcast is Jane. Here are Jane's characteristics,his characteristics should be taken into account when creating the dialogue but never mentionned outloud:\
        Jane is security auditor at a smaller cybersecurity consulting firm. She has exceptionnal cybersecurity technical knowledge, but more limited business understanding.\n"
    #TODO: add podcast dynamic between characters
    podcast_goal= "The goal of the podcast is to provide cybersecurity news to the listeners. The podcast is to be informative and factual but with a light tone."
    
    # Example podcast script
    exemple_podcast_script_template = """
    [Introduction, present the days and todays headlines]
    # jingle
    [discussion about first headline]
    #transition
    [discussion about second headline]
    #transition
    [...]
    #transition
    [discussion about last headline]
    #transition
    [Conclusion, thank the listeners for listening]
   """

    podcast_context = podcast_name \
        + podcast_goal \
        + podcast_number_prompt \
        + podcast_characters \
        + "Here is an example template of a podcast script:\n" \
        + exemple_podcast_script_template
    return podcast_context

# function that takes in headlines in json format and uses gpt4 to generate a full podcast script in 1 go
def headlines_to_podcast_script_gpt4(selected_headlines, podcast_number):
    # create prompt with all the articles content
    articles_string = ""
    for headline_index, headline in enumerate(selected_headlines):
        articles_string += "Headline " + str(headline_index) + ": " + headline["title"] + "\n"
        for link_index, link in enumerate(headline["links"]):
            article_text = extract_text_from_url(link)
            articles_string += "Link " + str(link_index) + ": " + link + "\n"
            articles_string += article_text + "\n"

     
    # podcast prompt
    task_prompt = "You will be given a list of headlines and the content of the articles they are about.\
                    You must write a podcast script that includes all the articles.\
                        You must include an introduction and a conclusion.\
                            You must include a transition between each article.\n\n"
    # prompt for music
    music_prompt = "You MUST mark transitions between articles with #transition.\n\
                    You MUST mark the end of the introduction with #jingle.\
                    You MUST but these markers on new lines. With only the marker on the line.\
                    For exemple in between the introduction and the first headline:\n \
                    John: That's right, Jane. So, let's dive right into our first headline.\n\
                    #jingle\n \
                    Jane: Today, we're looking into an article about ...\n\n"
    # format prompt
    format_prompt = "You MUST write the script for a single episode, the episode must last between 5 and 10 minutes. \
                    This means between 600 and 900 words more or less.\n"

    # replace with gpt4 generated prompts
    task_prompt = "You will be given a list of headlines and the content of the articles they correspond to.\
          Your task is to write a podcast script that covers all the articles. The script must include an introduction,\
              transitions between articles, and a conclusion."

    music_prompt = "Please indicate transitions between articles with #transition, and mark the end of the introduction with #jingle. Place these markers on new lines, with only the marker on the line. For example, between the introduction and the first headline:\n\
            John: That's right, Jane. So, let's dive right into our first headline.\n\
            #jingle\n\
            Jane: Today, we're looking into an article about ...\n"
    
    format_prompt = "Your script should be for a single episode, with a duration between 5 and 10 minutes.\
          This equates to approximately 600 to 900 words. Make sure the content is engaging and informative."

    # create context using podcast number
    podcast_context = create_podcast_context(podcast_number)
    # create full prompt
    full_prompt = task_prompt + podcast_context + music_prompt + format_prompt + articles_string

    # generate podcast script
    podcast_script = gpt4_complete(full_prompt)

    return podcast_script


def create_podcast_title(podcast_number, podcast_script):
    prompt = "You will be given a podcast script. You must write a podcast title that is relevant to the podcast script.\n\
            Example title: \"Episode 1: Iranian Hackers, Apple's Zero-Day Flaws, and Ex-Employee Password Risks\"\
                You will generate the title for Episode " + str(podcast_number) + ".\n\n" \
            + "Here is the script:\n" + podcast_script
    podcast_title = gpt4_complete(prompt)
    return podcast_title

def create_podcast_description(podcast_number, podcast_script, headlines):
    prompt = "You will be given a podcast script. You must write a podcast description that is relevant to the podcast script.\n\
            Example description: \"In the debut episode of The Cybersecurity AI Daily, hosts Jane and John discuss the latest cybersecurity news.\
                  Topics include the Iranian nation-state group MuddyWater disguising destructive attacks as ransomware operations,\
                      Apple's updates addressing zero-day vulnerabilities in iOS, iPadOS, macOS, and Safari, and the alarming rate of \
                        former employees using their old company passwords after leaving their jobs. Tune in for a concise and informative overview \
                            of today's most pressing cybersecurity concerns. \"\
                You will generate the description for episode " + str(podcast_number) + ".\n\n" \
            + "Here is the script:\n" + podcast_script
    podcast_description = gpt4_complete(prompt)

    # add disclaimer
    disclaimer = "Disclaimer: Please be aware that the content of this podcast is generated by AI technology, and as such, may contain inaccuracies or inconsistencies. Listener discretion is advised as we cannot guarantee the complete accuracy of the information presented.\n"

    # add sources at the end of the description
    sources = "\nSources:\n"
    for headline in headlines:
        for link in headline["links"]:
            sources += link + "\n"

    podcast_description = disclaimer + podcast_description + sources
    return podcast_description


def create_podcast_keywords(podcast_number, podcast_script):
    prompt = "You will be given a podcast script. You must write a list of comma separeted keywords that are relevant to the podcast script.\n\
            Exemple keywords output: \n\
            \"Cybersecurity, Iranian Hackers, MuddyWater, Ransomware, Apple, Zero-Day, Vulnerabilities, iOS, iPadOS, macOS, Safari, Former Employees, Password Risks\"\n\
            You will generate the keywords for episode " + str(podcast_number) + ".\n\n" \
            + "Here is the script:\n" + podcast_script
    podcast_keywords = gpt4_complete(prompt)
    return podcast_keywords


