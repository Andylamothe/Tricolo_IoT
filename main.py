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


def play_message(message_name):
    """Lit un message audio spécifique."""
    player = AudioPlayer()
    player.play(message_name)


def list_audio_files():
    """Liste tous les fichiers audio."""
    player = AudioPlayer()
    player.list_files()


if __name__ == '__main__':
    print("Tricolo IoT System")
    print("=" * 60 + "\n")
    
    # Générer tous les messages (à exécuter une seule fois)
    generate_all_messages()
    
    # Lister les fichiers disponibles
    list_audio_files()
    
    # Lire un message spécifique
    play_message("introduction")