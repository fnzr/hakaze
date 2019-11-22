import os
import json
from flask import Flask, request
from flask_pymongo import PyMongo
from dotenv import load_dotenv

load_dotenv()

mongo = None


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(SECRET_KEY="dev", MONGO_URI=os.getenv("MONGO_URI"))

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    global mongo
    mongo = PyMongo(app)

    # pylint: disable=import-outside-toplevel
    import hakaze.routes

    app.register_blueprint(hakaze.routes.root)

    return app
