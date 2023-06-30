# MGA802

Ce README est à destination des développeurs qui souhaiteraient reprendre ce projet et faire évaluer le code 
"gcode_editor.py". Nous détaillons ici les informations que nous avons jugées utiles pour travailler 
sur ce projet. Nous fournissons la structure du projet, les informations sur le fonctionnement du code, les tâches 
supplémentaires implémentées pour modifier le G-code et leurs instructions détaillées. Pour les explications relatives 
à l'utilisation de cet éditeur de G-code, référez-vous au fichier [README](README.md).

## Dépendances

Ce programme a été développé avec Python 3.9.5 et a été testé avec les versions 3.9.5 et 3.11.3. Ci-dessous la liste des
modules utilisés et leur version.

### Modules :

- `matplotlib==3.7.1`
- `numpy==1.24.3`
- `pandas==2.0.1`
- `requests==2.31.0`
- `scipy==1.10.1`
- `PyYAML==6.0`

## Description du projet

## Structure du projet

Le dossier du projet est organisé de la manière suivante :

````graphql
└──nom_projet/
  ├─ build/ - # Dossier de la documentation générée à l'aide de sphinx
  │  └─ doctrees/
  │  └─ html/
  ├─ data/ - # Dossier où sont rangées les données météorologiques à utiliser
  ├─ source/ - # Dossier source pour Sphinx
  ├─ README.md - # Fichier README
  ├─ README-dev.md - # Fichier README destiné aux développeurs
  ├─ requirements.txt
  
...

````

## Pistes d'améliorations

Si vous souhaitez reprendre ce projet et travailler dessus, voici quelques pistes d'amélioration sur lesquelles 
travailler.

### Optimiser et accélérer le traitement des données

Actuellement, nous sommes parvenus à accélérer le traitement des données en utilisant du parallélisme. 
Toutefois, lorsque l'on souhaite utiliser un maillage assez fin pour l'interpolation, le temps d'exécution du 
traitement des données reste long. De plus, l'exécution peut rapidement épuiser toute la mémoire disponible. Il est 
sans doute possible, d'optimiser l'utilisation du parallélisme et de façon générale le code lié aux traitements de 
données pour améliorer les performances.

### Prendre en compte la température

Actuellement, nous ignorons l'impact de la température sur la productivité des éoliennes. Cependant, les ensembles de
données de https://climate.weather.gc.ca, que nous avons utilisés pour collecter et traiter les mesures du 
vent, possèdent aussi des mesures sur la température. Les interpolations effectuées sur les données du vent pourraient 
aussi être effectuées sur celles de la température pour améliorer l'estimation de la production des éoliennes.

### Trouver une nouvelle solution pour les données d'élévation

Actuellement, nous collectons les données d'élévation des terrains d'étude avec l'API d'Open Elevation, et cette 
méthode ralentit fortement l'exécution du programme. Nous n'avons pour le moment pas eu le temps d'étudier sérieusement 
la possibilité d'exploiter les fichiers spécifiques aux données d'élévation. Par exemple, les fichiers GeoTIF fournis 
par le gouvernement canadien à l'adresse suivante : https://open.canada.ca/data/en/dataset/957782bf-847c-4644-a757-e383c0057995