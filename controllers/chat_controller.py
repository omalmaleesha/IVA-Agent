import random
import json
from ai.intent_classifier import IntentClassifier
from ai.llm_connector import LLMConnector
from services.conversation_service import ConversationService
from services.patient_service import PatientService
from services.appointment_service import AppointmentService
from services.doctor_service import DoctorService
from config import settings

class ChatController:
    def __init__(self):
        self.intent_classifier = IntentClassifier()
        self.llm_connector = LLMConnector()
        self.conversation_service = ConversationService()
        self.patient_service = PatientService()
        self.appointment_service = AppointmentService()
        self.doctor_service = DoctorService()

    def handle_message(self, user_input, conversation_id=None):
        conversation = self.conversation_service.get_conversation(conversation_id)
        conversation_id = conversation["conversation_id"]
        context = self.conversation_service.get_context(conversation_id, "current_process")

        if context == "patient_registration":
            return self.handle_patient_registration(user_input, conversation_id)
        elif context == "appointment_scheduling":
            return self.handle_appointment_scheduling(user_input, conversation_id)
        elif context == "appointment_cancellation":  # New context
            return self.handle_appointment_cancellation(user_input, conversation_id)
        elif context == "appointment_rescheduling":  # New context
            return self.handle_appointment_rescheduling(user_input, conversation_id)

        tag, confidence = self.intent_classifier.predict_intent(user_input)
        if confidence > 0.7:
            if tag == "patient_registration":
                self.conversation_service.set_context(conversation_id, "current_process", "patient_registration")
                self.conversation_service.set_context(conversation_id, "registration_step", 1)
                self.conversation_service.set_context(conversation_id, "registration_data", {})
                response = "Let's start with your registration. What's your first name?"
            elif tag == "appointment_booking":
                self.conversation_service.set_context(conversation_id, "current_process", "appointment_scheduling")
                self.conversation_service.set_context(conversation_id, "appointment_step", 1)
                self.conversation_service.set_context(conversation_id, "appointment_data", {})
                response = "Let's schedule an appointment. Do you have a preferred doctor or department?"
            elif tag == "appointment_cancel":
                self.conversation_service.set_context(conversation_id, "current_process", "appointment_cancellation")
                self.conversation_service.set_context(conversation_id, "cancellation_step", 1)
                self.conversation_service.set_context(conversation_id, "cancellation_data", {})
                response = "I can help you cancel your appointment. May I have your appointment details (date and time)?"
            elif tag == "appointment_reschedule":
                self.conversation_service.set_context(conversation_id, "current_process", "appointment_rescheduling")
                self.conversation_service.set_context(conversation_id, "reschedule_step", 1)
                self.conversation_service.set_context(conversation_id, "reschedule_data", {})
                response = "I can help reschedule your appointment. Let me get your current appointment details first (date and time)."
            else:
                response = self.get_response_from_intents(tag)
        else:
            response, success = self.llm_connector.generate_response(user_input, conversation["history"])
            if success:
                self.llm_connector.update_intents_with_response(user_input, "fallback", response)

        self.conversation_service.add_message(conversation_id, "user", user_input)
        self.conversation_service.add_message(conversation_id, "assistant", response)
        return response, conversation_id

    def handle_appointment_cancellation(self, user_input, conversation_id):
        step = self.conversation_service.get_context(conversation_id, "cancellation_step")
        data = self.conversation_service.get_context(conversation_id, "cancellation_data")

        if step == 1:
            # Expecting date and time (e.g., "2025-03-15 09:00")
            try:
                date, time = user_input.split()
                data["date"] = date
                data["time"] = time
                appointment = self.appointment_service.get_appointment_by_date_time(date, time)
                if appointment:
                    data["appointment_id"] = appointment["appointment_id"]
                    self.conversation_service.set_context(conversation_id, "cancellation_data", data)
                    self.conversation_service.set_context(conversation_id, "cancellation_step", 2)
                    response = f"Found appointment on {date} at {time}. Do you want to cancel it? (Yes/No)"
                else:
                    response = "No appointment found for that date and time. Please provide correct details."
            except ValueError:
                response = "Please provide the date and time in the format 'YYYY-MM-DD HH:MM' (e.g., 2025-03-15 09:00)."

        elif step == 2:
            if user_input.lower() in ["yes", "y"]:
                success, msg = self.appointment_service.cancel_appointment(data["appointment_id"])
                self.conversation_service.set_context(conversation_id, "current_process", None)
                response = msg
            else:
                self.conversation_service.set_context(conversation_id, "current_process", None)
                response = "Cancellation aborted. How else can I assist you?"

        self.conversation_service.add_message(conversation_id, "user", user_input)
        self.conversation_service.add_message(conversation_id, "assistant", response)
        return response, conversation_id

    def handle_appointment_rescheduling(self, user_input, conversation_id):
        step = self.conversation_service.get_context(conversation_id, "reschedule_step")
        data = self.conversation_service.get_context(conversation_id, "reschedule_data")

        if step == 1:
            try:
                date, time = user_input.split()
                appointment = self.appointment_service.get_appointment_by_date_time(date, time)
                if appointment:
                    data["appointment_id"] = appointment["appointment_id"]
                    data["doctor_id"] = appointment["doctor_id"]
                    self.conversation_service.set_context(conversation_id, "reschedule_data", data)
                    self.conversation_service.set_context(conversation_id, "reschedule_step", 2)
                    response = f"Found appointment on {date} at {time}. When would you like to reschedule it to? (e.g., 2025-03-16 10:00)"
                else:
                    response = "No appointment found for that date and time. Please provide correct details."
            except ValueError:
                response = "Please provide the date and time in the format 'YYYY-MM-DD HH:MM' (e.g., 2025-03-15 09:00)."

        elif step == 2:
            try:
                new_date, new_time = user_input.split()
                success, msg = self.appointment_service.reschedule_appointment(data["appointment_id"], new_date,
                                                                               new_time)
                if success:
                    self.conversation_service.set_context(conversation_id, "current_process", None)
                    response = msg
                else:
                    response = msg  # e.g., "Doctor not available"
            except ValueError:
                response = "Please provide the new date and time in the format 'YYYY-MM-DD HH:MM'."

        self.conversation_service.add_message(conversation_id, "user", user_input)
        self.conversation_service.add_message(conversation_id, "assistant", response)
        return response, conversation_id

    def get_response_from_intents(self, tag):
        with open(settings.INTENTS_FILE, 'r') as file:
            intents = json.load(file)
        for intent in intents['intents']:
            if intent['tag'] == tag:
                return random.choice(intent['responses'])
        return "I'm not sure how to respond. How can I assist you with your healthcare needs?"

    def handle_patient_registration(self, user_input, conversation_id):
        global response
        step = self.conversation_service.get_context(conversation_id, "registration_step")
        data = self.conversation_service.get_context(conversation_id, "registration_data")

        if step == 1:
            data["first_name"] = user_input
            self.conversation_service.set_context(conversation_id, "registration_data", data)
            self.conversation_service.set_context(conversation_id, "registration_step", 2)
            response = "What's your last name?"
        elif step == 2:
            data["last_name"] = user_input
            self.conversation_service.set_context(conversation_id, "registration_data", data)
            self.conversation_service.set_context(conversation_id, "registration_step", 3)
            response = "How old are you?"
        elif step == 3:
            try:
                data["age"] = int(user_input)
                self.conversation_service.set_context(conversation_id, "registration_data", data)
                self.conversation_service.set_context(conversation_id, "registration_step", 4)
                response = "Can you describe your symptoms?"
            except ValueError:
                response = "Please enter a valid age."
        elif step == 4:
            data["symptoms"] = user_input
            self.conversation_service.set_context(conversation_id, "registration_data", data)
            self.conversation_service.set_context(conversation_id, "registration_step", 5)
            response = "Do you need a special consultation or OPD?"
        elif step == 5:
            if "special" in user_input.lower():
                self.conversation_service.set_context(conversation_id, "registration_step", 6)
                response = "What kind of special consultation do you need?"
            else:
                patient, msg = self.patient_service.register_patient(data)
                self.conversation_service.set_context(conversation_id, "patient_id", patient["patient_id"])
                self.conversation_service.set_context(conversation_id, "current_process", "appointment_scheduling")
                self.conversation_service.set_context(conversation_id, "appointment_step", 1)
                response = "Patient registered. Let's schedule your appointment. Preferred doctor or department?"
        elif step == 6:
            data["special_consultation"] = user_input
            patient, msg = self.patient_service.register_patient(data)
            self.conversation_service.set_context(conversation_id, "patient_id", patient["patient_id"])
            self.conversation_service.set_context(conversation_id, "current_process", "appointment_scheduling")
            self.conversation_service.set_context(conversation_id, "appointment_step", 1)
            response = "Patient registered. Let's schedule your appointment. Preferred doctor or department?"

        self.conversation_service.add_message(conversation_id, "user", user_input)
        self.conversation_service.add_message(conversation_id, "assistant", response)
        return response, conversation_id

    def handle_appointment_scheduling(self, user_input, conversation_id):
        global response
        step = self.conversation_service.get_context(conversation_id, "appointment_step")
        data = self.conversation_service.get_context(conversation_id, "appointment_data")
        patient_id = self.conversation_service.get_context(conversation_id, "patient_id")

        if step == 1:
            doctors = self.doctor_service.get_doctors_by_specialization(user_input)
            if not doctors:
                response = "No doctors found matching that input. Try a department (e.g., Cardiology) or doctor name (e.g., Dr. Smith)."
            else:
                # Assume first match for simplicity
                data["doctor_id"] = doctors[0]["doctor_id"]
                data["doctor_name"] = doctors[0]["name"]
                self.conversation_service.set_context(conversation_id, "appointment_data", data)
                self.conversation_service.set_context(conversation_id, "appointment_step", 2)
                response = f"Found {doctors[0]['name']}. When would you like your appointment (e.g., 2025-03-15)?"
        elif step == 2:
            data["date"] = user_input
            slots = self.appointment_service.get_available_slots(data["doctor_id"], user_input)
            if not slots:
                response = "No slots available on that date. Try another?"
            else:
                self.conversation_service.set_context(conversation_id, "appointment_data", data)
                self.conversation_service.set_context(conversation_id, "appointment_step", 3)
                response = f"Available slots for {data['doctor_name']} on {user_input}: {', '.join(slots)}. Which time?"
        elif step == 3:
            data["time"] = user_input
            appointment, msg = self.appointment_service.schedule_appointment(
                patient_id, data["doctor_id"], data["date"], data["time"]
            )
            if appointment:
                self.conversation_service.set_context(conversation_id, "current_process", None)
                response = f"{msg} Your appointment ID is {appointment['appointment_id']}."
            else:
                response = "Couldn’t schedule the appointment. Try a different time."

        self.conversation_service.add_message(conversation_id, "user", user_input)
        self.conversation_service.add_message(conversation_id, "assistant", response)
        return response, conversation_id
