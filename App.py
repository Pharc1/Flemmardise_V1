from flask import Flask, render_template, Response
import tensorflow as tf
import cv2
import numpy as np

app = Flask(__name__)


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
    global last_prediction
    while True:
        success, frame = camera.read()
        if not success:
            break

        # Effectuer la prédiction
        prediction = predict_frame(frame)
        last_prediction = prediction  # Mettre à jour la dernière prédiction
        prediction_text = f"Prediction: {prediction:.2f}"

        # Déterminer la couleur du cadre en fonction de la prédiction
        color = (0, 255, 0) if prediction > 0.5 else (0, 0, 255)

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

if __name__ == '__main__':
    app.run(debug=True)
