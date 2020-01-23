import os
import math
from urllib.parse import urljoin
from pydantic import BaseModel
from fastapi import APIRouter
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates
from .database import db
import hakaze.database as database
from .exhentai import save_gallery

router = APIRouter()
templates = Jinja2Templates(directory="hakaze/templates")

thumbnail_url = f"{os.getenv('ASSETS_HOST')}/thumb/x285/"
image_url = f"{os.getenv('ASSETS_HOST')}/vault/"


class DownloadArgs(BaseModel):
    url: str


@router.get("/")
async def index(request: Request, p: int = 0, random: bool = False):
    if p < 0:
        return RedirectResponse(url=f"/?p=0")
    covers = database.covers(p * 9, 9, random)
    if not covers:
        return RedirectResponse(url=f"/?p={p-1}")
    return templates.TemplateResponse(
        "index.j2",
        {
            "request": request,
            "covers": covers,
            "current_page": p,
            "thumbnail_url": thumbnail_url,
            "random": random,
        },
    )


@router.get("/g/{gid}")
async def g(request: Request, gid, p: int = 0):
    if p < 0:
        return RedirectResponse(url=f"/g/{gid}?p=0")
    pages = database.pages(gid, p * 9, 9)
    if not pages:
        return RedirectResponse(url=f"/g/{gid}?p={p-1}")
    return templates.TemplateResponse(
        "gallery.j2",
        {
            "request": request,
            "pages": pages,
            "gid": gid,
            "current_chapter": p,
            "thumbnail_url": thumbnail_url,
            "gallery_title": database.gallery_title(gid),
        },
    )


@router.get("/p/{gid}/{page}")
async def p(request: Request, gid: str, page: int):
    if page < 1:
        return RedirectResponse(url=f"/p/{gid}/1")
    try:
        page = database.pages(gid, page - 1, 1)[0]
        base_url = f"/p/{gid}"
        return templates.TemplateResponse(
            "page.j2",
            {
                "request": request,
                "base_url": base_url,
                "page_number": page[0],
                "page": page[1],
                "gallery_url": f"/g/{gid}?p={math.floor(page[0] / 9)}",
                "image_url": image_url,
                "gallery_title": database.gallery_title(gid),
            },
        )
    except IndexError:
        return RedirectResponse(url=f"/p/{gid}/{page - 1}")


"""
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

"""


@router.post("/download-gallery")
def download_gallery(args: DownloadArgs):
    save_gallery(args.url)
