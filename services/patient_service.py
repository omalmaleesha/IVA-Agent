from utils.db_utils import PostgresDB
import uuid
import datetime


class PatientService:
    def __init__(self):
        self.db = PostgresDB()

    def register_patient(self, patient_data):
        required = ["first_name", "last_name", "age", "symptoms"]
        if not all(field in patient_data for field in required):
            return None, "Missing required fields"

        patient_id = f"PAT-{str(uuid.uuid4())[:8].upper()}"
        query = """
            INSERT INTO patients (patient_id, first_name, last_name, age, symptoms, special_consultation, registration_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            patient_id,
            patient_data["first_name"],
            patient_data["last_name"],
            patient_data["age"],
            patient_data["symptoms"],
            patient_data.get("special_consultation"),
            datetime.datetime.now(),
        )
        self.db.execute_update(query, params)
        return {"patient_id": patient_id}, "Patient registered successfully"


