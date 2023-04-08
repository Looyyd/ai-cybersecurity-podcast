import requests
import os


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
    with open(file_path, "rb") as audio_file:
        response = requests.put(upload_url, headers=headers, data=audio_file)

    return response

# create a new episode
def create_episode(show_id, title, summary, audio_url, number=1, description=""):
    url = "https://api.transistor.fm/v1/episodes"
    headers = {"x-api-key": TRANSISTOR_API_KEY}
    data = {
        "episode[show_id]": show_id,
        "episode[title]": title,
        "episode[summary]": summary,
        "episode[number]": number,
        "episode[description]": description,
        "episode[audio_url]": audio_url
    }
    
    response = requests.post(url, headers=headers, data=data)
    
    if response.status_code == 201:
        return response.json()
    else:
        raise ValueError(f"Failed to create episode, status code: {response.status_code}, message: {response.text}")



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
    response = create_episode(show_id, "test", "test", audio_url, number=podcast_number)
    print(response)



