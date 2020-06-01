import os
import math
from urllib.parse import urljoin
from pydantic import BaseModel
from fastapi import APIRouter
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates
from sqlitedict import SqliteDict
from .exhentai import save_gallery

router = APIRouter()
templates = Jinja2Templates(directory="hakaze/templates")

thumbnail_url = f"{os.getenv('ASSETS_HOST')}/thumb/x285/"
image_url = f"{os.getenv('ASSETS_HOST')}/vault/"

db = SqliteDict(os.getenv("DATABASE_FILE"))


class DownloadArgs(BaseModel):
    url: str


@router.get("/")
async def index(request: Request, p: int = 0, random: bool = False):
    if p < 0:
        return RedirectResponse(url=f"/?p=0")    
    return templates.TemplateResponse(
        "index.j2",
        {
            "request": request
        },
    )


@router.get("/g/{gid}")
async def g(request: Request, gid, p: int = 0):
    if p < 0:
        return RedirectResponse(url=f"/g/{gid}?p=0")    
    return templates.TemplateResponse(
        "gallery.j2",
        {            
            "request": request
        },
    )


@router.get("/p/{gid}/{page}")
async def p(request: Request, gid: str, page: int):
    if page < 1:
        return RedirectResponse(url=f"/p/{gid}/1")
    try:        
        base_url = f"/p/{gid}"
        return templates.TemplateResponse(
            "page.j2",
            {
                "request": request
            },
        )
    except IndexError:
        return RedirectResponse(url=f"/p/{gid}/{page - 1}")


@router.get("/download-complete/{torrent_file}")
async def d(request: Request, torrent_file: str):
    print("Complete: " + torrent_file)
    for key in db:
        if db[key]["torrent"] == torrent_file:
            print("noice")  
    print("done")  
    return ""
