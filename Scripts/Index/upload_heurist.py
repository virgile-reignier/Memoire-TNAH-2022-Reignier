import os
from Boîte_a_outils import chemin_actuel, dicts_to_csv, extract_data, PAYS
import pandas as pd
from defaultlist import defaultlist
from tqdm import tqdm
import json, csv

# source = os.path.join(chemin_actuel, "Paris_AN_JJ_inventaire_JJ37-50_index.xlsx")
Toponymes_enrichis = os.path.join(chemin_actuel, "geonames_final.csv")
# entrees_xl = pd.read_excel(source)

PAYS.append("France"), PAYS.append("")
CHANGE_COUNTRY = [PAYS, ["Greece", "Israel", "Turkey", "Italy", "Albania", "Belgium", "Spain", "Netherlands", "UK",
                         "Germany", "Switzerland", "Ireland", "", "Palestinian Territory, Occupied", "Germany",
                         "Turkey", "Portugal", "Luxembourg", "UK", "Spain", "Cyprus",
                         "Macedonia, Frmr Yugoslav Rep. of", "Croatia", "Egypt", "Serbia", "France", ""]]


def wash_result(list_of_list):
    """
    function to normalize empty data on frame and quotes
    """
    for list in list_of_list:
        for dico in list:
            for data in dico:
                if str(dico[data]) == "nan" or dico[data] == []:  # J'élimine des données vides
                    dico[data] = ""
                elif "“" in dico[data]:
                    dico[data] = dico[data].replace("“", "").replace("”", "")
                    # J'élimine les guillemets de certaines entrées
    return list_of_list


"""list_xl = {}  # Je transforme mes données en dictionnaire pour naviguer plus aisément à l'intérieur
for entree in entrees_xl.index:
    list_xl[entrees_xl.loc[entree]["xml:id"]] = [entrees_xl.loc[entree][h] for h in entrees_xl.head()]"""

# Etape 1 : Extraction des entrées pour préparer les tables Heurist

"""personnes = []  # J'extraie tous les noms de personnes
for entree in list_xl:
    ligne = entrees_xl.index[entrees_xl["xml:id"] == entree].tolist()[0]
    nom = entrees_xl.loc[entrees_xl.index[ligne], 'Entrée_simplifiée'].replace("(feu)", "").replace("(feue)", ""). \
        replace("(feu ", "(").replace("(feus)", "").replace("(feus ", "(")  # Elimination de marques inutiles
    # j'élimine ici les éléments personnes qui sont des entrées spécifiques pour les placer au niveau de la relation 
    # avec l'entrée d'inventaire
    if str(entrees_xl.loc[entrees_xl.index[ligne], 'Id terme générique']) == "nan" and \
            entrees_xl.loc[entrees_xl.index[ligne], 'Type'] == "person":
        personnes.append({"nom": nom,
                          "note": entrees_xl.loc[entrees_xl.index[ligne], 'Détails'],
                          "description": entrees_xl.loc[entrees_xl.index[ligne], 'supplément'],
                          "indexReference": "Paris_AN_JJ_inventaire_JJ37-50_index.xlsx#" + entree})

sujets = []  # J'extraie tous les sujets mentionnés
# C'est ici où ça va être moins facile car on veut des termes spécifiques mais pas ceux qui contiennent des renvois
for entree in list_xl:
    ligne = entrees_xl.index[entrees_xl["xml:id"] == entree].tolist()[0]
    if list_xl[entree][2] == "subject" and not \
            (str(entrees_xl.loc[entrees_xl.index[ligne], 'Id terme générique']) != "nan" and
             entrees_xl.loc[entrees_xl.index[ligne], 'Entrée'].split(" , — ")[-1].startswith("v. ")):
        # Je supprime les entrées génériques qui sont des renvois pour les placer au niveau de la relation
        sujets.append({"nom": entrees_xl.loc[entrees_xl.index[ligne], 'Entrée_simplifiée'],
                       "note": entrees_xl.loc[entrees_xl.index[ligne], 'Détails'],
                       "description": entrees_xl.loc[entrees_xl.index[ligne], 'supplément'],
                       "indexReference": "Paris_AN_JJ_inventaire_JJ37-50_index.xlsx#" + entree})

Toponymes_enrichis = extract_data(Toponymes_enrichis)  # Je récupère les localités enrichies de coordonnées
dico_lieux = {}
for tpn in Toponymes_enrichis[1:]:
    dico_lieux[tpn[1]] = tpn


def search_ref(data):
    '''
    Fonction to search which reference is use on this data
    '''
    if "geonames" in data:
        referentiel = "geonames"
    elif "dicotopo" in data:
        referentiel = "dicotopo"
    else:
        referentiel = ""
    return referentiel


def search_coor(data_with_coor):
    '''
    Fonction to extract data fron the frame geonames
    '''
    which_ref = search_ref(data_with_coor[17])
    if "," in data_with_coor[15]:  # Je gère le cas où j'ai plusieurs coordonnées
        case_insee = data_with_coor[14].replace("[", "").replace("]", "").split(", ")
        if not case_insee or case_insee == ['']:  # if case is empty
            case_insee = defaultlist(lambda: "")
        case_lon = data_with_coor[15].replace("[", "").replace("]", "").split(", ")
        case_lat = data_with_coor[16].replace("[", "").replace("]", "").split(", ")
        case_ref = data_with_coor[17].replace("[", "").replace("]", "").split("), (")
        if data_with_coor[8] == "Oui":  # Si c'est une étendue, je fais la moyenne
            lats, lons, refs, code_insee = [], [], [], []
            for sommet in case_lon:
                lon = sommet.replace("'", "")
                lat = case_lat[case_lon.index(sommet)]
                lat = lat.replace("'", "")
                id_ref = case_ref[case_lon.index(sommet)].replace("(", "").replace(")", "")
                id_ref = id_ref.replace("'", "").replace(which_ref, "").replace(", ", "")
                insee = case_insee[case_lon.index(sommet)]
                insee = insee.replace("'", "")
                lats.append(float(lat)), lons.append(float(lon)), refs.append(id_ref), code_insee.append(insee)
            coordonnées = [str(sum(lons) / len(lons)) + " " + str(sum(lats) / len(lats))]
            refs, code_insee = " ".join(refs), " ".join(code_insee)
        else:  # Sinon je crée un point par couple de coordonnées
            coordonnées, refs, code_insee = [], [], []
            for sommet in case_lon:
                lon = sommet.replace("'", "")
                lat = case_lat[case_lon.index(sommet)]
                lat = lat.replace("'", "")
                id_ref = case_ref[case_lon.index(sommet)].replace("(", "").replace(")", "")
                id_ref = id_ref.replace("'", "").replace(which_ref, "").replace(", ", "")
                insee = case_insee[case_lon.index(sommet)]
                insee = insee.replace("'", "")
                coordonnées.append(lon + " " + lat), refs.append(id_ref), code_insee.append(insee)
        ref = (which_ref, refs)
    else:  # Sinon je met tout dans une variable coordonnée
        lon = data_with_coor[15].replace("[", "").replace("]", "").replace("'", "")
        lat = data_with_coor[16].replace("[", "").replace("]", "").replace("'", "")
        id_ref = data_with_coor[17].replace("[", "").replace("]", "").replace("(", "").replace(")", "") \
            .replace("'", "").replace(which_ref, "").replace(", ", "")
        code_insee = data_with_coor[14].replace("[", "").replace("]", "").replace("'", "")
        ref = (which_ref, id_ref)
        coordonnées = [lon + " " + lat]
    if data_with_coor[19] == "commune" and data_with_coor[3] != data_with_coor[7]:
        nom_normalise = data_with_coor[7]
    else:
        nom_normalise = data_with_coor[3]
    id_wikidata = data_with_coor[18]
    return coordonnées, ref, code_insee, nom_normalise, id_wikidata


def admin_place(place):
    '''
    Function to extract admin information from the frame geonames
    '''
    if not place[5]:
        place[5] = ""
    return {"pays": place[5], "departement": place[4], "canton": place[6], "commune": place[7],
            "arrondissement": place[11], "comte": place[12], "province": place[13]}


lieux = []  # J'extraie tous les lieux mentionnés
# C'est ici où ça va être moins facile car on veut des termes spécifiques mais pas ceux qui contiennent des renvois
for entree in list_xl:
    ligne = entrees_xl.index[entrees_xl["xml:id"] == entree].tolist()[0]
    geonames, dicotopo = defaultlist(lambda: ""), defaultlist(lambda: "")  # Use to be called and get empty string
    if list_xl[entree][2] == "place" and not \
            (str(entrees_xl.loc[entrees_xl.index[ligne], 'Id terme générique']) != "nan" and
             entrees_xl.loc[entrees_xl.index[ligne], 'Entrée'].split(" , — ")[-1].startswith("v. ")):
        if entree in dico_lieux:  # Je commence par les lieux qui ont été alignés avec les référentiels en ligne
            localisation = dico_lieux[entree]
            coor, ref, insee, nom, wikidata = search_coor(localisation)
            admin = admin_place(localisation)
        else:  # S'ils ne le sont pas, je cherche les coordonnées au niveau du terme générique
            id_generique = entree
            while id_generique not in dico_lieux:
                id_generique = list_xl[id_generique][7]
            generique = dico_lieux[id_generique]
            coor, ref, insee, nom, wikidata = search_coor(generique)
            admin = admin_place(generique)
        if ref[0] == "geonames":
            geonames = ref[1]
        elif ref[0] == "dicotopo":
            dicotopo = ref[1]
        if len(coor) > 1:
            lieux.append({"nom": entrees_xl.loc[entrees_xl.index[ligne], 'Entrée_simplifiée'],
                          "note": entrees_xl.loc[entrees_xl.index[ligne], 'Détails'],
                          "description": entrees_xl.loc[entrees_xl.index[ligne], 'supplément'],
                          "indexReference": "Paris_AN_JJ_inventaire_JJ37-50_index.xlsx#" + entree,
                          "id_wikidata": wikidata})
            for c in coor:
                lieux.append({"nom": entrees_xl.loc[entrees_xl.index[ligne], 'Entrée_simplifiée'],
                              "nom_retenu": nom,
                              "id_geonames": geonames[coor.index(c)],
                              "id_dicotopo": dicotopo[coor.index(c)],
                              "code_insee": insee[coor.index(c)],
                              "coordonnees": c,
                              "pays": CHANGE_COUNTRY[1][CHANGE_COUNTRY[0].index(admin["pays"])],
                              "departement": admin["departement"],
                              "canton": admin["canton"],
                              "commune": admin["commune"],
                              "arrondissement": admin["arrondissement"],
                              "comté": admin["comte"],
                              "province": admin["province"]
                              })
        else:
            lieux.append({"nom": entrees_xl.loc[entrees_xl.index[ligne], 'Entrée_simplifiée'],
                          "note": entrees_xl.loc[entrees_xl.index[ligne], 'Détails'],
                          "description": entrees_xl.loc[entrees_xl.index[ligne], 'supplément'],
                          "indexReference": "Paris_AN_JJ_inventaire_JJ37-50_index.xlsx#" + entree,
                          "id_wikidata": wikidata,
                          "nom_retenu": nom,
                          "id_geonames": geonames,
                          "id_dicotopo": dicotopo,
                          "code_insee": insee,
                          "coordonnees": coor[0],
                          "pays": CHANGE_COUNTRY[1][CHANGE_COUNTRY[0].index(admin["pays"])],
                          "departement": admin["departement"],
                          "canton": admin["canton"],
                          "commune": admin["commune"],
                          "arrondissement": admin["arrondissement"],
                          "comté": admin["comte"],
                          "province": admin["province"]
                          })

# J'enregistre tout cela dans des tables prévues à cet effet
entrees_heurist = wash_result([personnes, sujets, lieux])
i = 0
for table in ["person", "subject", "place"]:
        result = os.path.join(chemin_actuel, "import_Heurist", table + ".csv")
        dicts_to_csv(entrees_heurist[i], result)
        i += 1"""

# Etape 2 : importer les données dans Heurist et les exporter avec leurs H-ID !


# Etape 3 : Extraction des relations avec les entités et établissement d'une table avec leurs H-ID
"""relations_ps, relations_sl, relations_pl, relations_ss, relations_ll, relations_pp = [], [], [], [], [], []

table_personne = {}
for t in extract_data(os.path.join(chemin_actuel, "import_Heurist", "Export_stutzmann_himanis_t10_Person.csv"))[1:]:
    id = t[2].replace("Paris_AN_JJ_inventaire_JJ37-50_index.xlsx#", "")
    table_personne[id] = t
table_sujet = {}
for t in extract_data(os.path.join(chemin_actuel, "import_Heurist", "Export_stutzmann_himanis_t104_Subject.csv"))[1:]:
    id = t[2].replace("Paris_AN_JJ_inventaire_JJ37-50_index.xlsx#", "")
    table_sujet[id] = t
table_lieux = {}
fichier_lieux = extract_data(os.path.join(chemin_actuel, "import_Heurist", "Export_stutzmann_himanis_t12_Place.csv"))[1:]
for t in fichier_lieux:
    if t[2]:
        id = t[2].replace("Paris_AN_JJ_inventaire_JJ37-50_index.xlsx#", "")
        table_lieux[id] = t
    else:  # Pour le cas où le lieu est une proposition issue d'un terme ambigu de l'index
        n = fichier_lieux[fichier_lieux.index(t) - 1]
        while t[1] != n[1] or not n[2]:
            n = fichier_lieux[fichier_lieux.index(n) - 1]
        relations_ll.append({"Place H-ID": t[0],
                             "Place_2 H-ID": n[0]})

# J'extraie les relations entre les entités
for entree in list_xl:
    associations = str(list_xl[entree][4]) + " " + str(list_xl[entree][10])
    for asso in associations.split():
        if str(asso) not in ["nan", "Not", "Found"]:
            while entree not in table_personne and entree not in table_lieux and entree not in table_sujet \
                    and str(list_xl[entree][7]) != "nan":  # Si c'est une entrée spécifique ne contenant qu'un renvoi
                entree = list_xl[entree][7]
            while asso not in table_personne and asso not in table_lieux and asso not in table_sujet\
                    and str(list_xl[asso][7]) != "nan":  # Pareil pour la cible:
                asso = list_xl[asso][7]
            relation = [(list_xl[entree][2], list_xl[asso][2]), (entree, asso)]
            if relation[0] == ("subject", "person"):
                relations_ps.append({"Subject H-ID": table_sujet[relation[1][0]][0],
                                    "Person H-ID": table_personne[relation[1][1]][0]})
            elif relation[0] == ("person", "subject"):
                relations_ps.append({"Person H-ID": table_personne[relation[1][0]][0],
                                    "Subject H-ID": table_sujet[relation[1][1]][0]})
            elif relation[0] == ("place", "subject"):
                relations_sl.append({"Place H-ID": table_lieux[relation[1][0]][0],
                                    "Subject H-ID": table_sujet[relation[1][1]][0]})
            elif relation[0] == ("subject", "place"):
                relations_sl.append({"Subject H-ID": table_sujet[relation[1][0]][0],
                                    "Place H-ID": table_lieux[relation[1][1]][0]})
            elif relation[0] == ("person", "place"):
                relations_pl.append({"Person H-ID": table_personne[relation[1][0]][0],
                                    "Place H-ID": table_lieux[relation[1][1]][0]})
            elif relation[0] == ("place", "person"):
                relations_pl.append({"Place H-ID": table_lieux[relation[1][0]][0],
                                    "Person H-ID": table_personne[relation[1][1]][0]})
            elif relation[0] == ("place", "place"):
                relations_ll.append({"Place H-ID": table_lieux[relation[1][0]][0],
                                    "Place_2 H-ID": table_lieux[relation[1][1]][0]})
            elif relation[0] == ("subject", "subject"):
                relations_ss.append({"Subject H-ID": table_sujet[relation[1][0]][0],
                                    "Subject_2 H-ID": table_sujet[relation[1][1]][0]})
            elif relation[0] == ("person", "person"):
                relations_pp.append({"Person H-ID": table_personne[relation[1][0]][0],
                                    "Person_2 H-ID": table_personne[relation[1][1]][0]})
relations = wash_result([relations_ps, relations_sl, relations_pl, relations_ss, relations_ll, relations_pp])


i = 0
for table in ["relations_person_subject", "relations_subject_place", "relations_person_place",
              "relations_subject_subject", "relations_place_place", "relations_person_person"]:
    result = os.path.join(chemin_actuel, "import_Heurist", table + ".csv")
    dicts_to_csv(relations[i], result)
    i += 1"""

# Etape 4 : Puis j'ajoute les données sur les actes

'''texts = []
with open(
        "/home/reignier/Bureau/Himanis/himanis-all-acts-json-JJ35-JJ91-metadata-htr_with_date_and_language_final.json",
        'r') as f:
    data = json.load(f)
for registre in data:
    acts = data[registre]
    for dict in tqdm(acts):
        for acte in dict:
            act = dict[acte]
            act["Date Heurist"] = defaultlist(lambda: "")
            for date in act["Date-normalisee"]:
                if date["year"]:  # Fonction pour construire ma forme iso
                    forme_normalisee = str(date["year"])
                    if date["month"]:
                        if len(str(date["month"])) == 1:
                            date["month"] = "0" + str(date["month"])
                        forme_normalisee = forme_normalisee + "-" + \
                                           str(date["month"])
                        if date["day"]:
                            if len(str(date["day"])) == 1:
                                date["day"] = "0" + str(date["day"])
                            forme_normalisee = forme_normalisee + "-" + \
                                               str(date["day"])
                    act["Date Heurist"].append(forme_normalisee)
            inventory_ref = act["Inventory_Name"]
            if act["Inventory_Nr"]:
                inventory_ref += "#" + act["Inventory_Nr"]
            languages = defaultlist(lambda: "") + act["normalized_language"]["language"]
            texts.append({
                "id_arkindex": act["Provisory_index_1"],
                "registre": act["Volume"],
                "num": act["Act_N"],
                "folio start": act["Folio_start"],
                "folio end": act["Folio_end"],
                "language_1": languages[0],
                "language_2": languages[1],
                "language_3": languages[2],
                "date_originelle" : act["Date"],
                "date_1": act["Date Heurist"][0],
                "date_2": act["Date Heurist"][1],
                "regeste": act["Regeste"],
                "inventoryReference": inventory_ref
            })

result = os.path.join(chemin_actuel, "import_Heurist", "actes.csv")
dicts_to_csv(texts, result)'''

# Etape 5 : Import des actes dans Heurist et export d'une table contenant des H-ID pour alignement

# Etape 5 bis : Mise à jour provisory index dans Heurist

"""table_actes = {}
for t in extract_data(os.path.join(chemin_actuel, "import_Heurist", "Export_stutzmann_himanis_t106_Act.csv"))[1:]:
    table_actes[t[1]] = t

new_index = []
with open(
        "/home/reignier/Bureau/Himanis/himanis-all-acts-json-JJ35-JJ91-metadata-htr_with_date_language_index_and_text_zone_modified.json",
        'r') as f:
    data = json.load(f)
for registre in data:
    acts = data[registre]
    for dict in tqdm(acts):
        for acte in dict:
            act = dict[acte]
            act_id = table_actes[act["Provisory_index_1"]][0]
            new_index.append({
                "Act H-ID": act_id,
                "Himanis_id": act["Provisory_index_3"]
            })

result = os.path.join(chemin_actuel, "import_Heurist", "act_update_index.csv")
dicts_to_csv(new_index, result)"""

# Etape 6 : Construction de la table des zones

"""table_actes = {}
for t in extract_data(os.path.join(chemin_actuel, "import_Heurist", "Export_stutzmann_himanis_t106_Act.csv"))[1:]:
    table_actes[t[1]] = t

# Use a table to associate image to name of the folio
table = "/home/reignier/Bureau/Himanis/table_concordance_images_folio.csv"
with open(table, 'r', encoding="utf8") as f:
    spamreader = csv.reader(f, delimiter='\t')
    table_conversion = {}
    for row in spamreader:
        table_conversion[row[0]] = row[1]

image_zones = []
with open(
        "/home/reignier/Bureau/Himanis/himanis-all-acts-json-JJ35-JJ91-metadata-htr_with_date_language_index_and_text_zone_modified.json",
        'r') as f:
    data = json.load(f)
for registre in data:
    acts = data[registre]
    for dict in tqdm(acts):
        for acte in dict:
            act = dict[acte]
            act_id = table_actes[str(act["Provisory_index_3"])][0]
            zones = act["Text_Region"]
            for zone in zones:
                address = zone["Address_bvmm"].split(",")[0]  # Je sectionne l'url au niveau des coordonnées
                if "https://iiif.irht.cnrs.fr" in address:
                    while address[-1] != "/":  # J'enlève tout ce qui précède le dernier slash
                        address = address[:-1]
                    address = address[:-1]  # J'enlève aussi le dernier slash
                    if address in table_conversion:
                        folio = table_conversion[address]
                    else:
                        folio = "unknown"
                if "Texte" in zone:
                    transcription = "\n".join(zone["Texte"])
                else:
                    transcription = ""
                image_zones.append({
                    "Folio": folio,
                    "Part": zone["type_act"],
                    "coordinates": zone["Graphical_coord"],
                    "Image": zone["Reference"],
                    "Address bvmm": zone["Address_bvmm"],
                    "Act H-ID": act_id,
                    "Texte": transcription
                })

for i in range(1, 17):
    result = os.path.join(chemin_actuel, "import_Heurist", "image_zones", "image_zones_" + str(i) + ".csv")
    end = i*2500
    if end > len(image_zones):
        to_save = image_zones[(i - 1) * 2500:]
    else:
        to_save = image_zones[(i-1)*2500:end]
    dicts_to_csv(to_save, result)

# Etape 7 : Construction des tables de relations entre entités et actes"""

"""relations_as, relations_ap, relations_al = [], [], []

table_actes = {}
for t in extract_data(os.path.join(chemin_actuel, "import_Heurist", "Export_stutzmann_himanis_t106_Act.csv"))[1:]:
    if "Paris_AN_JJ_inventaire_JJ37-50" in t[3]:
        id = t[3].replace("Paris_AN_JJ_inventaire_JJ37-50.xml#", "").split(" (")[0]
        table_actes[id] = t
table_personne = {}
for t in extract_data(os.path.join(chemin_actuel, "import_Heurist", "Export_stutzmann_himanis_t10_Person.csv"))[1:]:
    id = t[2].replace("Paris_AN_JJ_inventaire_JJ37-50_index.xlsx#", "")
    table_personne[id] = t
table_sujet = {}
for t in extract_data(os.path.join(chemin_actuel, "import_Heurist", "Export_stutzmann_himanis_t104_Subject.csv"))[1:]:
    id = t[2].replace("Paris_AN_JJ_inventaire_JJ37-50_index.xlsx#", "")
    table_sujet[id] = t
table_lieux = {}
fichier_lieux = extract_data(os.path.join(chemin_actuel, "import_Heurist", "Export_stutzmann_himanis_t12_Place.csv"))[1:]
for t in fichier_lieux:
    if t[2]:
        id = t[2].replace("Paris_AN_JJ_inventaire_JJ37-50_index.xlsx#", "")
        table_lieux[id] = t


# J'ai aussi besoin de la table des coordonnées pour en extraire les incertitudes repérées
Toponymes_enrichis = extract_data(Toponymes_enrichis)
dico_lieux = {}
for tpn in Toponymes_enrichis[1:]:
    dico_lieux[tpn[1]] = tpn


# J'extraie les relations entre les entités
for entree in list_xl:
    if str(list_xl[entree][12]) != "nan":
        associations = list_xl[entree][12].split("|")
        for asso in associations:
            if asso not in ['', '           ', '            ']:
                if asso not in table_actes and "bis" in asso or "ter" in asso or "quat" in asso:
                    if asso.replace(' ', '') in table_actes:
                        asso = asso.replace(' ', '')
                    else:
                        asso = asso.replace("bis", "").replace("ter", "").replace("quat", "").replace(" ", "")
                act = table_actes[asso][0]
                if list_xl[entree][2] == "subject":
                    relations_as.append({"Act H-ID": act,
                                        "Subject H-ID": table_sujet[entree][0]})
                elif list_xl[entree][2] == "person":
                    if str(list_xl[entree][7]) != "nan":
                        qualite = list_xl[entree][0].split(" , — ")[1:]
                    else:
                        qualite = ""
                    while str(list_xl[entree][7]) != "nan":
                        entree = list_xl[entree][7]
                    relations_ap.append({"Act H-ID": act,
                                        "Person H-ID": table_personne[entree][0],
                                         "Quality": "".join(qualite)})
                elif list_xl[entree][2] == "place":
                    if entree in table_lieux:
                        if entree in dico_lieux and (dico_lieux[entree][9] == "Oui" or "," in dico_lieux[entree][15]):
                            incertitude = "Not sure"
                        else:
                            incertitude = ""
                        relations_al.append({"Act H-ID": act,
                                            "Place H-ID": table_lieux[entree][0],
                                            "Incertitude": incertitude})
relations = wash_result([relations_as, relations_ap, relations_al])

i = 0
for table in ["relations_act_subject", "relations_act_person", "relations_act_place"]:
    result = os.path.join(chemin_actuel, "import_Heurist", table + ".csv")
    dicts_to_csv(relations[i], result)
    i += 1"""

# Etape 8 : Relations entités spécifiques vers génériques

"""table_sujet = {}
for t in extract_data(os.path.join(chemin_actuel, "import_Heurist", "Export_stutzmann_himanis_t104_Subject.csv"))[1:]:
    id = t[2].replace("Paris_AN_JJ_inventaire_JJ37-50_index.xlsx#", "")
    table_sujet[id] = t
table_lieux = {}
for t in extract_data(os.path.join(chemin_actuel, "import_Heurist", "Export_stutzmann_himanis_t12_Place.csv"))[1:]:
    if t[2]:
        id = t[2].replace("Paris_AN_JJ_inventaire_JJ37-50_index.xlsx#", "")
        table_lieux[id] = t

relations_sub_place, relations_sub_subjects = [], []
for entree in list_xl:
    if str(list_xl[entree][7]) != "nan" and list_xl[entree][2] in ["place", "subject"]:
        if list_xl[entree][2] == "place" and entree in table_lieux:
            relations_sub_place.append({"Place_general H-ID": table_lieux[entree][0],
                                        "Place_specific H-ID": table_lieux[list_xl[entree][7]][0]})
        elif list_xl[entree][2] == "subject" and entree in table_sujet:
            relations_sub_subjects.append({"Subject_general H-ID": table_sujet[entree][0],
                                           "Subject_specific H-ID": table_sujet[list_xl[entree][7]][0],
                                           "Type_of_relation": "Relation from specific to generic"})
relations = wash_result([relations_sub_place, relations_sub_subjects])

i = 0
for table in ["relations_subplace_place", "relations_subsubject_subject"]:
    result = os.path.join(chemin_actuel, "import_Heurist", table + ".csv")
    dicts_to_csv(relations[i], result)
    i += 1"""
