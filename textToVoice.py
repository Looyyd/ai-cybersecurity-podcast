import requests
import os
import re
import shutil
from pydub import AudioSegment


dialogue = "John: Welcome to the Cybersecurity Cybernews Podcast. Jane: That's right John. . John: That's right Jane. Jane: Absolutely John!"

def parse_dialogue(dialogue):
    dialogue_list = []
    lines = re.split(r'(?<=[.!?])\s+(?=[A-Za-z]+:)', dialogue)
    
    for line in lines:
        person, text = line.split(':', 1)
        dialogue_list.append({"person": person.strip(), "dialogue": text.strip()})
    
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


elevenLabsKey = os.getenv("ELEVENLABS_API_KEY")

eleven_domain = "https://api.elevenlabs.io/"
# get voices from api, put key into header xi-api-key
response = requests.get(eleven_domain + "v1/voices", headers={"xi-api-key": elevenLabsKey})
# TODO: add error handling

#print(response.json())

voices = response.json()["voices"]
#print(voices)

# get voices ids and names
for voice in voices:
    print(voice["voice_id"], voice["name"])

# get voice id of Male host and female host
male_id="5AnsleRivsVBr8bi8Zh3"
female_id="VtBQYxE6jqCxqZr2GUQO"

# parse dialogue into list of lines
parsed_dialogue = parse_dialogue(dialogue)

i=0
for line in parsed_dialogue:
    i = i+1
    # request the api for each person
    response = tts(line["dialogue"], line["person"])
    print(response.headers["Content-Type"])
    print(response)
    assert response.headers["Content-Type"] == "audio/mpeg"
    with open("audio/{}.mp3".format(i), "wb") as file:
        file.write(response.content)


# make the podcast
audio_files_to_podcast(1)