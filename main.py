import os
import pathlib
import re
from time import sleep
from typing import List, Optional, Tuple

import PySimpleGUI as sg
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials


def web_driver(headless: bool = True) -> webdriver:
    options = Options()
    options.add_argument(f"log-level=3")
    if headless:
        options.add_argument("--headless")
    return webdriver.Chrome(ChromeDriverManager().install(), options=options)


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


def get_asin(url_list: str) -> Optional[str]:
    for url in url_list:
        match = re.findall(
            r"^(?:https://.*([0-9B]{1}[0-9A-Z]{9}))", str(url), flags=re.VERBOSE)
        if match:
            return match[0]
    return None


def main():
    search_dir = sel_input_dir()
    if search_dir is None:
        exit()
    driver = web_driver()
    try:
        for path, artist, name in get_cd_info(search_dir):
            img_path = f"{path}\\{name}.jpg"
            if os.path.exists(img_path):
                continue
            sleep(1)
            url = f"https://www.google.com/search?q={artist}+{name}+amazon"
            driver.get(url)
            urls = [e.get_attribute("href")
                    for e in driver.find_elements_by_tag_name("a")]
            asin = get_asin(urls)
            if asin is None:
                continue
            img_url = f"http://images-jp.amazon.com/images/P/{asin}.6.LZZZZZZZ.jpg"
            res = requests.get(img_url)
            with open(img_path, "wb") as img_file:
                img_file.write(res.content)
            if os.path.getsize(img_path) < 100:
                os.remove(img_path)
    finally:
        driver.quit()


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

def _test():
    sp = spotify_auth()
    artist = "96猫"
    album = "嘘の火花"
    res = sp.search(f'"{artist}"&"{album}"', limit=1, offset=0, type="artist,album")
    items = res["albums"]["items"]
    if (img_url := _get_img_url(items)) is None:
        print("hoge")
    print(img_url)


if __name__ == "__main__":
    _test()
