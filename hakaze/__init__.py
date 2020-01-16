from starlette.staticfiles import StaticFiles
from fastapi import FastAPI
from dotenv import load_dotenv

def create_app():
    load_dotenv()
    app = FastAPI()
    app.mount("/static", StaticFiles(directory="static"), name="static")

    from . import routes
    app.include_router(routes.router)
    return app
