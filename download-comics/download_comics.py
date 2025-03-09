#!/usr/bin/env python3
"""
Download comics from xkcd.com
"""
import logging
import os
import pathlib
import requests
import pyinputplus as pyip

import bs4

BASE_URL = 'https://xkcd.com'
PREV_LINK_SELECTOR = 'div.box a[rel="prev"]'
COMIC_SELECTOR = 'div.box div#comic img'
CHUNK_SIZE = 8000

logging.basicConfig(level=logging.WARNING,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def get_resources(url):
    """
    Get the previous comic URL

    Args:
        url (String): URL of the current comic

    Returns:
        urls (Tuple): Tuple of the previous and the current comic URL
    """
    try:
        req = requests.get(url, timeout=3)
        req.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.exception("Error: %s", e)
        return None

    soup = bs4.BeautifulSoup(req.text, 'html.parser')
    result = soup.select(PREV_LINK_SELECTOR)
    if not result:
        logging.error("No previous URL found")
        return None
    href = result[0]['href']
    result = soup.select(COMIC_SELECTOR)
    if not result:
        logging.error("No comic found")
        return None
    comic = result[0]['src']
    return (f"{BASE_URL}{href}", f"{BASE_URL}{comic}")


def get_image(comic_url):
    """
    Get the image of the comic

    Args:
        comic_url (str): URL of the comic image

    Returns:
        None
    """
    comic_filename = pathlib.Path(os.path.join(
        os.getcwd(), comic_url.split('/')[-1]))
    comic_name = comic_url.split('/')[-1]
    if comic_filename.exists():
        logging.warning(
            "Comic %s already downloaded. Skipping", comic_name)
        return
    try:
        with requests.get(comic_url, timeout=3) as req:
            req.raise_for_status()
            print(f"Downloading comic {comic_name}")
            with open(comic_filename, 'wb') as file:
                for chunk in req.iter_content(CHUNK_SIZE):
                    file.write(chunk)
    except requests.exceptions.RequestException as e:
        logging.exception("Error: %s", e)
    except IOError as e:
        logging.exception("Error: %s", e)


def main():
    """
    Main function

    Returns:
        None
    """
    num_comics = pyip.inputNum("How many comics do you want to download? ",
                               min=1, max=30)
    res_url = [BASE_URL]
    for _ in range(num_comics):
        res_url = get_resources(res_url[0])
        if res_url is None:
            logging.error("Couldn't get the comic URLs")
            break
        get_image(res_url[1])


if __name__ == '__main__':
    main()
