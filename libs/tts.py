import requests
import os
import re
import shutil
from pydub import AudioSegment

# CONSTANTS
elevenLabsKey = os.getenv("ELEVENLABS_API_KEY")
eleven_domain = "https://api.elevenlabs.io/"
# voice id of Male host and female host
male_id="5AnsleRivsVBr8bi8Zh3"
female_id="VtBQYxE6jqCxqZr2GUQO"

#dialogue = "John: Welcome to the Cybersecurity Cybernews Podcast. Jane: That's right John. John: That's right Jane. Jane: Absolutely John!"
# read the dialogue from the file archives/finaldraft.txt

def read_dialogue_from_file(podcast_number):
    with open("archives/" + podcast_number + "/finaldraft.txt", "r") as text_file:
        dialogue = text_file.read()
    return dialogue

def parse_dialogue(dialogue):
    dialogue_list = []
    lines = re.split(r'(?<=[.!?])\s+(?=[A-Za-z#]+:)', dialogue)

    for line in lines:
        person, text = line.split(':', 1)
        person = person.strip()

        if person.startswith("#"):
            dialogue_list.append({"person": person[1:], "dialogue": ""})
        else:
            dialogue_list.append({"person": person, "dialogue": text.strip()})
    
    return dialogue_list

def tts(text, person="John"):
    request_body={
    "text": text,
    "voice_settings": {
        "stability": 0,
        "similarity_boost": 0
    }
    }
    male_api =  eleven_domain+"v1/text-to-speech/"+ male_id
    female_api =  eleven_domain+"v1/text-to-speech/"+ female_id

    if(person=="John"):
        api = male_api
    elif(person=="Jane"):
        api = female_api
    else:
        raise ValueError("Person must be John or Jane")
    # POST with request body to get mpeg audio file
    response = requests.post(api, headers={"xi-api-key": elevenLabsKey}, json=request_body)
    return response

def concatenate_audio_files(input_folder, output_file):
    audio_files = sorted(os.listdir(input_folder), key=lambda x: int(x.split('.')[0]))

    combined_audio = AudioSegment.empty()

    for audio_file in audio_files:
        audio_path = os.path.join(input_folder, audio_file)
        audio = AudioSegment.from_mp3(audio_path)
        combined_audio += audio

    combined_audio.export(output_file, format="mp3")

# archives the used audio files
def move_audio_files(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    audio_files = sorted(os.listdir(input_folder), key=lambda x: int(x.split('.')[0]))

    for audio_file in audio_files:
        input_path = os.path.join(input_folder, audio_file)
        output_path = os.path.join(output_folder, audio_file)

        if os.path.isfile(input_path):
            shutil.move(input_path, output_path)

# function that takes audio lines and makes them into the podcast audio
def audio_files_to_podcast(podcast_number):
    input_folder = "audio"
    output_file = "podcasts/{}.mp3".format(podcast_number)
    concatenate_audio_files(input_folder, output_file)
    # archive the audio files
    move_audio_files(input_folder, "archive/audio_archive{}".format(podcast_number))


# function that gets the list of available voices from the api
def get_voices():
    # get voices from api, put key into header xi-api-key
    # TODO: add error handling
    response = requests.get(eleven_domain + "v1/voices", headers={"xi-api-key": elevenLabsKey})
    voices = response.json()["voices"]
    for voice in voices:
        print(voice["voice_id"], voice["name"])
    return voices

# function that takes in an array of dialogue lines and returns the audio files
def parsed_dialogue_to_audio_files(parsed_dialogue):
    i=0
    for line in parsed_dialogue:
        i = i+1
        # if person is sound effect, add sound effect from assets folder
        if line["person"] == "transition":
            shutil.copy("assets/transition.mp3", "audio/{}.mp3".format(i))
            continue
        elif line["person"] == "jingle":
            shutil.copy("assets/jingle.mp3", "audio/{}.mp3".format(i))
            continue
        #if line is not sound effect, request the api for the audio
        else:
            # request the api for each person
            response = tts(line["dialogue"], line["person"])
            print(response.headers["Content-Type"])
            print(response)
            assert response.headers["Content-Type"] == "audio/mpeg"
            with open("audio/{}.mp3".format(i), "wb") as file:
                file.write(response.content)

# function that takes the gpt4 dialogue output and makes it into the podcast audio
def podcast_script_to_audio(script, podcast_number):
    #parse dialogue into array of json objects
    parsed_dialogue = parse_dialogue(script)
    #print(parsed_dialogue)
    # make the audio files using eleven labs api
    parsed_dialogue_to_audio_files(parsed_dialogue)
    # make the podcast by joining audio files together
    audio_files_to_podcast(podcast_number)
