from gpiozero import Button, RGBLED
from picamera2 import Picamera2
from datetime import datetime
import requests
import time
import os
from signal import pause
from threading import Thread, Event
from tts import AudioPlayer

# ============================================================================
# CONFIGURATION
# ============================================================================

# GPIO Pins
BUTTON_PIN = 12
STATUS_LED_PINS = (16, 20, 21)  # R, G, B
RESULT_LED_PINS = (5, 6, 13)    # R, G, B

# API Configuration
API_BASE_URL = "https://iotbackend-4ufq.onrender.com/api"
LOGIN_URL = f"{API_BASE_URL}/login"
UPLOAD_URL = f"{API_BASE_URL}/upload-image"
JETER_URL = f"{API_BASE_URL}/jeter"

# Credentials
USERNAME = "test"
PASSWORD = "test"

# Directories
IMAGE_DIR = "photos"

# LED Colors
COLORS = {
    'blue': (0, 0, 1),
    'orange': (1, 0.5, 0),
    'green': (0, 1, 0),
    'purple': (1, 0, 1),
    'red': (1, 0, 0),
    'off': (0, 0, 0)
}

# Category to LED color mapping
CATEGORY_COLORS = {
    "recyclage": COLORS['green'],
    "compost": COLORS['orange'],
    "poubelle": COLORS['purple']
}

# Category to audio message mapping
AUDIO_MESSAGES = {
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

# ============================================================================
# INITIALIZATION
# ============================================================================

os.makedirs(IMAGE_DIR, exist_ok=True)

button = Button(BUTTON_PIN, pull_up=True, bounce_time=0.1)
status_led = RGBLED(*STATUS_LED_PINS, active_high=False)
result_led = RGBLED(*RESULT_LED_PINS, active_high=False)

camera = Picamera2()
camera.configure(camera.create_still_configuration())
camera.start()
time.sleep(2)

auth_token = None
ready_event = Event()
audio_player = AudioPlayer()

# ============================================================================
# FUNCTIONS
# ============================================================================
# ============================================================================
# FUNCTIONS
# ============================================================================

def play_audio(category):
    """Joue un message audio selon la catégorie."""
    key = (category or "").strip().lower()
    message_file = AUDIO_MESSAGES.get(key, "erreur_detection")
    print(f"[AUDIO] {message_file}")
    audio_player.play(message_file)


def ready_animation():
    """Animation LED bleue quand le système est prêt."""
    while not ready_event.is_set():
        status_led.color = COLORS['blue']
        time.sleep(1)
        status_led.color = COLORS['off']
        time.sleep(0.5)


def login():
    """Authentifie l'utilisateur et récupère le token."""
    global auth_token
    print("[SYSTEME] Connexion au backend...")
    
    try:
        response = requests.post(
            LOGIN_URL,
            json={"username": USERNAME, "password": PASSWORD},
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        auth_token = data.get("accessToken")
        
        if not auth_token:
            raise Exception("Token non trouvé dans la réponse")
        
        print("[SYSTEME] Authentification réussie")
        
    except Exception as e:
        print(f"[ERREUR] Échec de connexion: {e}")
        raise


def upload_image(image_path, retry=False):
    """Upload l'image au backend et gère le retry en cas de token expiré."""
    global auth_token
    
    headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
    
    try:
        with open(image_path, "rb") as img:
            files = {"image": ("photo.jpg", img, "image/jpeg")}
            response = requests.post(UPLOAD_URL, files=files, headers=headers, timeout=30)
        
        # Vérification erreur token
        try:
            message = response.json().get("message", "")
        except ValueError:
            message = ""
        
        if message in ("Token manquant", "Token invalide ou expiré") and not retry:
            print("[AVERTISSEMENT] Token expiré, reconnexion...")
            login()
            return upload_image(image_path, retry=True)
        
        return response
        
    except Exception as e:
        print(f"[ERREUR] Upload échoué: {e}")
        raise


def send_jeter_request(category):
    """Envoie la requête POST au endpoint /jeter."""
    try:
        url = f"{JETER_URL}/{category}"
        payload = {"categorieAnalyser": category}
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        print(f"[SYSTEME] Requête /jeter envoyée pour: {category}")
    except Exception as e:
        print(f"[ERREUR] Échec requête /jeter: {e}")


def set_result_led(category):
    """Configure la LED de résultat selon la catégorie."""
    color = CATEGORY_COLORS.get(category, COLORS['red'])
    result_led.color = color
    print(f"[LED] Couleur: {category} -> {color}")


def reset_system():
    """Réinitialise le système après 10 secondes."""
    time.sleep(10)
    
    result_led.off()
    status_led.off()
    
    ready_event.clear()
    Thread(target=ready_animation, daemon=True).start()
    
    print("[SYSTEME] Réinitialisé. Prêt pour le prochain objet.")


def take_and_send_photo():
    """Workflow principal: photo -> upload -> classification -> feedback."""
    print("[SYSTEME] Bouton appuyé, prise de photo...")
    
    # Arrêt animation ready
    ready_event.set()
    result_led.off()
    
    # LED orange + message attente
    status_led.color = COLORS['orange']
    play_audio("attente")
    
    # Capture photo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_path = f"{IMAGE_DIR}/photo_{timestamp}.jpg"
    camera.capture_file(image_path)
    print(f"[SYSTEME] Photo capturée: {image_path}")
    
    try:
        # Upload image
        response = upload_image(image_path)
        print(f"[SYSTEME] Upload status: {response.status_code}")
        
        status_led.off()
        
        # Récupération catégorie
        category = response.text.strip().lower()
        print(f"[SYSTEME] Catégorie: {category}")
        
        # Envoi requête /jeter
        send_jeter_request(category)
        
        # LED de résultat
        set_result_led(category)
        
        # Messages audio
        play_audio(category)
        play_audio("merci")
        
        # Reset asynchrone
        Thread(target=reset_system, daemon=True).start()
        
    except Exception as e:
        print(f"[ERREUR] Traitement échoué: {e}")
        status_led.off()
        result_led.color = COLORS['red']
        play_audio("erreur")
        Thread(target=reset_system, daemon=True).start()
    finally:
        if os.path.exists(image_path):
            try:
                os.remove(image_path)
                print(f"[SYSTEME] Photo supprimée: {image_path}")
            except Exception as e:
                print(f"[ERREUR] Suppression photo échouée: {e}")

# ============================================================================
# MAIN
# ============================================================================
# ============================================================================
# MAIN
# ============================================================================

# Démarrage animation ready
ready_event.clear()
Thread(target=ready_animation, daemon=True).start()

# Configuration du bouton
button.when_pressed = take_and_send_photo

# Message d'introduction
print("[SYSTEME] Tricolo IoT démarré")
play_audio("introduction")

# Boucle principale
pause()
