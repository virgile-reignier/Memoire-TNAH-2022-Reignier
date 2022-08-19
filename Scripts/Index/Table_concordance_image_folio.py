from arkindex import ArkindexClient, options_from_env
import logging, csv

'''
Script pour requêter automatiquement toutes les éléments page d'un corpus Arkindex et associer le nom de l'élément avec
le nom du fichier image qui correspond à cet élément.
'''

# result = "/home/reignier/Bureau/Himanis/table_concordance_images_folio.csv"
result = "/home/reignier/Bureau/Himanis/erreurs_alignement_arkindex.csv"

# create an arkindex client
ark_client = ArkindexClient()
# logger configuration
logging.basicConfig(
    format="[%(levelname)s] %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main():
    with open(result, 'r', encoding="utf8") as f:
        spamreader = csv.reader(f, delimiter='\t')
        file = []
        for row in spamreader:
            file.append(row)
    with open(result, 'w', encoding="utf8", newline='') as f:
        spamwriter = csv.writer(f, delimiter='\t')
        for row in file:
            spamwriter.writerow(row)
        for i in range(1, 159):
            image_folio = {}
            # log in on arkindex with your credentials
            ark_client.configure(**options_from_env())
            for page in ark_client.request('ListElements', corpus='ed249464-96c5-4ca6-a717-f99fc9bf4ce6', type='page',
                                               with_zone=True, with_corpus=False, page_size=500, page=i)['results']:
                image_folio[page['zone']['image']['url']] = page['name']
            for url in image_folio:
                spamwriter.writerow([url, image_folio[url]])


if __name__ == '__main__':
    main()
