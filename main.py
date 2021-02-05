import re
import os
from time import sleep
import pathlib
from typing import List, Tuple, Optional

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


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


def web_driver(headless: bool = True) -> webdriver:
    options = Options()
    options.add_argument(f"log-level=3")
    if headless:
        options.add_argument("--headless")
    return webdriver.Chrome(ChromeDriverManager().install(), options=options)


def get_asin(url_list: str) -> Optional[str]:
    for url in url_list:
        match = re.findall(r"^(?:https://.*([0-9B]{1}[0-9A-Z]{9}))", str(url), flags=re.VERBOSE)
        if match:
            return match[0]
    return None


def main():
    driver = web_driver()
    try:
        for path, artist, name in get_cd_info(r"E:\Music\01oldLinux\Afterglow"):
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


if __name__ == "__main__":
    main()
