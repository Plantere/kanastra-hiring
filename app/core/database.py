from pymongo import MongoClient
import os

class MongoDBConnection:
    def __init__(self):
        self.MONGO_USER = os.getenv("MONGO_INITDB_ROOT_USERNAME")
        self.MONGO_PASSWORD = os.getenv("MONGO_INITDB_ROOT_PASSWORD")
        self.MONGO_DB = os.getenv("MONGO_INITDB_DATABASE")
        self.MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
        self.MONGO_PORT = os.getenv("MONGO_PORT", "27017")

        self.MONGODB_URL = os.getenv(
            "MONGODB_URL", 
            f"mongodb://{self.MONGO_USER}:{self.MONGO_PASSWORD}@{self.MONGO_HOST}:{self.MONGO_PORT}/{self.MONGO_DB}?authSource=admin"
        )

        self.client = MongoClient(self.MONGODB_URL)
        self.db = self.client[self.MONGO_DB]

    def get_database(self):
        return self.db

    def close_connection(self):
        self.client.close()