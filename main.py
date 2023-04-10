from libs.text_generation import *
from libs.headlines_selection import *
from libs.tts import *
from libs.audio_to_video import *
from libs.upload_podcast import *
from libs.file_manipulation import *
import json
import argparse



# select headlines and put them in a file
def create_headlines_file(podcast_number, n_headlines=4, days=1):
    selected_headlines = select_headlines(n_headlines, days)
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
def create_podcast_audio(podcast_number, file_path="podcast"):
    podcast_script = import_string_from_file("{}/script{}.txt".format(file_path, podcast_number))
    parsed_dialogue = parse_dialogue(podcast_script)
    # TODO: add path to audio files
    podcast_script_to_audio(podcast_script, podcast_number, file_path=file_path)
    print("Audio files created in {}".format(file_path))

# create a podcast draft on transistor.fm using the audio files and metadata
def create_podcast_draft(podcast_number):
    file_path="podcast/podcast{}.mp3".format(podcast_number)

    # get title and description from files
    title = import_string_from_file("podcast/title{}.txt".format(podcast_number))
    description = import_string_from_file("podcast/description{}.txt".format(podcast_number))
    keywords = import_string_from_file("podcast/keywords{}.txt".format(podcast_number))

    SHOW_ID = str(40581)
    response = audio_file_to_podcast(file_path, title, description, podcast_number=podcast_number, keywords=keywords, show_id=SHOW_ID)
    # archive episode id in text file for next step
    episode_id = response["data"]["id"]
    episode_id_path = "podcast/episode_id{}.txt".format(podcast_number)
    with open(episode_id_path, "w") as f:
        f.write(episode_id)
    print("Episode draft created in transistor.fm")
    return response

# archive all podcast files, final step
def archive_podcast_files(episode_number):
    # put every file from podcast folder in a zip file and into archive folder
    zip_path = "archive/podcast{}.zip".format(episode_number)
    zip_and_delete_files("podcast", zip_path)
    print("Podcast files archived in archive folder: {}".format(zip_path))
    return

# publish episode on transistor.fm
def publish_episode(episode_number):
    # get episode id from text file
    episode_id_path = "podcast/episode_id{}.txt".format(episode_number)
    with open(episode_id_path, "r") as f:
        episode_id = f.read()
    response = publish_episode_transitor(episode_id=episode_id)
    print("Episode published on Transistor")
    return response

# generate podcast title, description and keywords
def generate_metadata(episode_number):
    # get script from file
    script = import_string_from_file("podcast/script{}.txt".format(episode_number))

    # get headlines from file
    headlines = import_json_from_file("podcast/headlines{}.json".format(episode_number))

    podcast_title = create_podcast_title(episode_number, script)
    podcast_description = create_podcast_description(episode_number, script, headlines)
    podcast_keywords = create_podcast_keywords(episode_number, script)


    # write title and description and keywords to files
    title_path = "podcast/title{}.txt".format(episode_number)
    description_path = "podcast/description{}.txt".format(episode_number)
    keywords_path = "podcast/keywords{}.txt".format(episode_number)

    export_string_to_file(podcast_title, title_path)
    export_string_to_file(podcast_description, description_path)
    export_string_to_file(podcast_keywords, keywords_path)

    print("Wrote title, description and keywords to files: {} , {} and {}".format(title_path, description_path, keywords_path))
    return podcast_title, podcast_description


def main(episode_number, step, days=1):
    print(f"Episode number: {episode_number}")
    print(f"Step: {step}")

    if step == 1:
        # select headlines and put them in a file
        create_headlines_file(episode_number, n_headlines=4, days=days)
    elif step == 2:
        # create the podcast script from the headlines file
        create_podcast_script(episode_number)
    elif step == 3:
        # create the audio files from the podcast script file, and generate metadata(description, title, keywords)
        create_podcast_audio(episode_number, file_path="podcast")
        generate_metadata(episode_number)
    elif step == 4:
        # create the podcast draft on transistor.fm
        create_podcast_draft(episode_number)
    elif step == 5:
        # publish episode on transistor.fm
        response = publish_episode(episode_number)
        archive_podcast_files(episode_number=episode_number)
    else :
        print("Invalid step number.")
        exit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process command line arguments.")
    parser.add_argument("--episode_number", type=int, required=True, help="Episode number.")
    parser.add_argument("--step", type=int, required=True, help="Step number.")
    parser.add_argument("--days", type=int, required=False, help="Number of days to look back for headlines. (default: 1)", default=1)

    args = parser.parse_args()

    main(args.episode_number, args.step, days=args.days)