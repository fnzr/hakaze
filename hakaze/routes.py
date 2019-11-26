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
                "path": {"$concat": ["$_id", "/", {"$arrayElemAt": [ "$pages", 0 ]}]},
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
                "filenames": {
                    "$map": {
                        "input": {"$slice": ["$pages", skip, limit]},
                        "as": "page",
                        "in": {"$concat": ["$_id", "/", "$$page",]},
                    }
                }
            }
        },
    ]
    filenames = mongo.db.galleries.aggregate(pipeline).next()["filenames"]
    result = {}
    for index, filename in enumerate(filenames):
        result[index + skip + 1] = filename
    return jsonify(result)


@root.route("/count-galleries", methods=["POST"])
def count_galleries():
    pipeline = [{"$count": "count"}]
    return jsonify(mongo.db.galleries.aggregate(pipeline).next())


@root.route("/gallery/<gallery_id>", methods=["GET"])
def gallery_data(gallery_id):
    gallery = mongo.db.galleries.find_one(
        {"_id": gallery_id}, {"_id": False, "pages": False}
    )
    result = {} if gallery is None else gallery
    return jsonify(result)
