from libs.dialogue_generation import *
from libs.headlines_selection import *
from libs.tts import *
from libs.audio_to_video import *
from libs.upload_podcast import *
#from libs.upload_podcast import *


# test upload
youtube = get_authenticated_service()
upload_video_youtube(youtube, 'videos/1.mp4', 'Podcast Episode Title', 'Podcast Episode Description')
exit()

selected_headlines = select_headlines()
podcast_script = headlines_to_podcast_script_gpt4(selected_headlines)

print(podcast_script)

# debug with script only
parsed_dialogue = parse_dialogue(podcast_script)
print(parsed_dialogue)
#podcast_audio = podcast_script_to_audio(podcast_script)

# audio to video

# notes improve script:
# no jingle at the end