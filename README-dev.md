# WindFarmPlacement

Ce README est à destination des développeurs qui souhaiteraient reprendre le projet `WindFarmPlacement` et le faire 
évoluer. Nous détaillons ici les informations que nous avons jugées utiles pour travailler sur ce projet. 
Nous fournissons la structure du projet, des informations sur le fonctionnement du code et des pistes de travail
pour continuer à améliorer le projet. Pour les explications d'ordre général (installation, paramètres, ...), 
référez-vous au fichier [README](README.md).

## Table des matières

- [1. Dépendances](#dépendances)
- [2. Description du projet](#description-du-projet)
- [3. Structure du projet](#structure-du-projet)
- [4. Pistes d'améliorations](#pistes-d'améliorations)
  - [4.1. Optimiser et accélérer le traitement des données](#optimiser-et-accélérer-le-traitement-des-données)
  - [4.2. Prendre en compte la température](#prendre-en-compte-la-température)
  - [4.3. Trouver une nouvelle solution pour les données d'élévation](#trouver-une-nouvelle-solution-pour-les-données-d'élévation)

## Dépendances

Ce programme a été développé avec Python 3.9.5 et a été testé avec les versions 3.7, 3.9.5 et 3.11.3. 
Ci-dessous la liste des modules utilisés et leur version.

### Modules :

- `matplotlib==3.7.1`
- `numpy>=1.24.3`
- `pandas>=2.0.1`
- `requests==2.31.0`
- `scipy>=1.10.1`
- `PyYAML==6.0`

## Description du projet

Le projet `WindFarmPlacement` est un package Python ayant pour but de trouver, à partir de données météorologiques
historiques, des parcelles de terrain pouvant accueillir des champs d'éoliennes définis par l'utilisateur. Il
contient des méthodes pour estimer la moyenne et les probabilités de vitesse du vent dans une zone d'étude, des méthodes
pour définir des champs d'éoliennes et calculer la puissance théorique maximum qu'il peut produire et enfin des méthodes
pour proposer des parcelles de terrain permettant d'atteindre un objectif de puissance.

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
## Description des fichiers


### WeatherData
##### fasthistorymonthprocess: 
Processus de calcul rapide de l'historique pour un mois spécifique.
##### fasthistoryyearprocess: 
Processus de calcul rapide de l'historique sur une année spécifique.
##### station: 
Objet représentant une station météorologique.
##### windhistory: 
Objet conceptuel représentant l'historique du vent dans une zone par la vitesse moyenne du vent et l'histogramme des classes de vent. Les classes de vent sont les différentes tranches de vitesse du vent : 0 m/s, 1 m/s, 2 m/s, ...


### WindFarm
##### windfarm:
Objet représentant un parc éolien.
#### windmill:
Objet représentant une éolienne.


### elevationdata:
Objet conceptuel représentant les caractéristiques topographiques d'une zone d'étude.

### utils:
Fichier contenant plusieurs fonction utilitaires au programme.

### windfarmplacement:
Objet conceptuel représentant un "gestionnaire" qui s'occupe de faire le lien entre le calcul des données du vent dans la zone étudiée et la puissance productible par des éoliennes dans cette zone, afin de trouver les meilleures parcelles où placer un champ d'éoliennes.



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
