import os
import math
import logging
import urllib
from pydantic import BaseModel
from fastapi import APIRouter
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates
from sqlitedict import SqliteDict
from .exhentai import save_gallery
from . import database

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)

router = APIRouter()
templates = Jinja2Templates(directory="hakaze/templates")

thumbnail_url = f"{os.getenv('ASSETS_HOST')}/thumb/x285/"
image_url = f"{os.getenv('ASSETS_HOST')}/vault/"

db = SqliteDict(os.getenv("DATABASE_FILE"))

VAULT_DIR = os.getenv("VAULT_DIR")
ARCHIVE_DIR = os.getenv("ARCHIVE_DIR")

class DownloadArgs(BaseModel):
    url: str


@router.get("/")
async def index(request: Request, p: int = 0, random: bool = False):    
    if p < 0:
        return RedirectResponse(url="/?p=0")
    covers = database.get_covers(p*9, 9, random)
    if len(covers) == 0:
        return RedirectResponse(url=f"/?p={p-1}")
    return templates.TemplateResponse(
        "index.j2",
        {
            "request": request,
            "covers": covers,
            "current_page": p,
            "random": random
        },
    )


@router.get("/g/{dirname}")
async def g(request: Request, dirname: str, p: int = 0):
    if p < 0:
        name = urllib.parse.quote(dirname)
        return RedirectResponse(url=f"/g/{name}")
    title, pages = database.get_thumbnails(dirname, p * 9, 9)    
    if len(pages) == 0:
        name = urllib.parse.quote(dirname)
        return RedirectResponse(url=f"/g/{name}?p={p-1}")
    return templates.TemplateResponse(
        "gallery.j2",
        {            
            "request": request,
            "pages": pages,
            "dirname": dirname,
            "current_chapter": p,
            "thumbnail_url": f"/thumb/x285/{dirname}/",
            "gallery_title": title,
        },
    )


@router.get("/p/{dirname}/{page_number}")
async def p(request: Request, dirname: str, page_number: int):
    dirname = dirname.replace("&amp;", "&")
    if page_number < 1:
        name = urllib.parse.quote(dirname)
        return RedirectResponse(url=f"/p/{name}/1")    
    gallery = database.get_gallery(dirname)
    logger.info(gallery.length)
    if page_number > gallery.length:
        name = urllib.parse.quote(dirname)
        return RedirectResponse(url=f"/p/{name}/{gallery.length}")
    try:        
        base_url = f"/p/{dirname}"
        return templates.TemplateResponse(
            "page.j2",
            {
                "request": request,
                "base_url": base_url,
                "page_number": page_number,
                "file_url": gallery.get_image(page_number),
                "gallery_url": f"/g/{dirname}?p={math.floor(page_number / 9)}",                
                "gallery_title": gallery.title,
            },
        )
    except IndexError:
        return RedirectResponse(url=f"/p/{dirname}/{page_number - 1}")


@router.get("/download-complete")
async def d():
    # shit is bugged so I cant find out which download completed
    database.extract_missing_archives()
    return ""
