from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
import google.auth

def get_authenticated_service():
    # Replace with your own OAuth 2.0 client ID and secret
    credentials = Credentials.from_authorized_user_file('secrets/client_secret.json', scopes=['https://www.googleapis.com/auth/youtube.upload'])
    return build('youtube', 'v3', credentials=credentials)

def upload_video_youtube(youtube, file_path, title, description):
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'categoryId': '22'
        },
        'status': {
            'privacyStatus': 'public'
        }
    }

    with open(file_path, 'rb') as video_file:
        request = youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=google.auth.transport.requests.MediaFileUpload(video_file, chunksize=-1, resumable=True)
        )
        response = request.execute()

    print(f'Video was uploaded with video ID "{response["id"]}" and title "{response["snippet"]["title"]}".')



if __name__ == '__main__':
    youtube = get_authenticated_service()
    upload_video_youtube(youtube, 'path/to/your/video.mp4', 'Podcast Episode Title', 'Podcast Episode Description')
