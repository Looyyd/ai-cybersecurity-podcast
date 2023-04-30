import datetime
import argparse
from libs.text_generation import create_podcast_title, create_podcast_description, create_podcast_keywords, headlines_to_podcast_script_gpt4
from libs.headlines_selection import select_headlines
from libs.tts import podcast_script_to_audio
from libs.upload_podcast import audio_file_to_podcast, publish_episode_transitor
from libs.file_manipulation import export_json_to_file, import_json_from_file, export_string_to_file, import_string_from_file, zip_and_delete_files



# select headlines and put them in a file
def create_headlines_file(podcast_number, n_headlines=4, days=1, file_env="OS"):
    selected_headlines = select_headlines(n_headlines, days)
    file_path=f"podcasts/podcast{podcast_number}/headlines.json"
    
    # TODO: better error handling
    #try export print error if fails
    try:
        export_json_to_file(selected_headlines, file_path, file_env=file_env)
    except Exception as e:
        print("Error: ", e)
        return
    print(f"Headlines file created at {file_path}")
    # TODO: return something useful?

# create the podcast script from the headlines file
def create_podcast_script(podcast_number, file_env="OS"):
    selected_headlines = import_json_from_file(f"podcasts/podcast{podcast_number}/headlines.json", file_env=file_env)
    podcast_script = headlines_to_podcast_script_gpt4(selected_headlines, podcast_number)
    
    file_path=f"podcasts/podcast{podcast_number}/script.txt"
    export_string_to_file(podcast_script, file_path, file_env=file_env)
    print(f"Podcast script created at {file_path}")

# create the audio files from the podcast script file
def create_podcast_audio(podcast_number, file_path="podcasts", file_env="OS"):
    podcast_script = import_string_from_file(f"{file_path}/podcast{podcast_number}/script.txt", file_env=file_env)
    #parsed_dialogue = parse_dialogue(podcast_script)
    # TODO: add path to audio files
    podcast_script_to_audio(podcast_script, podcast_number,file_env=file_env)
    print(f"Audio files created in {file_path}/podcast{podcast_number}/audio.mp3")

# create a podcast draft on transistor.fm using the audio files and metadata
def create_podcast_draft(podcast_number, file_env="OS"):
    file_path=f"podcasts/podcast{podcast_number}/audio.mp3"

    # get title and description from files
    title = import_string_from_file(f"podcasts/podcast{podcast_number}/title.txt", file_env=file_env)
    description = import_string_from_file(f"podcasts/podcast{podcast_number}/description.txt", file_env=file_env)
    keywords = import_string_from_file(f"podcasts/podcast{podcast_number}/keywords.txt", file_env=file_env)

    show_id = str(40581)
    response = audio_file_to_podcast(file_path, title, description, podcast_number=podcast_number, keywords=keywords, show_id=show_id, file_env=file_env)
    # archive episode id in text file for next step
    episode_id = response["data"]["id"]
    episode_id_path = f"podcasts/podcast{podcast_number}/episode_id.txt"
    export_string_to_file(episode_id, episode_id_path, file_env=file_env)
    print("Episode draft created in transistor.fm")
    return response

# archive all podcast files, final step
def archive_podcast_files(episode_number, file_env="OS"):
    # put every file from podcast folder in a zip file and into archive folder
    zip_path = f"podcasts/podcast{episode_number}/archive.zip"
    zip_and_delete_files(f"podcasts/podcast{episode_number}/", zip_path, file_env=file_env)
    print(f"Podcast files archived in archive folder: {zip_path}")

# publish episode on transistor.fm
def publish_episode(episode_number, file_env="OS"):
    # get episode id from text file
    episode_id_path = f"podcasts/podcast{episode_number}/episode_id.txt"
    episode_id = import_string_from_file(episode_id_path, file_env=file_env)

    response = publish_episode_transitor(episode_id=episode_id)
    # increment episode number in text file
    last_episode_n = import_string_from_file("podcasts/last_episode_n.txt", file_env=file_env)
    last_episode_n = int(last_episode_n) + 1
    export_string_to_file(str(last_episode_n), "podcasts/last_episode_n.txt", file_env=file_env)

    print(f"Episode published on Transistor, last episode number: {last_episode_n}")
    return response

# generate podcast title, description and keywords
def generate_metadata(episode_number, file_env="OS"):
    # get script from file
    script = import_string_from_file(f"podcasts/podcast{episode_number}/script.txt", file_env=file_env)

    # get headlines from file
    headlines = import_json_from_file(f"podcasts/podcast{episode_number}/headlines.json", file_env=file_env)

    podcast_title = create_podcast_title(episode_number, script)
    podcast_description = create_podcast_description(episode_number, script, headlines)
    podcast_keywords = create_podcast_keywords(episode_number, script)


    # write title and description and keywords to files
    title_path = f"podcasts/podcast{episode_number}/title.txt"
    description_path = f"podcasts/podcast{episode_number}/description.txt"
    keywords_path = f"podcasts/podcast{episode_number}/keywords.txt"

    export_string_to_file(podcast_title, title_path, file_env=file_env)
    export_string_to_file(podcast_description, description_path, file_env=file_env)
    export_string_to_file(podcast_keywords, keywords_path, file_env=file_env)

    print(f"Wrote title, description and keywords to files: {title_path} , {description_path} and {keywords_path}")
    return podcast_title, podcast_description


def main(episode_number, step, days=1, file_env="OS", debug=False):
    print(f"Episode number: {episode_number}")
    print(f"Step: {step}")
    n_headlines = 4

    if debug:
        # run 4 steps
        create_headlines_file(episode_number, n_headlines=n_headlines, days=days, file_env=file_env)
        create_podcast_script(episode_number, file_env=file_env)
        create_podcast_audio(episode_number, file_env=file_env)
        generate_metadata(episode_number, file_env=file_env)
        create_podcast_draft(episode_number, file_env=file_env)
    elif step == 1:
        # select headlines and put them in a file
        create_headlines_file(episode_number, n_headlines=n_headlines, days=days, file_env=file_env)
    elif step == 2:
        # create the podcast script from the headlines file
        create_podcast_script(episode_number, file_env=file_env)
    elif step == 3:
        # create the audio files from the podcast script file, and generate metadata(description, title, keywords)
        create_podcast_audio(episode_number, file_env=file_env)
        generate_metadata(episode_number, file_env=file_env)
    elif step == 4:
        # create the podcast draft on transistor.fm
        create_podcast_draft(episode_number, file_env=file_env)
    elif step == 5:
        # publish episode on transistor.fm
        publish_episode(episode_number, file_env=file_env)
        #archive_podcast_files(episode_number=episode_number, file_env=file_env)
    elif step==-1:
        # run all steps
        create_headlines_file(episode_number, n_headlines=n_headlines, days=days, file_env=file_env)
        create_podcast_script(episode_number, file_env=file_env)
        create_podcast_audio(episode_number, file_env=file_env)
        generate_metadata(episode_number, file_env=file_env)
        create_podcast_draft(episode_number, file_env=file_env)
        publish_episode(episode_number, file_env=file_env)
        #archive_podcast_files(episode_number=episode_number, file_env=file_env)
    else :
        print("Invalid step number.")
        exit()

if __name__ == "__main__":
    # default days is 3 if monday, 1 if other day
    if datetime.datetime.today().weekday() == 0:
        days = 3
    else:
        days = 1
    parser = argparse.ArgumentParser(description="Process command line arguments.")
    parser.add_argument("--episode_number", type=int, required=False, help="Episode number.", default=-1)
    parser.add_argument("--step", type=int, required=False, help="Step number.", default=-1)
    parser.add_argument("--days", type=int, required=False, help="Number of days to look back for headlines. (default: 1,except 3 on mondays)", default=days)
    parser.add_argument("--file_env", type=str, required=False, help="File environment variable. (default: OS, can be OS or AZURE)", default="OS")
    parser.add_argument("--debug", action="store_true", default=False, help="Enable debug mode, this will run all steps but not publish the episode.")


    args = parser.parse_args()

    # get last published episode number from file podcasts/last_episode.txt
    #if episode number is not specified, use last episode number + 1
    if args.episode_number == -1:
        last_episode = import_string_from_file("podcasts/last_episode_n.txt", file_env=args.file_env)
        args.episode_number = int(last_episode) + 1

    main(args.episode_number, args.step, days=args.days, file_env=args.file_env, debug=args.debug)