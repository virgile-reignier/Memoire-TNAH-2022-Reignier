import csv, os

chemin_actuel = os.path.dirname(os.path.abspath(__file__)).replace('python', 'Inventaires_index')

DEPARTEMENTS = ["Ain", "Aisne", "Allier", "Alpes-de-Haute-Provence", "Hautes-Alpes", "Alpes-Maritimes", "Ardèche", "Ardennes",
                "Ariège", "Aube", "Aude", "Aveyron", "Bouches-du-Rhône", "Calvados", "Cantal", "Charente", "Charente-Maritime",
                "Cher", "Corrèze", "Corse", "Côte-d'Or", "Côtes d'Armor", "Creuse", "Dordogne", "Doubs", "Drôme", "Eure", "Eure-et-Loir",
                "Finistère", "Gard", "Haute-Garonne", "Gers", "Gironde", "Hérault", "Ille-et-Vilaine", "Indre", "Indre-et-Loire",
                "Isère", "Jura", "Landes", "Loir-et-Cher", "Loire", "Haute-Loire", "Loire-Atlantique", "Loiret", "Lot",
                "Lot-et-Garonne", "Lozère", "Maine-et-Loire", "Manche", "Marne", "Haute-Marne", "Mayenne", "Meurthe-et-Moselle",
                "Meuse", "Morbihan", "Moselle", "Nièvre", "Nord", "Oise", "Orne", "Pas-de-Calais", "Puy-de-Dôme", "Pyrénées-Atlantiques",
                "Hautes-Pyrénées", "Pyrénées-Orientales", "Bas-Rhin", "Haut-Rhin", "Rhône", "Haute-Saône", "Saône-et-Loire",
                "Sarthe", "Savoie", "Haute-Savoie", "Paris", "Seine-Maritime", "Seine-et-Marne", "Seine-et-Oise", "Deux-Sèvres",
                "Somme", "Tarn", "Tarn-et-Garonne", "Var", "Vaucluse", "Vendée", "Vienne", "Haute-Vienne", "Vosges", "Yonne",
                "Territoire-de-Belfort", "Yvelines", "Seine", "Seine-Inférieure", "Loire-Inférieure", "Basses-Pyrénées",
                "Côtes-du-Nord"]

PAYS = ["Grèce", "Israël", "Turquie", "Italie", "Albanie", "Belgique", "Espagne", "Pays-Bas", "Angleterre", "Saint-Empire Romain Germanique",
        "Suisse", "Irlande", "Yougoslavie", "Palestine", "Allemagne", "Empire de Constantinople", "Portugal", "Luxembourg",
        "Grande-Bretagne", "Navarre", "Chypre", "Macédoine du Nord", 'Croatie', "Egypte", "Serbie"]


def extract_data(file):
    '''
    :param file : file to extract
    return : list of row contains in this file
    '''
    with open(file, 'r', encoding="utf8") as f:
        spamreader = csv.reader(f, delimiter='\t')
        data = []
        for row in spamreader:
            data.append(row)
    return data


def dicts_to_csv(dicts, file):
    '''
    :param dicts: list of dictionnaries
    :param file: path for file
    :return: Save dictionnaries from dict to file
    '''
    with open(file, 'w', encoding="utf8", newline='') as f:
        spamwriter = csv.writer(f, delimiter='\t')
        keys = []
        for dict in dicts:
            for key in dict.keys():
                if key not in keys:
                    keys.append(key)
        spamwriter.writerow(keys)
        for dict in dicts:
            row = []
            for column in keys:
                try:
                    row.append(dict[column])
                except:
                    row.append("")
            spamwriter.writerow(row)