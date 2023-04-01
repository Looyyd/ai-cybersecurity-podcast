from libs.dialogue_generation import *
from libs.headlines_selection import *
from libs.tts import *
#from libs.upload_podcast import *



selected_headlines = select_headlines()
podcast_script = headlines_to_podcast_script(selected_headlines)

# debug with script only
parsed_dialogue = parse_dialogue(podcast_script)
#podcast_audio = podcast_script_to_audio(podcast_script)