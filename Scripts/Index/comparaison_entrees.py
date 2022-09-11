import os
from bs4 import BeautifulSoup
from Boîte_a_outils import chemin_actuel
import pandas as pd

"""
Code pour comparer la cohérence des entrées entre le xml et le résultat final et pour traiter les cas des redondances
dans les noms de personnes. Les modèles de la forme "Barres (Jean de)" sont comparés à leur correspondant "Jean de
Barres" pour vérifier que les entrées d'inventaires sont les mêmes. Si tel est le cas c'est un rajout automatique,
donc je les élimine. Puis je crée un lien de type "terme rejeté" entre les deux entrées.
"""

source = os.path.join(chemin_actuel, "Ajout_id.xml")
traitement = os.path.join(chemin_actuel, "index-complet.xlsx")

'''with open(source, 'r', encoding="ISO-8859-1") as f:
    xml_doc = f.read()
soup = BeautifulSoup(xml_doc, features="xml")
entrees_xml = soup.find_all('seg')

list_xml = {}
# Je construit un dictionnaire associant chaque xml:id au contenu de l'entrée (nom et liste references inventaire)
for entree in entrees_xml:
    if "xml:id" in entree.attrs:  # Je ne cherche que dans les entrées qui ont un xml:id
        nums = entree.find_all('idno')
        list_nums = []
        for num in nums:
            list_nums.append(num.get_text())
        list_xml[entree["xml:id"]] = (entree.term.get_text(), list_nums)'''

entrees_xl = pd.concat([pd.read_excel(traitement, 'SUJETS'), pd.read_excel(traitement, 'PERSONNES-LIEUX')],
                        ignore_index=True)
list_xl = {}  # Je fais la même chose avec les entrées une fois traitées dans le csv
for entree in entrees_xl.index:
    list_xl[entrees_xl.loc[entree]["xml:id"]] = (entrees_xl.loc[entree]["Entrée"],
                                                   str(entrees_xl.loc[entree]["Idno"]).split('|')[:-1])

'''# Puis je fais un test pour vérifier qu'aucune entrée du xml ne s'est perdue en chemin

for entree in list_xml:
    erreurs = []
    if entree not in ["d1e146475", "d1e151369", "d1e170511", "d1e184551", "d1e194385", "d1e198908", "d1e202844",
                      "d1e279126", "d1e285154"]:
        # J'élimine ici les éléments supprimés depuis le xml
        for reference in list_xml[entree][1]:
            if reference not in list_csv[entree][1]:
                if entree not in erreurs:
                    erreurs.append(entree)
    for entree in erreurs:
        print(entree, list_xml[entree], list_csv[entree])'''

#  J'en fais un second pour éliminer les répétition entre les entrées renvoyant à la même entité
K = []  # Liste contenant les K à traiter
for entree in list_xl:
    if "(" in list_xl[entree][0] and list_xl[entree][1] and list_xl[entree][0].split("(")[1].split(")")[0][0].isupper() \
            and len(list_xl[entree][0].split("(")[1].split(")")[0].split()) > 1:
        # Je récupère tout ce qui ressemble à un nom
        if list_xl[entree][0].split("(")[1].split(")")[0][-1] == "'":
            separateur = ""
        else:
            separateur = " "
        mot_a_chercher = list_xl[entree][0].split("(")[1].split(")")[0] + separateur + \
                         list_xl[entree][0].split()[0]
        for entree_bis in list_xl:
            if list_xl[entree_bis][0].startswith(mot_a_chercher):
                # Et je cherche s'il est présent dans une autre entrée
                k = (entree, mot_a_chercher, entree_bis)
                K.append(k)

for k in K:  # Puis je modifie le dataframe pour supprimer les idno et rajouter un terme retenu
    ligne = entrees_xl.index[entrees_xl["xml:id"] == k[0]].tolist()[0]
    entrees_xl.loc[entrees_xl.index[ligne], 'Idno'] = ""
    entrees_xl.loc[entrees_xl.index[ligne], 'Termes retenu'] = k[1]
    entrees_xl.loc[entrees_xl.index[ligne], 'Id termes retenu'] = k[2]

file_name = os.path.join(chemin_actuel, 'index_complet_corrige.xlsx')  # Et j'en fais un fichier excel
entrees_xl.to_excel(file_name)