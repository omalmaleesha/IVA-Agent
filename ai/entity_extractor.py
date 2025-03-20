import re
import nltk
from groq import Groq
from config import settings

# Download required NLTK data
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')


class EntityExtractor:
    def __init__(self):
        self.client = Groq(
            api_key=settings.GROQ_API_KEY,
        )
        self.model = settings.LLM_MODEL

    def extract_entities_rule_based(self, text):
        """Extract entities using rule-based methods"""
        entities = {
            "name": None,
            "age": None,
            "phone": None,
            "email": None,
            "date": None,
            "time": None,
            "symptoms": [],
            "doctor": None,
            "department": None
        }

        # Extract names (basic approach)
        name_pattern = re.compile(r'my name is ([\w\s]+)', re.IGNORECASE)
        name_match = name_pattern.search(text)
        if name_match:
            entities["name"] = name_match.group(1).strip()

        # Extract age
        age_pattern = re.compile(r'(\d+) years? old|age (?:is|:) (\d+)', re.IGNORECASE)
        age_match = age_pattern.search(text)
        if age_match:
            age = age_match.group(1) if age_match.group(1) else age_match.group(2)
            entities["age"] = int(age)

        # Extract phone numbers
        phone_pattern = re.compile(r'(\+\d{1,3}[-\.\s]??)?\(?\d{3}\)?[-\.\s]?\d{3}[-\.\s]?\d{4}')
        phone_match = phone_pattern.search(text)
        if phone_match:
            entities["phone"] = phone_match.group(0)

        # Extract email
        email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        email_match = email_pattern.search(text)
        if email_match:
            entities["email"] = email_match.group(0)

        # Extract dates
        date_patterns = [
            r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2})(?:st|nd|rd|th)?(?:\s*,\s*|\s+)(\d{4})',
            r'(\d{1,2})(?:st|nd|rd|th)?\s+(january|february|march|april|may|june|july|august|september|october|november|december)(?:\s*,\s*|\s+)?(\d{4})?',
            r'(\d{1,2})[/.-](\d{1,2})[/.-](\d{2,4})'
        ]

        for pattern in date_patterns:
            date_match = re.search(pattern, text, re.IGNORECASE)
            if date_match:
                entities["date"] = date_match.group(0)
                break

        # Extract time
        time_pattern = re.compile(r'(\d{1,2}):(\d{2})\s*(am|pm)?', re.IGNORECASE)
        time_match = time_pattern.search(text)
        if time_match:
            entities["time"] = time_match.group(0)

        # Extract department/specialty (simple keyword matching)
        departments = [
            "cardiology", "neurology", "pediatrics", "orthopedics", "dermatology",
            "ophthalmology", "gynecology", "urology", "psychiatry", "oncology",
            "radiology", "endocrinology", "gastroenterology", "pulmonology"
        ]

        for dept in departments:
            if re.search(r'\b' + dept + r'\b', text, re.IGNORECASE):
                entities["department"] = dept
                break

        return entities

    def extract_entities_llm(self, text):
        """Extract entities using LLM"""
        prompt = f"""Extract the following entities from the text if present:
        - name: Full name of the person
        - age: Age in years
        - phone: Phone number
        - email: Email address
        - date: Any mention of a date (appointment, etc.)
        - time: Any mention of a time
        - symptoms: List of any symptoms mentioned
        - doctor: Doctor name if mentioned
        - department: Medical department or specialty if mentioned

        Text: "{text}"

        Respond in valid JSON format with the extracted entities. Use null for missing values and an empty array for empty lists."""

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are an entity extraction assistant for a healthcare system."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                max_tokens=500,
                temperature=0.1,
                response_format={"type": "json_object"}
            )

            import json
            response = chat_completion.choices[0].message.content
            extracted_entities = json.loads(response)
            return extracted_entities
        except Exception as e:
            print(f"Error extracting entities with LLM: {e}")
            # Fall back to rule-based extraction
            return self.extract_entities_rule_based(text)

    def extract_entities(self, text, use_llm=True):
        """Extract entities from text using both methods and merge results"""
        if use_llm:
            # Try LLM-based extraction first
            try:
                return self.extract_entities_llm(text)
            except Exception as e:
                print(f"LLM extraction failed: {e}")
                # Fall back to rule-based
                return self.extract_entities_rule_based(text)
        else:
            # Use rule-based extraction
            return self.extract_entities_rule_based(text)