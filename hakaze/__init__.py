from fastapi import FastAPI


def create_app():
    app = FastAPI()

    from . import routes

    app.include_router(routes.router)
    return app
