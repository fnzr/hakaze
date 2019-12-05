from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()


def create_app():
    app = FastAPI()

    from . import routes

    app.include_router(routes.router)
    return app
