from starlette.staticfiles import StaticFiles
from fastapi import FastAPI
from . import database

database.load_db()
database.sync_dirs_to_db()
database.extract_missing_archives()

app = FastAPI()
app.mount("/static", StaticFiles(directory="hakaze/static"), name="static")

from . import routes

app.include_router(routes.router)
