# **Healthcare Virtual Assistant (IVA)**  

## **Overview**  
The **Healthcare Virtual Assistant (IVA)** is an AI-powered tool designed to streamline healthcare processes, including **patient registration, appointment scheduling, and answering general healthcare queries**. Built with **Python, Flask, MongoDB, and Groq’s LLM**, it provides a web-based chat interface to enhance user interaction with healthcare services efficiently.  

## **Features**  
🔹 **Patient Registration** – Step-by-step guidance for user registration.  
🔹 **Appointment Scheduling** – Book, cancel, or reschedule appointments with doctors.  
🔹 **Healthcare Queries** – Responds to general health-related questions.  
🔹 **Natural Language Processing (NLP)** – Uses intent classification for better user understanding.  
🔹 **Automatic Retraining** – Updates intent models when new patterns are added.  
🔹 **Database Integration** – Stores and retrieves patient data using MongoDB.  

## **Prerequisites**  
Ensure you have the following installed before setting up the project:  
- 🐍 **Python 3.8+**  
- 🗄️ **MongoDB** (running locally or accessible via URI)  
- 🔑 **Groq API Key** (for LLM integration)  
- 📦 Dependencies listed in `requirements.txt`  

## **Installation**  

### **1. Clone the Repository**  
```bash
git clone <repository-url>
cd healthcare_iva
```

### **2. Set Up a Virtual Environment**  
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### **3. Install Dependencies**  
```bash
pip install -r requirements.txt
```

### **4. Configure Environment Variables**  
Create a `.env` file in the root directory and add:  
```plaintext
GROQ_API_KEY=your_groq_api_key_here
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=healthcare_iva
```

### **5. Start MongoDB**  
```bash
mongod
```

### **6. Train the Initial Model**  
```bash
python -c "from ai.training import train_model; train_model()"
```

### **7. Start the Application**  
```bash
python main.py
```

### **8. Access the UI**  
Open your browser and visit:  
```
http://127.0.0.1:5000
```

---

## **Project Structure**  

```plaintext
healthcare_iva/
├── main.py                  # Flask app entry point
├── config.py                # Configuration settings
├── .env                     # Environment variables
├── requirements.txt         # Dependencies
├── data/
│   ├── intents.json         # Intent training data
│   └── training_logs/       # Training logs
├── models/
│   ├── intent_model/        # Trained intent model
├── utils/
│   ├── db_utils.py          # MongoDB utilities
├── services/
│   ├── patient_service.py   # Patient management
│   ├── appointment_service.py # Appointment handling
│   ├── doctor_service.py    # Doctor management
│   ├── conversation_service.py # Conversation flow
├── ai/
│   ├── intent_classifier.py # Intent classification
│   ├── entity_extractor.py  # Entity extraction
│   ├── llm_connector.py     # LLM integration
│   ├── training.py          # Model training
├── controllers/
│   ├── chat_controller.py   # Chat logic
├── templates/
│   └── index.html           # Web UI template
└── README.md                # This file
```

---

## **Usage**  
- 🏥 **Register a Patient** → Type `"I want to register"` and follow the prompts.  
- 📅 **Schedule an Appointment** → Say `"Book an appointment"` and specify details.  
- ❌ **Cancel/Reschedule** → Use `"Cancel my appointment"` or `"Reschedule appointment."`  

---

## **Troubleshooting**  
💡 **Socket Error (Windows)** → Restart your PC or change the port in `main.py` (e.g., `port=5001`).  
💡 **UI Not Working?** → Check the browser console (`F12`) and ensure `main.js` is in `templates/static/js/`.  
💡 **Model Not Trained?** → Run the training command if `intents.json` is updated.  

---

## **Future Enhancements**  
🚀 **Voice Input Support** – Enable users to interact using speech.  
🌍 **Multi-Language Support** – Extend to different languages.  
📑 **EHR Integration** – Connect with electronic health records (EHR).  

---

## **License**  
This project is **unlicensed** and available for **personal use and experimentation**.  

---

