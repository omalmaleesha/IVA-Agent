import uuid
import datetime
from utils.db_utils import MongoDB


class AppointmentService:
    def __init__(self):
        self.db = MongoDB()
        self.collection_name = "appointments"

    def schedule_appointment(self, patient_id, doctor_id, date, time):
        if not self.check_doctor_availability(doctor_id, date, time):
            return None, "Doctor not available"

        appointment_id = f"APT-{str(uuid.uuid4())[:8].upper()}"
        appointment = {
            "appointment_id": appointment_id,
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "appointment_date": date,
            "appointment_time": time,
            "status": "scheduled",
            "created_at": datetime.datetime.now()
        }
        self.db.insert_document(self.collection_name, appointment)
        return appointment, "Appointment scheduled successfully"

    def check_doctor_availability(self, doctor_id, date, time):
        doctor = self.db.find_document("doctors", {"doctor_id": doctor_id})
        if not doctor:
            return False
        appointments = self.db.find_documents(self.collection_name, {"doctor_id": doctor_id, "appointment_date": date})
        for apt in appointments:
            if apt["appointment_time"] == time:
                return False
        return True

    def get_available_slots(self, doctor_id, date):
        doctor = self.db.find_document("doctors", {"doctor_id": doctor_id})
        if not doctor:
            return []
        appointments = self.db.find_documents(self.collection_name, {"doctor_id": doctor_id, "appointment_date": date})
        booked_times = [apt["appointment_time"] for apt in appointments]
        all_slots = [f"{h:02d}:00" for h in range(9, 17)]  # 9 AM to 5 PM
        return [slot for slot in all_slots if slot not in booked_times]

    def get_appointment_by_date_time(self, date, time):
        return self.db.find_document(self.collection_name, {
            "appointment_date": date,
            "appointment_time": time,
            "status": {"$in": ["scheduled", "confirmed"]}
        })
