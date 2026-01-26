# WasteWise - Systeme IoT d'Analyse de Dechets

## Description du Projet

WasteWise est un systeme IoT intelligent base sur Raspberry Pi Zero 2 W concu pour analyser les dechets, automatiser les actions de tri et guider les utilisateurs vers les conteneurs appropries. Ce depot contient le code Python pour la partie embarquee du projet.

## Objectifs

- Analyser automatiquement les types de dechets a l'aide de capteurs et de vision par ordinateur
- Classifier les dechets en categories (recyclable, compostable, dechets menagers, etc.)
- Informer les utilisateurs sur le conteneur approprie pour chaque type de dechet
- Collecter des donnees pour optimiser la gestion des dechets
- Reduire la contamination des flux de recyclage

## Specifications Techniques

### Materiel Requis

- Raspberry Pi Zero 2 W
- Camera compatible Raspberry Pi (Camera Module v2 ou HQ recommandee)
- Capteurs (a definir selon les besoins):
  - Capteur de poids
  - Capteur de proximite
  - LED/ecran pour les indications visuelles
- Alimentation 5V/2.5A minimum
- Carte microSD (16 GB minimum, classe 10 recommandee)

### Logiciels Requis

- Raspberry Pi OS Lite (Bullseye ou version superieure)
- Python 3.9 ou superieur
- Bibliotheques Python (voir requirements.txt):
  - OpenCV pour la vision par ordinateur
  - TensorFlow Lite pour l'inference de modeles de machine learning
  - GPIO libraries pour le controle des capteurs
  - Flask/FastAPI pour l'interface API (optionnel)

## Installation

### 1. Preparation du Raspberry Pi

Installez Raspberry Pi OS sur votre carte microSD:

```bash
# Mettre a jour le systeme
sudo apt-get update
sudo apt-get upgrade -y
```

### 2. Installation des Dependances

```bash
# Installer Python et pip
sudo apt-get install python3-pip python3-dev -y

# Installer les bibliotheques systeme necessaires
sudo apt-get install libatlas-base-dev libopenjp2-7 libtiff5 -y
```

### 3. Cloner le Depot

```bash
git clone https://github.com/Andylamothe/WasteWise.git
cd WasteWise
```

### 4. Installer les Dependances Python

```bash
pip3 install -r requirements.txt
```

### 5. Configuration

Creez un fichier de configuration `config.json`:

```json
{
  "camera": {
    "resolution": [640, 480],
    "framerate": 30
  },
  "sensors": {
    "weight_pin": 17,
    "proximity_pin": 27
  },
  "categories": {
    "recyclable": "Bac bleu",
    "compostable": "Bac vert",
    "ordures": "Bac noir"
  }
}
```

## Utilisation

### Demarrage du Systeme

```bash
# Lancer le programme principal
python3 main.py
```

### Mode de Test

```bash
# Tester les capteurs
python3 test_sensors.py

# Tester la camera
python3 test_camera.py
```

## Architecture du Systeme

Le systeme est compose de plusieurs modules:

1. **Module de Capture**: Gere la camera et l'acquisition d'images
2. **Module d'Analyse**: Utilise des modeles de machine learning pour classifier les dechets
3. **Module de Capteurs**: Interface avec les capteurs de poids et de proximite
4. **Module de Communication**: Envoie les resultats aux clients (affichage, API, etc.)
5. **Module de Stockage**: Enregistre les donnees pour analyse ulterieure

## Structure du Code

```
WasteWise/
├── main.py                 # Point d'entree principal
├── config.json             # Configuration du systeme
├── requirements.txt        # Dependances Python
├── modules/
│   ├── camera.py          # Gestion de la camera
│   ├── classifier.py      # Classification des dechets
│   ├── sensors.py         # Interface capteurs
│   └── communication.py   # Communication avec les clients
├── models/                # Modeles de machine learning
└── tests/                 # Tests unitaires
```

## Fonctionnalites Principales

### Detection et Classification

Le systeme detecte automatiquement la presence d'un dechet et:
1. Capture une image du dechet
2. Analyse l'image avec un modele de classification
3. Determine la categorie du dechet
4. Mesure le poids (si applicable)

### Guidage Utilisateur

Une fois le dechet analyse, le systeme:
1. Affiche la categorie determinee
2. Indique le conteneur approprie
3. Peut activer des LED pour guider physiquement l'utilisateur
4. Enregistre la transaction pour les statistiques

## Developpement

### Ajouter de Nouvelles Categories

Modifiez le fichier `config.json` pour ajouter de nouvelles categories de dechets.

### Entrainer un Nouveau Modele

Utilisez le script `train_model.py` pour entrainer un nouveau modele de classification:

```bash
python3 train_model.py --dataset /path/to/dataset --epochs 50
```

## Contribution

Les contributions sont les bienvenues. Pour contribuer:

1. Forkez le projet
2. Creez une branche pour votre fonctionnalite (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Committez vos changements (`git commit -m 'Ajout d'une nouvelle fonctionnalite'`)
4. Poussez vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Ouvrez une Pull Request

## Depannage

### La camera ne fonctionne pas

Verifiez que la camera est activee:
```bash
sudo raspi-config
# Interface Options > Camera > Enable
```

### Erreurs de memoire

Le Raspberry Pi Zero 2 W a une memoire limitee. Reduisez la resolution de la camera dans `config.json`.

### Problemes de GPIO

Assurez-vous que l'utilisateur a les permissions necessaires:
```bash
sudo usermod -a -G gpio $USER
```

## Performance et Optimisation

- Utilisez TensorFlow Lite pour des modeles optimises
- Limitez la resolution de la camera pour economiser la memoire
- Implementez un systeme de mise en cache pour les predictions frequentes
- Utilisez des threads pour paralleliser le traitement

## Securite et Confidentialite

- Les images sont traitees localement sur le Raspberry Pi
- Aucune image n'est envoyee vers le cloud par defaut
- Les donnees statistiques peuvent etre anonymisees avant transmission

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de details.

## Support et Contact

Pour toute question ou probleme, veuillez ouvrir une issue sur GitHub.

## Ressources Additionnelles

- Documentation Raspberry Pi: https://www.raspberrypi.org/documentation/
- TensorFlow Lite: https://www.tensorflow.org/lite
- OpenCV: https://opencv.org/

## Roadmap

- Integration avec des API de gestion de dechets municipaux
- Support multi-langues pour les instructions
- Dashboard web pour visualiser les statistiques
- Mode hors-ligne avec synchronisation differee
- Support pour d'autres modeles de Raspberry Pi
