import uuid
import datetime
from utils.db_utils import MongoDB


class PatientService:
    def __init__(self):
        self.db = MongoDB()
        self.collection_name = "patients"

    def register_patient(self, patient_data):
        required = ["first_name", "last_name", "age", "symptoms"]
        if not all(field in patient_data for field in required):
            return None, "Missing required fields"

        patient_id = f"PAT-{str(uuid.uuid4())[:8].upper()}"
        patient = {
            "patient_id": patient_id,
            "first_name": patient_data["first_name"],
            "last_name": patient_data["last_name"],
            "age": patient_data["age"],
            "symptoms": patient_data["symptoms"],
            "special_consultation": patient_data.get("special_consultation"),
            "registration_date": datetime.datetime.now()
        }
        self.db.insert_document(self.collection_name, patient)
        return patient, "Patient registered successfully"
