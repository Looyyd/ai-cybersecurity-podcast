from moviepy.editor import *



def audio_to_video(audio_path, image_path, output_path):
    # Load the image and set the duration
    image_clip = ImageClip(image_path)

    # Load the audio file
    audio_clip = AudioFileClip(audio_path)

    # Set the image duration to the audio duration
    image_clip = image_clip.set_duration(audio_clip.duration)

    # Set the audio of the image clip to the audio file
    final_clip = image_clip.set_audio(audio_clip)

    # Write the final clip to an MP4 video file
    final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
