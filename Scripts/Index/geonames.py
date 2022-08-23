import csv, os, requests, json, time
from bs4 import BeautifulSoup
from Boîte_a_outils import chemin_actuel, DEPARTEMENTS, extract_data
from collections import defaultdict

# I - Je définis toutes les variables dont j'ai besoin

file = os.path.join(chemin_actuel, "toponymes_final.csv")
results = os.path.join(chemin_actuel, "geonames.csv")

DEPARTEMENTS_COUVERTS = ["Aude", "Hérault", "Pyrénées-Atlantiques", "Gard", "Hautes-Alpes", "Drôme", "Ardèche",
                         "Loire", "Haute-Loire", "Cantal", "Dordogne", "Ain", "Saône-et-Loire", "Côte d'Or",
                         "Haute-Marne", "Vosges", "Haut-Rhin", "Moselle", "Meurthe-et-Moselle", "Meuse", "Marne", "Aube",
                         "Yonne", "Nièvre", "Cher", "Indre", "Creuse", "Vienne", "Deux-Sèvres", "Loire-Atlantique",
                         "Morbilhan", "Sarthe", "Loir-et-Cher", "Eure-et-Loir", "Eure", "Calvados", "Seine-Maritime",
                         "Pas-de-Calais", "Somme", "Oise", "Aisne"]

CODE_PAYS = [["France", "Belgique", "Grèce", "Israël", "Turquie", "Italie", "Albanie", "Espagne", "Pays-Bas",
              "Angleterre", "Suisse", "Irlande", "Allemagne", "Grande-Bretagne", "Navarre", "Macédoine du Nord",
              "Croatie", "Serbie", "Palestine", "Luxembourg", "Portugal", "Croatie"],
            ["FR", "BE", "GR", "IL", "TR", "IT", "AL", "ES", "NL", "GB",
             "CH", "IE", "DE", "GB", "ES", "MK", "HR", "RS", "PS", "LU", "PT"]]

DEPARTEMENTS_MAJ = [["Côtes-du-Nord", "Loire-Inférieure", "Basses-Pyrénées", "Seine-Inférieure", "Seine"],
                    ["Côtes d'Armor", "Loire-Atlantique", "Pyrénées-Atlantiques", "Seine-Maritime", "Paris"]]

user = '&username=virgile_reignier'

# Extraction des toponymes du csv
data = extract_data(file)
colonnes = data[0] + ["code_insee", "long", "lat", "dicotopo_id / geonames_id",
                      "Proposition(s) retenue(s)", "erreur(s)"]

#data = data[48:50]

# II - Je definis mes fonctions de recherche


def search_dicotopo(nom, dpt, commune=None, search_commune=False):
    '''
    Fonction pour requêter dans l'api dicotopo
    param nom : nom du toponyme qu'on veut chercher
    param commune : permet d'indiquer si on cherche une commune ou non
    return : propositions de localisation ou erreurs
    '''
    erreurs, localisation, propositions, retour = [], [], [], []
    try:
        # 1 - Je requête l'api
        requete = "https://dicotopo.cths.fr/api/1.0/search?query=label:" + nom
        dicotopo = json.loads(requests.get(requete).content)["data"]
        # 2 - Je sélectionne mes données
        if dicotopo:
            # Je crée une boucle pour trouver les entrées de DicoTopo qui concernent le bon département
            for match in dicotopo:
                if int(match["attributes"]["dpt"]) == dpt:
                    propositions.append(match)
            if propositions:
                if search_commune:  # Si je cherche une commune, je cherche son nom exact
                    n = 0
                    while nom != propositions[n]["attributes"]["commune-label"]:
                        n += 1
                        if n == len(propositions):
                            erreurs.append("Nom de commune introuvable dans dicotopo")
                            break
                    else:
                        localisation = [defaultdict(str, propositions[n]["attributes"])]
                else:  # Sinon je récupère toutes les occurences du toponyme
                    if commune != nom and commune != "":  # Si une commune est renseignée, je cherche en fonction
                        n = 0
                        while commune != propositions[n]["attributes"]["commune-label"]:
                            n += 1
                            if n == len(propositions):
                                erreurs.append("Toponyme introuvable dans cette commune dans dicotopo")
                                break
                        else:
                            localisation = [defaultdict(str, propositions[n]["attributes"])]
                    else:
                        communes = []
                        for p in propositions:
                            commune = p["attributes"]["commune-label"]
                            label = p["attributes"]["place-label"]
                            if nom == label:
                                communes = [nom]
                                if not commune:
                                    localisation.append(defaultdict(str, p["attributes"]))
                                elif commune not in communes:
                                    localisation.append(defaultdict(str, p["attributes"]))
                            elif (nom not in communes) and (nom in label.split('-') or nom in label.split(' ')):
                                if not commune:
                                    localisation.append(defaultdict(str, p["attributes"]))
                                elif commune not in communes:
                                    communes.append(commune)
                                    localisation.append(defaultdict(str, p["attributes"]))
            else:  # Si le toponyme n'est pas présent dans le département
                erreurs.append("Aucun retour dans ce département pour dicotopo")
        # 3 - Je structure mes résultats
        if localisation:
            lon, lat = [], []
            for l in localisation:
                if l["longlat"]:
                    lon.append(l["longlat"].split(', ')[0][1:])
                    lat.append(l["longlat"].split(', ')[1][:-1])
                else:
                    lon.append(None)
                    lat.append(None)
            # 4 - Je construit les retours de ma fonction
            retour = [[l["localization-insee-code"] for l in localisation], lon,
                      lat, [("dicotopo", l["place-id"]) for l in localisation]]
            taille = len(localisation)
        elif not erreurs:  # Retour si le résultat est vide
            erreurs.append("Donnée manquante dans dicotopo")
    except:  # Si le serveur ne répond pas
        erreurs.append("Erreur de connexion")
    if retour:
        return erreurs, retour, taille
    else:
        return erreurs, None, 0


def search_commune_in_geonames(nom, pays, dpt):
    '''
    Fonction pour chercher une commune dans l'api geonames
    param nom : nom du toponyme qu'on veut chercher
    param pays : pays dans lequel il se situe
    param dpt : département s'il se situe en France
    return : propositions de localisation ou erreurs
    '''
    localisation, erreurs, retour = [], [], []
    try:
        url = "http://api.geonames.org/postalCodeSearch?placename="
        # 1 - Je construit mes requêtes
        if dpt:
            if dpt == "78":
                requetes = []
                for d in ["78", "91", "92", "93", "94", "95"]:
                    requetes.append(url + nom + "&country=" + pays + "&adminCode2=" + d + user)
            else:
                requetes = [url + nom + "&country=" + pays + "&adminCode2=" + dpt + user]
        else:
            requetes = [url + nom + "&country=" + pays + user]
        for r in requetes:  # 2 - Je les éxécute
            geonames = BeautifulSoup(requests.get(r).content, features="xml")
            if geonames.status:
                time.sleep(3620)
                geonames = BeautifulSoup(requests.get(r).content, features="xml")
            if int(geonames.totalResultsCount.get_text()) > 0:
                data = geonames.find_all('code')
                communes = []
                # 3 - J'ajoute chaque réponse à mon résultat
                for code in data:
                    commune = code.find('name').get_text()   # J'évite d'avoir plusieurs fois la même commune
                    if nom == commune:   # Je vérifie que le résultat correspond bien à ce que je cherche
                        localisation= [code]
                        communes = [nom]
                    elif (nom not in communes and commune not in communes) and (nom in commune.split('-') or nom in commune.split(' ')):
                        localisation.append(code)
                        communes.append(commune)
        # 4 - J'utilise les éléments récupérés pour construire une nouvelle requête et trouver ce qu'il me manque
        if localisation:
            insee, geo_id = [], []
            for l in localisation:
                new_url = "http://api.geonames.org/search?style=FULL&q=" + l.find('postalcode').get_text() + "&name=" \
                          + l.find('name').get_text() + user
                new_data = BeautifulSoup(requests.get(new_url).content, features="xml")
                if new_data.status:
                    time.sleep(3620)
                    new_data = BeautifulSoup(requests.get(r).content, features="xml")
                if int(new_data.totalResultsCount.get_text()) > 0:
                    insee.append(new_data.geoname.find('adminCode4').get_text())
                    geo_id.append(("geonames", new_data.geoname.find('geonameId').get_text()))
                else:  # Retour si le résultat est vide
                    erreurs.append("Problème dans la requête par code postal dans geonames")
            # 5 - Je construit les retours de ma fonction
            retour = [insee, [l.find('lng').get_text() for l in localisation],
                      [l.find('lat').get_text() for l in localisation], geo_id]
            taille = len(localisation)
        elif not erreurs:  # Retour si le résultat est vide
            erreurs.append("Donnée manquante dans geonames")
    except:  # ça c'est pour au cas où il y aurait une erreur dans le retour serveur
        erreurs.append("Erreur de connexion")
    if retour:
        return erreurs, retour, taille
    else:
        return erreurs, None, 0


def search_geonames(nom, commune, pays, dpt):
    '''
    Fonction pour chercher une commune dans l'api geonames
    param nom : nom du toponyme qu'on veut chercher
    param commune : commune dans lequel il se situe
    param pays : pays dans lequel il se situe
    param dpt : département s'il se situe en France
    return : propositions de localisation ou erreurs
    '''
    localisation, erreurs, retour = [], [], []
    try:
        url = "http://api.geonames.org/search?style=FULL&name="
        # 1 - Je construit mes requêtes
        if dpt:
            if dpt == "91":
                requetes = []
                for d in ["91", "92", "93", "94", "95"]:
                    requetes.append(url + nom + "&country=" + pays + "&adminCode2=" + d + user)
            else:
                requetes = [url + nom + "&country=" + pays + "&adminCode2=" + dpt + user]
        else:
            requetes = [url + nom + "&country=" + pays + user]
        if commune:
            for r in requetes:
                r += "q=" + commune
        for r in requetes:  # 2 - Je les éxécute
            geonames = BeautifulSoup(requests.get(r).content, features="xml")
            if geonames.status:
                time.sleep(3620)
                geonames = BeautifulSoup(requests.get(r).content, features="xml")
            if int(geonames.totalResultsCount.get_text()) > 0:
                data = geonames.find_all('geoname')
                communes = []
                # 3 - J'ajoute chaque réponse à mon résultat
                for code in data:
                    nom_geoname = code.find('name').get_text()
                    try:
                        commune = code.find('adminName4').get_text() # J'évite d'avoir plusieurs fois la même commune
                        if nom == nom_geoname:  # Je vérifie que le résultat correspond bien à ce que je cherche
                            localisation.append(code)
                            communes.append(nom)
                        elif (nom not in communes and commune not in communes) and (
                                nom in commune.split('-') or nom in commune.split(' ')):
                            localisation.append(code)
                            communes.append(commune)
                    except:
                        try:
                            nom_francais = code.find('alternateName', lang='fr').get_text()
                            if nom == nom_francais:
                                localisation.append(code)
                        except:
                            try:
                                if nom == code.toponymName.get_text():
                                    localisation.append(code)
                            except:
                                None
        # 4 - Je construit les retours de ma fonction
        if localisation:
            try:
                insee = [l.find('adminCode4').get_text() for l in localisation]
            except:
                insee = None
            retour = [insee, [l.find('lng').get_text() for l in localisation],
                      [l.find('lat').get_text() for l in localisation],
                      [("geonames", l.find('geonameId').get_text()) for l in localisation]]
            taille = len(localisation)
        elif not erreurs:  # Retour si le résultat est vide
            erreurs.append("Donnée manquante dans geonames")
    except:  # ça c'est pour au cas où il y aurait une erreur dans le retour serveur
        erreurs.append("Erreur de connexion")
    if retour:
        return erreurs, retour, taille
    else:
        return erreurs, None, 0

# III Je stocke mes résultats dans un csv


with open(results, 'w', encoding="utf8", newline='') as f:
    spamwriter = csv.writer(f, delimiter='\t')
    spamwriter.writerow(colonnes)
    for toponyme in data[1:]:
        erreurs, dpt_id, proposition, localisation, error, taille = [], None, [], [], [], 0
        pays, dpt = toponyme[5], toponyme[4]
        if pays:
            # 1 - Petit nettoyage / actualisation des données
            pays = CODE_PAYS[1][CODE_PAYS[0].index(pays)]  # Je commence par le nom du pays
            if dpt and pays == "FR":  # Je fais de même avec le département
                if dpt in DEPARTEMENTS_MAJ[0]:
                    dpt = DEPARTEMENTS_MAJ[1][DEPARTEMENTS_MAJ[0].index(dpt)]
                else:
                    dpt = dpt
                dpt_id = str(DEPARTEMENTS.index(dpt) + 1)
                if len(dpt_id) == 1:
                    dpt_id = "0" + dpt_id
            commune = toponyme[7]
            if commune:  # 2 - Je cherche les coordonnées des communes
                erreurs, proposition, taille = search_commune_in_geonames(commune, pays, dpt_id)
                if erreurs and pays == "FR" and dpt in DEPARTEMENTS_COUVERTS:
                    erreurs, proposition, taille = search_dicotopo(commune, int(dpt_id), search_commune=True)
            else:
                erreurs.append("Commune non-renseignée")
            # 3 - Je cherche l'entrée si elle est différente de la commune
            try:
                if toponyme[2].split("(")[1].split(")")[0][0].islower():
                    nom = toponyme[2].split(" (")[0]
                else:
                    nom = toponyme[2][:-1]
            except:
                try:
                    toponyme[2].split(",")[1]
                    nom = toponyme[2].split(",")[0]
                except:
                    nom = toponyme[2][:-1]
            if commune != nom:
                if pays == "FR" and dpt in DEPARTEMENTS_COUVERTS:
                    error, localisation, size = search_dicotopo(nom, int(dpt_id), commune)
                else:
                    error, localisation, size = search_geonames(nom, commune, pays, dpt_id)
            # 4 - Si les recherches par commune ou par entrée renvoient une erreur, alors je cherche la forme retenue
            if (erreurs and not localisation) or (error and not proposition):
                nom = toponyme[3]
                if pays == "FR" and dpt in DEPARTEMENTS_COUVERTS:
                    error, localisation, taille = search_dicotopo(nom, int(dpt_id), commune)
                else:
                    error, localisation, taille = search_geonames(nom, commune, pays, dpt_id)
            # Je récupère les erreurs issues de ces recherches
            for e in error:
                erreurs.append(e)
            # 5 - Si aucune des recherches ne renvoi de résultat, on conserve les coordonnées de la commune
            if not localisation:
                localisation = proposition
                taille = "commune"
        else:
            erreurs.append("Pays non renseigné")
        # 6 - J'ajoute les résultats au fichier retour
        if localisation:
            toponyme_enrichi = [e for e in toponyme]
            toponyme_enrichi.append(localisation[0])
            toponyme_enrichi.append(localisation[1])
            toponyme_enrichi.append(localisation[2])
            toponyme_enrichi.append(localisation[3])
            if type(taille) == str or taille > 1:
                toponyme_enrichi.append(taille)
            else:
                toponyme_enrichi.append(None)
            if len(localisation[3]) > 1:
                erreurs.append("Localisation incertaine")
            if erreurs:
                toponyme_enrichi.append(erreurs)
            spamwriter.writerow(toponyme_enrichi)
        else:
            # Si j'ai pas de résultats, j'indique pourquoi
            rep_vide = toponyme + ["", "", "", "", ""]
            rep_vide.append(erreurs)
            spamwriter.writerow(rep_vide)