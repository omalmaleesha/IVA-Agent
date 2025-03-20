# ai/training.py
import os
import threading
import time
from config import settings
from ai.intent_classifier import IntentClassifier

def train_model():
    classifier = IntentClassifier()
    return classifier.train_model()

class TrainingWatcher:
    def __init__(self):
        self.last_modified_time = os.path.getmtime(settings.INTENTS_FILE) if os.path.exists(settings.INTENTS_FILE) else 0
        self.lock = threading.Lock()
        self.running = True

    def start_watching(self):
        thread = threading.Thread(target=self._watch_loop, daemon=True)
        thread.start()

    def stop_watching(self):
        self.running = False

    def _watch_loop(self):
        while self.running:
            if os.path.exists(settings.INTENTS_FILE):
                mtime = os.path.getmtime(settings.INTENTS_FILE)
                if mtime > self.last_modified_time:
                    with self.lock:
                        print("Training model due to intents.json change...")
                        train_model()
                        self.last_modified_time = mtime
            time.sleep(5)

watcher = TrainingWatcher()
watcher.start_watching()