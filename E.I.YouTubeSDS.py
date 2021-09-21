import os
from datetime import datetime
from tkinter import Tk, filedialog

import youtube_dl
from mutagen.easyid3 import EasyID3
from pydub import AudioSegment

Title = """
---------------------------------------
Youtube Soundtrack Download n Slice
---------------------------------------
"""

Menu = """Note: You need to store your URLs in a txt File

Type in option number and press Enter

1. Download Only
2. Download MP3
3. Download Slice by Chapters
"""

Folder = "E.I.YoutubeSDS Download/"

_slice = False
_mp3 = False
parent = datetime.now().strftime("%Y%m%d%H%M%S")


def select_file(title="Select File", defaultextension="", filetypes=((),)):
    root = Tk()
    root.overrideredirect(True)
    root.attributes("-alpha", 0)
    file_path = filedialog.askopenfilename(title=title, defaultextension=defaultextension, filetypes=filetypes)
    root.destroy()
    return file_path


def download(video_url, parent=None):
    video_info = youtube_dl.YoutubeDL().extract_info(url=video_url, download=False)
    if parent:
        filename = "{}{}{}.mp3".format(Folder, parent + "/", video_info['title'])
    else:
        filename = "{}{}.mp3".format(Folder, video_info['title'])
    try:
        chapters = video_info["chapters"]
    except:
        chapters = None
    options = {
        'audioformat': 'mp3',
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'keepvideo': False,
        'outtmpl': filename,
    }
    with youtube_dl.YoutubeDL(options) as ydl:
        ydl.download([video_info['webpage_url']])

    return filename, chapters


def slice(filename, chapters):
    if chapters:
        song = AudioSegment.from_file(filename)
        max_lens = len(song)
        for chapter in chapters:
            start_time, end_time, title = int(chapter["start_time"] * 1000), int(chapter["end_time"] * 1000), \
                                          chapter[
                                              "title"]
            if end_time > max_lens: end_time = max_lens
            parent_name = os.path.basename(filename)
            parent_folder = filename.replace(parent_name, "")
            parent_name.replace(".mp3", "")
            output_song = "{}{} - {}.mp3".format(parent_folder, parent_name, title)
            song[start_time:end_time].export(output_song, format="mp3")
            write_metadata(output_song, title=title)
        os.remove(filename)


def write_metadata(filename, title="", artist="", album="", composer=""):
    audio = EasyID3(filename)
    audio['title'] = title
    audio['artist'] = artist
    audio['album'] = album
    audio['composer'] = composer
    audio.save()


def task(music_url, _slice: bool, _mp3: bool, parent=None):
    try:
        filename, chapters = download(music_url, parent=parent)
        if _slice:
            slice(filename, chapters)
        else:
            if _mp3:
                AudioSegment.from_file(filename).export(filename, format="mp3")
                song_name = os.path.splitext(os.path.basename(filename))[0]
                write_metadata(filename, title=song_name)
    except:
        print("Something happened...")


def process(_slice: bool, _mp3: bool):
    with open(select_file(title="Select Slice Info", defaultextension=".txt", filetypes=(("Text Document", "*.txt"),)),
              "r") as file:
        music_url_list = file.read().splitlines()
    music_url_list = [i for i in music_url_list if i]
    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
    for music_url in music_url_list:
        task(music_url, _slice, _mp3, current_time)
    print("""
=============================================
  Download completed
  Go check folder [E.I.YouTubeSDS Download]
=============================================
""")


def home():
    print(Title)
    print(Menu)
    while True:
        try:
            option = int(input("Option: "))
            print()
            if option == 1:
                process(_slice=False, _mp3=False)
            elif option == 2:
                process(_slice=False, _mp3=True)
            elif option == 3:
                process(_slice=True, _mp3=True)
            elif option == 88:
                print("""老爸老妈我爱你们哟~""")
                break
            else:
                raise Exception
            input("Press Enter to continue\n")
            print("===========================================")
        except:
            print("""
========================
  Bad choice!
  Please select again.
========================
""")
            continue


if __name__ == '__main__':
    home()
