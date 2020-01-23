import re
import os
import datetime
import threading
import logging
import shutil
import random
import time
import requests
from bs4 import BeautifulSoup
from .database import db

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)
SOFT_LIMIT = 3500
ESTIMATED_PAGE_COST = 15
BATCH_JOBS = 30
COOLDOWN_HOURS = 2

VAULT_ROOT = os.getenv("VAULT_ROOT")
if not os.path.isdir(VAULT_ROOT):
    if os.path.isdir("/vault"):
        logger.warn("VAULT_ROOT %s is not a dir. Defaulting to /vault.", VAULT_ROOT)
        VAULT_ROOT = "/vault"
    else:
        raise ValueError("Neither VAULT_ROOT nor /vault exist.")


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
    # with open("/mnt/c/temp/cero.html") as f:
    # return BeautifulSoup(f.read(), "html.parser")


def get_current_limit():
    soup = get_soup("https://e-hentai.org/home.php")
    return int(soup.select_one(".homebox p strong").text)


def download_image(job):
    try:
        soup = get_soup(job["url"])
        try:
            image_url = soup.select_one("#i7 a")["href"]
            filename = None
        except TypeError:
            image_url = soup.select_one("#i3 img")["src"]
            filename = image_url.split("/")[-1]
        logger.debug(
            "Obtained URL for Gallery [%s], page [%d]: %s",
            job["gallery_id"],
            job["page"],
            image_url,
        )
        response = session.get(image_url, stream=True)
        expected_size = int(response.headers["Content-Length"])
        if filename is None:
            filename = response.headers["Content-Disposition"].split("=")[1]

        target_dir = os.path.join(VAULT_ROOT, job["gallery_id"])
        os.makedirs(target_dir, exist_ok=True)
        filepath = os.path.join(target_dir, filename)
        with open(filepath, "wb") as out:
            shutil.copyfileobj(response.raw, out)
        response.close()
        real_size = os.path.getsize(filepath)
        if real_size != expected_size:
            raise ValueError(
                (
                    "Downloaded file does not have expected size. ",
                    f"Expected: {expected_size}. Real: {real_size}",
                )
            )
        db.galleries.update_one(
            {"_id": job["gallery_id"]},
            {"$push": {"_pages": {"$each": [filename], "$position": int(job["page"])}}},
        )
        return True
    except Exception as e:
        logger.error(e)
        return False


def process_queued_jobs(schedule=True):
    now = datetime.datetime.now()
    queued_jobs = list(db.dl_queue.find({"scheduled": {"$lte": now}}).limit(50))
    current_limit = get_current_limit()
    if SOFT_LIMIT < current_limit + (ESTIMATED_PAGE_COST * len(queued_jobs)):
        threading.Timer(
            datetime.timedelta(hours=COOLDOWN_HOURS).total_seconds(),
            process_queued_jobs,
        ).start()
        logger.info(
            "Reached soft limit at %d points. Stopping for %d hours",
            current_limit,
            COOLDOWN_HOURS,
        )
        return
    for job in queued_jobs:
        success = download_image(job)
        if success:
            message = "Done page [%d] for gallery [%s] "
            db.dl_queue.delete_one({"_id": job["_id"]})
        else:
            message = "Failed page [%d] for gallery [%s]. Trying again after delay."
            next_schedule = now + datetime.timedelta(minutes=10)
            db.dl_queue.update_one(
                {"_id": job["_id"]}, {"$set": {"scheduled": next_schedule}}
            )
        logger.info(message, job["page"], job["gallery_id"])
        time.sleep(random.uniform(2, 4))
    if schedule and len(queued_jobs) > 0:
        threading.Timer(
            datetime.timedelta(minutes=1).total_seconds(), process_queued_jobs
        ).start()


def queue_pages(url, gallery_id, max_chapter):
    now = datetime.datetime.now()
    for chapter in range(max_chapter):
        pages = []
        soup = get_soup(url, {"p": chapter})
        for a in soup.select("#gdt .gdtl a"):
            pages.append(
                {
                    "gallery_id": gallery_id,
                    "page": int(a.img["alt"]),
                    "url": a["href"],
                    "scheduled": now,
                }
            )
        db.dl_queue.insert_many(pages)
    threading.Timer(1, process_queued_jobs).start()
    return


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


def save_gallery(url):
    regex = re.compile(r"\/g\/([\d\w]+)\/([\d\w]+)")
    match = regex.search(url)
    if match.lastindex < 2:
        raise ValueError(f"Could not parse dir from [{url}]")
    now = datetime.datetime.now()
    gallery = {
        "_id": f"{match.group(1)}.{match.group(2)}",
        "url": url,
        "created": now,
        "updated": now,
    }

    soup = get_soup(url)
    gallery["title"] = soup.select_one("#gn").text
    gallery["original_title"] = soup.select_one("#gj").text

    lengthStr = soup.select_one("#gdd tr:nth-child(6) td:nth-child(2)").text
    gallery["length"] = int(lengthStr.split(" ")[0])

    tag_index, gallery["tags"] = parse_tags(soup)

    gallery["category"] = soup.select_one("#gdc").text.lower()

    db.galleries.update_one({"_id": gallery["_id"]}, {"$set": gallery}, upsert=True)
    for tag, groups in tag_index.items():
        push = {}
        for group in groups:
            push[group] = gallery["_id"]
        print(push)
        db.tags.update_one(
            {"_id": tag}, {"$set": {"_id": tag}, "$push": push}, upsert=True
        )
    max_chapter = int(soup.select_one(".ptt td:nth-last-child(2)").text)
    queue_pages(url, gallery["_id"], max_chapter)
