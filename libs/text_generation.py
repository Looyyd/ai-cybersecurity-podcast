import json
import openai
import os
from newspaper import Article
from libs.file_manipulation import create_directory_if_not_exists
from libs.gpt import gpt35_complete, gpt4_complete, gpt_complete_until_format
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


# fuction that takes an array of json headlines and returns a string that can be given to gpt4
def json_headlines_to_prompt(headlines):
    titles_string = ""
    i=1
    for headline in headlines:
        titles_string += "Headline {}".format(i) + headline["title"] + "\n"
        i+=1
    return titles_string


# create podcast context string from podcast number
def create_podcast_context(podcast_number):
    podcast_name = "The name of the podcast is The Cybersecurity AI Daily.\n"
    podcast_number_prompt = "This is episode {} of the podcast. Today's date is {}.\n".format(podcast_number, date.today().strftime("%B %d, %Y"))
    podcast_characters =" The characters in the podcast are:\n\
        1. The host\n\
            The host of the podcast is John. Here are John's characteristics, his characteristics should be taken into account when creating the dialogue but never mentionned outloud:\n\
        John is a CISO at a large company. He has good foundational cybersecurity and computerscience knowledge, and great a understanding of businesses\n\
        2. The co-host\n\
            The co-host of the podcast is Jane. Here are Jane's characteristics,his characteristics should be taken into account when creating the dialogue but never mentionned outloud:\n\
        Jane is security auditor at a smaller cybersecurity consulting firm. She has exceptionnal cybersecurity technical knowledge, but more limited business understanding.\n"
    #TODO: add podcast dynamic between characters
    podcast_goal= "The goal of the podcast is to provide cybersecurity news to the listeners. The podcast is to be informative and factual but with a light tone.\n"
    
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
        + "Here is an example template of a podcast script, when writing the script replace the instructions between brackets with actual dialogue:\n\
            Exemple script template:\n\"\"\"" \
        + exemple_podcast_script_template \
        + "\"\"\"\n\n"

    return podcast_context

# sump up article content using gpt3.5
def summarize_article_gpt35(article_text):
    # create prompt
    prompt = "Summarize the following article:\n\"\"\"\n" + article_text + "\n\"\"\"\n"
    # generate summary
    summary = gpt35_complete(prompt)
    return summary

# create headlines to podcast prompt
# takes in headlines in json format and podcast episode number and returns a string that can be given to gpt4
def create_headlines_to_podcast_prompt(selected_headlines, podcast_number):
    # Try to follow best practices: https://help.openai.com/en/articles/6654000-best-practices-for-prompt-engineering-with-openai-api

    # create prompt with all the articles content
    articles_string = "Here are the articles you will be covering:\n"
    for headline_index, headline in enumerate(selected_headlines):
        articles_string += "Headline " + str(headline_index+1) + ": " + headline["title"] + "\n"
        for link_index, link in enumerate(headline["links"]):
            article_text = extract_text_from_url(link)
            summarized_article_text = summarize_article_gpt35(article_text)
            articles_string += "Link " + str(link_index+1) + ": " + link + "\n"
            #articles_string += "Content of link:\n\"\"\"\n" + article_text + "\n\"\"\"\n"
            articles_string += "Summary of link content:\n\"\"\"\n" + summarized_article_text + "\n\"\"\"\n"

     
    # replace with gpt4 generated prompts
    task_prompt = "You will be given a list of headlines and the content of the articles they correspond to.\
Your task is to write a podcast script that covers all the articles. The script must include an introduction,\
transitions between articles, and a conclusion.\n"

    music_prompt = "Please indicate transitions between articles with #transition, and mark the end of the introduction with #jingle. Place these markers on new lines, with only the marker on the line.\
For example, in between the introduction and the first headline:\n\
\"\"\"\n\
John: That's right, Jane. So, let's dive right into our first headline.\n\
#jingle\n\
Jane: Today, we're looking into ...\n\
\"\"\"\n"
                #IMPORTANT: keep at least a sample dialogue otherwise the model will not dialogue
   
    format_prompt = "Your script should be for a single episode, with a duration between 5 and 10 minutes.\
This equates to approximately 600 to 900 words. Make sure the content is engaging and informative. Make the characters exchange 3 to 5 times on each subject.\
Example dialogue format for 1 exchange:\n\
\"\"\"\n\
John:[introduces the topic]\n\
Jane:[gives technical details]\n\
John:[asks a question on the details]\n\
Jane:[answers the question]\n\
John:[gives business impact and sums up the topic]\n\
\"\"\"\n"

    # create context using podcast number
    podcast_context = create_podcast_context(podcast_number)
    # create full prompt
    full_prompt = task_prompt + podcast_context + music_prompt + format_prompt + articles_string
    return full_prompt

# function that takes in headlines in json format and uses gpt4 to generate a full podcast script in 1 go
def headlines_to_podcast_script_gpt4(selected_headlines, podcast_number):
    full_prompt = create_headlines_to_podcast_prompt(selected_headlines, podcast_number)
    #get the number of headlines
    n_headlines = len(selected_headlines)
    # generate podcast script
    # TODO: trying self healing gpt4
    podcast_script, error = gpt_complete_until_format(full_prompt, higher_order_validate_podcast(n_headlines=n_headlines), debug=True)
    #podcast_script = gpt4_complete(full_prompt)
    return podcast_script

# function of higher order that returns validate podcast_script with the rights parameters
def higher_order_validate_podcast(n_headlines):
    def wrapper(script):
        return validate_podcast_script_format(script, n_headlines)
    return wrapper

# function that takes in a podcast script and sees if it matches the format
def validate_podcast_script_format(podcast_script, n_headlines):
    # prompt that will be given to gpt for validation
    validation_prompt=""
    # check if all non blank lines start with a character name or a music marker
    for line in podcast_script.splitlines():
        if line.strip() != "":
            if not line.startswith("#") and not line.startswith("John:") and not line.startswith("Jane:"):
                validation_prompt += "FAIL. The line \"" + line + "\" does not start with a character name or a music marker.\n"
                return False, validation_prompt
    # passed lines start
    validation_prompt += "OK. All lines start with a character name or a music marker.\n"

    # check if transition is equal to the number of headlines
    n_transitions = 0
    for line in podcast_script.splitlines():
        if line.strip() == "#transition":
            n_transitions += 1
    if n_transitions != n_headlines :
        validation_prompt += "FAIL. The number of transitions is not equal to the number of headlines1. There must be a transition between every headline, and between the last headline and the transition\n"
        return False, validation_prompt
    # passed transition check
    validation_prompt += "OK. The number of transitions is equal to the number of headlines.\n"

    # there must be a single jingle at the beginning, after the introduction
    # check that jingle is the first sound effect
    for line in podcast_script.splitlines():
        # if the line is not a sound effect, continue
        if not line.startswith("#"):
            continue
        # if the line is a sound effect, check if it is a jingle
        if line.strip() == "#jingle":
            # if it is a jingle, break
            break
        else:
            # if it is not a jingle, fail
            validation_prompt += "FAIL. The first sound effect is not a jingle.\n"
            return False, validation_prompt
    # passed jingle check
    validation_prompt += "OK. The first sound effect is a jingle.\n"

    # There must be a single jingle
    n_jingles = 0
    for line in podcast_script.splitlines():
        if line.strip() == "#jingle":
            n_jingles += 1
    if n_jingles != 1:
        validation_prompt += "FAIL. There must be a single jingle.\n"
        return False, validation_prompt
    # passed jingle check
    validation_prompt += "OK. There is a single jingle.\n"

    # check if there is at least an average of 3 exchanges per section(in between 2 sound effects)
    n_lines= 0
    wanted_exchange = 3
    for line in podcast_script.splitlines():
        #if line is empty, continue
        if line.strip() == "":
            continue
        # if line is sound effect, continue
        if line.startswith("#"):
            continue
        # if line is dialogue(start with Person:), increment n_lines
        # TODO: don't hardcode the names
        if line.startswith("John:") or line.startswith("Jane:"):
            n_lines += 1
    # add 2 for conclusion and introduction
    average_exchange = n_lines / (n_headlines + 2)
    if (average_exchange < wanted_exchange):
        validation_prompt += "FAIL. The average number of exchanges per section is less than " + str(wanted_exchange) + ". Please add more exchanges in the dialogue.\n"
        return False, validation_prompt
    # passed average exchange check
    validation_prompt += "OK. The average number of exchanges per section is at least " + str(wanted_exchange) + ".\n"

    # debug check, verify the first line id #DEBUG
    #TODO: remove this check
    if not podcast_script.splitlines()[0].startswith("#DEBUG"):
        validation_prompt += "FAIL. The first line is not #DEBUG.\n"
        return False, validation_prompt

    # all checks passed
    return True, validation_prompt


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


