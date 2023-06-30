# MGA802

Ce README est à destination des utilisateurs du projet Gcode editor. Pour les développeurs qui seraient intéressés à 
reprendre ce projet, veuillez vous référer au fichier [README-dev](README-dev.md).

## Présentation


## Récupérér des données supplémentaires

Certaines limitations de GitHub ne nous ont pas permis de fournir avec notre projet des archives .zip de l'ensemble des 
données météorologiques que nous avons utilisés. Nous aurions du donc déposer tous les fichiers séparément ce qui
aurait augmenté très fortement la taille de ce dépôt de plusieurs gigaoctets. Pour éviter, cela nous avons fait le choix de
ne fournir les données que pour une seule année afin de pouvoir effectuer des premiers tests.

Cependant, ces données étant publiques, vous pouvez les récupérer vous-mêmes. Afin de vous aider dans cette tâche, vous
trouverez dans ce dépôt les fichiers `data.sh` et `clean.py` qui vous permettront de récupérer automatiquement tous
les fichiers nécessaires pour la période de votre choix.

### Utilisation


1. Ouvrir un terminal de commande et rendez-vous dans le dossier où vous avez décompressez l'archive.

Exemple :
````commandline
cd Desktop/*/*/nom_projet
````

2. Lancer le fichier `data.sh` en passant en argument l'année de départ et l'année de fin de la période sur laquelle
vous souhaitez récupérer les données.

Exemple : On récupère toutes les données de 2013 jusqu'à 2023.
````commandline
./data.sh 2013 2023
````

L'ensemble des données du Canada vont être récupérées, l'exécution du script va donc prendre un certain temps.
Nous vous conseillons d'exécuter ce script durant la nuit.

4. Installer les modules `numpy` et `pandas` sur votre Python si nécessaire.

````commandline
pip install numpy
pip install pandas
````

5. Exécuter le fichier `clean.py` pour supprimer l'ensemble des fichiers inutiles.

````commandline
python clean.py
````

