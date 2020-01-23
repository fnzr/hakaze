from starlette.staticfiles import StaticFiles
from fastapi import FastAPI

app = FastAPI()
app.mount("/static", StaticFiles(directory="hakaze/static"), name="static")

from . import routes

app.include_router(routes.router)
