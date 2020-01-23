import os
import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ConfigurationError

logger = logging.getLogger(__name__)
try:
    mongo = MongoClient(os.getenv("MONGO_URI"), connectTimeoutMS=3)
    mongo.db.command('ismaster')
except (ConnectionFailure, ConfigurationError):
    logger.warn("Could not connect to MONGO_URI. Defaulting to localhost.")
    mongo = MongoClient("mongodb://root:root@localhost:27017/hakaze", connectTimeoutMS=3)
    mongo.db.command('ismaster')

db = mongo["hakaze"]


def covers(skip, limit, random=False):
    project = {
        "$project": {
            "title": True,
            "category": True,
            "length": True,
            "path": {
                "$concat": [
                    "$_id",
                    "/",
                    {"$arrayElemAt": ["$pages", 0]},
                ]
            },
            "updated": True,
        }
    }
    if random:
        pipeline = [{"$sample": {"size": limit}}, project]
    else:
        pipeline = [
            {"$skip": skip},
            {"$limit": limit},
            {"$sort": {"updated": -1}},
            project,
        ]
    return list(db.galleries.aggregate(pipeline))


def pages(dir, skip, limit):
    pipeline = [
        {"$match": {"_id": dir}},
        {
            "$project": {
                "filenames": {
                    "$map": {
                        "input": {"$slice": ["$pages", skip, limit]},
                        "as": "page",
                        "in": {"$concat": ["$_id", "/", "$$page",]},
                    }
                }
            }
        },
    ]
    filenames = {}
    try:
        filenames = db.galleries.aggregate(pipeline).next()["filenames"]
    except StopIteration:
        pass
    result = []
    for index, filename in enumerate(filenames):
        result.append((index + skip + 1, filename))
    return result

def gallery_title(gid):
    return db.galleries.find_one({'_id': gid}, {'title': True})['title']
