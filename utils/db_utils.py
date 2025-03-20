from pymongo import MongoClient
from config import settings

class MongoDB:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDB, cls).__new__(cls)
            cls._instance.client = MongoClient(settings.MONGO_URI)
            cls._instance.db = cls._instance.client[settings.MONGO_DB_NAME]
        return cls._instance

    def get_collection(self, collection_name):
        return self.db[collection_name]

    def insert_document(self, collection_name, document):
        collection = self.get_collection(collection_name)
        result = collection.insert_one(document)
        return result.inserted_id

    def find_document(self, collection_name, query):
        collection = self.get_collection(collection_name)
        return collection.find_one(query)

    def find_documents(self, collection_name, query=None):
        collection = self.get_collection(collection_name)
        return list(collection.find(query or {}))

    def update_document(self, collection_name, query, update):
        collection = self.get_collection(collection_name)
        result = collection.update_one(query, {"$set": update})
        return result.modified_count

def initialize_db():
    mongo = MongoDB()
    mongo.get_collection("patients").create_index("patient_id", unique=True)
    mongo.get_collection("appointments").create_index("appointment_id", unique=True)
    mongo.get_collection("doctors").create_index("doctor_id", unique=True)
    mongo.get_collection("conversations").create_index("conversation_id", unique=True)