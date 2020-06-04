import os
import datetime
import logging
import shutil
import random
import time
import requests
from bs4 import BeautifulSoup
from . import database

VAULT_DIR = os.getenv("VAULT_DIR")

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)

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

def get_soup(url, params=None) -> BeautifulSoup:
    response = session.get(url, params=params)
    if response.status_code == 200:
        return BeautifulSoup(response.content, "html.parser")
    raise ValueError(
        f"Request for [{url}] returned with status [{response.status_code}]"
    )

def download_image(image_url, gallery_name, page_number):
    try:
        response = session.get(image_url, stream=True)
        ext = image_url[-4:]
        filename = str(page_number).zfill(3) + ext
        target_dir = os.path.join(VAULT_DIR, gallery_name)
        os.makedirs(target_dir, exist_ok=True)
        filepath = os.path.join(target_dir, filename)
        with open(filepath, "wb") as out:
            shutil.copyfileobj(response.raw, out)
        expected_size = int(response.headers["content-length"])
        response.close()        
        
        real_size = os.path.getsize(filepath)
        if real_size != expected_size:
            os.remove(filepath)
            raise ValueError(
                (
                    "Downloaded file does not have expected size. ",
                    f"Expected: {expected_size}. Real: {real_size}",
                )
            )
        return True
    except Exception as e:
        logger.error(e)
        return False


def download_page(page_url, gallery_name, page_number):
    soup = get_soup(page_url)

    image_url = soup.select_one("#image-container img")["src"]
    if download_image(image_url, gallery_name, page_number):
        logger.info(f"Done page {page_number}")
    try:
        return soup.select_one("#pagination-page-bottom .next")['href']
    except KeyError:
        return None


def save_gallery(url, starting_page=1):
    now = datetime.datetime.now()
    
    gallery = {
        "url": url,
        "created": now,
        "updated": now
    }

    soup = get_soup(url)    
    #gallery["original_title"] = soup.select_one("#info h2").text
    #length_str = soup.select_one("#info > div").text.split(" ")[0]
    #gallery["length"] = int(length_str)

    gallery = database.Gallery(soup.select_one("#info h1").text)

    current_page = starting_page
    container = soup.select_one(f"#thumbnail-container .thumb-container:nth-child({starting_page}) a")
    page_url = container["href"]
    while page_url:
        page_url = download_page("https://nhentai.net" + page_url, gallery.dirname, current_page)
        current_page += 1
        time.sleep(random.randint(4, 7))
    db = database.get_db()
    db[gallery.dirname] = gallery
    db.commit()