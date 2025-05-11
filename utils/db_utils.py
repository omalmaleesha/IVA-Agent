from pymongo import MongoClient
from config import settings
import psycopg2
from psycopg2.extras import RealDictCursor

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

class PostgresDB:
    def __init__(self):
        self.connection = psycopg2.connect(settings.POSTGRES_URI)
        self.connection.autocommit = True

    def execute_query(self, query, params=None):
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params)
            if query.strip().lower().startswith("select"):
                return cursor.fetchall()
            return None

    def execute_update(self, query, params=None):
        with self.connection.cursor() as cursor:
            cursor.execute(query, params)

    def close(self):
        self.connection.close()

def initialize_db():
    mongo = MongoDB()
    mongo.get_collection("patients").create_index("patient_id", unique=True)
    mongo.get_collection("appointments").create_index("appointment_id", unique=True)
    mongo.get_collection("doctors").create_index("doctor_id", unique=True)
    mongo.get_collection("conversations").create_index("conversation_id", unique=True)

    db = PostgresDB()
    db.execute_update("""
        CREATE TABLE IF NOT EXISTS patients (
            patient_id VARCHAR(50) PRIMARY KEY,
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            age INT,
            symptoms TEXT,
            special_consultation TEXT,
            registration_date TIMESTAMP
        );
    """)
    db.execute_update("""
        CREATE TABLE IF NOT EXISTS appointments (
            appointment_id VARCHAR(50) PRIMARY KEY,
            patient_id VARCHAR(50),
            doctor_id VARCHAR(50),
            appointment_date DATE,
            appointment_time TIME,
            status VARCHAR(20),
            created_at TIMESTAMP
        );
    """)
    db.execute_update("""
        CREATE TABLE IF NOT EXISTS doctors (
            doctor_id VARCHAR(50) PRIMARY KEY,
            name VARCHAR(100),
            specialization VARCHAR(100)
        );
    """)
    db.execute_update("""
        CREATE TABLE IF NOT EXISTS conversations (
            conversation_id VARCHAR(50) PRIMARY KEY,
            history JSONB,
            context JSONB,
            created_at TIMESTAMP
        );
    """)