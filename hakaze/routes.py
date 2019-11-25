from flask import Blueprint, request, jsonify
from hakaze import mongo

root = Blueprint("root", __name__)


@root.route("/covers", methods=["POST"])
def covers():
    data = request.get_json(force=True)
    limit = data["limit"] if "limit" in data else 20
    skip = data["offset"] if "offset" in data else 0
    pipeline = [
        {"$skip": skip},
        {"$limit": limit},
        {
            "$project": {
                "title": True,
                "category": True,
                "length": True,
                "path": {"$concat": ["$_id", "/", "$pages.1"]},
            }
        },
    ]
    return jsonify(list(mongo.db.galleries.aggregate(pipeline)))


@root.route("/pages", methods=["POST"])
def pages():
    data = request.get_json(force=True)
    limit = data["limit"] if "limit" in data else 20
    skip = data["offset"] if "offset" in data else 0

    pipeline = [
        {"$match": {"_id": data["dir"]}},
        {
            "$project": {
                "pages": {
                    "$map": {
                        "input": {"$slice": ["$pages_ar", skip, limit]},
                        "as": "page",
                        "in": {"$concat": ["$_id", "/", "$$page"]},
                    }
                }
            }
        },
    ]
    return jsonify(mongo.db.galleries.aggregate(pipeline).next()["pages"])


@root.route("/count-galleries", methods=["POST"])
def count_galleries():
    pipeline = [{"$count": "count"}]
    return jsonify(mongo.db.galleries.aggregate(pipeline).next())
