import re
import os
import datetime
import threading
import logging
import shutil
import random
import time
import json
import requests
from bs4 import BeautifulSoup
from . import database

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)

"""
VAULT_ROOT = os.getenv("VAULT_ROOT")
if not os.path.isdir(VAULT_ROOT):
    if os.path.isdir("/vault"):
        logger.warn("VAULT_ROOT %s is not a dir. Defaulting to /vault.", VAULT_ROOT)
        VAULT_ROOT = "/vault"
    else:
        raise ValueError("Neither VAULT_ROOT nor /vault exist.")
"""

session = requests.session()
session.headers.update(
    {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            " AppleWebKit/537.36 (KHTML, like Gecko)"
            " Chrome/74.0.3729.169 Safari/537.36"
        )
    }
)

session.cookies = requests.utils.cookiejar_from_dict(
    {
        "ipb_pass_hash": os.getenv("IPB_PASS_HASH"),
        "ipb_member_id": os.getenv("IPB_MEMBER_ID"),
    }
)


def get_soup(url, params=None) -> BeautifulSoup:
    response = session.get(url, params=params)
    if response.status_code == 200:
        return BeautifulSoup(response.content, "html.parser")
    raise ValueError(
        f"Request for [{url}] returned with status [{response.status_code}]"
    )


def download_torrent(url):    
    try:        
        logger.debug("Downloading torrent: " + url)
        response = session.get(url, stream=True)
        expected_size = int(response.headers["Content-Length"])
        filename = response.headers["Content-Disposition"].split("=")[1].strip("\"")
        filepath = os.path.join(os.getenv("TORRENTS_DIR"), filename)
        with open(filepath, "wb") as out:
            shutil.copyfileobj(response.raw, out)
        response.close()
        real_size = os.path.getsize(filepath)
        if real_size != expected_size:
            raise ValueError(
                (
                    "Torrent file does not have expected size. ",
                    f"Expected: {expected_size}. Real: {real_size}",
                )
            )        
        return filename
    except Exception as e:
        logger.error(e)
        return None


def parse_tags(soup):
    divs = soup.select("#taglist tbody div")
    tags = {}
    for div in divs:
        parts = (div["id"][3:]).split(":")[::-1]
        if parts[0] not in tags:
            tags[parts[0]] = []
        if len(parts) == 1:
            tags[parts[0]].append("misc")
        else:
            tags[parts[0]].append(parts[1])
    gallery_tags = {}
    for tag, group in tags.items():
        for item in group:
            if item not in gallery_tags:
                gallery_tags[item] = []
            gallery_tags[item].append(tag)
    return tags, gallery_tags


def decide_torrent_file(soup):
    torrents_popup_event = soup.select_one(".gm #gd5 p:nth-child(3) a")['onclick']
    regex = re.compile(r"\('(.*)',")
    match = regex.search(torrents_popup_event)

    torrent_soup = get_soup(match.group(1))    
    forms = torrent_soup.select("#torrentinfo div:nth-child(1) form")    
    if len(forms) == 0:
        logger.info("No torrent exists for this gallery")
        return None

    options = []
    urls = []
    for form in forms:
        tbody = form.select_one("table")        
        options.append({
            "posted": tbody.select_one("tr:nth-child(1) td:nth-child(1)").text,
            "size": tbody.select_one("tr:nth-child(1) td:nth-child(2)").text,
            "seeds": tbody.select_one("tr:nth-child(1) td:nth-child(4)").text,
            "name": tbody.select_one("tr:nth-child(3) a").text,
        })

        torrent_event = tbody.select_one("tr:nth-child(3) a")['onclick']
        regex = re.compile(r"\='(.*)';")
        match = regex.search(torrent_event)
        urls.append(match.group(1))
    for option in options:
        print(" | ".join(option.values()))
    index = int(input("Torrent to download: "))
    return download_torrent(urls[index])

    
def save_gallery(url):
    now = datetime.datetime.now()
    gallery = {
        "url": url,
        "created": now,
        "updated": now,
        "done": False
    }

    soup = get_soup(url)
    gallery["title"] = soup.select_one("#gn").text
    gallery["original_title"] = soup.select_one("#gj").text

    lengthStr = soup.select_one("#gdd tr:nth-child(6) td:nth-child(2)").text
    gallery["length"] = int(lengthStr.split(" ")[0])

    _, gallery["tags"] = parse_tags(soup)

    gallery["category"] = soup.select_one("#gdc").text.lower()

    torrent_file = decide_torrent_file(soup)
    """ dunno how to save this
    if torrent_file:
        gallery["torrent"] = torrent_file
        db = database.get_db()
        if url in db:
            logger.warn("URL already existed in database")
        db[url] = gallery
        db.commit()
    """
