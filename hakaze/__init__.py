from starlette.staticfiles import StaticFiles
from fastapi import FastAPI


def create_app():
    app = FastAPI()
    app.mount("/static", StaticFiles(directory="static"), name="static")

    from . import routes
    app.include_router(routes.router)
    return app
