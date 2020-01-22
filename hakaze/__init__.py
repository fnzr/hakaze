import logging
from starlette.staticfiles import StaticFiles
from fastapi import FastAPI
from dotenv import load_dotenv

logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("chardet").setLevel(logging.WARNING)


def create_app():
    load_dotenv()
    app = FastAPI()
    app.mount("/static", StaticFiles(directory="static"), name="static")

    from . import routes

    app.include_router(routes.router)
    return app
