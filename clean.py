# On va trier et renommer les fichiers selon leur contenue. Si un fichier est vide, on le supprime, sinon on le renomme
# pour indiquer les mesures qu'il contient : _T -> Température , _W -> Vent

import numpy as np
import pandas as pd
import os


def full_missing_data(dataframe):
    """Fonction qui vérifie si toutes les données d'une colonne sont manquantes.

    :param dataframe: Colonne de données.
    :type dataframe: pd.Series
    :return: True si toutes les données sont manquantes, False sinon.
    :rtype: bool
    """

    check_missing = False
    nb_entries = len(dataframe)
    if len(np.where(dataframe == "M")) == nb_entries:
        check_missing = True
    return check_missing


for root, dirpath, filenames in os.walk('./data'):
    for filename in filenames:
        print(root+"/"+filename)
        df = pd.read_csv(root+"/"+filename, usecols=(9, 19))
        if df.isna().all(axis=None):
            # On reçoit toujours un csv même lorsqu'il n'y a pas de données mesurées. On supprime les fichiers vides.
            print(f"Supprimer {filename}")
            os.remove(root+"/"+filename)
        # On ne passe pas sur les fichiers déjà traités lors d'une exécution antérieure
        elif "_T" not in filename and "_W" not in filename:
            new_filename = [filename.split(".")[0]]
            # Hypothèse : Si la température max est mesuré, on a toute les températures.
            if not df["Temp (°C)"].isnull().all() and not full_missing_data(df["Temp (°C)"]):
                new_filename.append("_T")
            # Hypothèse : Idem, mais pour le vent.
            if not df["Wind Spd (km/h)"].isnull().all() and not full_missing_data(df["Wind Spd (km/h)"]):
                new_filename.append("_W")
            new_filename.append(".csv")
            new_filename = "".join(new_filename)
            if filename != new_filename:
                print(f"Renommer {root}\{filename} -> {root}\{new_filename}")
                os.rename(root+"/"+filename, root+"/"+new_filename)
        if not os.listdir(root):
            print(f"Supprimer dossier {root}")
            os.removedirs(root)
