import os
import shutil

from love2d_helper import get_game_data, unpack, repack
from patcher import patch_game

if __name__ == "__main__":
    exe = input("Balatro.exe: ")
    with open("game.love", "wb") as love_file:
        love_file.write(get_game_data(exe))
    unpack("game.love")
    patch_game("game")
    os.remove("game.love")
    repack("game")
    shutil.rmtree("game")
