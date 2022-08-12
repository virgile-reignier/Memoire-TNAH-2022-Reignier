import os
from Boîte_a_outils import chemin_actuel
import pandas as pd


source = os.path.join(chemin_actuel, "index_complet_corrige.xlsx")
entrees_xl = pd.read_excel(source)

list_xl = {}  # Je transforme mes données en dictionnaire pour naviguer plus aisément à l'intérieur
for entree in entrees_xl.index:
    list_xl[entrees_xl.loc[entree]["xml:id"]] = [entrees_xl.loc[entree][h] for h in entrees_xl.head()]

# Extraction des éléments contenus dans l'entrée
for entree in list_xl:
    forme_retenue = list_xl[entree][0]
    if "[" in list_xl[entree][0] and str(list_xl[entree][7]) == "nan":
        # Je commence par isoler les éléments entre crochets
        precision = list_xl[entree][0].split('[')[1].split(']')[0]
        forme_retenue = list_xl[entree][0].split('[')[0]
        # J'adapte ma forme retenue en fonction de la présence d'éléments après les crochets
        if list_xl[entree][0].split(precision)[-1] != "]":
            fin = list_xl[entree][0].split(']')[1]
            while fin[0] == " ":
                fin = fin[1:]
            if fin[0] == "," and "—" not in fin and forme_retenue[-1] == " ":  # J'élimine certains espaces
                forme_retenue = forme_retenue[:-1]  # Je rajoute ces éléments à la donnée
            forme_retenue = forme_retenue + fin
        list_xl[entree].append(precision)
    if str(list_xl[entree][4]) != "nan" and " v." in forme_retenue:  # Puis j'élimine les renvois
        forme_retenue = "".join(forme_retenue.split(" v.")[:-1])
    while forme_retenue[-1] in (" ", "—", ","):  # J'élimine les éléments parasite à la fin de l'entrée
        forme_retenue = forme_retenue[:-1]
    if "," in forme_retenue and str(list_xl[entree][7]) == "nan":
        # Puis j'isole les éléments de détails restants pour garder une forme retenue la plus propre possible
        precision = ",".join(forme_retenue.split(",")[1:])
        while precision[0] in ("—", " ", ","):
            precision = precision[1:]
        if len(list_xl[entree]) == 13:  # Je rajoute encore un élément à la donnée
            list_xl[entree].append("")
        list_xl[entree].append(precision)
        if "(" in forme_retenue.split(",")[-1]:
            fin = " (" + forme_retenue.split("(")[1]
        else:
            fin = ""
        forme_retenue = forme_retenue.split(",")[0]
        while forme_retenue[-1] == " ":
            forme_retenue = forme_retenue[:-1]
        forme_retenue = forme_retenue + fin
    list_xl[entree][0] = forme_retenue  # Je met à jour mon entrée
    if str(list_xl[entree][7]) != "nan":
        # Je finis par simplifier les termes spécifiques
        terme_generique = list_xl[str(list_xl[entree][7])][0]
        while terme_generique[-1] == " ":
            terme_generique = terme_generique[:-1]
        if " , —" in forme_retenue and " , —" not in terme_generique:
            forme_retenue = terme_generique + " , — " + forme_retenue.split(" , — ")[-1]
        elif " , —" in forme_retenue and " , —" in terme_generique:
            if forme_retenue.split(" , — ")[-1] != terme_generique.split(" , — ")[-1]:
                forme_retenue = terme_generique + " , — " + forme_retenue.split(" , — ")[-1]
            else:
                forme_retenue = terme_generique
        else:
            forme_retenue = terme_generique
        list_xl[entree][0] = forme_retenue  # Je met à jour mon entrée
    ligne = entrees_xl.index[entrees_xl["xml:id"] == entree].tolist()[0] # Je met à jour le dataframe
    entrees_xl.loc[entrees_xl.index[ligne], 'Entrée_simplifiée'] = list_xl[entree][0]
    if len(list_xl[entree]) > 13:
        entrees_xl.loc[entrees_xl.index[ligne], 'Détails'] = list_xl[entree][13]
    if len(list_xl[entree]) > 14:
        entrees_xl.loc[entrees_xl.index[ligne], 'supplément'] = list_xl[entree][14]

result = os.path.join(chemin_actuel, "index_complet_simplifié_pour_import.xlsx")
entrees_xl.to_excel(result)