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


if __name__ == '__main__':
    response = authorize_upload('test.mp3')
    print(response.json())
    json_response = response.json()
    upload_url = json_response['data']['attributes']['upload_url']
    audio_url = json_response['data']['attributes']['audio_url']
    print(upload_url)
    print(audio_url)


