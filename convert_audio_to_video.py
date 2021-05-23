from moviepy.editor import *


def convert():
    audio = AudioFileClip('song.mp4')
    print("Audio duration: ", audio.duration)
    image = ImageClip('image.jpg').set_duration(audio.duration)

    video = image.set_audio(audio)
    print("Video duration: ", video.duration)
    outfile = "converted.mp4"

    video.write_videofile(outfile,
                          fps=1,
                          codec='libx264',
                          audio_codec='aac',
                          temp_audiofile='temp-audio.m4a',
                          remove_temp=True, threads=10, logger='bar')
