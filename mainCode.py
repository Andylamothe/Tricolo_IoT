from gpiozero import Button, RGBLED
from picamera2 import Picamera2
from datetime import datetime
import requests
import time
import os
from signal import pause
from threading import Thread, Event
from tts import AudioPlayer


BUTTON = 12

STATUS_LED = (16, 20, 21) #R,G,B
RESULT_LED = (5, 6, 13) #R,G,B

UPLOAD_URL = "https://iotbackend-4ufq.onrender.com/api/upload-image"
LOGIN_URL = "https://iotbackend-4ufq.onrender.com/api/login"
CATEGORIE_URL = "https://iotbackend-4ufq.onrender.com/api/jeter/"
IMAGE_DIR = "photos"

USERNAME = "test"
PASSWORD = "test"


os.makedirs(IMAGE_DIR, exist_ok=True)

button = Button(BUTTON, pull_up=True, bounce_time=0.1)

status_led = RGBLED(*STATUS_LED, active_high=False)
result_led = RGBLED(*RESULT_LED, active_high=False)

camera = Picamera2()
camera.configure(camera.create_still_configuration())
camera.start()
time.sleep(2)  # laisser camera se reveiller

auth_token = None  # stocké après login

BLUE = (0, 0, 1)
ORANGE = (1, 0.5, 0)
GREEN = (0, 1, 0)
PURPLE = (1, 0, 1)
RED = (1, 0, 0)
OFF = (0, 0, 0)

ready_event = Event()

def play_response(category):
    """Joue un message audio selon la catégorie backend."""
    player = AudioPlayer()

    category_map = {
        "introduction": "introduction",
        "attente": "attente",
        "recyclage": "recyclage",
        "compost": "compost",
        "poubelle": "dechets",
        "dechets": "dechets",
        "bac_plein": "bac_plein",
        "erreur": "erreur_detection",
        "merci": "merci",
    }

    key = (category or "").strip().lower()
    message_file = category_map.get(key, "erreur_detection")
    print(f"[SYSTEME] Catégorie détectée: {key}")
    print(f"[SYSTEME] Lecture du message: {message_file}")
    player.play(message_file)

def ready_animation():
    while not ready_event.is_set():
        status_led.color = BLUE
        time.sleep(1)
        status_led.color = OFF
        time.sleep(0.5)

ready_event.clear()
Thread(target=ready_animation, daemon=True).start()


def login():
    global auth_token
    print("Token non trouvé, login...")

    payload = {
        "username": USERNAME,
        "password": PASSWORD
    }

    r = requests.post(LOGIN_URL, json=payload, timeout=30)
    r.raise_for_status()

    data = r.json()
    print(data)
    auth_token = data.get("accessToken")

    if not auth_token:
        raise Exception("Aucun token trouvé du server")

    print("Token recu")


def upload_image(image_path, retry=False):
    global auth_token

    headers = {}
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"

    # pour ne pas laisser le fichier ouvert
    with open(image_path, "rb") as img:
        files = {
            "image": ("photo.jpg", img, "image/jpeg")
        }
        response = requests.post(
            UPLOAD_URL,
            files=files,
            headers=headers,
            timeout=30
        )

    # verif erreur token
    try:
        message = response.json().get("message")
    except ValueError:
        message = None

    if message in ("Token manquant", "Token invalide ou expiré") and not retry:
        login()
        return upload_image(image_path, retry=True)

    return response

def reset_system():
    time.sleep(10)

    result_led.off()
    status_led.off()

    ready_event.clear()
    Thread(target=ready_animation, daemon=True).start()

    print("Système réinitialisé. Prêt pour le prochain objet.")

def take_and_send_photo():
    global auth_token
    print("Bouton appuyé, prise de photo en cours...")

    ready_event.set()

    result_led.off()

    status_led.color = ORANGE

    play_response("attente")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_path = f"{IMAGE_DIR}/photo_{timestamp}.jpg"

    camera.capture_file(image_path)

    print(f"Uploading {image_path}...")

    try:
        response = upload_image(image_path)

        print("Upload status:", response.status_code)
        print("Server response:", response.text)
        status_led.off()

        category = response.text.strip().lower()
        

        payload = {
        "categorieAnalyser": category
            } 
        URL_ =  f"https://iotbackend-4ufq.onrender.com/api/jeter/{category}"  
        cat = requests.post(URL_, json=payload)
        
        cat.raise_for_status()

        data = cat.json()
        print(data)
        auth_token = data.get("accessToken")

        if category == "recyclage":
            result_led.color = GREEN
        elif category == "compost":
            result_led.color = ORANGE
        elif category == "poubelle":
            result_led.color = PURPLE
        else:
            result_led.color = RED

        play_response(category)
        play_response("merci")

        Thread(target=reset_system, daemon=True).start()

    except Exception as e:
        print("Upload failed:", e)
        status_led.off()
        result_led.color = RED
        Thread(target=reset_system, daemon=True).start()


button.when_pressed = take_and_send_photo

print("Appuyez sur le buton pour prendre une photo.")

# Message d'introduction au démarrage
play_response("introduction")

# mieux qu'un while loop
pause()