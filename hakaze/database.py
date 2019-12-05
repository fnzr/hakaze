import os
from pymongo import MongoClient

mongo = MongoClient(os.getenv("MONGO_URI"))

db = mongo["hakaze"]
