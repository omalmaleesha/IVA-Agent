import os
import json
from groq import Groq
from config import settings

class LLMConnector:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.LLM_MODEL
        self.max_tokens = settings.LLM_MAX_TOKENS
        self.temperature = settings.LLM_TEMPERATURE

    def get_healthcare_system_prompt(self):
        return """You are a healthcare virtual assistant specialized in handling patient inquiries, 
        appointment scheduling, and providing general healthcare information. 
        Only respond to healthcare-related queries. For non-healthcare topics, politely explain 
        that you're specialized in healthcare and cannot assist with other topics.
        Ensure all responses are medically appropriate, professional, and empathetic.
        Do not provide specific medical diagnoses, but suggest general steps or when to see a doctor.
        Respect patient privacy and avoid asking for sensitive personal information unnecessarily."""

    def is_healthcare_related(self, user_input):
        prompt = f"""Determine if the following query is related to healthcare, medicine, wellness, 
        or healthcare system services (like appointments, registrations, etc.).
        Note: Date and time inputs (e.g., '2025-03-15 09:00') are valid in appointment contexts.

        Query: "{user_input}"

        Respond with only "YES" if healthcare-related or "NO" if not."""
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a classifier for healthcare-related queries."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                max_tokens=10,
                temperature=0.1
            )
            response = chat_completion.choices[0].message.content.strip().upper()
            return response == "YES"
        except Exception as e:
            print(f"Error checking healthcare relevance: {e}")
            return True  # Default to true to avoid false negatives

    def generate_response(self, user_input, conversation_history=None):
        if not self.is_healthcare_related(user_input):
            return "I'm sorry, but I'm specialized in healthcare-related queries only. I can't assist with other topics. Please try a healthcare-related question.", False

        if conversation_history is None:
            conversation_history = []

        messages = [{"role": "system", "content": self.get_healthcare_system_prompt()}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_input})

        try:
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            response = chat_completion.choices[0].message.content
            return response, True
        except Exception as e:
            print(f"Error generating LLM response: {e}")
            return "I'm sorry, I encountered an issue. Please try again.", False

    def update_intents_with_response(self, user_input, tag, response):
        try:
            with open(settings.INTENTS_FILE, 'r') as file:
                intents_data = json.load(file)

            for intent in intents_data['intents']:
                if intent['tag'] == tag:
                    if user_input not in intent['patterns']:
                        intent['patterns'].append(user_input)
                    if response not in intent['responses']:
                        intent['responses'].append(response)
                    break
            else:
                new_intent = {
                    "tag": tag,
                    "patterns": [user_input],
                    "responses": [response],
                    "context": []
                }
                intents_data['intents'].append(new_intent)

            with open(settings.INTENTS_FILE, 'w') as file:
                json.dump(intents_data, file, indent=2)
            return True
        except Exception as e:
            print(f"Error updating intents: {e}")
            return False
