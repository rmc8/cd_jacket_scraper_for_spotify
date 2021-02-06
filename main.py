import os
import pathlib
import re
from time import sleep
from typing import List, Optional, Tuple

import PySimpleGUI as sg
import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


def sel_input_dir():
    layout = [
        [sg.Text("ディレクトリ"), sg.InputText(key="ret"),
         sg.FolderBrowse(key="dir")],
        [sg.Submit(), sg.Exit()],
    ]
    window = sg.Window("Input", layout)
    while True:
        event, values = window.read()
        if event == "Submit":
            ret = values["ret"]
            break
        elif event in (sg.WINDOW_CLOSED, "Exit"):
            ret = None
            break
    window.close()
    return ret


def get_cd_info(path: str) -> Tuple[str, str, str]:
    """
    Search to the lowest directory and return the name of the CD, the name of the artist and its file path.
    Args:
        path ([str]): File path to search
    Yields:
        [Tuple[str]]: dir_path, artist, cd_name
    """
    for root, dirs, _ in os.walk(path):
        if not dirs:
            p = pathlib.Path(root)
            yield root, p.parent.name, p.name
        for dir in dirs:
            get_cd_info(f"{path}\\{dir}")


def spotify_auth():
    CLIENT_ID = os.environ["SPOTIFY_CLIENT_ID"]
    CLIENT_SECRET = os.environ["SPOTIFY_SECRET_ID"]
    client_credentials_manager = spotipy.oauth2.SpotifyClientCredentials(
        CLIENT_ID, CLIENT_SECRET
    )
    return spotipy.Spotify(client_credentials_manager=client_credentials_manager)


def _get_img_url(jsn):
    try:
        return jsn[0]["images"][0]["url"]
    except TypeError:
        return None
    except IndexError:
        return None


def main():
    search_dir = sel_input_dir()
    sp = spotify_auth()
    if search_dir is None:
        exit()
    for path, artist, album in get_cd_info(search_dir):
        img_path = f"{path}\\{album}.jpg"
        if os.path.exists(img_path):
            continue
        for try_num in range(2):
            sleep(1)
            album = re.sub(r"\s*(\[|\(|（|【){1}.*(\]|\)|）|】)", "", album)
            query = album if try_num else f'"{artist}"&"{album}"'
            q_type = "album" if try_num else "artist,album"
            res = sp.search(query, limit=1, offset=0, type=q_type)
            items = res["albums"]["items"]
            if (img_url := _get_img_url(items)) is None:
                print(f"[SKIP] {img_file}")
                break
            res = requests.get(img_url)
            with open(img_path, "wb") as img_file:
                img_file.write(res.content)
            print(f"[DONE] {img_file}")
            break


if __name__ == "__main__":
    main()
