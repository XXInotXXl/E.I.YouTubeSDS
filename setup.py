from cx_Freeze import setup, Executable

base = None

setup(
    name="E.I.YouTubeSDS",
    version="1.0",
    executables=[Executable("E.I.YouTubeDS.py", base=base, icon="icon.ico")]
)
