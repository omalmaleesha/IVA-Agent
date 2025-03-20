import json
import numpy as np
import pickle
import os
import nltk
from nltk.stem import WordNetLemmatizer
import tensorflow as tf
from config import settings

nltk.download('punkt')
nltk.download('wordnet')

class IntentClassifier:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.model_path = os.path.join(settings.MODEL_DIR, "intent_model.h5")
        self.words_path = os.path.join(settings.MODEL_DIR, "words.pkl")
        self.classes_path = os.path.join(settings.MODEL_DIR, "classes.pkl")
        if os.path.exists(self.model_path):
            self.load_model()
        else:
            self.model = None

    def load_model(self):
        self.model = tf.keras.models.load_model(self.model_path)
        with open(self.words_path, 'rb') as file:
            self.words = pickle.load(file)
        with open(self.classes_path, 'rb') as file:
            self.classes = pickle.load(file)

    def train_model(self):
        os.makedirs(settings.MODEL_DIR, exist_ok=True)
        with open(settings.INTENTS_FILE, 'r') as file:
            intents = json.load(file)

        documents = []
        words = []
        classes = []
        ignore_words = ['?', '!', '.', ',']

        for intent in intents['intents']:
            for pattern in intent['patterns']:
                word_list = nltk.word_tokenize(pattern)
                words.extend(word_list)
                documents.append((word_list, intent['tag']))
                if intent['tag'] not in classes:
                    classes.append(intent['tag'])

        words = [self.lemmatizer.lemmatize(w.lower()) for w in words if w not in ignore_words]
        words = sorted(list(set(words)))
        classes = sorted(list(set(classes)))

        with open(self.words_path, 'wb') as file:
            pickle.dump(words, file)
        with open(self.classes_path, 'wb') as file:
            pickle.dump(classes, file)

        training = []
        output_empty = [0] * len(classes)
        for doc in documents:
            bag = [1 if w in [self.lemmatizer.lemmatize(word.lower()) for word in doc[0]] else 0 for w in words]
            output_row = output_empty.copy()
            output_row[classes.index(doc[1])] = 1
            training.append([bag, output_row])

        training = np.array(training, dtype=object)
        train_x = np.array(list(training[:, 0]))
        train_y = np.array(list(training[:, 1]))

        model = tf.keras.Sequential([
            tf.keras.layers.Dense(128, input_shape=(len(train_x[0]),), activation='relu'),
            tf.keras.layers.Dropout(0.5),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dropout(0.5),
            tf.keras.layers.Dense(len(train_y[0]), activation='softmax')
        ])
        model.compile(optimizer=tf.keras.optimizers.SGD(learning_rate=0.01, momentum=0.9),
                      loss='categorical_crossentropy', metrics=['accuracy'])
        model.fit(train_x, train_y, epochs=200, batch_size=5, verbose=1)
        model.save(self.model_path)
        self.model = model
        self.words = words
        self.classes = classes
        return True

    def predict_intent(self, sentence):
        if not self.model:
            self.load_model()
        sentence_words = [self.lemmatizer.lemmatize(w.lower()) for w in nltk.word_tokenize(sentence)]
        bag = [1 if w in sentence_words else 0 for w in self.words]
        result = self.model.predict(np.array([bag]))[0]
        max_index = np.argmax(result)
        confidence = result[max_index]
        return self.classes[max_index], confidence
