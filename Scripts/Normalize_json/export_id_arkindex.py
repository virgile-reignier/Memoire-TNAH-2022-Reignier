from arkindex import ArkindexClient, options_from_env
import logging, os, csv

chemin_actuel = os.path.dirname(os.path.abspath(__file__))


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


table_actes = {}
for t in extract_data(os.path.join(chemin_actuel,
                                   "Export_stutzmann_himanis_t106_Act_pour_alignement_avec_Arkindex.csv"))[1:]:
    table_actes[t[1]] = t[0]
result = "/home/reignier/Bureau/Himanis/Act_with_id_Arkindex.csv"

# create an arkindex client
ark_client = ArkindexClient()
# logger configuration
logging.basicConfig(
    format="[%(levelname)s] %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


alignement = {}
ark_client.configure(**options_from_env())
i, j = True, 1
while i:
    print("tout va bien")
    acts = ark_client.request('ListElements', corpus='ed249464-96c5-4ca6-a717-f99fc9bf4ce6', type='act',
                                   with_zone=True, with_corpus=False, page_size=500, page=j)
    print(acts["next"], i, j)
    for page in acts["results"]:
        metadata = ark_client.request('ListElementMetaData', id=page["id"])
        for m in metadata:
            if m["name"] == "himanisId":
                himanis_id = m["value"]
                alignement[himanis_id] = page["id"]
    if not acts["next"]:
        i = False
    else:
        j += 1


with open(result, 'w', encoding="utf8", newline='') as f:
    spamwriter = csv.writer(f, delimiter='\t')
    spamwriter.writerow(["Act H-ID", "Arkindex_id"])
    for act in table_actes:
        spamwriter.writerow([table_actes[act], alignement[act]])
