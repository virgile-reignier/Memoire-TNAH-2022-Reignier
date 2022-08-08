import json
import csv

json_file = "/home/reignier/Bureau/Himanis/himanis-all-acts-json-JJ35-JJ91-metadata-htr_with_date_language_index.json"

#index = []
erreurs = []

def metadata(file):
    with open(file, 'r') as f:
        data = json.load(f)

    metadata = {}
    for registre in data:
        for r in data[registre]:
            for s in r:
                acte = r[s]
                for meta in acte:
                    meta = meta + "-" + str(type(acte[meta]))  # J'associe chaque méta-donnée à son type
                    if meta == "Text_Region-<class 'list'>":  # Je récupère les métadonnées contenues dan les text_region
                        for t in acte["Text_Region"]:
                            if "https://iiif.irht.cnrs.fr" not in t["Address_bvmm"]:
                            # Pour identifier les éléments anormaux dans cette donnée
                                erreurs.append(acte)
                            for a in t:
                                a = "Text_region_" + a + str(type(t[a]))
                                if a == "Text_region_Texte<class 'list'>":  # Je vérifie que ces éléments sont des chaînes
                                    for text in t["Texte"]:
                                        if type(text) != str:
                                            print("erreur")
                                    a = a + "_str"
                                if a not in metadata:  # Je crée aussi une entrée pour ces variables
                                    metadata[a] = 1
                                else:
                                    metadata[a] += 1
                    '''if meta == "Provisory_index_1-<class 'str'>":
                        index.append(int(acte["Provisory_index_1"].split("bis")[0]))'''
                    '''if meta == "Provisory_index_1-<class 'str'>": 
                        # Pour vérifier si la donnée est systématiquement pleine
                        if not acte["Provisory_index_1"]:
                            meta = "Provisory_index_1-<class 'str'>_empty"
                        else:
                            meta = "Provisory_index_1-<class 'str'>_full"'''
                    # if meta == "Language-<class 'str'>": # Pour compter les langues mentionnées
                    #    meta = acte["Language"]
                    if meta not in metadata:  # Je crée une entrée par type de métadonnée
                        metadata[meta] = 1
                    else:
                        metadata[meta] += 1
    for m in metadata:
        print(m, metadata[m])


metadata(json_file)

with open("/home/reignier/Bureau/Himanis/zone_images_vides.csv", 'w', encoding="utf8", newline='') as f:
    spamwriter = csv.writer(f, delimiter='\t')
    for e in erreurs:
        spamwriter.writerow([e["Volume"], e["Folio_start"], e["Provisory_index_3"], [t["Address_bvmm"] for t in e["Text_Region"]]])



'''erreurs = [("Act_N", "Volume + Folio_start", "VOL_FOL_START")]
for registre in data:
    for r in data[registre]:
        for s in r:
            acte = r[s]
            if acte["VOL_FOL_START"] != acte["Volume"] + "_" + acte["Folio_start"]:
                erreurs.append((acte["Act_N"], acte["Volume"] + "_" + acte["Folio_start"], acte["VOL_FOL_START"]))

with open("/home/reignier/Bureau/Himanis/incoherences.csv", 'w', encoding="utf8", newline='') as f:
    spamwriter = csv.writer(f, delimiter='\t')
    for e in erreurs:
        spamwriter.writerow(e)'''

'''erreurs = [("ImageStart_UPVLC_BVMM", "ImageStart_READ")]
for registre in data:
    for r in data[registre]:
        for s in r:
            acte = r[s]
            if acte["F"] != "":
                erreurs.append((acte["ImageStart_UPVLC_BVMM"]))

with open("/home/reignier/Bureau/Himanis/incoherences_2.csv", 'w', encoding="utf8", newline='') as f:
    spamwriter = csv.writer(f, delimiter='\t')
    for e in erreurs:
        spamwriter.writerow(e)'''

"""index.sort()  # To know if provisory index are systematic or not
t = 1
for i in index:
    if int(i) == t:
        t +=1
    else:
        print(i)
        t = int(i) + 1"""