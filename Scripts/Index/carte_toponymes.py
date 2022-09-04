import folium, os
from Boîte_a_outils import chemin_actuel, extract_data
from folium.plugins import HeatMap
import pandas as pd

index = os.path.join(chemin_actuel, "Paris_AN_JJ_inventaire_JJ37-50_index.xlsx")
file = os.path.join(chemin_actuel, "geonames_final.csv")
carte1 = os.path.join(chemin_actuel, "carte_avec_Paris.html")
carte2 = os.path.join(chemin_actuel, "carte_sans-Paris.html")
carte3 = os.path.join(chemin_actuel, "carte_sans_Paris_avec_points.html")
map_osm = folium.Map(location=[48.85, 2.34], zoom_start=5)

# I/ Extraction des données sources

# Je commence par extraire les données structurées sur chaque toponyme pour les ranger dans un doctionnaire

data = extract_data(file)
coordonnees = {}
for row in data[1:]:
    key = row[1]
    valeur = [e for e in row]
    coordonnees[key] = valeur

# Puis j'extrais mes entrées d'index et les range dans un dictionnaire

entrees_xl = pd.read_excel(index)
entrees, index = {}, []
for entree in entrees_xl.index:
    index.append([entrees_xl.loc[entree][h] for h in entrees_xl.head()])
    entrees[entrees_xl.loc[entree]["xml:id"]] = [entrees_xl.loc[entree][h] for h in entrees_xl.head()]

# II/ Liaison entre entités et coordonnées

# Je commence par associer chaque entité de lieu de l'index avec le toponyme enrichi qui lui correspond
data_for_map = []
for entree in index:
    if entree[2] == 'place':
        eac = entree_avec_coordonnees = {}
        eac["entree"], eac["id"] = entree[0], entree[1]  # Je conserve les attributs principaux
        eac["forme retenue"] = entree[0].split(" , — ")[-1]
        occurences = []  # J'extrait le nombre d'occurence de chaque entrée dans l'inventaire
        if str(entree[12]) != "nan":
            for o in entree[12].split('|'):
                occurences.append(o)
        eac["nombre_occurences"] = len(occurences) - 1
        eac["id-retenu"] = eac["id"]
        while eac["id-retenu"] not in coordonnees and eac["id-retenu"] != "":
            # Si l'entrée ne dispose pas de coordonnée, je cherche dans son entrée générique
            eac["id-retenu"] = entree[7]
            entree = entrees[eac["id-retenu"]]
        point = coordonnees[eac["id-retenu"]]  # Puis je récupère les coordonnées
        eac["lon"], eac["lat"], eac["etendue"] = point[15], point[16], point[8]
        if eac["id"] == eac["id-retenu"]:  # Je simplifie l'entrée pour créer des étiquettes
            eac["forme retenue"] = point[2][:-1]
        else:
            eac["forme retenue"] = point[2][:-1] + " (" + eac["forme retenue"] + ")"
        data_for_map.append(eac)

# Puis j'en extrais les points à afficher sur la carte
points = []
for line in data_for_map:  # Je crée un point pour chaque proposition de situation
    longitude = []
    if line["lon"]:
        for t in line["lon"].split(','):
            if "None" not in t:
                longitude.append(t.split("'")[1])
    latitude = []
    if line["lat"]:
        for t in line["lat"].split(','):
            if "None" not in t:
                latitude.append(t.split("'")[1])
    if line["etendue"] and longitude:
        longitude = [sum([float(l) for l in longitude])/len(longitude)]
        latitude = [sum([float(l) for l in latitude])/len(latitude)]
    for a in latitude:
        p = [line["forme retenue"], a, longitude[latitude.index(a)], (line["nombre_occurences"]/len(latitude)), line["nombre_occurences"]]
        points.append(p)

# III/ Création des cartes

# Je commence par celle avec Paris

points_chaleur = [[], [], []]
for c in points:
    points_chaleur[0].append(c[1]), points_chaleur[1].append(c[2]), points_chaleur[2].append(c[3])
heatmap = HeatMap(list(zip(points_chaleur[0], points_chaleur[1], points_chaleur[2])),
                   min_opacity=0.20,
                   radius=40, blur=20,
                   max_zoom=1)
heatmap.add_to(map_osm)
map_osm.save(carte1)

# Puis celle sans Paris

points_chaleur = [[], [], []]
for point in points:
    if "Paris" not in point[0]:
        points_chaleur[0].append(point[1]), points_chaleur[1].append(point[2]), points_chaleur[2].append(point[3])
heatmap = HeatMap(list(zip(points_chaleur[0], points_chaleur[1], points_chaleur[2])),
                   min_opacity=0.20,
                   radius=40, blur=20,
                   max_zoom=1,
                   name="Heatmap",
                   control=True,
                   show=False)
heatmap.add_to(map_osm)
map_osm.save(carte2)

# Et j'y ajoute les points

for point in points:
    if point[4] > 0 and "Paris" not in point[0]:
        folium.Marker(location=point[1:3], popup=point[0] + "\n Nombre d'occurences : " + str(point[4])).add_to(map_osm)
# folium.LayerControl().add_to(map_osm). Je ne sais pas gérer cette fonctionalité mais elle supprime bien la couche créée
map_osm.save(carte3)

