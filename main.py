from flask import Flask, render_template, request, jsonify
from controllers.chat_controller import ChatController
from utils.db_utils import initialize_db
from ai.training import watcher
import socketserver
import threading

# Fix for Windows socket issue
socketserver.TCPServer.allow_reuse_address = True

app = Flask(__name__)
chat_controller = ChatController()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get('message')
    conversation_id = data.get('conversation_id')
    response, conv_id = chat_controller.handle_message(user_input, conversation_id)
    return jsonify({'response': response, 'conversation_id': conv_id})


if __name__ == '__main__':
    initialize_db()
    # Add sample doctors
    doctor_service = chat_controller.doctor_service
    doctor_service.add_doctor({"name": "Dr. Smith", "specialization": "Cardiology"})
    doctor_service.add_doctor({"name": "Dr. Jones", "specialization": "Pediatrics"})

    # Run Flask in a way that avoids socket conflicts
    try:
        app.run(debug=True, use_reloader=False, host='127.0.0.1', port=5000)
    except Exception as e:
        print(f"Error starting server: {e}")