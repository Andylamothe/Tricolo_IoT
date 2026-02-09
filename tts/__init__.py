"""Module TTS - Synthèse vocale et lecture audio."""

from .generator import TextToSpeechGenerator
from .player import AudioPlayer

__all__ = ['TextToSpeechGenerator', 'AudioPlayer']
