from flask import Flask, render_template, Response, request, jsonify
import tensorflow as tf
import cv2
import numpy as np
from openai import OpenAI
import os
from pathlib import Path

app = Flask(__name__)

# Initialisation de l'API OpenAI

client = OpenAI(
  api_key=''
)
# Vérifier la disponibilité du GPU
physical_devices = tf.config.list_physical_devices('GPU')
if physical_devices:
    print("GPU détecté :", physical_devices)
else:
    print("Aucun GPU détecté, utilisation du CPU.")
    
# Charger le modèle pré-entraîné
model = tf.keras.models.load_model('model/Flemardise_V1.keras')

# Configuration de la caméra
camera = cv2.VideoCapture(0)  # 0 pour la caméra par défaut

# Variable globale pour stocker les détails de la session
session_details = {}
new_audio_generated = False


def preprocess_image(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = cv2.resize(image, (160, 160))  # Assurez-vous que la taille correspond à celle du modèle
    image = image / 255.0  # Normaliser l'image
    return np.expand_dims(image, axis=0)  # Ajouter une dimension pour le batch

def predict_frame(frame):
    image = preprocess_image(frame)
    prediction = model.predict(image)
    return prediction[0][0]  # Pour une classification binaire

last_prediction = None  # Déclarez une variable globale pour stocker la dernière prédiction

def generate_frames():
    global last_prediction, new_audio_generated
    while True:
        success, frame = camera.read()
        if not success:
            break

        # Effectuer la prédiction
        prediction = predict_frame(frame)
        last_prediction = prediction  # Mettre à jour la dernière prédiction
        prediction_text = f"Prediction: {prediction:.2f}"

        # Si la prédiction indique que l'utilisateur ne travaille pas
        if prediction > 0.5:
            send_motivation()
            

        # Déterminer la couleur du cadre en fonction de la prédiction
        color = (0, 255, 0) if prediction <= 0.5 else (0, 0, 255)

        # Dessiner le cadre autour de l'image
        cv2.rectangle(frame, (0, 0), (frame.shape[1], frame.shape[0]), color, 2)

        # Ajouter la prédiction en texte sur l'image avec une taille plus petite
        cv2.putText(frame, prediction_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1, cv2.LINE_AA)

        # Encoder l'image au format JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/motivate', methods=['POST'])
def motivate():
    global session_details
    session_details = request.json
    return jsonify(message="Details enregistrés avec succès")

@app.route('/check_motivation')
def check_motivation():
    global new_audio_generated
    if new_audio_generated:
        new_audio_generated = False
        return jsonify(new_audio=True)
    else:
        return jsonify(new_audio=False)

def send_motivation():
    global session_details,new_audio_generated
    response = client.completions.create(
    model="gpt-3.5-turbo-instruct-0914",
    prompt = f"Je suis en train de {session_details['activity']} pendant {session_details['duration']} minutes. Ma motivation est {session_details['motivation']}. Les conséquences si je ne travaille pas sont {session_details['consequences']}. Donne-moi un message de motivation.",
    temperature=1,
    max_tokens=121,
    top_p=1,
    best_of=1,
    frequency_penalty=0,
    presence_penalty=1.02
    )

    message = response.choices[0].text.strip()
    generate_audio_message(message)
    new_audio_generated = True

def generate_audio_message(message):
    # Utilisation du TTS d'OpenAI pour générer un message audio
    speech_file_path = Path(__file__).parent / "static" / "speech.mp3"
    response = client.audio.speech.create(
    model="tts-1",
    voice="nova",
    input=message
    )
    response.stream_to_file(speech_file_path)

if __name__ == '__main__':
    app.run(debug=True)
