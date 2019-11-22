import os
import json
import re
import pymongo

mongo_uri = os.getenv("MONGO_URI")


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
        g["_id"] = g["dir"]
        del g["dir"]
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
        gallery = client.hakaze.galleries.find_one({"id": tag["id"]})
        entries[tag["name"]][tag["group"]].append(gallery["_id"])

    client.hakaze.tags.insert_many(entries.values())
    #client.hakaze.galleries.update_many({}, {'$unset': {'id': True}})


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
    client.hakaze.tags.delete_many({"_id": re.compile(r"\|")})


def _id_to_dir():
    galleries = client.hakaze.galleries.find()
    for gallery in galleries:
        new_gallery = gallery
        new_gallery["_id"] = gallery["dir"]
        new_gallery["old_id"] = gallery["_id"]
        del new_gallery["dir"]
        client.hakaze.galleries.delete_one({"_id": gallery["_id"]})
        client.hakaze.galleries.insert_one(new_gallery)