# On va trier et renommer les fichiers selon leur contenue. Si un fichier est vide, on le supprime, sinon on le renomme
# pour indiquer les mesures qu'il contient : _T -> Température , _W -> Vent

import pandas as pd
import os

for root, dirpath, filenames in os.walk('./data'):
    for filename in filenames:
        print(root+"/"+filename)
        df = pd.read_csv(root+"/"+filename)
        if df.iloc[:, 9:].isna().all(axis=None):
            # Dans les deux cas, les neuf premières colonnes sont remplies d'informations sur la date et la position
            # même lorsqu'il n'y a pas de données mesurées.
            print(f"Supprimer {filename}")
            os.remove(root+"/"+filename)
        elif "_T" not in filename and "_W" not in filename:
            new_filename = [filename.split(".")[0]]
            if "Hourly" in root:
                # Hypothèse : Si la température max est mesuré, on a toute les températures.
                if not df["Temp (°C)"].isnull().all():
                    new_filename.append("_T")
                # Hypothèse : Idem, mais pour le vent.
                if df["Wind Spd (km/h)"].isnull().all():
                    new_filename.append("_W")
            else:  # "Daily" in root
                # Hypothèse : Si la température max est mesuré, on a toutes les températures.
                if not df["Max Temp (°C)"].isnull().all():
                    new_filename.append("_T")
                # Hypothèse : Idem, mais pour le vent.
                if not df["Spd of Max Gust (km/h)"].isnull().all():
                    new_filename.append("_W")
            new_filename.append(".csv")
            new_filename = "".join(new_filename)
            if filename != new_filename:
                print(f"Renommer {root}\{filename} ->  {root}\{new_filename}")
                os.rename(root+"/"+filename, root+"/"+new_filename)
        if not os.listdir(root):
            print(f"Supprimer dossier {root}")
            os.removedirs(root)
