from libs.dialogue_generation import *
from libs.headlines_selection import *
from libs.tts import *
from libs.audio_to_video import *
from libs.upload_podcast import *
from libs.file_manipulation import *
import json
import argparse
#from libs.upload_podcast import *



# select headlines and put them in a file
def create_headlines_file(podcast_number):
    selected_headlines = select_headlines()
    file_path="podcast/headlines{}.json".format(podcast_number)
    export_json_to_file(selected_headlines, file_path)
    print("Headlines file created at {}".format(file_path))

# create the podcast script from the headlines file
def create_podcast_script(podcast_number):
    selected_headlines = import_json_from_file("podcast/headlines{}.json".format(podcast_number))
    podcast_script = headlines_to_podcast_script_gpt4(selected_headlines, podcast_number)
    
    file_path="podcast/script{}.txt".format(podcast_number)
    export_string_to_file(podcast_script, file_path)
    print("Podcast script created at {}".format(file_path))

# create the audio files from the podcast script file
def create_podcast_audio(podcast_number):
    podcast_script = import_string_from_file("podcast/script{}.txt".format(podcast_number))
    parsed_dialogue = parse_dialogue(podcast_script)
    # TODO: add path to audio files
    file_path="podcast"
    podcast_script_to_audio(podcast_script, podcast_number, file_path=file_path)
    print("Audio files created in {}".format(file_path))

# function to upload audio files
def upload_audio_files(podcast_number):
    #upload_audio(podcast_number)
    return


def main(episode_number, step):
    print(f"Episode number: {episode_number}")
    print(f"Step: {step}")

    if step == 1:
        create_headlines_file(episode_number)
    elif step == 2:
        create_podcast_script(episode_number)
    elif step == 3:
        create_podcast_audio(episode_number, file_path="podcast")
    elif step == 4:
        upload_audio_files(episode_number)
    else :
        print("Invalid step number.")
        exit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process command line arguments.")
    parser.add_argument("--episode_number", type=int, required=True, help="Episode number.")
    parser.add_argument("--step", type=int, required=True, help="Step number.")

    args = parser.parse_args()

    main(args.episode_number, args.step)