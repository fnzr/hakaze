import os
import json
from flask import Flask, request
from pymongo import MongoClient
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

load_dotenv()

mongo = MongoClient(os.getenv("MONGO_URI"))


class PagesArgs(BaseModel):
    dir: str
    skip = 0
    limit = 20


def create_app():
    app = FastAPI()

    @app.post("/pages")
    def pages(args: PagesArgs):
        pipeline = [
            {"$match": {"_id": args.dir}},
            {
                "$project": {
                    "filenames": {
                        "$map": {
                            "input": {"$slice": ["$pages", args.skip, args.limit]},
                            "as": "page",
                            "in": {"$concat": ["$_id", "/", "$$page",]},
                        }
                    }
                }
            },
        ]
        filenames = {}
        try:
            filenames = mongo.hakaze.galleries.aggregate(pipeline).next()["filenames"]
        except StopIteration:
            pass
        result = {}
        for index, filename in enumerate(filenames):
            result[index + args.skip + 1] = filename
        return result

    @app.get("/gallery/{gallery_id}")
    def gallery_data(gallery_id: str):
        gallery = mongo.hakaze.galleries.find_one(
            {"_id": gallery_id}, {"_id": False, "pages": False}
        )
        result = {} if gallery is None else gallery
        return result

    return app

    """
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
    """
