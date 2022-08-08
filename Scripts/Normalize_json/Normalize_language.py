import json

file = "/home/reignier/Bureau/Himanis/himanis-all-acts-json-JJ35-JJ91-metadata-htr_with_date.json"
result = "/home/reignier/Bureau/Himanis/himanis-all-acts-json-JJ35-JJ91-metadata-htr_with_date_and_language_final.json"

with open(file, 'r') as f:
    data = json.load(f)

for registre in data:
    contenu_registre = data[registre]
    for serie in contenu_registre:
        for acte in serie:
            data_acte = serie[acte]
            language = data_acte["Language"].lower()
            if language in ["fr.", "fr. fr.", "fr", "fr. ", "francais", "fra", "français"]:
                language = {"norme": "iso-639-3", "language": ["frm"]}
            elif language in ["lat.", "lat", "lat. lat.", "lat..", "lat.?", "Latin", "latin"]:
                language = {"norme": "iso-639-3", "language": ["lat"]}
            elif language in ["lat. fr.", "lat.fr.", "lat. et fr.", "lat. et français", "lat. et français.",
                              "LatinÂ ?français", "Latinfrançais", "latin fra", "latinfrançais",
                              "latinâ ?français", "fr. et latin"]:
                language = {"norme": "iso-639-3", "language": ["lat", "frm"]}
            elif language in ["", " "]:
                language = {"norme": "iso-639-3", "language": ["und"]}
            elif language == "lat. fr.langue d'oc":
                language = {"norme": "iso-639-3", "language": ["lat", "frm", "pro"]}
            data_acte["normalized_language"] = language

# Sur la norme iso : https://lorexplor.istex.fr/Wicri/Linguistique/fr/index.php/Liste_des_codes_ISO_639-2

with open(result, 'w') as f:
    json.dump(data, f)

from metadata import metadata
metadata(file)
metadata(result)
