from tts import TextToSpeechGenerator, AudioPlayer

# Messages du système Tricolo
MESSAGES = {
    "introduction": (
        "Bienvenue sur Tricolo, le système intelligent de tri des déchets. "
        "Appuyez sur le bouton et présentez votre déchet devant la caméra."
    ),
    "recyclage": (
        "Ce déchet va dans le bac de recyclage. "
        "Merci de contribuer à la protection de l'environnement."
    ),
    "compost": (
        "Ce déchet va dans le bac à compost. "
        "Parfait pour nourrir la terre."
    ),
    "dechets": (
        "Ce déchet va dans le bac des déchets ordinaires. "
        "Merci pour votre participation."
    ),
    "autre": (
        "Ce déchet ne va dans aucun des bacs présents à votre droite. "
        "Merci pour votre participation."
    ),
    "bac_plein": (
        "Attention, le bac est plein. "
        "Veuillez contacter le service d'entretien."
    ),
    "erreur_detection": (
        "Désolé, je n'ai pas pu identifier votre déchet. "
        "Veuillez réessayer en le positionnant mieux devant la caméra."
    ),
    "attente": (
        "Analyse en cours, veuillez patienter."
    ),
    "merci": (
        "Merci d'utiliser Tricolo. À bientôt!"
    )
}


def generate_all_messages():
    """Génère tous les messages audio du projet."""
    print("=" * 60)
    print("Génération des messages audio Tricolo")
    print("=" * 60 + "\n")
    
    generator = TextToSpeechGenerator(voice='fr-FR-DeniseNeural')
    
    for name, text in MESSAGES.items():
        print(f"[{name}] {text}")
        generator.save(text, name)
    
    print("Tous les messages ont été générés!\n")


def play_response(category):
    """
    Joue un message audio en fonction de la réponse du backend.
    
    Args:
        category (str): Catégorie retournée par le backend
            Options: 'RECYCLAGE', 'COMPOST', 'DECHETS', 'AUTRE', 'BAC_PLEIN', 'ERREUR'
    """
    player = AudioPlayer()
    
    # Mapping des catégories vers les fichiers audio
    category_map = {
        'RECYCLAGE': 'recyclage',
        'COMPOST': 'compost',
        'DECHETS': 'dechets',
        'AUTRE': 'autre',
        'BAC_PLEIN': 'bac_plein',
        'ERREUR': 'erreur_detection',
        'ATTENTE': 'attente',
        'MERCI': 'merci',
        'INTRODUCTION': 'introduction'
    }
    
    # Convertir en majuscules et chercher le message
    category_upper = category.upper()
    
    if category_upper in category_map:
        message_file = category_map[category_upper]
        print(f"\n[SYSTEME] Catégorie détectée: {category}")
        print(f"[SYSTEME] Lecture du message: {message_file}")
        player.play(message_file)
    else:
        print(f"[ERREUR] Catégorie inconnue: {category}")
        print(f"[INFO] Catégories valides: {', '.join(category_map.keys())}")


def simulate_backend_response(category):
    """
    Simule une réponse du backend et joue le message correspondant.
    
    Args:
        category (str): Catégorie simulée du backend
    """
    print(f"\n{'='*60}")
    print(f"Simulation de réponse backend: {category}")
    print(f"{'='*60}")
    play_response(category)


def list_audio_files():
    """Liste tous les fichiers audio."""
    player = AudioPlayer()
    player.list_files()


if __name__ == '__main__':
    print("Tricolo IoT System")
    print("=" * 60 + "\n")
    
    # 1. Générer tous les messages (à exécuter une seule fois)
    # generate_all_messages()
    
    # 2. Tester avec différentes catégories
    # simulate_backend_response("RECYCLAGE")
    # simulate_backend_response("COMPOST")
    # simulate_backend_response("DECHETS")
    # simulate_backend_response("AUTRE")
    # simulate_backend_response("BAC_PLEIN")
    # simulate_backend_response("ERREUR")
    
    # 3. Lister les fichiers disponibles
    list_audio_files()
