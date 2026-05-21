# =========================================================
# IMPORTS
# =========================================================

from gpiozero import Button, RGBLED
import cv2
from datetime import datetime
import requests
import time
import os
from signal import pause
from threading import Thread, Event
from tts import AudioPlayer
import RPi.GPIO as GPIO


# =========================================================
# GPIO CONFIGURATION
# =========================================================

BUTTON = 12

STATUS_LED = (16, 20, 21) #R,G,B
RESULT_LED = (5, 6, 13) #R,G,B

TRIG = 23
ECHO = 24


# =========================================================
# ULTRASONIC SENSOR CONFIG
# =========================================================

SPEED_OF_SOUND = 34300  # cm/s
FULL_DURATION = 10

BIN_RANGES = {
    "recyclabe": (10, 40),
    "compost": (41, 70),
    "poubelle": (71, 100),
}


# =========================================================
# API CONFIGURATION
# =========================================================

UPLOAD_URL = "https://iotbackend-4ufq.onrender.com/api/upload-image"
LOGIN_URL = "https://iotbackend-4ufq.onrender.com/api/login"

USERNAME = "test"
PASSWORD = "test"


# =========================================================
# FILE CONFIGURATION
# =========================================================

IMAGE_DIR = "photos"
os.makedirs(IMAGE_DIR, exist_ok=True)


# =========================================================
# HARDWARE INITIALIZATION
# =========================================================

button = Button(BUTTON, pull_up=True, bounce_time=0.1)

status_led = RGBLED(*STATUS_LED, active_high=False)
result_led = RGBLED(*RESULT_LED, active_high=False)

# initialisation de la camera
camera = cv2.VideoCapture(0)

if not camera.isOpened():
    raise Exception("Impossible d'ouvrir la webcam")

time.sleep(2)  # laisser camera se reveiller


# =========================================================
# LED COLORS
# =========================================================

WHITE = (1, 1, 1)
BLUE = (0, 0, 1)
ORANGE = (1, 0.5, 0)
GREEN = (0, 1, 0)
PURPLE = (1, 0, 1)
RED = (1, 0, 0)
OFF = (0, 0, 0)


# =========================================================
# GPIO SETUP
# =========================================================

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)


# =========================================================
# GLOBAL VARIABLES
# =========================================================

auth_token = None  # stocké après login
current_status = "ready"

ready_event = Event()
processing_event = Event()
stop_event = Event()

# =========================================================
# TEXT-TO-SPEECH
# =========================================================

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
        "autre": "autre",
        "bac_plein": "bac_plein",
        "erreur": "erreur_detection",
        "merci": "merci",
    }

    key = (category or "").strip().lower()
    message_file = category_map.get(key, "erreur_detection")
    print(f"[SYSTEME] Catégorie détectée: {key}")
    print(f"[SYSTEME] Lecture du message: {message_file}")
    player.play(message_file)


# =========================================================
# STATUS LED THREAD
# =========================================================

def status_manager():
    global current_status

    while not stop_event.is_set():

        # Prêt = flash bleu lent
        if current_status == "ready":
            status_led.color = BLUE
            time.sleep(1)
            status_led.off()
            time.sleep(0.5)

        # En marche = flash blanc rapide
        elif current_status == "processing":
            status_led.color = WHITE
            time.sleep(0.4)
            status_led.off()
            time.sleep(0.4)

        elif current_status == "off":
            status_led.off()
            time.sleep(0.1)

status_thread = Thread(target=status_manager)
status_thread.start()


# =========================================================
# AUTHENTIFICATION
# =========================================================

def login():
    # cherche token JWT du backend

    global auth_token
    
    print("Token non trouvé, login...")

    payload = {
        "username": USERNAME,
        "password": PASSWORD
    }

    response = requests.post(
        LOGIN_URL,
        json=payload,
        timeout=30
    )
    
    response.raise_for_status()

    data = response.json()

    auth_token = data.get("accessToken")

    if not auth_token:
        raise Exception("Aucun token trouvé du server")

    print("Token recu")


# =========================================================
# ENVOIE DE L'IMAGE
# =========================================================

def upload_image(image_path, retry=False):
    # envoie l'image au backend
    # reéssaie si token expiré
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


# =========================================================
# CAPTEUR ULTRASONIQUE
# =========================================================

def get_distance():
    # Mesure distance des bacs

    GPIO.output(TRIG, False)
    time.sleep(0.0002)

    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    pulse_start = time.time()
    pulse_end = time.time()

    timeout = time.time() + 1

    # Début de l'echo
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
        if pulse_start > timeout:
            return None
        
    # Fin de l'echo
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()
        if pulse_end > timeout:
            return None

    pulse_duration = pulse_end - pulse_start

    distance = pulse_duration * 17150

    return round(distance, 1)


# =========================================================
# DÉTECTION NIVEAU DE REMPLISSAGE DES BACS
# =========================================================

def bin_monitor():
    # Verifie si bacs sont pleins

    current_bin = None
    start_time = None
    full_reported = False

    while not stop_event.is_set():

        distance = get_distance()
        #print(distance) # Spam distance en cm dans la console

        if distance is None:
            time.sleep(0.2)
            continue

        detected_bin = None

        # Determine c'est quel bac
        for name, (min_d, max_d) in BIN_RANGES.items():
            if min_d <= distance <= max_d:
                detected_bin = name
                break

        if detected_bin:

            # Si toujours même bac
            if detected_bin == current_bin:

                if start_time and (time.time() - start_time >= FULL_DURATION):

                    if not full_reported:

                        print(f"Bac {detected_bin} plein !")

                        full_reported = True

                        try:
                            payload = {
                                "isFull": True
                            }

                            URL_ =  f"https://iotbackend-4ufq.onrender.com/api/notif/{detected_bin}"
                            
                            response = requests.post(
                                URL_,
                                json=payload
                            
                            )
                            response.raise_for_status()

                        except Exception as e:
                            print("erreur du bac plein", e)

            else:
                # Nouveau bac détecté
                current_bin = detected_bin
                start_time = time.time()
                full_reported = False

        else:
            # Au aucun bac détecté
            current_bin = None
            start_time = None
            full_reported = False

        time.sleep(0.2)


# =========================================================
# RÉINITIALISATION DU SYSTÈME
# =========================================================

def reset_system():
    # Reset les LED et retourne le status à ready 

    global current_status

    result_led.off()
    status_led.off()

    current_status = "ready"

    print("Système réinitialisé. Prêt pour le prochain objet.")


# =========================================================
# FONCTION PRINCIPALE DE PHOTO
# =========================================================

def take_and_send_photo():
    global auth_token, current_status
    print("Bouton appuyé, prise de photo en cours...")

    current_status = "processing"

    result_led.off()

    play_response("attente")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_path = f"{IMAGE_DIR}/photo_{timestamp}.jpg"

    ret, frame = camera.read()

    if not ret:
        raise Exception("Erreur capture webcam")

    cv2.imwrite(image_path, frame)

    print(f"Uploading {image_path}...")

    try:
        response = upload_image(image_path)

        print("Upload status:", response.status_code)
        print("Server response:", response.text)

        category = response.text.strip().lower()

        if category == "autre": 
            payload = {
            "categorieAnalyser": "autre"
                } 
            URL_ =  f"https://iotbackend-4ufq.onrender.com/api/jeter/Autre"
            cat = requests.post(URL_, json=payload)

            cat.raise_for_status()

        else :
            payload = {
            "categorieAnalyser": category
                } 
            URL_ =  f"https://iotbackend-4ufq.onrender.com/api/jeter/{category}"
            cat = requests.post(URL_, json=payload)

            cat.raise_for_status()

        current_status = "off"
        status_led.off()

        if category == "recyclage":
            result_led.color = GREEN
        elif category == "compost":
            result_led.color = ORANGE
        elif category == "poubelle":
            result_led.color = PURPLE
        else:
            result_led.color = RED

        print("avant play response")
        play_response(category)
        play_response("merci")
        
        try:
            os.remove(image_path)
            print(f"Photo supprimée: {image_path}")
        except Exception as e:
            print(f"Erreur suppression photo: {e}")

        Thread(target=reset_system, daemon=True).start()

    except Exception as e:
        print("Upload failed:", e)
        status_led.off()
        result_led.color = RED
        category = "autre"
        print("avant play response")
        play_response(category)
        play_response("merci")
        Thread(target=reset_system, daemon=True).start()

bin_thread = Thread(target=bin_monitor)
bin_thread.start()

button.when_pressed = take_and_send_photo

print("Appuyez sur le buton pour prendre une photo.")

# Message d'introduction au démarrage
play_response("introduction")

try:
    pause()

except KeyboardInterrupt:
    print("\nArrêt du programme...")

finally:
    stop_event.set()

    status_thread.join()
    bin_thread.join()

    status_led.off()
    result_led.off()

    camera.release()

    GPIO.cleanup()
