import requests
import os
from libs.file_manipulation import import_bytes_from_file


# API DOC: https://developers.transistor.fm/#episodes
TRANSISTOR_API_KEY = os.getenv("TRANSISTOR_API_KEY")


# Authorize an episode audio upload
# returns an url to upload the audio to
def authorize_upload(filename):
    url = 'https://api.transistor.fm/v1/episodes/authorize_upload'
    headers = {'x-api-key': TRANSISTOR_API_KEY}
    params = {'filename': filename}

    response = requests.get(url, headers=headers, params=params)
    return response

# upload audio to the url returned by authorize_upload
def upload_audio(upload_url, file_path):
    headers = {"Content-Type": "audio/mpeg"}
    data = import_bytes_from_file(file_path)
    #TODO: test file manipulation
    response = requests.put(upload_url, headers=headers, data=data)

    return response

# create a new episode
def create_episode(show_id, title, description, audio_url, number=1, keywords=""):
    url = "https://api.transistor.fm/v1/episodes"
    headers = {"x-api-key": TRANSISTOR_API_KEY}

    # replace newlines in description with html linebreaks <br> and \n to fit all formats
    description = description.replace("\n", "<br>\n")

    data = {
        "episode[show_id]": show_id,
        "episode[title]": title,
        "episode[number]": number,
        "episode[description]": description,
        "episode[audio_url]": audio_url,
        "episode[keywords]": keywords
    }
    
    response = requests.post(url, headers=headers, data=data)
    
    if response.status_code == 201:
        return response.json()
    else:
        raise ValueError(f"Failed to create episode, status code: {response.status_code}, message: {response.text}")


# function to publish an episode
def publish_episode_transitor(episode_id, status="published"):
    url = "https://api.transistor.fm/v1/episodes/{}/publish".format(episode_id)
    headers = {"x-api-key": TRANSISTOR_API_KEY}
    data = {
        "episode[status]": status,
    }
    response = requests.patch(url, headers=headers, data=data)
    return response

def audio_file_to_podcast(path_to_audio, title, description, podcast_number, keywords="", show_id=str(40581), file_env="OS"):
    filename = os.path.basename(path_to_audio)
    response = authorize_upload(filename=filename)
    json_response = response.json()
    upload_url = json_response['data']['attributes']['upload_url']
    audio_url = json_response['data']['attributes']['audio_url']

    response = upload_audio(upload_url, path_to_audio)

    response = create_episode(show_id, title, description, audio_url, number=podcast_number, keywords=keywords)
    episode_id = response["data"]["id"]
    return response

if __name__ == '__main__':
    response = authorize_upload('test.mp3')
    print(response.json())
    json_response = response.json()
    upload_url = json_response['data']['attributes']['upload_url']
    audio_url = json_response['data']['attributes']['audio_url']
    print(upload_url)
    print(audio_url)

    # TODO: add it to function
    podcast_number = 1
    file_path = "podcast/podcast{}.mp3".format(podcast_number)
    response = upload_audio(upload_url, file_path)
    print(response)

    show_id = str(40581)
    title = "test"
    description = "test"
    response = create_episode(show_id, title, description, audio_url, number=podcast_number)
    print(response)
    # TODO: add description, transcript
    episode_id = response["data"]["id"]
    response = publish_episode_transitor(episode_id)




