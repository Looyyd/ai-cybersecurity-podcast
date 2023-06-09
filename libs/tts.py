import requests
import os
import re
import shutil
from libs.file_manipulation import *

# CONSTANTS
elevenLabsKey = os.getenv("ELEVENLABS_API_KEY")
eleven_domain = "https://api.elevenlabs.io/"
# voice id of Male host and female host
male_id="5AnsleRivsVBr8bi8Zh3"
female_id="VtBQYxE6jqCxqZr2GUQO"


def read_dialogue_from_file(podcast_number):
    with open("archives/" + podcast_number + "/finaldraft.txt", "r") as text_file:
        dialogue = text_file.read()
    return dialogue

def parse_dialogue(dialogue):
    dialogue_list = []
    lines=dialogue.splitlines()

    for line in lines:
        # if line is empty, skip
        if len(line) <= 1:
            continue
        #if first letter is #, it's a jingle or transition
        elif line.startswith("#"):
            # take the first word and append as a person
            sound_effect = line.split(' ', 1)[0]
            dialogue_list.append({"person": sound_effect, "dialogue": ""})
            continue
        else:
            # try to split, if it fails it's because there's no person in front of dialogue, let's make john speak then
            try:
                person, text = line.split(':', 1)
                person = person.strip()
            except ValueError:
                person = "John"
                text = line
            except Exception as e:
                raise e
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




# function that takes audio lines and makes them into the podcast audio
def audio_files_to_podcast(podcast_number, file_path_audio_input, file_path_output, file_env="OS"):
    concatenate_audio_files(file_path_audio_input, file_path_output, file_env=file_env)


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
def parsed_dialogue_to_audio_files(parsed_dialogue, file_path, file_env="OS"):
    i=0
    create_directory_if_not_exists(file_path, file_env=file_env)
    for line in parsed_dialogue:
        i = i+1
        audio_path = "{}/{:03d}.mp3".format(file_path, i)
        # if person is sound effect, add sound effect from assets folder
        if line["person"] == "#transition":
            copy_file("assets/transition.mp3", audio_path, file_env=file_env)
            continue
        elif line["person"] == "#jingle":
            copy_file("assets/jingle.mp3", audio_path, file_env=file_env)
            continue
        #if line is not sound effect, request the api for the audio
        else:
            # request the api for each person
            for attempt in range(3):
                response = tts(line["dialogue"], line["person"])
                # if content type is not audio/mpeg, raise error
                if response.headers["Content-Type"] != "audio/mpeg":
                    # if something went wrong,  try again
                    if attempt < 2:
                        continue
                    else:
                        print(response.json())
                        raise ValueError("Content type is not audio/mpeg")
                else:
                    # if everything went well, break
                    break
            #with open(audio_path, "wb") as file:
                #file.write(response.content)
            # TODO: does this work with audio?
            export_bytes_to_file(response.content, audio_path, file_env=file_env)

# function that takes the gpt4 dialogue output and makes it into the podcast audio
def podcast_script_to_audio(script, podcast_number, file_env="OS"):
    #parse dialogue into array of json objects
    parsed_dialogue = parse_dialogue(script)
    file_path_parts="podcasts/podcast{}/audio".format(podcast_number)
    file_path_final="podcasts/podcast{}/audio.mp3".format(podcast_number)
    # make the audio files using eleven labs api
    parsed_dialogue_to_audio_files(parsed_dialogue, file_path=file_path_parts, file_env=file_env)
    # make the podcast by joining audio files together
    audio_files_to_podcast(podcast_number, file_path_parts, file_path_final, file_env=file_env)

