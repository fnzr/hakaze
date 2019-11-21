import os
import json
import re
import pymongo

mongo_uri = os.getenv("MONGO_URI")
client = pymongo.MongoClient(mongo_uri)


def gallery_and_page_pg_json():
    with open("/mnt/c/temp/gallery_page.json") as f:
        galleries = json.loads(f.read())

    all_galleries = []
    for g in galleries:
        parsed_pages = dict()
        pages = g["pages"].split(",")
        for page in pages:
            name, number = page.split("|")
            parsed_pages[number] = name
        g["pages"] = parsed_pages
        g["_id"] = g["id"]
        del g["id"]
        all_galleries.append(g)
        # break

    client.hakaze.galleries.insert_many(all_galleries)


def tags_pg_json():
    with open("/mnt/c/temp/tag_gallery.json") as f:
        tags = json.loads(f.read())
    entries = {}
    for tag in tags:
        if tag["name"] not in entries:
            entries[tag["name"]] = {"_id": tag["name"]}
        if tag["group"] not in entries[tag["name"]]:
            entries[tag["name"]][tag["group"]] = []
        entries[tag["name"]][tag["group"]].append(tag["id"])

    client.hakaze.tags.insert_many(entries.values())


def sync_gallery_tags():
    tags = client.hakaze.tags.find()
    entries = {}
    for tag in tags:
        for group in tag:
            if group == "_id":
                continue
            for gid in tag[group]:
                if gid not in entries:
                    entries[gid] = {}
                if group not in entries[gid]:
                    entries[gid][group] = []
                entries[gid][group].append(tag["_id"])
    for _id, gtags in entries.items():
        client.hakaze.galleries.update_one({"_id": _id}, {"$set": {"tags": gtags}})


def break_piped_tags():
    tags = client.hakaze.tags.find({"_id": re.compile(r"\|")})
    entries = {}
    for tag in tags:
        parts = tag["_id"].split("|")
        for part in parts:
            entries[part.strip()] = {}
            for key in tag:
                if key == "_id":
                    continue
                if key not in entries[part.strip()]:
                    entries[part.strip()][key] = []
                for gid in tag[key]:
                    entries[part.strip()][key].append(gid)
    for _id, tags in entries.items():
        tag_entry = client.hakaze.tags.find_one({"_id": _id})
        if tag_entry is None:
            tag_entry = {"_id": _id}
        for group, gids in tags.items():
            if group not in tag_entry:
                tag_entry[group] = []
            for gid in gids:
                tag_entry[group].append(gid)
        client.hakaze.tags.update_one({"_id": _id}, {"$set": tag_entry}, upsert=True)
