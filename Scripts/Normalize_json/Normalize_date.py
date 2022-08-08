import json

file = "/home/reignier/Bureau/Himanis/himanis-all-acts-json-JJ35-JJ91-metadata-htr.json"
result = "/home/reignier/Bureau/Himanis/poubelle_1.json"

with open(file, 'r') as f:
    data = json.load(f)

# J'ai eu quelques problèmes dans le format des éléments présents sous forme d'intervalles !

mois = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre",
        "décembre"]

for registre in data:
    contenu_registre = data[registre]
    for serie in contenu_registre:
        for acte in serie:
            data_acte = serie[acte]
            date_normalisee = {"annee": None, "mois": None, "jour": None, "date à traiter manuellement": None}
            taq, tpq = None, None
            date = data_acte["Date"].lower()
            if "," in date and date[-1] != "," and date.split(",")[1][0] != " ":
                # Pour éliminer les cas où la virgule n'est pas suivie d'un espace
                date = date.split(",")[0] + ", " + date.split(",")[1]
            if "la véritable date est" in date:
                date = date.split("la véritable date est : ")[1]
            if "pour" in date:
                date = date.split("pour ")[1]
            if "ou " in date:
                date = date.split(" ou")[0] + "-" + date.split("ou ")[1]
            if "de" in date and "à" in date:
                date = date.split("de")[0] + date.split("de")[1].split(" à")[0] + "-" + date.split("à ")[1]
            date = date.replace(".", "").replace(",", "").replace("\"&gt;", "").replace("(cancellé)","")\
                .replace("sic", "").replace("/", "").replace("fin ", "").replace("vers", "").replace("- paris", "").\
                replace("louvre- lès-paris", "").replace("?", "").replace("paris", "")
            # J'élimine les éléments gênants
            date = date.replace("decembre", "décembre").replace("fevrier", "février").replace("1er", "01") \
                .replace("1 er", "01").replace("aôut", "août").replace("avil", "avril").replace("aoüt", "août")\
                .replace("août1358", "août 1358").replace("sl n d", "").replace("avant pâques", "").replace("()", "")\
                .replace("1351(ns)", "1351 (ns)").replace("printemps", "mars-juin")\
                .replace("premier trimestre", "janvier-mars").replace("1310)", "1310").replace("févrrier", "février")
            # Je normalise les formes courantes
            date = date.split()
            if len(date) > 1 and date[0] == "sd":
                # J'élimine les éléments sans date quand elle est devinée
                date = date[1:]
            if not date:  # Si la valeur est vide, je laisse le champs vides
                date_normalisee["annee"], date_normalisee["mois"], date_normalisee["jour"] = None, None, None
            elif len(date) > 1:  # Si la forme contient plus d'un élément
                if date[0].isdigit() and len(date[0]) == 4:  # Formes qui commencent par l'année
                    date_normalisee["annee"] = int(date[0])
                    if date[1] in mois:  # Puis par un second élément mois
                        date_normalisee["mois"] = mois.index(date[1]) + 1
                        if len(date) > 2:  # Et un troisième jour
                            if date[2].isdigit() and len(date[2]) == 2:
                                date_normalisee["jour"] = int(date[2])
                            elif date[2] in ["(ns)", "(nst)"] or date[2:] == ['(n', 'st)']:  # Récupération du style
                                date_normalisee["jour"] = None
                                date_normalisee["style"] = "nouveau"
                            elif date[2] == "(as)":
                                date_normalisee["jour"] = None
                                date_normalisee["style"] = "ancien"
                                date_normalisee["annee"] = date_normalisee["annee"] + 1
                            else:
                                date_normalisee["date à traiter manuellement"] = "OOOO"
                                print(date)
                        else:
                            date_normalisee["jour"] = None
                    elif "-" in date[1] and not (len(date) > 2 and date[2].isnumeric()):
                        # Si les mois sont sous forme d'intervalle
                        intervalle = date[1].split("-")
                        if intervalle[1].isnumeric() and len(intervalle[1]) == 4:
                            # Si le deuxième élément de l'intervalle est une année !
                            if len(date) > 2 and "-" in date[2]:  # Si jamais il comporte aussi une intervalle
                                second_mois = date[2].split("-")[1]
                            else:
                                second_mois = date[2]
                            tpq = {"type": "notBefore", "year": date_normalisee["annee"],
                                    "month": mois.index(intervalle[0]) + 1, "day": None}
                            taq = {"type": "notAfter", "year": intervalle[1],
                                    "month": mois.index(second_mois) + 1, "day": None}
                        else:
                            tpq = {"type": "notBefore", "year": date_normalisee["annee"],
                                   "month": mois.index(intervalle[0]) + 1, "day": None}
                            taq = {"type": "notAfter", "year": date_normalisee["annee"],
                                   "month": mois.index(intervalle[1]) + 1, "day": None}
                    elif len(date) > 2 and date[1].isdigit() and len(date[1]) < 3:  # Ou par un second élément jour
                        date_normalisee["jour"] = int(date[1])
                        if date[2] in mois:  # Et un troisième mois
                            date_normalisee["mois"] = mois.index(date[2]) + 1
                        else:
                            date_normalisee["date à traiter manuellement"] = "OOOO"
                            print(date)
                    elif date[1] == "(ns)" or date[1:] == ['(n', 'st)']:
                        date_normalisee["style"] = "nouveau"
                        date_normalisee["jour"], date_normalisee["mois"] = None, None
                    elif date[1] == "(as)":
                        date_normalisee["style"] = "ancien"
                        date_normalisee["annee"] = date_normalisee["annee"] + 1
                        date_normalisee["jour"], date_normalisee["mois"] = None, None
                    else:
                        date_normalisee["date à traiter manuellement"] = "OOOO"
                        print(date)
                elif date[0] in mois:  # Formes qui commencent par le mois
                    date_normalisee["mois"], date_normalisee["jour"] = mois.index(date[0]) + 1, None
                    if date[1].isdigit() and len(date[1]) == 4:  # Puis l'année
                        date_normalisee["annee"] = int(date[1])
                    else:
                        date_normalisee["date à traiter manuellement"] = "OOOO"
                        print(date)
                    if len(date) > 2:  # Et éventuellement le style
                        if date[2] == "(ns)" or date[2:] == ['(n', 'st)']:
                            date_normalisee["style"] = "nouveau"
                        elif date[2] == "(as)":
                            date_normalisee["style"] = "ancien"
                            date_normalisee["annee"] = date_normalisee["annee"] + 1
                        else:
                            date_normalisee["date à traiter manuellement"] = "OOOO"
                            print(date)
                elif date[0].isdigit() and len(date[0]) < 3 and date[1] in mois:
                    # Formes qui commencent par le jour et le mois
                    date_normalisee["jour"], date_normalisee["mois"] = int(date[0]), mois.index(date[1]) + 1
                    if len(date) > 2:  # Puis l'année
                        if date[2].isdigit() and len(date[2]) == 4:
                            date_normalisee["annee"] = int(date[2])
                        else:
                            date_normalisee["date à traiter manuellement"] = "OOOO"
                            print(date)
                    else:
                        date_normalisee["date à traiter manuellement"] = "OOOO"
                        print(date)
                elif date == ['s', 'd']:  # Formes sans date
                    date_normalisee["annee"], date_normalisee["mois"], date_normalisee["jour"] = None, None, None
                elif "-" in date[0] and "+" not in date[0]:
                    intervalle = date[0].split("-")
                    date_jour, date_mois = None, None
                    if len(date) > 1:
                        if intervalle[0].isnumeric():
                            if len(date) > 2:
                                if date[1].isnumeric():
                                    date_jour = date[1]
                                date_mois = date[2]
                            else:
                                date_mois = date[1]
                            tpq = {"type": "notBefore", "year": intervalle[0],
                                   "month": date_mois, "day": date_jour}
                            taq = {"type": "notAfter", "year": intervalle[1],
                                   "month": date_mois, "day": date_jour}
                        else:
                            tpq = {"type": "notBefore", "year": date[1],
                                   "month": mois.index(intervalle[0]) + 1, "day": None}
                            taq = {"type": "notAfter", "year": date[1],
                                   "month": mois.index(intervalle[1]) + 1, "day": None}
                    else:
                        intervalle = date[0].split("-")
                        tpq = {"type": "notBefore", "year": intervalle[0],
                               "month": date_mois, "day": date_jour}
                        taq = {"type": "notAfter", "year": intervalle[1],
                               "month": date_mois, "day": date_jour}
                else:
                    date_normalisee["date à traiter manuellement"] = "OOOO"
                    print(date)
            elif date[0].isdigit():  # Si la valeur est juste une année
                date_normalisee["annee"], date_normalisee["mois"], date_normalisee["jour"] = int(date[0]), None, None
            elif date[0] in ["undated", "none", "sd"]:  # Si c'est un champ signifiant qu'elle est vide
                date_normalisee["annee"], date_normalisee["mois"], date_normalisee["jour"] = None, None, None
            else:
                date = date[0].split("-")
                if len(date) > 1:  # Si c'est une intervalle
                    if "," in date[1]:
                        mois_intervalle = mois.index(date[1].split(",")[1]) + 1
                    else:
                        mois_intervalle = None
                    tpq = {"type": "notBefore", "year": int(date[0]), "month": mois_intervalle, "day": None}
                    taq = {"type": "notAfter", "year": int(date[1]), "month": mois_intervalle, "day": None}
                else:  # Sinon c'est un truc compliqué
                    date_normalisee["date à traiter manuellement"] = "OOOO"
                    print(date)
            if taq and tpq:
                data_acte["Date-normalisee"] = [tpq, taq]
            else:
                data_acte["Date-normalisee"] = [{"type": "when", "year": date_normalisee["annee"],
                                                 "month": date_normalisee["mois"], "day": date_normalisee["jour"]}]
            if date_normalisee["date à traiter manuellement"] == "OOOO":
                data_acte["Date à traiter manuellement"] = True

with open(result, 'w') as f:
    json.dump(data, f)

from metadata import metadata
metadata(file)
metadata(result)