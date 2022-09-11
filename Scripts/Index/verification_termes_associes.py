from Boîte_a_outils import chemin_actuel, extract_data
import os

'''
Code pour vérifier que les termes associés des entrées d'index ont les mêmes entrées d'inventaire que l'entrée à
laquelle elle se rattache
'''


index = extract_data(os.path.join(chemin_actuel, "index_in_csv.csv"))

entrees = {}
for entree in index[1:]:
    key = entree[1]
    valeur = [e for e in entree]
    entrees[key] = valeur

i = []
for row in index[1:]:
    if row[10] and row[10] != "Not Found" and row[12]:
        nums = row[12].split('|')[:-1]
        renvois = row[10].split()
        for renvoi in renvois:
            if renvoi in entrees:
                nums_bis = entrees[renvoi][12].split('|')[:-1]
                if nums != nums_bis:
                    if row not in i:
                        i.append(row)

for r in i:
    print(r)
print(len(i))