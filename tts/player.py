"""Lecteur de fichiers audio."""

import os
import subprocess
from pathlib import Path

AUDIO_DIR = Path("audio")


class AudioPlayer:
    """Lit les fichiers audio MP3."""
    
    def play(self, filename):
        """
        Lit un fichier audio.
        
        Args:
            filename (str): Nom du fichier (avec ou sans .mp3)
        """
        if not filename.endswith('.mp3'):
            filename = f"{filename}.mp3"
        
        filepath = AUDIO_DIR / filename
        
        if not filepath.exists():
            print(f"[ERREUR] Fichier non trouvé: {filepath}")
            return False
        
        print(f"Lecture: {filename}")
        
        try:
            if os.name == 'nt':  # Windows
                os.startfile(filepath)
            elif os.uname().sysname == 'Darwin':  # macOS
                subprocess.run(['afplay', str(filepath)], check=True)
            else:  # Linux
                subprocess.run(['mpg123', str(filepath)], check=True)
            return True
        except Exception as e:
            print(f"[AVERTISSEMENT] Erreur lors de la lecture: {e}")
            return False
    
    def list_files(self):
        """Liste tous les fichiers audio disponibles."""
        if not AUDIO_DIR.exists():
            print("[ERREUR] Dossier audio/ n'existe pas")
            return []
        
        files = list(AUDIO_DIR.glob("*.mp3"))
        
        if not files:
            print("Aucun fichier audio trouvé")
            return []
        
        print("\nFichiers audio disponibles:")
        for i, file in enumerate(files, 1):
            size_mb = file.stat().st_size / (1024 * 1024)
            print(f"  {i}. {file.name} ({size_mb:.2f} MB)")
        
        return files
