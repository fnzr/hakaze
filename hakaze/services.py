import os
from .database import db


def missing_disk_galleries():
    for gallery in db.galleries.find({}, {"_id": True, "url": True}):
        path = os.path.join(os.getenv("VAULT_ROOT"), gallery["_id"])
        if not os.path.isdir(path):
            print(gallery["url"])


def missing_db_galleries():
    for gid in os.listdir(os.getenv("VAULT_ROOT")):
        if db.galleries.find_one({"_id": gid}, {"url": True, "_id": True}) is None:
            print(gid)
