# WindFarmPlacement

Ce README est à destination des utilisateurs du projet `WindFarmPlacement`. Pour les développeurs qui seraient intéressés à 
reprendre ce projet, veuillez vous référer au fichier [README-dev](README-dev.md).

## Table des matières

- [1. Présentation](#présentation)
- [2. Récupérer des données supplémentaires](#récupérer-des-données-supplémentaires)
- [3. Utiliser un autre ensemble de données](#utiliser-un-autre-ensemble-de-données)
- [4. Installation](#installation)
- [5. Paramètres utilisateurs](#explication-des-paramètres)
  - [5.1 Paramètres sur les fichiers de données](#paramètres-sur-les-fichiers-de-données)
  - [5.2 Paramètres sur la zone d'étude](#paramètres-sur-la-zone-d'étude)
  - [5.3 Paramètres sur le traitement des données](#paramètres-sur-le-traitement-des-données)
- [6. Ressources et références](#ressources-et-références)
  - [6.1. Ressources](#ressources)
  - [6.2. Références](#références)

## Présentation

...Pour décider de où placer des éoliennes il faut étudier l'histoire... bla bla


## Installation

Cette section présente la démarche à suivre pour récupérer ce projet et installer les modules Python nécessaires.

Prérequis : Installer [Python](https://www.python.org/downloads/) (Versions testées 3.7, 3.9.5, 3.11.3).

1. Aller sur la page ["Releases"](https://github.com/LeoBernabeu/MGA802_Projet/releases) de GitHub et télécharger
l'archive *Source code (zip)* présente dans l'onglet *Assets*.

2. Décompresser l'archive obtenue dans le dossier de votre choix.

Vous devriez alors avoir le dossier qui suit :

````graphql
└──nom_projet/
  ├─ build/ - # Dossier de la documentation générée à l'aide de sphinx
  │  └─ doctrees/
  │  └─ html/
  ├─ data/ - # Dossier où sont rangées les données météorologiques à utiliser
  ├─ README.md - # Fichier README
  ├─ README-dev.md - # Fichier README destiné aux développeurs
  ├─ requirements.txt
  ...
````

3. Ouvrir un terminal de commande et rendez-vous dans le dossier où vous avez décompressez l'archive.

Exemple :
````commandline
cd Desktop/*/*/gcode_editor
````

4. Installer les modules nécessaires au programme puis lancer Python.

````commandline
pip install -r requirements.txt
python
````


## Récupérer des données supplémentaires

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

4. Si vous n'avez pas installé précédemment les modules requis pour ce projet, effectuer l'installation avec le fichier
`requirements.txt` certains vont être nécessaire pour l'étape suivante.

````commandline
pip install -r requirements.txt
````

5. Exécuter le fichier `clean.py` pour supprimer l'ensemble des fichiers inutiles.

````commandline
python clean.py
````

## Utiliser un autre ensemble de données

Nous avons programmé notre module dans l'optique d'être utilisé avec des données de station météorologiques, ce qui 
a influé sur l'organisation du dossier `data` et donc sur les méthodes de lecture des fichiers. Par conséquent, notre
module n'a pas adapté à l'utilisation de données dont la structure diffère des nôtres.

Cependant, il est tout de même possible d'utiliser vos propres ensembles de données, mais il sera nécessaire que vous 
les réorganisiez de la façon suivante :

````graphql
  ├─ data/ - # Dossier où sont rangées les données météorologiques à utiliser
  │  ├─ id_1/
  │  │   ├─ Year_1/
  │  │   │   ├─ 1_W.csv # Mois de Janvier
  │  │   │   └─ 2_W.csv # Mois de Février
  │  │   │   └─ ...
  │  │   └─ Year_2/
  │  └─ id_2/
````

Chacun des fichiers month_X.csv devra comporter une colonne "Wind Spd (km/h)" avec les mesures du vent en (km/h).

Exemple :
`````text
"Wind Spd (km/h)"
"12"
"11"
...
`````

De plus, il vous faudra un fichier de référence en .csv dans lequel seront indiquées les coordonnées de longitudes et de 
latitudes associées à chaque identifiant.

`````text
"id","Latitude (Decimal Degrees)","Longitude (Decimal Degrees)"
"1","-122.34","44.3"
...
`````

## Explication des paramètres

### Paramètres sur les fichiers de données

Dans le cas où vous souhaiteriez utiliser votre propre ensemble de données ou bien que le dossier *data* n'est pas dans
votre dossier de travail, les paramètres suivants peuvent avoir besoin d'être définis.

- `path_to_data`: Le chemin relatif vers le dossier qui contient le dossier *data* et le fichier de référence à utiliser
pour les données météorologiques. Le chemin relatif correspond au chemin à effectuer depuis le répertoire courant pour 
atteindre le dossier cible. Par exemple, si l'on se situe dans le dossier *Documents/dossier_1* et que l'on veut 
atteindre un dossier dans *Documents/dossier_2/sous_dossier*, le chemin sera *../dossier_2/sous_dossier*. Si ce
paramètre est laissé vide, on utilisera par défaut *./* ce qui signifie que le dossier *data* est présent dans le 
répertoire courant.
- `reference_file`: Le nom du fichier de référence décrit dans la section [Utiliser un autre ensemble de données](#utiliser-un-autre-ensemble-de-données)
lorsque vous souhaitez utiliser votre propre ensemble de données. Si ce paramètre est laissé vide, on utilisera par
défaut le fichier *Station_Inventory_EN.csv* qui est le fichier de référence des stations de Climate Weather Canada.

### Paramètres sur la zone d'étude

Notre package travaille exclusivement avec des coordonnées en longitudes et en latitudes sous forme de degrés décimaux. 
Pour définir la zone d'étude, il faut donc entrer en paramètre les coordonnées limites de la zone d'étude.

- `lon_min`: La borne inférieure des coordonnées de longitude.
- `lon_max`: La borne supérieure des coordonnées de longitude.
- `lat_min`: La borne inférieure des coordonnées de latitude.
- `lat_max`: La borne supérieure des coordonnées de latitude.

Il est nécessaire aussi de définir le nombre de points qui vont définir le maillage de la zone d'étude. Plus, le nombre
de points est élevé plus le nombre de calculs effectués sera important. Le temps d'exécution du programme sera donc
allongé. 

- `precision_lon`: Le nombre de points pour le maillage pour les coordonnées de longitude.
- `precision_lat`: Le nombre de points pour le maillage pour les coordonnées de longitude. 

### Paramètres sur le traitement des données

Il est nécessaire de fournir les années à utiliser pour le traitement des données, ainsi que l'altitude à laquelle on
souhaite déterminer les vitesses du vent.

- `study_years`: La liste des années a utilisé pour le traitement des données. On fournit une liste en paramètre de la
façon suivante :
````yaml
study_years:
  - 2017
  - 2018
  - 2019
````
- `study_alt`: L'altitude à laquelle on souhaite déterminer les vitesses du vent. Les stations météorologiques utilisées
par Climate Weather Canada mesurant toutes les altitudes à 10 mètres au-dessus du sol, nous considèrons que toutes les
données traitées sont aussi à 10 mètres au-dessus du sol. Nous utilisons ensuite le profil vertical du vent pour
déterminer la vitesse à l'altitude souhaitée.

Notre package utilise le parallélisme pour accélérer le traitement des données. Pour cela, chaque année est traitée
une à une et pour chacune d'entre elles tous les mois sont traités simultanément. Nous proposons aussi de rajouter
du parallélisme au niveau des années pour effectuer l'ensemble du traitement des données en simultané.

- `activate_multi_process`: Un booléen (true / false) pour activer ou désactiver le parallélisme au niveau des années.
Attention, activer ce niveau de parallélisme supplémentaire avec beaucoup d'années à traiter va utiliser une grande
quantité de mémoire. Il est donc nécessaire d'avoir une machine suffisamment puissante.

## Ressources et références

Voici un résumé des ressources et des références que nous avons utilisées pour ce projet :

### Ressources

- Climate Weather Canada : https://climate.weather.gc.ca
- Open Elevation API : https://www.open-elevation.com

### Références

- Choix de la méthode d'interpolation : https://www.researchgate.net/publication/234295032_A_Simple_Method_for_Spatial_Interpolation_of_the_Wind_in_Complex_Terrain
- Hypothèses et formules pour la puissance des éoliennes : https://eolienne.f4jr.org/eolienne_etude_theorique
- Les documentations de NumPy, matplotlib, pandas et multiprocessing
- Premier pas avec le parallélisme en Python : https://wiki.ilylabs.com/en/knowledge_center/electronics/datax_arduino_pyserial