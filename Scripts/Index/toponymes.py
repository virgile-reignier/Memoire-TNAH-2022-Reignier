import csv, os
from Boîte_a_outils import DEPARTEMENTS, PAYS, chemin_actuel

file = os.path.join(chemin_actuel, "index_to_csv.csv")
results = os.path.join(chemin_actuel, "toponymes.csv")

# Extraction du csv des lignes dont on veut chercher les références et suppression les doublons issues des sous-entrées
with open(file, 'r', encoding="utf8") as f:
    spamreader = csv.reader(f, delimiter='\t')
    noms = []
    data = []
    for row in spamreader:
        if row[2] == 'place':
            name = row[0].split(' , — ')[0]
            if name not in noms:
                noms.append(name)
                data.append(row)

# Code pour structurer les entrées en fonction des éléments géographiques qu'elles contiennent
localités = []
for name in data:
    description = []
    situation = {"entrée_complète": name[0], "id": name[1]}
    # On différencie l'entrée de la forme retenue du nom qu'on modifiera par la suite
    try:
        situation["entrée"] = name[0].split("[")[0]
        nom_normalise = name[0].split(" [")[0]
    except:
        situation["entrée"], nom_normalise = name[0]
    # On élimine de cette forme retenue les détails qui peuvent être proposés
    try:
        nom_normalise = nom_normalise.split(",")[0]
    except:
        None
    # On insère la particule devant le nom pour la forme retenue
    try:
        particule = nom_normalise.split("(")[1].split(")")[0]
        if particule[0].isupper():
            if "'" in particule or "’" in particule:
                nom_normalise = particule + nom_normalise.split(" (")[0]
            else:
                nom_normalise = particule + " " + nom_normalise.split(" (")[0]
    except:
        None
    try:
        #Puis on découpe la description à partir des virgules
        localisation = name[0].split("[")[1].split("]")[0].split(", ")
        #On traite le cas où la description ne commence pas par un nom de département
        premiere_indication = localisation[0]
        p = premiere_indication[0]
        if premiere_indication not in DEPARTEMENTS and premiere_indication not in PAYS:
            #Cas où le premier mot vient en complément de l'entrée
            if p == "-":
                nom_normalise = nom_normalise + localisation[0]
            #Cas où le premier mot est une normalisation de l'entrée
            elif p.isupper():
                nom_normalise = localisation[0]
            #Cas où il s'agit d'une actualisation
            elif premiere_indication[:4] == "auj." and premiere_indication[5].isupper():
                nom_normalise = localisation[0].split("auj. ")[1]
            #Autres cas
            else:
                description.append(localisation[0])
        situation["nom_normalise"] = nom_normalise
        #On traite chacun des éléments présents dans la localosation
        for mot in localisation:
            #On par regarder s'il s'agit d'un département
            if mot in DEPARTEMENTS:
                situation["département"] = mot
                situation["pays"] = "France"
            #Puis on regarde s'il s'agit d'un pays
            elif mot in PAYS:
                situation["pays"] = mot
            elif "cne " in mot or "ar. " in mot or "prov. " in mot or "con " in mot or "cnes " in mot or "cons " in mot:
                #On cherche la commune
                try:
                    situation["commune"] = mot.split("cnes ")[1].replace(" ?", "").replace("?", "")
                except:
                    try:
                        situation["commune"] = mot.split("cne ")[1].replace(" ?", "").replace("?", "")
                    except:
                        None
                #Puis le canton
                try:
                    situation["canton"] = mot.split("cons ")[1].replace(" ?", "").replace("?", "")
                except:
                    try:
                        situation["canton"] = mot.split("con ")[1].replace(" ?", "").replace("?", "")
                        try:
                            situation["canton"] = situation["canton"].split("cne ")[1]
                        except:
                            None
                    except:
                        None
                #Puis l'arrondissement
                try:
                    situation["arrondissement"] = mot.split("ar. ")[1].replace(" ?", "").replace("?", "")
                    try:
                        situation["arrondissement"] = situation["arrondissement"].split("con ")[1]
                    except:
                        None
                except:
                    None
                #Et enfin la province
                try:
                    situation["province"] = mot.split("prov. ")[1]
                except:
                    None
            elif mot == "incertain" or "?" in mot:
                #On rentre aussi les éléments d'incertitude
                situation["incertitude"] = "Oui"
            elif mot not in description and mot not in situation.values() and mot != premiere_indication:
                # On rejete tout ce qui ne rentre pas ailleurs dans une variable
                description.append(mot)
            #J'utilise ces mots séparateurs pour mettre en valeur les éléments compris entre plusieurs entités
            #Ou les incertitudes qu'il me faut rentrer deux fois
            if "et " in mot:
                situation["etendue"] = "Oui"
            if "ou " in mot:
                situation["A doublonner"] = "Oui"
        # Dans les cas où la commune n'est pas précisée, on estime d'office qu'il s'agit du nom retenu
        # sauf si l'on dispose d'une indication particuilière sur sa nature
        try:
            situation["commune"] or situation["détail"]
        except:
            try:
                if nom_normalise.split("(")[1].split(")")[0][0].isupper():
                    situation["commune"] = nom_normalise
            except:
                situation["commune"] = nom_normalise
        #Pour entrer notre variable qui sert à tout
        if description:
            situation["description"] = description
        #Pour visualiser mes problèmes qui n'ont pas été encodés par ailleurs!
        '''if len(description) > 2:
            print(situation["entrée_complète"])
            print(situation["description"])'''
    except:
        #On a toute façon besoin de rentrer la forme normalisée du nom
        situation["nom_normalise"] = nom_normalise
    #Pour finir on ajoute tous ces éléments à la liste des entités
    localités.append(situation)


#On insère les données dans un CSV
from Boîte_a_outils import dicts_to_csv
dicts_to_csv(localités, results)