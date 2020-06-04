import os
import zipfile
import logging
import random
import shutil
import urllib
from natsort import natsorted
from sqlitedict import SqliteDict

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)

VAULT_URL = "/vault/"
THUMB_URL = "/thumb/x285/"

ARCHIVE_DIR = os.getenv("ARCHIVE_DIR")
VAULT_DIR = os.getenv("VAULT_DIR")

_database = None
_galleries = None

def load_db():
    global _database
    _database = SqliteDict(os.getenv("DATABASE_FILE"))


def get_db():    
    if _database is None:
        load_db()
    return _database


class Gallery():    

    def __init__(self, dirname=""):
        self.source = ""
        self.dirname = dirname
        self._title = ""
        self.category = ""
        self.length = 0
        self.torrent = ""
        self.cover = ""
        self.created = None
        self.updated = None
        self.tags = {}        
        self._pages = None

    @property
    def title(self):
        return self._title if self._title else self.dirname

    @property
    def path(self):
        return os.path.join(VAULT_DIR, self.dirname)

    @property
    def base_url(self):
        return urllib.parse.urljoin(VAULT_URL, urllib.parse.quote(self.dirname))

    @property
    def thumb_url(self):
        return urllib.parse.urljoin(THUMB_URL, urllib.parse.quote(self.dirname))    

    @property
    def cover_url(self):
        return os.path.join(self.thumb_url, self.cover)

    def _load_pages(self):        
        files = [f for f in os.listdir(self.path) if os.path.isfile(os.path.join(self.path, f))]
        self._pages = list(zip(range(0, len(files)), natsorted(files)))

    def get_pages(self, skip=0, limit=-1):
        if self._pages is None:
            self._load_pages()
        if limit == -1:
            limit = len(self._pages)
        return self._pages[skip:skip+limit]

    def get_image(self, page_number):
        pages = self.get_pages()        
        return os.path.join(self.base_url, pages[page_number - 1][1])

    def get_thumbnails(self, skip, limit):
        pages = self.get_pages(skip, limit)
        return list(map(lambda p: (p[0], os.path.join(self.thumb_url, p[1])), pages))

    @property
    def files(self):
        return [f for f in os.listdir(self.path) if os.path.isfile(os.path.join(self.path, f))]
    

def get_galleries():
    global _galleries    
    if not _galleries:
        _galleries = []
        db = get_db()
        for g in db.values():
            if os.path.exists(os.path.join(VAULT_DIR, g.dirname)):
                _galleries.append(g)
    return _galleries

def get_covers(skip=0, limit=9, randomize=False):
    all_galleries = get_galleries()
    if randomize:
        galleries = random.sample(all_galleries, limit)
    else:
        galleries = all_galleries[skip:skip+limit]
    covers = []
    for gallery in galleries:
        covers.append({
            "title": gallery.title,
            "length": gallery.length,
            "url": gallery.cover_url
        })
    return covers

def get_thumbnails(dirname, skip, limit):
    db = get_db()
    gallery = db[dirname]
    return gallery.title, gallery.get_thumbnails(skip, limit)

def get_gallery(dirname) -> Gallery: 
    db = get_db()
    return db[dirname]


def sync_dirs_to_db():
    db = get_db()
    for d in os.listdir(VAULT_DIR):
        gallery_path = os.path.join(VAULT_DIR, d)
        if not os.path.isdir(gallery_path):
            logger.debug("Skipped: " + d)
            continue
        try:
            gallery = db[d]
        except KeyError:
            gallery = Gallery(d)

        if not gallery.cover:
            gallery.cover = natsorted(gallery.files)[0]
        #if gallery.length == 0:
        gallery.length = len(gallery.files)
        db[d] = gallery    
    db.commit()
    """
    g = get_galleries()
    gs = [x.__dict__ for x in g]
    import json
    print(json.dumps(gs))
    """
        
def extract_missing_archives():
    db = get_db()    
    for f in os.listdir(ARCHIVE_DIR):
        archive_file = os.path.join(ARCHIVE_DIR, f)
        if not os.path.isfile(archive_file):
            continue
        filename = os.path.splitext(f)[0]
        gallery_path = os.path.join(VAULT_DIR, filename)
        if os.path.exists(gallery_path):
            continue
        try:
            #logger.debug(f"Extracting: {f}")
            with zipfile.ZipFile(archive_file, 'r') as z:                
                z.extractall(gallery_path)
                try:
                    gallery = db[filename]
                except KeyError:
                    gallery = Gallery()
                gallery.dirname = filename
                gallery.cover = sorted(os.listdir(gallery_path))[0]
            logger.info("Found new gallery: " + filename)
        except zipfile.BadZipFile:
            # download not finished
            #logger.debug(f"BadZipFile: {f}")
            shutil.rmtree(gallery_path, ignore_errors=True)
        except Exception:
            logger.error(f"Error trying to unzip {f}")
            
    db.commit()
