# WasteWise - Système IoT d'Analyse de Déchets

## Description du Projet

WasteWise est un système IoT intelligent basé sur Raspberry Pi Zero 2 W conçu pour analyser les déchets, automatiser les actions de tri et guider les utilisateurs vers les conteneurs appropriés. Ce dépôt contient le code Python pour la partie embarquée du projet.

## Objectifs

- Analyser automatiquement les types de déchets à l'aide de capteurs et de vision par ordinateur
- Classifier les déchets en catégories (recyclable, compostable, déchets ménagers, etc.)
- Informer les utilisateurs sur le conteneur approprié pour chaque type de déchet
- Collecter des données pour optimiser la gestion des déchets
- Réduire la contamination des flux de recyclage

## Spécifications Techniques

### Matériel Requis

- Raspberry Pi Zero 2 W
- Caméra compatible Raspberry Pi (Camera Module v2 ou HQ recommandée)
- 5 LED (2 pour l'état du système, 3 pour les types de bacs)
- 1 capteur ultrasonique pour détecter si les bacs sont remplis
- 1 bouton tactile pour prendre des photos avec la caméra
- 1 haut-parleur pour le système de synthèse vocale (Text-to-Speech)
- 1 powerbank pour la portabilité de la machine
- Carte microSD (16 GB minimum, classe 10 recommandée)

### Logiciels Requis

- Raspberry Pi OS Lite (Bullseye ou version supérieure)
- Python 3.9 ou supérieur
- Bibliothèques Python (voir requirements.txt):
  - OpenCV pour la vision par ordinateur
  - TensorFlow Lite pour l'inférence de modèles de machine learning
  - RPi.GPIO pour le contrôle des GPIO (LED, bouton, capteur ultrasonique)
  - gTTS ou pyttsx3 pour la synthèse vocale (Text-to-Speech)
  - Flask/FastAPI pour l'interface API (optionnel)

## Installation

### 1. Préparation du Raspberry Pi

Installez Raspberry Pi OS sur votre carte microSD:

```bash
# Mettre à jour le système
sudo apt-get update
sudo apt-get upgrade -y
```

### 2. Installation des Dépendances

```bash
# Installer Python et pip
sudo apt-get install python3-pip python3-dev -y

# Installer les bibliothèques système nécessaires
sudo apt-get install libatlas-base-dev libopenjp2-7 libtiff5 -y
```

### 3. Cloner le Dépôt

```bash
git clone https://github.com/Andylamothe/WasteWise.git
cd WasteWise
```

### 4. Installer les Dépendances Python

```bash
pip3 install -r requirements.txt
```

### 5. Configuration

Créez un fichier de configuration `config.json`:

```json
{
  "camera": {
    "resolution": [640, 480],
    "framerate": 30
  },
  "gpio": {
    "led_status_1": 17,
    "led_status_2": 27,
    "led_recyclable": 22,
    "led_compostable": 23,
    "led_ordures": 24,
    "ultrasonic_trigger": 5,
    "ultrasonic_echo": 6,
    "touch_button": 18,
    "speaker": 12
  },
  "categories": {
    "recyclable": "Bac bleu",
    "compostable": "Bac vert",
    "ordures": "Bac noir"
  }
}
```

**Note**: Le haut-parleur peut être connecté via la sortie audio intégrée du Raspberry Pi ou via un amplificateur audio connecté au GPIO 12 (PWM). Pour une meilleure qualité audio, utilisez la sortie audio jack 3.5mm ou un DAC I2S.

## Utilisation

### Démarrage du Système

```bash
# Lancer le programme principal
python3 main.py
```

### Mode de Test

```bash
# Tester les capteurs
python3 test_sensors.py

# Tester la caméra
python3 test_camera.py
```

## Architecture du Système

Le système est composé de plusieurs modules:

1. **Module de Capture**: Gère la caméra et l'acquisition d'images via le bouton tactile
2. **Module d'Analyse**: Utilise des modèles de machine learning pour classifier les déchets
3. **Module de Capteurs**: Interface avec le capteur ultrasonique pour détecter le niveau de remplissage des bacs
4. **Module de Communication**: Gère les LED d'indication et la synthèse vocale
5. **Module de Stockage**: Enregistre les données pour analyse ultérieure

## Structure du Code

```
WasteWise/
├── main.py                 # Point d'entrée principal
├── config.json             # Configuration du système
├── requirements.txt        # Dépendances Python
├── modules/
│   ├── camera.py          # Gestion de la caméra
│   ├── classifier.py      # Classification des déchets
│   ├── sensors.py         # Interface capteurs (ultrasonique, bouton)
│   ├── leds.py            # Contrôle des LED d'état et de catégorie
│   ├── tts.py             # Synthèse vocale (Text-to-Speech)
│   └── communication.py   # Communication avec les clients
├── models/                # Modèles de machine learning
└── tests/                 # Tests unitaires
```

## Fonctionnalités Principales

### Détection et Classification

Le système permet à l'utilisateur de classifier un déchet:
1. L'utilisateur appuie sur le bouton tactile pour déclencher la capture
2. Capture une image du déchet avec la caméra
3. Analyse l'image avec un modèle de classification
4. Détermine la catégorie du déchet (recyclable, compostable ou ordures)

### Guidage Utilisateur

Une fois le déchet analysé, le système:
1. Affiche la catégorie déterminée via les LED correspondantes
2. Annonce vocalement le type de bac approprié via le haut-parleur (synthèse vocale)
3. Vérifie avec le capteur ultrasonique si le bac approprié est plein
4. Guide physiquement l'utilisateur avec les LED de catégorie (recyclable, compostable, ordures)
5. Enregistre la transaction pour les statistiques

## Développement

### Ajouter de Nouvelles Catégories

Modifiez le fichier `config.json` pour ajouter de nouvelles catégories de déchets.

### Entraîner un Nouveau Modèle

Utilisez le script `train_model.py` pour entraîner un nouveau modèle de classification:

```bash
python3 train_model.py --dataset /path/to/dataset --epochs 50
```

## Contribution

Les contributions sont les bienvenues. Pour contribuer:

1. Forkez le projet
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Committez vos changements (`git commit -m 'Ajout d'une nouvelle fonctionnalité'`)
4. Poussez vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Ouvrez une Pull Request

## Dépannage

### La caméra ne fonctionne pas

Vérifiez que la caméra est activée:
```bash
sudo raspi-config
# Interface Options > Camera > Enable
```

### Erreurs de mémoire

Le Raspberry Pi Zero 2 W a une mémoire limitée. Réduisez la résolution de la caméra dans `config.json`.

### Problèmes de GPIO

Assurez-vous que l'utilisateur a les permissions nécessaires:
```bash
sudo usermod -a -G gpio $USER
```

## Performance et Optimisation

- Utilisez TensorFlow Lite pour des modèles optimisés
- Limitez la résolution de la caméra pour économiser la mémoire
- Implémentez un système de mise en cache pour les prédictions fréquentes
- Utilisez des threads pour paralléliser le traitement

## Sécurité et Confidentialité

- Les images sont traitées localement sur le Raspberry Pi
- Aucune image n'est envoyée vers le cloud par défaut
- Les données statistiques peuvent être anonymisées avant transmission

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## Support et Contact

Pour toute question ou problème, veuillez ouvrir une issue sur GitHub.

## Ressources Additionnelles

- Documentation Raspberry Pi: https://www.raspberrypi.org/documentation/
- TensorFlow Lite: https://www.tensorflow.org/lite
- OpenCV: https://opencv.org/

## Roadmap

- Intégration avec des API de gestion de déchets municipaux
- Support multi-langues pour les instructions
- Dashboard web pour visualiser les statistiques
- Mode hors-ligne avec synchronisation différée
- Support pour d'autres modèles de Raspberry Pi
