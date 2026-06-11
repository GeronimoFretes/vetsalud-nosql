import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()


def get_mongo_client() -> MongoClient:
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    return MongoClient(mongo_uri)


def get_database():
    db_name = os.getenv("MONGO_DB_NAME", "vetsalud")
    client = get_mongo_client()
    return client[db_name]