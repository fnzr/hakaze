from pydantic import BaseModel
from fastapi import APIRouter
from .database import db
from .exhentai import save_gallery

router = APIRouter()


class PagesArgs(BaseModel):
    dir: str
    skip = 0
    limit = 20


class CoverArgs(BaseModel):
    skip = 0
    limit = 20
    random = False


class DownloadArgs(BaseModel):
    url: str


@router.post("/covers")
def covers(args: CoverArgs):
    project = {
        "$project": {
            "title": True,
            "category": True,
            "length": True,
            "path": {"$concat": ["$_id", "/", {"$arrayElemAt": ["$pages", 0]}]},
            "updated": True,
        }
    }
    if args.random:
        pipeline = [{"$sample": {"size": args.limit}}, project]
    else:
        pipeline = [
            {"$skip": args.skip},
            {"$limit": args.limit},
            {"$sort": {"updated": -1}},
            project,
        ]
    return list(db.galleries.aggregate(pipeline))


@router.post("/pages")
def pages(args: PagesArgs):
    pipeline = [
        {"$match": {"_id": args.dir}},
        {
            "$project": {
                "filenames": {
                    "$map": {
                        "input": {"$slice": ["$pages", args.skip, args.limit]},
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
    result = {}
    for index, filename in enumerate(filenames):
        result[index + args.skip + 1] = filename
    return result


@router.post("/count-galleries")
def count_galleries():
    pipeline = [{"$count": "count"}]
    result = db.galleries.aggregate(pipeline).next()
    return result if result is not None else {}


@router.get("/gallery/{gallery_id}")
def gallery_data(gallery_id: str):
    gallery = db.galleries.find_one({"_id": gallery_id}, {"_id": False, "pages": False})
    result = {} if gallery is None else gallery
    return result


@router.post("/download-gallery")
def download_gallery(args: DownloadArgs):
    save_gallery(args.url)
