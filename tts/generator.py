"""Générateur de fichiers audio avec Edge TTS."""

import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

try:
    from edge_tts import Communicate
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False
    Communicate = None

# Créer le dossier audio s'il n'existe pas
AUDIO_DIR = Path("audio")
AUDIO_DIR.mkdir(exist_ok=True)


class TextToSpeechGenerator:
    """Génère des fichiers audio MP3 avec Microsoft Edge TTS."""
    
    def __init__(self, voice='fr-FR-DeniseNeural'):
        """
        Initialise le générateur TTS.
        
        Args:
            voice (str): Voix Edge TTS
                Français: 'fr-FR-DeniseNeural', 'fr-FR-HenriNeural', 'fr-FR-AlainNeural'
                Anglais: 'en-US-AriaNeural', 'en-US-GuyNeural'
        """
        if not EDGE_TTS_AVAILABLE:
            raise ImportError("edge-tts n'est pas installé. Utilisez: pip install edge-tts")
        self.voice = voice
    
    def save(self, text, filename):
        """
        Génère et sauvegarde un fichier audio MP3 dans le dossier 'audio/'.
        
        Args:
            text (str): Le texte à convertir
            filename (str): Nom du fichier (sans extension, .mp3 sera ajouté)
        """
        if not filename.endswith('.mp3'):
            filename = f"{filename}.mp3"
        
        filepath = AUDIO_DIR / filename
        
        print(f"Génération: {filepath}")
        asyncio.run(self._async_save(text, str(filepath)))
        print(f"Fichier généré: {filepath}\n")
    
    async def _async_save(self, text, filepath):
        """Fonction asynchrone pour sauvegarder avec Edge TTS."""
        communicate = Communicate(text, self.voice)
        await communicate.save(filepath)
    
    def set_voice(self, voice):
        """Change la voix utilisée."""
        self.voice = voice
        print(f"Voix changée à: {voice}")
    
    def get_available_voices(self):
        """Affiche les voix disponibles."""
        print("\nVoix disponibles:")
        print("  fr-FR-DeniseNeural (femme, naturelle)")
        print("  fr-FR-HenriNeural (homme, naturel)")
        print("  fr-FR-AlainNeural (homme, conteur)")
        print("  en-US-AriaNeural (femme, anglais)")
        print("  en-US-GuyNeural (homme, anglais)")
        print(f"\nVoix actuelle: {self.voice}")
