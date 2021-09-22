import os
import time
from datetime import datetime
from tkinter import Tk, filedialog

import youtube_dl
from mutagen.easyid3 import EasyID3
from pydub import AudioSegment

TITLE = """
------------------------------
  Youtube Download and Slice
------------------------------
"""

MENU = """
Type in option number and press Enter

1. Download Video
2. Download MP3
3. Download Video and Slice by Chapters
4. Download MP3 and Slice by Chapters
"""

ROOT = "Download/"

FOLDER = datetime.now().strftime("%Y%m%d%H%M%S") + "/"


def select_file(title="Select File", defaultextension="", filetypes=((),)):
    root = Tk()
    root.overrideredirect(True)
    root.attributes("-alpha", 0)
    file_path = filedialog.askopenfilename(title=title, defaultextension=defaultextension, filetypes=filetypes)
    root.destroy()
    return file_path


def make_path(file: dict):
    return ROOT + FOLDER + file['title'] + '.' + file['ext']


def write_title(file: dict):
    path = make_path(file)
    if "mp3" in path:
        print(path)
        write_metadata(path, file['title'])


def downloads(url, keepvideo=False):
    def __ext(value):
        if keepvideo:
            return value
        return 'mp3'

    files = []
    options = {
        True: {
            'outtmpl': ROOT + FOLDER + '%(title)s.%(ext)s',
            'format': 'best'
        },
        False: {
            'audioformat': 'mp3',
            'outtmpl': ROOT + FOLDER + '%(title)s.%(ext)s',
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'keepvideo': False,
        }
    }

    with youtube_dl.YoutubeDL(options[keepvideo]) as ydl:
        metadata = ydl.extract_info(url, download=True)
        if "playlist" in url:
            for video in metadata['entries']:
                files.append({
                    'title': video.get('title'),
                    'ext': __ext(video.get('ext')),
                    'chapters': video.get('chapters')
                })
        else:
            files.append({
                'title': metadata.get('title'),
                'ext': __ext(metadata.get('ext')),
                'chapters': metadata.get('chapters')
            })
    for file in files:
        try:
            write_title(file)
        except:
            continue
    return files


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


def task(urls, keepvideo: bool, _slice: bool):
    try:
        for url in urls:
            temp = downloads(url, keepvideo)
            for file in temp:
                if _slice:
                    slice(make_path(file), file['chapters'])
    except:
        return


def process(urls, opt):
    if opt == "1":
        task(urls, keepvideo=True, _slice=False)
    elif opt == "2":
        task(urls, keepvideo=False, _slice=False)
    elif opt == '3':
        task(urls, keepvideo=True, _slice=True)
    elif opt == '4':
        task(urls, keepvideo=False, _slice=True)
    elif opt == '88':
        print("""老爸老妈我爱你们哟~""")


class Home:
    def valid(self, opt: str):
        try:
            opt = int(opt)
            if 1 <= opt <= 4 or opt == 88:
                return True
            return False
        except:
            return False

    def option(self):
        return input("Option: ")

    def read(self):
        print("""
Please copy and paste all your urls without any blank lines.
If you wish to use urls placed in a txt file, enter "txt".

Create a new line (press "Enter") to continue.
-------------------------------------------------------------""")
        lis = []
        while True:
            _input = input()
            if _input:
                lis.append(_input)
            else:
                break
        if "txt" in lis:
            with open(select_file(title="Select Slice Info", defaultextension=".txt",
                                  filetypes=(("Text Document", "*.txt"),)),
                      "r") as file:
                music_url_list = file.read().splitlines()
            return [i for i in music_url_list if i]
        return lis

    def main(self):
        print(TITLE)
        print(MENU)
        opt = self.option()
        while True:
            if self.valid(opt):
                urls = self.read()
                process(urls, opt)
                break
            else:
                print("""
        ------------------------
          Bad choice!
          Please select again.
        ------------------------
        """)
                opt = self.option()
        time.sleep(1)
        print()
        input("""Press "Enter" to leave.\n""")


if __name__ == '__main__':
    Home().main()
