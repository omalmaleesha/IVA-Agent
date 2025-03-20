import uuid

from utils.db_utils import MongoDB

class DoctorService:
    def __init__(self):
        self.db = MongoDB()
        self.collection_name = "doctors"

    def add_doctor(self, doctor_data):
        doctor_id = f"DOC-{str(uuid.uuid4())[:8].upper()}"
        doctor = {
            "doctor_id": doctor_id,
            "name": doctor_data["name"],
            "specialization": doctor_data["specialization"]
        }
        self.db.insert_document(self.collection_name, doctor)
        return doctor

    def get_doctors_by_specialization(self, specialization):
        # Case-insensitive search for specialization or name
        query = {
            "$or": [
                {"specialization": {"$regex": specialization, "$options": "i"}},
                {"name": {"$regex": specialization, "$options": "i"}}
            ]
        }
        return self.db.find_documents(self.collection_name, query)
